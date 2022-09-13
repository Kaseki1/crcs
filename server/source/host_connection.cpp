#include "headers/host_connection.hpp"

namespace crcs
{
    bool operator==(host_connection hst1, host_connection hst2)
    {
        if(hst1.session_id == hst2.session_id)
            return true;
        return false;
    }
    
    std::string host_connection::gen_hkey()
    {
        std::random_device rd;
        std::mt19937 mersenne(rd());
        char id[129] {};

        for(int i {}; i < 128; i++)
            while(!std::isalnum(id[i] = mersenne() % 75 + 48));
            return std::string(id);
    }
    
    int host_connection::init(std::string hname, std::string pid, std::string ip, std::string& hkey)
    {
        int err;
        do{
            err = conn_db.add_host(hname, pid, (hkey = gen_hkey()), ip);
            if(err == ERR_SEND_QUERY)
                return ERR_DATABASE;
        }while(err == ERR_INVALID_HOST_KEY);
        session_id = hkey;
        return 0;
    }
    int host_connection::connect(std::string hkey)
    {
        if(conn_db.get_user_info(hkey, hostname, pool_id) == ERR_INVALID_HOST_KEY)
            return ERR_INVALID_KEY;
        session_id = hkey;
        return 0;
    }
    
    int host_connection::leave_pool(std::string hkey)
    {
        if(conn_db.delete_host(hkey) == ERR_INVALID_HOST_KEY)
            return ERR_INVALID_KEY;
        return 0;
    }
}