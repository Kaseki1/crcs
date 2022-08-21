#include "headers/host_connection.hpp"

namespace crcs
{
    int host_connection::init(std::string hname, std::string pid, std::string& hid)
    {
        conn_db.add_host(hname, pid, hid);
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