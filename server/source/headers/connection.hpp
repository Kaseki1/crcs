#pragma once
#include <string>
#include <sys/socket.h>
#include <unistd.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <deque>
#include <poll.h>
#include "database.hpp"

namespace crcs
{
    const int ERR_INVALID_PACKET = 1;
    const int ERR_DATABASE = 2;
    
    class connection
    {
    protected:
        int sock;
        SSL* ssl;
        database conn_db;
        std::string session_id;
        std::deque<std::string> message_queue;
        
        virtual SSL_CTX *create_context()
        {
            const SSL_METHOD *method;
            SSL_CTX *ctx;

            method = TLS_server_method();

            ctx = SSL_CTX_new(method);
            if (!ctx) {
                perror("Unable to create SSL context");
                ERR_print_errors_fp(stderr);
                exit(EXIT_FAILURE);
            }

            return ctx;
        }
        
        virtual void configure_context(SSL_CTX *ctx)
        {
            /* Set the key and cert */
            if (SSL_CTX_use_certificate_file(ctx, "/etc/crcs/ssl/cert.pem", SSL_FILETYPE_PEM) <= 0)
            {
                ERR_print_errors_fp(stderr);
                exit(EXIT_FAILURE);
                if (SSL_CTX_use_PrivateKey_file(ctx, "/etc/crcs/ssl/key.pem", SSL_FILETYPE_PEM) <= 0 )
                {
                    ERR_print_errors_fp(stderr);
                    exit(EXIT_FAILURE);
                }
            }
        }
    public:
        connection(int s, std::string db_host, std::string db_user,
                   std::string db_passwd, std::string db_name,
                   unsigned db_port) :
                   sock(s), conn_db(db_host, db_user, db_passwd,
                   db_name, db_port)
        {
//            SSL_CTX *ctx;
//            ctx = create_context();
//            configure_context(ctx);
//            ssl = SSL_new(ctx);
//            SSL_set_fd(ssl, sock);
//            SSL_set_mode(ssl, SSL_MODE_ASYNC);
//            if (SSL_accept(ssl) <= 0)
//                ERR_print_errors_fp(stderr);
        }
                   
        void close_connection()
        {
//            SSL_shutdown(ssl);
//            SSL_free(ssl);
            shutdown(sock, SHUT_RDWR);
            close(sock);
        }

    
        
        virtual int send_message(std::string &msg)
        {
//            SSL_write(ssl, msg.c_str(), msg.length());
            send(sock, msg.c_str(), msg.length(), 0);
            return 0;
        }
        
        virtual int recv_message(std::string &msg)
        {
            char buff[2] {};
//            pollfd fd;
//            fd.fd = sock;
//            fd.events = POLLIN;
//            poll(&fd, 1, 0);
            do
            {
//                SSL_read(ssl, buff, 1);
                recv(sock, buff, 1, 0);
                msg += buff;
            }while(buff[0] != '}' && buff[0] != '\0');
            if(buff[0] == '\0')
                return ERR_INVALID_PACKET;
            return 0;
        }
    };
}
