#include <algorithm>
#include <iostream>
#include <vector>
#include <list>
#include <json/json.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>
#include "headers/listener.hpp"
#include "headers/database.hpp"
#include "headers/admin_connection.hpp"
#include "headers/host_connection.hpp"

std::string DB_HOSTNAME = "localhost";
std::string DB_USERNAME = "root";
std::string DB_PASSWORD = "qwerty";
std::string DB_DBNAME = "crcs_db";
int DB_PORT = 3306;

/*////////////////////////////////////////
// TODO:                                //
// - сделать таймаут соединений         //
// - ограничить количество сессий       //
// - автоматическое удаление сессий     //
//   по истечении опред. времени        //
// - реализовать чтение конфига         //
////////////////////////////////////////*/
// /ᐠ - ˕ - ﾏ
std::list<crcs::host_connection*> active_hosts;
void* admin_connection_handler(void* param)
{
    crcs::admin_connection adm_conn(*static_cast<int*>(param), DB_HOSTNAME,
                                    DB_USERNAME, DB_PASSWORD, DB_DBNAME, DB_PORT);
    Json::Value data;
    Json::Reader reader;
    unsigned response;
    std::string resp_data = "null";
    std::string message;
    
    response = adm_conn.recv_message(message);
    
    if(response == crcs::ERR_INVALID_PACKET)
    {
        adm_conn.close_connection();
        delete static_cast<int*>(param);
        pthread_exit(0);
    }
    
    reader.parse(message, data);
    
    if(data["op_type"] == std::string("reg"))
    {
        std::string login = data["login"].asString();
        std::string password = data["password"].asString();
        std::string email = data["email"].asString();
        response = adm_conn.register_admin(login, password, email);
        
    }
    else if(data["op_type"] == std::string("auth"))
    {
        std::string login = data["login"].asString();
        std::string password = data["password"].asString();
        response = adm_conn.authenticate(login, password, resp_data);
        resp_data = std::string("\"") + resp_data;
        resp_data.push_back('"');
    }
    
    else if(data["op_type"] == std::string("server"))
    {
        std::string request = data["request"].asString();
        std::string sid = data["sessionuid"].asString();
        std::string additional_data = data["additional_data"].asString();
        if(request == std::string("CREATE_POOL"))
            response = adm_conn.create_pool(sid);
        if(request == std::string("GET_ADMIN_POOLS"))
        {
            std::vector<std::string> pools;
            response = adm_conn.get_admin_pools(sid, pools);
            resp_data = "[";
            for(int i {}; i < (static_cast<int>(pools.size()) - 1); i++)
            {
                resp_data += pools[i] + ", ";
            }
            if(pools.size() != 0)
                resp_data += pools.back();
            resp_data += "]";
        }
        else if(request == std::string("GET_POOL_MEMBERS"))
        {
            std::vector<std::string> members;
            response = adm_conn.get_pool_members(sid, additional_data, members);
            resp_data = "[";
            int i {};
            for(; i < (static_cast<int>(members.size()) - 2); i += 2)
            {
                resp_data += "{\"hostname\": " + members[i] + ", \"host_id\": " + members[i+1] + "}" + ", ";
            }
            if(members.size() != 0)
                resp_data += "{\"hostname\": " + members[i] + ", \"host_id\": " + members[i+1] + "}";
            resp_data += "]";
        }
        else if(data["request"] == std::string("DESTROY_POOL"))
        {
            response = adm_conn.delete_pool(sid, additional_data);
        }
    }
    else if(data["op_type"] == std::string("command"))
    {
        std::string command = data["command"].asString();
        std::string sid = data["sessionuid"].asString();
        std::string reciever = data["reciever"].asString();
        std::string pool = data["pool"].asString();
        std::vector<std::string> pools;
        response = adm_conn.get_admin_pools(sid, pools);
        if(reciever == std::string("broadcast"))
        {
            std::vector<std::string>::iterator p = find(pools.begin(), pools.end(), pool);
            if(pools.end() != p || pools.back() == pool)
            {
                std::list<crcs::host_connection*>::iterator it=active_hosts.begin();
                if(!active_hosts.empty())
                    do
                    {
                        if((*it)->get_pool_id() == pool)
                        {
                            std::string packet = static_cast<std::string>("{\"op_type\": \"command\", ") +
                                                 "\"command\": " + command + "\"}";
                            (*it)->send_message(packet);
                        }
                        it++;
                    }while(it != active_hosts.end());
                response = 0;
            }
            else
                response = crcs::ERR_POOL_ACCESS_DENIED;
        }
        else
        {
            std::string hkey = data["reciever"].asString();
            std::list<crcs::host_connection*>::iterator it=active_hosts.begin();
            if(!active_hosts.empty() && !pools.empty())
                do
                {
                    if((*it)->get_host_key() == hkey)
                    {
                        std::string packet = static_cast<std::string>("{\"op_type\": \"command\", ") +
                                             "\"command\": " + command + "\", \"verbose\": \"true\"}";
                        (*it)->send_message(packet);
                        packet = "";
                        (*it)->recv_message(packet);
                        adm_conn.send_message(packet);
                        break;
                    }
                    it++;
                }while(it != active_hosts.end());
        }
    }
    
    std::string resp;
    
    switch(response)
    {
        case crcs::ERR_INVALID_CREDINTAILS:
            resp = static_cast<std::string>("{\"code\": \"error\", ") +
                               "\"comment\": \"Invalid credintails\", "
                               "\"data\": null}"; break;
        case crcs::ERR_DATABASE:
            resp = static_cast<std::string>("{\"code\": \"error\", ") +
                               "\"comment\": \"Database error\", "
                               "\"data\": null}"; break;
        case crcs::ERR_LOGIN_IS_USED:
            resp = static_cast<std::string>("{\"code\": \"error\", ") +
                               "\"comment\": \"Login is already used\", "
                               "\"data\": null}"; break;
        case crcs::ERR_INVALID_SESSION:
            resp = static_cast<std::string>("{\"code\": \"error\", ") +
                               "\"comment\": \"Invalid session\", "
                               "\"data\": null}"; break;
        case crcs::ERR_CREATE_POOL:
            resp = static_cast<std::string>("{\"code\": \"error\", ") +
                               "\"comment\": \"Can not create pool\", "
                               "\"data\": null}"; break;
        case crcs::ERR_HOST_ACCESS_DENIED:
            resp = static_cast<std::string>("{\"code\": \"error\", ") +
                               "\"comment\": \"Access to host denied\", "
                               "\"data\": null}"; break;
        case crcs::ERR_POOL_ACCESS_DENIED:
            resp = static_cast<std::string>("{\"code\": \"error\", ") +
                               "\"comment\": \"Access to pool denied\", "
                               "\"data\": null}"; break;
        case 0:
            resp = static_cast<std::string>("{\"code\": \"success\", ") +
                               "\"comment\": null, "
                               "\"data\": " + resp_data + "}"; break;
        default: resp = "No response";
    }
    
    adm_conn.send_message(resp);
    
    adm_conn.close_connection();
    delete static_cast<int*>(param);
    pthread_exit(0);
}

void* host_connection_handler(void* param)
{
    unsigned resp_code;
    std::string resp_data = "null";
    
    crcs::host_connection* hst_conn = new crcs::host_connection(*static_cast<int*>(param), DB_HOSTNAME,
                                                                DB_USERNAME, DB_PASSWORD, DB_DBNAME, DB_PORT);
    Json::Value data;
    Json::Reader reader;
    std::string message;
    resp_code = hst_conn->recv_message(message);
    reader.parse(message, data);
    
    if(data["op_type"] == std::string("init"))
    {
        std::string hname = data["hostname"].asString();
        std::string pid = data["pool_id"].asString();
        std::string ip = "NULL"; // TODO: make a normal ip handling
        resp_code = hst_conn->init(hname, pid, ip, resp_data);
        resp_data = std::string("\"") + resp_data;
        resp_data.push_back('"');
    }
    else if(data["op_type"] == std::string("connect"))
    {
        std::string hkey = data["host_id"].asString();
        if(!(resp_code = hst_conn->connect(hkey)))
            active_hosts.push_back(hst_conn);
    }
    
    std::string response;
    
    switch(resp_code)
    {
        case crcs::ERR_INVALID_KEY:
            response = static_cast<std::string>("{\"code\": \"error\", ") +
                               "\"comment\": \"Invalid host key\", "
                               "\"data\": " + resp_data + "}"; break;
        case crcs::ERR_DATABASE:
            response = static_cast<std::string>("{\"code\": \"error\", ") +
                               "\"comment\": \"Error in database\", "
                               "\"data\": " + resp_data + "}"; break;
        default:
            response = static_cast<std::string>("{\"code\": \"success\", ") +
                               "\"comment\": null, "
                               "\"data\": " + resp_data + "}"; break;
    }
    hst_conn->send_message(response);
    if(data["op_type"] == std::string("init"))
       hst_conn.close_connection();
//    char buff;
//    while(recv(*(int*)param, &buff, 1, MSG_PEEK | MSG_DONTWAIT))
//    {
//        if(errno == ENOTCONN)
//            break;
//    }
    pthread_exit(0);
}

int main()
{
    std::list<pthread_t> admins;
    std::list<pthread_t> hosts;
    crcs::listener admin_listen(9090, true);
    crcs::listener host_listen(9091, false);
    if(admin_listen.init() != 0)
    {
        std::cerr << "Error init listening" << std::endl;
        std::cerr << errno << std::endl;
        exit(1);
    }
    host_listen.init();

    while(true)
    {
        unsigned last_error;
        int newconn;
        if((last_error = admin_listen.get_first_unhandled(newconn)))
        {
            // TODO: реализовать логирование ошибок
        }
        else
        {
            pthread_t new_thread;
            int* conn = new int;
            *conn = newconn;
            pthread_create(&new_thread, NULL, admin_connection_handler, conn);
            admins.push_back(new_thread);
        }

        if((last_error = host_listen.get_first_unhandled(newconn)))
        {
            // TODO: реализовать логирование ошибок
        }
        else
        {
            pthread_t new_thread;
            int* conn = new int;
            *conn = newconn;
            pthread_create(&new_thread, NULL, host_connection_handler, conn);
            admins.push_back(new_thread);
        }
    }
}
