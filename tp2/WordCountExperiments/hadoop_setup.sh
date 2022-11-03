#!/bin/bash

# Download, extract and install Hadoop (latest)
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz
tar -xzvf hadoop-3.3.4.tar.gz
sudo mv hadoop-3.3.4 /usr/local/hadoop

# Configure Hadoop's Java Home
echo 'export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")' >> /usr/local/hadoop/etc/hadoop/hadoop-env.sh

# Add Hadoop to PATH (so we can run hadoop command from anywhere)
echo 'export HADOOP_PREFIX=/usr/local/hadoop' >> ~/.profile
echo 'export PATH=$HADOOP_PREFIX/bin:$PATH' >> ~/.profile
source .profile

# Edit the core-site.xml and modify the following properties:

# nano /usr/local/hadoop/etc/hadoop/core-site.xml
# <configuration>
#     <property>
#         <name>hadoop.tmp.dir</name>
#         <value>/var/lib/hadoop</value>
#     </property>
# </configuration>

# Edit the hdfs-site.xml and modify the following properties:

# nano /usr/local/hadoop/etc/hadoop/hdfs-site.xml
# <configuration>
#     <property>
#         <name>dfs.replication</name>
#         <value>1</value>
#     </property>
# </configuration>

# Set up SSH
sudo apt-get update
sudo apt-get install ssh openssh-server
sudo service ssh start

cd ~/.ssh
ssh-keygen
cat id_rsa.pub >> authorized_keys
chmod 640 authorized_keys
sudo service ssh restart

# # Configuring the Base HDFS Directory
sudo mkdir /var/lib/hadoop
sudo chmod 777 /var/lib/hadoop

# Edit the core-site.xml and modify the following properties:

# nano /usr/local/hadoop/etc/hadoop/core-site.xml
# <configuration>
#     <property>
#         <name>hadoop.tmp.dir</name>
#         <value>/var/lib/hadoop</value>
#     </property>
# </configuration>

# Formatting the HDFS Filesystem
hdfs namenode -format

# Starting NameNode Daemon and DataNode Daemon
$HADOOP_PREFIX/sbin/start-dfs.sh