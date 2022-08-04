#include <mysql/mysql.h>
#include "headers/database.hpp"

namespace crcs
{
    bool database::db_connect()
    {
        MYSQL crcs_db;
        mysql_init(&crcs_db);
        if(!mysql_real_connect(&crcs_db, hostname, username, password, dbname, port, NULL, NULL))
        {
            std::cerr << "Failed to connect to database: Error: " << mysql_error(&crcs_db) << std::endl;
        }
    }

    bool database::db_register_admin(const string login, const string passwd, const string pass_check, const string email)
    {}
    bool database::db_auth_admin(const string login, const string password)
    {}
    bool database::db_add_host(hname, ip, pool)
    {}
    bool database::db_set_host_up(hid)
    {}
    bool database::db_set_host_down(hid)
    {}
    bool database::db_disconnect()
    {
        mysql_close(&crcs_db);
        mysql_library_end();
    }
}
