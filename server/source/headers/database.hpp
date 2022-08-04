#include <mysql/mysql.h>

namespace crcs
{
    class database
    {
    private:
        MYSQL crcs_db;

        const char* hostname;
        const int port;
        const char* username;
        const char* password;
        const char* dbname;

    public:
        database() : hostname("localhost"), port(3306), username("root"), password("qwerty"), dbname("remote_admin")
        {}
        bool db_connect();
        bool db_register_admin(const string login, const string passwd, const string pass_check, const string email);
        bool db_auth_admin(const string login, const string password);
        bool db_add_host(hname, ip, pool);
        bool db_set_host_up(hid);
        bool db_set_host_down(hid);
        db_disconnect();
    }
}
