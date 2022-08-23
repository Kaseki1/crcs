#pragma once

#include <deque>
#include <random>
#include "connection.hpp"
#include "database.hpp"

namespace crcs
{
    class host_connection : public connection
    {
    private:
        unsigned pool_id;
        std::deque<std::string> messages;
        std::string gen_hkey();
    public:
        host_connection(int s, std::string db_host, std::string db_user, std::string db_passwd, std::string db_name, unsigned db_port) : 
                         connection(s, db_host, db_user, db_passwd, db_name, db_port)
        {
            if(conn_db.connect() != 0)
                std::cout << "failed to connect db" << std::endl;
        }

        int init(std::string hname, std::string pid, std::string ip, std::string& hkey);
        int connect(std::string hid);
        int get_hid(std::string& hid);
        int get_command(std::string& command);
        int push_command(std::string command);
        
        ~host_connection()
        {
            conn_db.disconnect();
        }
    };
}