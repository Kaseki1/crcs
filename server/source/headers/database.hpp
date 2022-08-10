#include <mysql/mysql.h>
#include <string>

namespace crcs
{
    // глобальные переменные, идентифицирующие код ошибки
    namespace database
    {
        const int ERR_INIT_MYSQL_OBJECT = 1;
        const int ERR_CONNECTING_DATABASE = 2;
        const int ERR_PASSWD_CONFIRM = 3;
        const int ERR_SEND_QUERY = 4;
        const int ERR_FREE_LOCAL_TABLES = 5;

        class database
        {
        private:
            MYSQL* crcs_db = NULL;

            const char* hostname;
            const int port;
            const char* username;
            const char* password;
            const char* dbname;

        public:
            database() : hostname("localhost"), port(3306), username("root"), password("qwerty"), dbname("crcs_db")
            {}
            database(st)
            int db_connect();
            int db_register_admin(const std::string login, const std::string passwd,
                                  const std::string pass_check, const std::string email);
            int db_auth_admin(const std::string login, const std::string password);
            int db_add_host(std::string hname, std::string ip, unsigned pool);
            int db_set_host_up(unsigned hid);
            int db_set_host_down(unsigned hid);
            int db_disconnect();
        };
    }
}
