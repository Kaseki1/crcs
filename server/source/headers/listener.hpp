#pragma once

#include <iostream>
#include <string>
#include <deque>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>

namespace crcs
{
    const unsigned ERR_CREATE_SOCKET = 1;
    const unsigned ERR_BIND_SOCKET = 2;
    const unsigned ERR_LISTEN_SOCKET = 3;
    const unsigned ERR_CREATE_ACCEPT_THREAD = 4;
    const unsigned ERR_NO_UNHANDLED = 5;
    const unsigned ERR_STOP_ACCEPTING = 6;
    const unsigned ERR_SHUTDOWN_SOCKET = 7;
    const unsigned ERR_CLOSE_SOCKET = 8;

    void* accepter(void*);

    class listener
    {
    private:
        unsigned listen_port;
        int sock {-1};
        pthread_t accepter_thread;
        bool type;

        struct sockaddr_in ADDRESS {};
        unsigned ADDRLEN;
        std::deque<int> unhandled_connections;
    public:
        listener(unsigned p, bool t) : listen_port(p), type(t)
        {}
        void set_port(unsigned);
        int init();                     // инициализация прослушивания
        int get_first_unhandled(int&);      // возвращает первое необработанное подключение
        int close_listener();        // прекращает прослушивание и закрывает сокет
        friend void* accepter(void*);
    };
}
