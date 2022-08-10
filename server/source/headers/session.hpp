namespace crcs
{
    class session
    {
    private:
        int sock;
        std::string session_id;
        bool client_type;           // true - admin, false - controlled host
    public:
        int authenticate();

    };
}
