all: main.o admin_connection.o host_connection.o listener.o database.o
	[[ -d debug ]] || mkdir debug
	g++ -std=c++2a -ljsoncpp -lmariadb -lcrypt main.o admin_connection.o host_connection.o listener.o database.o -o ./debug/server

main.o:
	g++ -std=c++2a -g -c ./source/main.cpp

admin_connection.o:
	g++ -std=c++2a -g -c ./source/admin_connection.cpp
host_connection.o:
	g++ -std=c++2a -g -c ./source/host_connection.cpp

listener.o:
	g++ -std=c++2a -g -c ./source/listener.cpp

database.o:
	g++ -std=c++2a -g -c ./source/database.cpp

clean:
	rm -rf *.o
