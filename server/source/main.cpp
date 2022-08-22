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
// - получение количества хостов в пуле //
////////////////////////////////////////*/

std::list<crcs::host_connection> active_hosts;
void* admin_connection_handler(void* param)
{
    crcs::admin_connection adm_conn(*static_cast<int*>(param), DB_HOSTNAME,
                                    DB_USERNAME, DB_PASSWORD, DB_DBNAME, DB_PORT);
    Json::Value data;
    Json::Reader reader;
    std::string message;
    adm_conn.recv_message(message);
    reader.parse(message, data);
    
    unsigned response;
    std::string resp_data = "null";
    
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
        }
        if(request == std::string("GET_POOL_MEMBERS"))
        {
            std::vector<std::string> members;
            response = adm_conn.get_pool_members(sid, additional_data, members);
        }
        if(request == std::string("get_pool_members"))
        {
            
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
        case 0:
            resp = static_cast<std::string>("{\"code\": \"success\", ") +
                               "\"comment\": null, "
                               "\"data\": " + resp_data + "}"; break;
        default: resp = "No response";
    }
    
    adm_conn.send_message(resp);
    
    adm_conn.close_connection();
    delete static_cast<int*>(param);
}

void* host_connetion_handler(void* param)
{
    crcs::admin_connection adm_conn(*static_cast<int*>(param), DB_HOSTNAME,
                                    DB_USERNAME, DB_PASSWORD, DB_DBNAME, DB_PORT);
    Json::Value data;
    Json::Reader reader;
    std::string message;
    adm_conn.recv_message(message);
    reader.parse(message, data);
    
    if(data["op_type"] == std::string("init"))
    {
        std::string hname = data["hostname"].asString();
        std::string pid = data["pool_id"].asString();
    }
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
            pthread_create(&new_thread, NULL, admin_connection_handler, conn);
            admins.push_back(new_thread);
        }
    }
}
