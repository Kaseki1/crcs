namespace crcs
{
    void* accepter(void*);
    const unsigned DEFAULT_PORT = 701;

    class network
    {
    private:
        unsigned listen_port;
        int sock {-1};
        pthread_t accepter_thread;
        std::list<int> unhandled_connections;

        struct sockaddr_in ADDRESS {};
        unsigned ADDRLEN;
    public:
        network() : listen_port(DEFAULT_PORT)
        {}
        network(unsigned port) : listen_port(port)
        {}
        // в случае ошибок функции с типом bool возвращают false,
        // а с типом int возвращают -1
        bool init();                // инициализация сетевого сокета
        bool start_listening();     // начать прослушивание
        bool stop_listening();      // прекратить прослушивание
        int get_unhandled_conn();   // возвращает первое необработанное соединение
        friend void* accepter(void*);
    };
}
