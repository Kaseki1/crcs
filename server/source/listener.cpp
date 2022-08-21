#include "headers/listener.hpp"

namespace crcs
{
    // Функция прослушивает соединения и добавляет сокет
    // в конец списка необработанных соединений
    void* accepter(void* net)
    {
        int new_socket;
        crcs::listener* lst = static_cast<crcs::listener*>(net);
        while(true)
        {
            if((new_socket = accept(lst->sock, (struct sockaddr*)&(lst->ADDRESS), &(lst->ADDRLEN))) != -1)
                lst->unhandled_connections.push_back(new_socket);
        }
    }

    void listener::set_port(unsigned port)
    {
        listen_port = port;
    }
    // Инициализация прослушивающего сокета
    int listener::init()
    {
        ADDRESS.sin_family = AF_INET;
        ADDRESS.sin_addr.s_addr = INADDR_ANY;
        ADDRESS.sin_port = htons(listen_port);
        ADDRLEN = sizeof(ADDRESS);
    
        if((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1)
            return 1;   // ERR_CREATE_SOCKET
        if(bind(sock, (struct sockaddr*)&ADDRESS, sizeof(ADDRESS)) == -1)
            return 2;   // ERR_BIND_SOCKET
        if(listen(sock, 20) == -1)
            return 3;   // ERR_LISTEN_SOCKET
        if(pthread_create(&accepter_thread, NULL, accepter, this) != 0)
            return 4;   // ERR_CREATE_ACCEPT_THREAD
        return 0;
    }
    // Получить первое необработанное соединение
    int listener::get_first_unhandled(int &conn)
    {
        if(unhandled_connections.empty())
            return 5;   // ERR_NO_UNHANDLED
        conn = unhandled_connections.front();
        unhandled_connections.pop_front();
        
        return 0;
    }
    // Закрыть прослушивающий сокет
    int listener::close_listener()
    {
        if(pthread_kill(accepter_thread, 15) != 0)
            return 6;   // ERR_STOP_ACCEPTING
        if(shutdown(sock, SHUT_RDWR) == -1)
            return 7;   // ERR_SHUTDOWN_SOCKET
        if(close(sock) == -1)
            return 8;   // ERR_CLOSE_SOCKET
        return 0;
    }
}
