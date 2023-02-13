FROM archlinux:latest

# Prepare libraries
RUN pacman-key --init
RUN pacman-key --populate
RUN pacman -Syyu --noconfirm
RUN pacman --noconfirm -S mariadb mariadb-libs jsoncpp

# Copy project files to container
COPY debug/server /usr/src/crcs/
COPY db.sql /usr/src/crcs/
RUN chmod 755 /usr/src/crcs/server

# Prepare database
RUN mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
RUN systemctl start mariadb
RUN mariadb -u root < db.sql
RUN mariadb -u root -e 'ALTER USER 'root'@'localhost' IDENTIFIED BY 'qwerty'

# Run server
CMD ["/usr/src/crcs/server"]
EXPOSE 9090
EXPOSE 9091
