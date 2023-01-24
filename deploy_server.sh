#!/bin/bash
# please run script as sudo

test -e /etc/systemd/system/crcsd.service && systemctl stop crcsd.service

cat <<EOF > /etc/systemd/system/crcsd.service
[Unit]
Type=exec
Description=CRCS server daemon unit file

[Service]
User=root
ExecStart=/opt/crcsd/crcsd
ExecStop=kill $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

test -d /opt/crcsd || mkdir /opt/crcsd
cp build/server /opt/crcsd/crcsd
chmod +x /opt/crcsd/crcsd

systemctl start crcsd
