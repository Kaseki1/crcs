#pragma once
#include <mysql/mysql.h>
#include <string>
#include <cstring>
#include <iostream>
#include <vector>
#include <crypt.h>

namespace crcs
{
    // глобальные переменные, идентифицирующие код ошибки
    const int ERR_INIT_MYSQL_OBJECT = 1;
    const int ERR_CONNECTING_DATABASE = 2;
    const int ERR_SEND_QUERY = 3;
    const int ERR_USER_EXIST = 4;
    const int ERR_INVALID_LOGIN = 5;
    const int ERR_INVALID_SESSION_ID = 6;
    const int ERR_ACCESS_DENIED = 7;
    const int ERR_INVALID_HOST_KEY = 8;

    class database
    {
    private:
        MYSQL* crcs_db = NULL;

        const std::string hostname;
        const std::string username;
        const std::string password;
        const std::string dbname;
        const int port;
    public:
        database(std::string hst, std::string usr, std::string pswd,
                 std::string dbnm, int prt) : hostname(hst), username(usr),
                                              password(pswd), dbname(dbnm),
                                              port(prt)
        {}
        int connect();
        int register_admin(const std::string login, const std::string hash, const std::string email);
        int get_hash(const std::string login, std::string &hash);
        int add_session(std::string login, std::string sid);
        int get_admin_pools(const std::string sid, std::vector<std::string>& pools);
        int get_pool_size(const std::string sid, const std::string pid, std::string& size);
        int get_pool_members(const std::string sid, const std::string pid, std::vector<std::string>& members);
        int add_host(const std::string hname, const std::string pid, const std::string& hkey, const std::string ip);
        int get_user_info(std::string hkey, std::string& hname, std::string& pool);
        int create_pool(const std::string sid);
        int disconnect();
    };
}
