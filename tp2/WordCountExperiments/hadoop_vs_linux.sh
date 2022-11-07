#!/bin/bash

# Assumes Hadoop is already installed on the machine
# Otherwise, please run hadoop_setup.sh first

# Also assumes the input file already exists in ~/inputs
# Otherwise, please download using: wget https://www.gutenberg.org/cache/epub/4300/pg4300.txt -o ~/inputs/pg4300.txt

# Cleanup any existing Hadoop output folder
rm -rf ~/hadoop_vs_linux
mkdir ~/hadoop_vs_linux

# Time Hadoop execution
echo 'Measuring Hadoop performance for pg4300.txt:'
{ time -p hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/pg4300.txt ~/hadoop_vs_linux/run1_output > /dev/null ; } 2> ~/hadoop_vs_linux/temp.txt
cat ~/hadoop_vs_linux/temp.txt | tail -3 > ~/hadoop_vs_linux/hadoop_performance.txt
rm ~/hadoop_vs_linux/temp.txt
cat ~/hadoop_vs_linux/hadoop_performance.txt
echo 'Performance saved in ~/hadoop_vs_linux/hadoop_performance.txt'

# Time Linux execution
echo 'Measuring Linux performance for pg4300.txt:'
{ time -p cat ~/inputs/pg4300.txt | tr ' ' '\n' | sort | uniq -c > /dev/null ; } 2> ~/hadoop_vs_linux/linux_performance.txt
cat ~/hadoop_vs_linux/linux_performance.txt
echo 'Performance saved in ~/hadoop_vs_linux/linux_performance.txt'