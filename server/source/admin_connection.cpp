#include "headers/admin_connection.hpp"

namespace crcs
{
    std::string admin_connection::gen_hash(std::string passwd)
    {
        const std::string prefix = "$2b$";
        crypt_data params;
        char* salt = crypt_gensalt_ra(prefix.c_str(), 16, NULL, 0);
        strcpy(params.input, passwd.c_str());
        strcpy(params.setting, salt);
        params.initialized = 0;
        crypt_r(passwd.c_str(), params.setting, &params);
        delete [] salt;
        return static_cast<std::string>(params.output);
    }

    bool admin_connection::verify_hash(std::string passwd, std::string hash)
    {
        crypt_data params;
        strcpy(params.input, passwd.c_str());
        strcpy(params.setting, hash.c_str());
        params.initialized = 0;
        crypt_r(passwd.c_str(), hash.c_str(), &params);
        if(hash == static_cast<std::string>(params.output))
            return true;
        return false;
    }
    std::string admin_connection::gen_session()
    {
        std::random_device rd;
        std::mt19937 mersenne(rd());
        char id[129] {};

        for(int i {}; i < 128; i++)
            while(!std::isalnum(id[i] = mersenne() % 75 + 48));
            return std::string(id);
    }

    int admin_connection::authenticate(std::string login, std::string passwd, std::string& sid)
    {
        std::string hash;
        conn_db.get_hash(login, hash);
        if(verify_hash(passwd, hash) == ERR_INVALID_LOGIN)
            return ERR_INVALID_CREDINTAILS;
        int addstatus;
        do{
            addstatus = conn_db.add_session(login, (sid = gen_session()));
            if(addstatus == ERR_SEND_QUERY)
                return ERR_DATABASE;
        }while(addstatus == ERR_INVALID_SESSION_ID);
        session_id = sid;
        return 0;
    }

    int admin_connection::register_admin(std::string login, std:: string passwd, std::string email)
    {
        int err;
        err = conn_db.register_admin(login, gen_hash(passwd), email);
        if(err != 0)
        {
            switch(err)
            {
                case ERR_SEND_QUERY : return ERR_DATABASE;
                case ERR_USER_EXIST : return ERR_LOGIN_IS_USED;
            }
        }
        return 0;
    }
    
    int admin_connection::create_pool(std::string sid)
    {
        unsigned err = conn_db.create_pool(sid);
        if(err == ERR_INVALID_SESSION_ID)
            return ERR_CREATE_POOL;
        return 0;
    }
    
    int admin_connection::get_pool_size(std::string sid, std::string pid, std::string& size)
    {
        unsigned err = conn_db.get_pool_size(sid, pid, size);
        switch(err)
        {
            case ERR_SEND_QUERY: return ERR_DATABASE; break;
            case ERR_INVALID_SESSION_ID: return ERR_INVALID_SESSION; break;
        }
        return 0;
    }
    int admin_connection::get_pool_members(std::string sid, std::string pid, std::vector<std::string>& members)
    {
        return 0;
    }
}
