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

int main()
{
    crcs::network net(8080);
    net.init();
    net.start_listening();
    sleep(60);
    net.stop_listening();
}
