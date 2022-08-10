#include <mysql/mysql.h>
#include <string>
#include "headers/database.hpp"
#include <iostream>

namespace crcs
{
    int database::db_connect()
    {
        if(!(crcs_db = mysql_init(crcs_db)))
            return 1;           // ERR_INIT_MYSQL_OBJECT
        if(!mysql_real_connect(crcs_db, hostname, username, password, dbname, port, NULL, 0))
            return 2;           // ERR_CONNECTING_DATABASE
        return 0;
    }

    int database::db_register_admin(const std::string login,
                                    const std::string passwd,
                                    const std::string pass_check,
                                    const std::string email)
    {
        if(passwd != pass_check)
            return 3;           // ERR_PASSWD_CONFIRM
        std::string check_query = static_cast<std::string>("SELECT COUNT(*) FROM admins WHERE login = '") +
                                  login + static_cast<std::string>("'");
        std::string create_query = static_cast<std::string>("INSERT INTO admins (login, email, password) VALUES ('") +
                                   login + "', '" + email + "', '" + passwd + "')";
        if(mysql_query(crcs_db, check_query.c_str()))
        {
            std::cerr << mysql_error(crcs_db);
            return 4;           // ERR_SEND_QUERY
        }
        MYSQL_RES* count_res = mysql_store_result(crcs_db);
        MYSQL_ROW count_row = mysql_fetch_row(count_res);
        if(static_cast<std::string>(count_row[0]) != static_cast<std::string>("0"))
        {
            mysql_free_result(count_res);
            return 5;           // ERR_FREE_LOCAL_TABLES
        }
        mysql_free_result(count_res);
        if(mysql_query(crcs_db, create_query.c_str()))
            return 4;           // ERR_QUERY
        return 0;
    }
    int database::db_auth_admin(const std::string login, const std::string password)
    {}
    int database::db_add_host(const std::string hname, const unsigned pool)
    {}
    int database::db_set_host_up(const unsigned hid)
    {}
    int database::db_set_host_down(const unsigned hid)
    {}
    int database::db_disconnect()
    {
        mysql_close(crcs_db);
        mysql_library_end();
    }
}
