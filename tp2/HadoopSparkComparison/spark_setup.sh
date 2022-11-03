#!/bin/bash

# Download, extract and install Spark 2.0.0
wget https://archive.apache.org/dist/spark/spark-2.0.0/spark-2.0.0-bin-hadoop2.7.tgz
tar zxvf spark-2.0.0-bin-hadoop2.7.tgz
sudo mv spark-2.0.0-bin-hadoop2.7 /usr/local/spark

# Start Spark master node
/usr/local/spark/sbin/start-master.sh

# Start Spark slave node (assuming user is 'ubuntu')
/usr/local/spark/sbin/start-slave.sh spark://ubuntu:7077