#!/usr/bin/bash

yum install java-1.8.0-openjdk
pip install mongo mongo-connector

cat "replSet = ceilometer_replica" >> /etc/mongod.conf
systemctl restart mongod

echo <<EOF >> enable_replica.py
#!/usr/bin/env python
import socket
import time
from pymongo import MongoClient

client = MongoClient(socket.gethostbyname(socket.gethostname()))
config = {'_id': 'ceilometer_replica', 'members': [
              {'_id':0, 'host': str(socket.gethostbyname(socket.gethostname()))+':27017'}
         ]}
client.admin.command("replSetInitiate", config)
time.sleep(1)
client.admin.command("replSetGetStatus")
EOF
python enable_replica.py

wget https://download.elasticsearch.org/elasticsearch/release/org/elasticsearch/distribution/rpm/elasticsearch/2.0.0/elasticsearch-2.0.0.rpm
wget https://download.elastic.co/kibana/kibana/kibana-4.2.0-linux-x64.tar.gz
tar -zxvf kibana-4.2.0-linux-x64.tar.gz
rpm -i logstash-2.0.0-1.noarch.rpm elasticsearch-2.0.0.rpm

systemctl enable elasticsearch.service
systemctl start elasticsearch.service

echo "Please run manually :"
echo "$ mongo-connector --auto-commit-interval=0 -m 127.0.0.1:27017 -t 127.0.0.1:9200 -d elastic_doc_manager"
echo "$ ./kibana-4.2.0-linux-x64/bin/kibana"
