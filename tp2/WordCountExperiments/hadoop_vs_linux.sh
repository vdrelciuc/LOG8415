#!/bin/bash

# Assumes hadoop_setup.sh has been run before

# Download input file
wget https://www.gutenberg.org/cache/epub/4300/pg4300.txt -o pg4300.txt

# Time Hadoop execution (repeat 3 times)
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount pg4300.txt output

# Time Linux execution (repeat 3 times)
time cat pg4300.txt | tr ' ' '\n' | sort | uniq -c