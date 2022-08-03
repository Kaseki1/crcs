#include <iostream>
#include <list>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>
#include "headers/network.hpp"

namespace crcs
{
    // Функция прослушивает соединения и добавляет сокет
    // в конец списка необработанных соединений
    void* accepter(void* net)
    {
        int new_socket;
        pthread_t connection;
        while(true)
        {
            while((new_socket = accept(static_cast<network*>(net)->sock,
                 (struct sockaddr*)&(static_cast<network*>(net)->ADDRESS),
                 &(static_cast<network*>(net)->ADDRLEN))) == -1)
                sleep(1);
            static_cast<network*>(net)->unhandled_connections.push_back(new_socket);
        }
    }
    // Инициализация прослушивающего сокета
    bool network::init()
    {
        ADDRESS.sin_family = AF_INET;
        ADDRESS.sin_addr.s_addr = INADDR_ANY;
        ADDRESS.sin_port = htons(listen_port);
        ADDRLEN = sizeof(ADDRESS);
    
        if((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1)
        {
            std::cerr << "Error opening socket" << std::endl
                      << "Error number: " << errno << std::endl;
            exit(1);
        }

        if(bind(sock, (struct sockaddr*)&ADDRESS, sizeof(ADDRESS)) == -1)
        {
            std::cerr << "Error binding socket" << std::endl
                      << "Error number: " << errno << std::endl;
            exit(1);
        }
    }
    // Прослушивание порта и вызов функции, принимающей соединения
    bool network::start_listening()
    {
        if(listen(sock, 20) == -1)
        {
            std::cerr << "Error listening socket" << std::endl;
            exit(1);
        }
        pthread_create(&accepter_thread, NULL, accepter, &sock);
    }
    bool network::stop_listening()
    {
        pthread_kill(accepter_thread, 15);
    }
    bool network::close()
    {
        shutdown(sock, SHUT_RDWR);
        close(sock);
    }
}
