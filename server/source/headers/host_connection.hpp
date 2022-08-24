#pragma once

#include <deque>
#include <random>
#include "connection.hpp"
#include "database.hpp"

namespace crcs
{
    const int ERR_INVALID_KEY = 3;
    
    class host_connection : public connection
    {
    private:
        std::string pool_id;
        std::string hostname;
        std::string gen_hkey();
    public:
        host_connection(int s, std::string db_host, std::string db_user, std::string db_passwd, std::string db_name, unsigned db_port) : 
                         connection(s, db_host, db_user, db_passwd, db_name, db_port)
        {
            if(conn_db.connect() != 0)
                std::cout << "failed to connect db" << std::endl;
        }

        std::string get_pool_id()
        {
            return pool_id;
        }
        std::string get_host_key()
        {
            return session_id;
        }
        
        int init(std::string hname, std::string pid, std::string ip, std::string& hkey);
        int connect(std::string key);
        friend bool operator==(host_connection, host_connection);
        
        ~host_connection()
        {
            conn_db.disconnect();
        }
    };
}