#!/bin/bash

WORKING_DIR=~/hadoop_vs_linux

# Assumes Hadoop is already installed on the machine
# Otherwise, please run hadoop_setup.sh first

# Also assumes the input file already exists in ~/inputs
# Otherwise, please download using: wget https://www.gutenberg.org/cache/epub/4300/pg4300.txt -o ~/inputs/pg4300.txt

# Cleanup any existing working directory
rm -rf $WORKING_DIR
mkdir $WORKING_DIR

# Time Hadoop execution
testHadoop() {
    echo "Hadoop performance for $1:" >> $WORKING_DIR/hadoop_performance.txt
    for i in 1; # could be updated if we wanted to perform more runs
    do
        echo "Run #$i:" >> $WORKING_DIR/hadoop_performance.txt
        # Because Hadoop and 'time' both output in STDERR, we discard STDOUT and tail only the last 3 lines of STDERR (output of 'time')
        { time -p hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/$1 $WORKING_DIR/hadoop_outputs/$1_run$i > /dev/null ; } 2> $WORKING_DIR/temp.txt
        cat $WORKING_DIR/temp.txt | tail -3 >> $WORKING_DIR/hadoop_performance.txt
        rm $WORKING_DIR/temp.txt
    done
}

touch $WORKING_DIR/hadoop_performance.txt

testHadoop "pg4300.txt"

cat $WORKING_DIR/hadoop_performance.txt
echo "Hadoop performance saved in: $WORKING_DIR/hadoop_performance.txt"

# Time Linux execution
testLinux() {
    echo "Linux performance for $1:" >> $WORKING_DIR/linux_performance.txt
    for i in 1; # could be updated if we wanted to perform more runs
    do
        echo "Run #$i:" >> $WORKING_DIR/linux_performance.txt
        # 'cat' outputs to STDOUT, so we discard that and save time's output from STDERR
        { time -p cat ~/inputs/pg4300.txt | tr ' ' '\n' | sort | uniq -c > /dev/null ; } 2> $WORKING_DIR/linux_performance.txt
    done
}

touch $WORKING_DIR/linux_performance.txt

testLinux "pg4300.txt"

cat $WORKING_DIR/linux_performance.txt
echo "Linux performance saved in: $WORKING_DIR/linux_performance.txt"