#include "headers/host_connection.hpp"

namespace crcs
{
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
    int host_connection::connect(std::string hid)
    {
        return 0;
    }
    int host_connection::get_hid(std::string& hid)
    {
        return 0;
    }
    int host_connection::get_command(std::string& command)
    {
        return 0;
    }
    int host_connection::push_command(std::string command)
    {
        return 0;
    }
}