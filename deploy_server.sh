#!/bin/bash
# please run script as sudo

if `systemctl status crcsd`; then
    systemtl stop crcsd
    systemctl disable crcsd
fi

cat << EOF
[Unit]
Type=exec
Description=CRCS server daemon unit file

[Service]
User=root
ExecStart=/bin/crcs
ExecStop=kill $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF > /etc/systemd/system/crcsd.service

test -d /opt/crcsd || mkdir /opt/crcsd
cp build/server /opt/crcsd/crcsd
chmod +x /opt/crcsd/crcsd

systemctl start crcsd
