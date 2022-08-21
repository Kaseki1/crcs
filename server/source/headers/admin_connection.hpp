#pragma once
#include <string>
#include <random>
#include <unistd.h>
#include "database.hpp"
#include "connection.hpp"

namespace crcs
{
    const int ERR_INVALID_CREDINTAILS = 2;
    const int ERR_DATABASE = 3;
    const int ERR_LOGIN_IS_USED = 4;
    const int ERR_INVALID_SESSION = 5;
    const int ERR_CREATE_POOL = 6;
//    const int SUCCESS_CREATE_POOL
//    const int SUCCESS_
//    const int SUCCESS
    
    class admin_connection : public connection
    {
    private:
        std::string gen_hash(std::string);
        std::string gen_session();
        bool verify_hash(std::string, std::string);
    public:
        admin_connection(int s, std::string db_host, std::string db_user, std::string db_passwd, std::string db_name, unsigned db_port) : 
                         connection(s, db_host, db_user, db_passwd, db_name, db_port)
        {
            if(conn_db.connect() != 0)
                std::cout << "failed to connect db" << std::endl;
        }
        int authenticate(std::string login, std::string passwd, std::string& sid);
        int add_session(std::string login, std::string sid);
        int register_admin(std::string login, std::string passwd, std::string email);
        int create_pool(std::string sid);
        int get_pools(std::string sid, unsigned pools[]);
        int get_pool_size(std::string sid, std::string pid, std::string& size);
        int get_pool_members(std::string sid, std::string pid, std::vector<std::string>& members);
        int get_on_pool_members(std::string sid, unsigned pid);
        
        ~admin_connection()
        {
            conn_db.disconnect();
        }
    };
}
