#!/bin/bash

# install dependencies first: on CentOS7, we only have python 2.7.5, and so pip does not work well ...
# 

yum install python-pip pcapy
pip install pika impacket

for module in network_spotlight_agent openstack_panel ; do
    echo $module
    pushd $module
    python setup.py install
    popd
done

cat <<\EOF > /etc/systemd/system/network-spotlight-agentd.service
[Unit]
Description=Qosmos Network Spotlight Agent Daemon
After=syslog.target network.target rabbitmq-server.service
ConditionPathExists=/etc/network_spotlight_agentd/

[Service]
StandardOutput=syslog
StandardError=syslog
ExecStart=/usr/bin/network_spotlight_agentd
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
EOF

systemctl enable /etc/systemd/system/network-spotlight-agentd.service
systemctl start network-spotlight-agentd.service
systemctl restart httpd
