#include "headers/database.hpp"

namespace crcs
{
    int database::connect()
    {
        if(!(crcs_db = mysql_init(crcs_db)))
            return 1;           // ERR_INIT_MYSQL_OBJECT
        if(!mysql_real_connect(crcs_db, hostname.c_str(), username.c_str(), password.c_str(), dbname.c_str(), port, NULL, 0))
            return 2;           // ERR_CONNECTING_DATABASE
        return 0;
    }

    int database::register_admin(const std::string login,
                                 const std::string hash,
                                 const std::string email)
    {
        std::string check_query = static_cast<std::string>("SELECT COUNT(*) FROM admins WHERE login = '") +
                                  login + static_cast<std::string>("'");
        std::string create_query = static_cast<std::string>("INSERT INTO admins (login, email, password) VALUES ('") +
                                   login + "', '" + email + "', '" + hash + "')";
        if(mysql_query(crcs_db, check_query.c_str()))
        {
            std::cerr << mysql_error(crcs_db);
            return 3;           // ERR_SEND_QUERY
        }
        MYSQL_RES* count_res = mysql_store_result(crcs_db);
        MYSQL_ROW count_row = mysql_fetch_row(count_res);
        if(static_cast<std::string>(count_row[0]) != static_cast<std::string>("0"))
        {
            mysql_free_result(count_res);
            return 4;           // ERR_USER_EXIST
        }
        mysql_free_result(count_res);
        if(mysql_query(crcs_db, create_query.c_str()))
            return 3;           // ERR_SEND_QUERY
        return 0;
    }
    int database::get_hash(const std::string login, std::string &hash)
    {
        std::string check_query = static_cast<std::string>("SELECT COUNT(*) FROM admins WHERE login = '") +
                                                           login + static_cast<std::string>("'");
        std::string hash_query = static_cast<std::string>("SELECT password FROM admins WHERE login = '") +
                                                           login + "'";
        if(mysql_query(crcs_db, check_query.c_str()))
        {
            return 3;           // ERR_SEND_QUERY
        }
        MYSQL_RES* count_res = mysql_store_result(crcs_db);
        MYSQL_ROW count_row = mysql_fetch_row(count_res);
        if(static_cast<std::string>(count_row[0]) == static_cast<std::string>("0"))
        {
            mysql_free_result(count_res);
            return 5;           // ERR_INVALID_LOGIN
        }
        mysql_free_result(count_res);

        if(mysql_query(crcs_db, hash_query.c_str()))
        {
            std::cerr << mysql_error(crcs_db);
            return 3;           // ERR_SEND_QUERY
        }
        MYSQL_RES* hash_res = mysql_store_result(crcs_db);
        MYSQL_ROW hash_row = mysql_fetch_row(hash_res);
        hash = hash_row[0];
        mysql_free_result(hash_res);

        return 0;
    }
    int database::add_session(std::string login, std::string sid)
    {
        std::string check_query = static_cast<std::string>("SELECT COUNT(*) FROM admin_session WHERE session_id = '") +
                                                           sid + static_cast<std::string>("'");
        std::string create_query = static_cast<std::string>("INSERT INTO admin_session (session_id, admin_id) ") +
                                                           "VALUES ('" + sid +"', ("
                                                           "SELECT admin_id FROM admins WHERE login = '" + login + "'))";
        if(mysql_query(crcs_db, check_query.c_str()))
        {
            std::cout << mysql_error(crcs_db) << std::endl;
            return 3;           // ERR_SEND_QUERY
        }
        MYSQL_RES* count_res = mysql_store_result(crcs_db);
        MYSQL_ROW count_row = mysql_fetch_row(count_res);
        if(static_cast<std::string>(count_row[0]) != static_cast<std::string>("0"))
        {
            mysql_free_result(count_res);
            return 6;           // ERR_INVALID_SESSION_ID
        }
        mysql_free_result(count_res);

        if(mysql_query(crcs_db, create_query.c_str()))
        {
            std::cout << mysql_error(crcs_db) << std::endl;
            return 3;           // ERR_SEND_QUERY
        }
        return 0;
    }
    
    int database::create_pool(const std::string sid)
    {
        std::string check_query = static_cast<std::string>("SELECT COUNT(*) FROM admin_session WHERE session_id = '") +
                                                           sid + static_cast<std::string>("'");
        std::string create_query = static_cast<std::string>("INSERT INTO pools (admin_id) ") +
                                                           "VALUES ((" +
                                                           "SELECT admin_id FROM admin_session" + 
                                                           " WHERE session_id = '" + sid + "'))";
        if(mysql_query(crcs_db, check_query.c_str()))
        {
            std::cout << mysql_error(crcs_db) << std::endl;
            return ERR_SEND_QUERY;
        }
        MYSQL_RES* count_res = mysql_store_result(crcs_db);
        MYSQL_ROW count_row = mysql_fetch_row(count_res);
        if(static_cast<std::string>(count_row[0]) == static_cast<std::string>("0"))
        {
            mysql_free_result(count_res);
            return ERR_INVALID_SESSION_ID;
        }
        mysql_free_result(count_res);

        if(mysql_query(crcs_db, create_query.c_str()))
        {
            std::cout << mysql_error(crcs_db) << std::endl;
            return ERR_SEND_QUERY;
        }
        return 0;
    }
    
    int database::get_pool_size(const std::string sid, const std::string pid, std::string& size)
    {
        std::string check_query = static_cast<std::string>("SELECT COUNT(*) FROM admin_session WHERE session_id = '") +
                                                           sid + static_cast<std::string>("'");
        std::string get_query = static_cast<std::string>("SELECT COUNT(*) FROM hosts WHERE pool_id = '") +
                                                           pid + static_cast<std::string>("'");
        if(mysql_query(crcs_db, check_query.c_str()))
        {
            std::cout << mysql_error(crcs_db) << std::endl;
            return ERR_SEND_QUERY;
        }
        MYSQL_RES* check_res = mysql_store_result(crcs_db);
        MYSQL_ROW check_row = mysql_fetch_row(check_res);
        if(static_cast<std::string>(check_row[0]) == static_cast<std::string>("0"))
        {
            mysql_free_result(check_res);
            return ERR_INVALID_SESSION_ID;
        }
        
        if(mysql_query(crcs_db, get_query.c_str()))
        {
            std::cout << mysql_error(crcs_db) << std::endl;
            return ERR_SEND_QUERY;
        }
        MYSQL_RES* get_res = mysql_store_result(crcs_db);
        MYSQL_ROW get_row = mysql_fetch_row(get_res);
        size = static_cast<std::string>(get_row[0]);
        mysql_free_result(get_res);
        return 0;
    }
    
    int database::get_pool_members(const std::string sid, const std::string pid, std::vector<std::string> members)
    {
        std::string check_query = static_cast<std::string>("SELECT COUNT(*) FROM admin_session WHERE session_id = '") +
                                                           sid + static_cast<std::string>("'");
        std::string access_query = static_cast<std::string>("SELECT COUNT(*) FROM pools WHERE admin_id = ") +
                                                            "(SELECT admin_id FROM admin_session WHERE session_id = '" +
                                                            sid + static_cast<std::string>("') ") +
                                                            "AND pool_id = '" + pid + "'";
        std::string get_query = static_cast<std::string>("SELECT COUNT(*) FROM hosts WHERE pool_id = '") +
                                                           pid + static_cast<std::string>("'");
        if(mysql_query(crcs_db, check_query.c_str()))
        {
            std::cout << mysql_error(crcs_db) << std::endl;
            return ERR_SEND_QUERY;
        }
        MYSQL_RES* check_res = mysql_store_result(crcs_db);
        MYSQL_ROW check_row = mysql_fetch_row(check_res);
        if(static_cast<std::string>(check_row[0]) == static_cast<std::string>("0"))
        {
            mysql_free_result(check_res);
            return ERR_INVALID_SESSION_ID;
        }
        
        if(mysql_query(crcs_db, access_query.c_str()))
        {
            std::cout << mysql_error(crcs_db) << std::endl;
            return ERR_SEND_QUERY;
        }
        MYSQL_RES* access_res = mysql_store_result(crcs_db);
        MYSQL_ROW access_row = mysql_fetch_row(check_res);
        if(static_cast<std::string>(check_row[0]) == static_cast<std::string>("0"))
        {
            mysql_free_result(check_res);
            return ERR_ACCESS_DENIED;
        }
        
        if(mysql_query(crcs_db, get_query.c_str()))
        {
            std::cout << mysql_error(crcs_db) << std::endl;
            return ERR_SEND_QUERY;
        }
        MYSQL_RES* get_res = mysql_store_result(crcs_db);
        MYSQL_ROW get_row;
        while((get_row = mysql_fetch_row(get_res)) != NULL)
        {
            members.push_back(static_cast<std::string>(get_row[2]));
            members.push_back(static_cast<std::string>(get_row[3]));
        }
        mysql_free_result(get_res);
        return 0;
    }
    
    int database::get_admin_pools(const std::string sid, std::vector<std::string>& pools)
    {
        std::string check_query = static_cast<std::string>("SELECT COUNT(*) FROM admin_session WHERE session_id = '") +
                                                           sid + static_cast<std::string>("'");
        std::string get_query = static_cast<std::string>("SELECT pool_id FROM pools WHERE ") +
                                                           "admin_id = ((" +
                                                           "SELECT admin_id FROM admin_session" + 
                                                           " WHERE session_id = '" + sid + "'))";
        if(mysql_query(crcs_db, check_query.c_str()))
        {
            std::cout << mysql_error(crcs_db) << std::endl;
            return ERR_SEND_QUERY;
        }
        MYSQL_RES* count_res = mysql_store_result(crcs_db);
        MYSQL_ROW count_row = mysql_fetch_row(count_res);
        if(static_cast<std::string>(count_row[0]) == static_cast<std::string>("0"))
        {
            mysql_free_result(count_res);
            return ERR_INVALID_SESSION_ID;
        }
        mysql_free_result(count_res);

        MYSQL_RES* get_res = mysql_store_result(crcs_db);
        MYSQL_ROW get_row;
        while((get_row = mysql_fetch_row(get_res)) != NULL)
        {
            pools.push_back(static_cast<std::string>(get_row[0]));
        }
        mysql_free_result(get_res);
        return 0;
    }
    
    int database::add_host(const std::string hname, const std::string pid, const std::string hid)
    {
        return 0;
    }
    int database::set_host_up(const unsigned hid)
    {
        return 0;
    }
    int database::set_host_down(const unsigned hid)
    {
        return 0;
    }
    int database::disconnect()
    {
        mysql_close(crcs_db);
        mysql_library_end();
        return 0;
    }
}
