#pragma once
#include <string>
#include <sys/socket.h>
#include <unistd.h>
#include <deque>
#include "database.hpp"

namespace crcs
{
    const int ERR_TIMEOUT = 1;
    class connection
    {
    protected:
        int sock;
        database conn_db;
        std::string session_id;
        std::deque<std::string> message_queue;
    public:
        connection(int s, std::string db_host, std::string db_user,
                   std::string db_passwd, std::string db_name,
                   unsigned db_port) :
                   sock(s), conn_db(db_host, db_user, db_passwd,
                   db_name, db_port)
        {}
                   
        void close_connection()
        {
            shutdown(sock, SHUT_RDWR);
            close(sock);
        }
        
        virtual int send_message(std::string &msg)
        {
            write(sock, msg.c_str(), msg.length()+1);
            return 0;
        }
        
        virtual int recv_message(std::string &msg)
        {
            char buff[2] {};
            unsigned counter {};
            do
            {
                read(sock, buff, 1);
                msg += buff;
                if(counter >= 1000)
                    return ERR_TIMEOUT;
            }while(buff[0] != '}');
            return 0;
        }
    };
}
