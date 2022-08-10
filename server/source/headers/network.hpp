#pragma once
#include <string>
#include <deque>

namespace crcs
{
    void* accepter(void*);
    const unsigned DEFAULT_PORT = 701;

    class listener
    {
    private:
        unsigned listen_port;
        int sock {-1};
        pthread_t accepter_thread;
        struct sockaddr_in ADDRESS {};
        unsigned ADDRLEN;
        std::deque<int> unhandled_connections;
    public:
        listener() : listen_port(DEFAULT_PORT)
        {}
        void set_port(unsigned);
        int init();                     // инициализация прослушивания
        int get_first_unhandled();      // возвращает первое необработанное подключение
        int close_listener();        // прекращает прослушивание и закрывает сокет
        friend void* accepter(void*);
    };
}
