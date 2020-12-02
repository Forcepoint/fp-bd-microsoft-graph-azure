#!/bin/bash
#
# Download and install Kafka
cd /root
yum install wget -y
wget https://www.apache.org/dist/kafka/2.1.1/kafka_2.11-2.1.1.tgz
tar -zxf /root/kafka_2.11-2.1.1.tgz
mv /root/kafka_2.11-2.1.1 /root/kafka
mv /root/kafka "$1"
