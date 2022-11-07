#!/bin/bash

WORKING_DIR=~/hadoop_vs_spark

# Assumes Hadoop and Spark are already installed on the machine
# Otherwise, please run hadoop_setup.sh and spark_setup.sh first

# Also assumes the input files already exist in ~/inputs
# Otherwise, please download using: wget http://www.gutenberg.ca/ebooks/buchanj-midwinter/buchanj-midwinter-00-t.txt -o ~/inputs/buchanj-midwinter-00-t.txt

# Cleanup any existing working directory
rm -rf $WORKING_DIR
mkdir $WORKING_DIR

# Benchmark Hadoop execution
testHadoop() {
    echo "Hadoop performance for $1:" >> $WORKING_DIR/hadoop_performance.txt
    for i in 1 2 3;
    do
        echo "Run #$i:" >> $WORKING_DIR/hadoop_performance.txt
        # Because Hadoop and 'time' both output in STDERR, we discard STDOUT and tail only the last 3 lines of STDERR (output of 'time')
        { time -p hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/$1 $WORKING_DIR/hadoop_outputs/$1_run$i > /dev/null ; } 2> $WORKING_DIR/temp.txt
        cat $WORKING_DIR/temp.txt | tail -3 >> $WORKING_DIR/hadoop_performance.txt
        rm $WORKING_DIR/temp.txt
    done
}

touch $WORKING_DIR/hadoop_performance.txt

testHadoop "buchanj-midwinter-00-t.txt"
testHadoop "carman-farhorizons-00-t.txt"
testHadoop "charlesworth-scene-00-t.txt"
testHadoop "cheyneyp-darkbahama-00-t.txt"
testHadoop "colby-champlain-00-t.txt"
testHadoop "delamare-bumps-00-t.txt"
testHadoop "delamare-lucy-00-t.txt"
testHadoop "delamare-myfanwy-00-t.txt"
testHadoop "delamare-penny-00-t.txt"

cat $WORKING_DIR/hadoop_performance.txt
echo "Hadoop performance saved in: $WORKING_DIR/hadoop_performance.txt"

# Benchmark Spark execution
testSpark() {
    echo "Spark performance for $1:" >> $WORKING_DIR/spark_performance.txt
    for i in 1 2 3;
    do
        echo "Run #$i:" >> $WORKING_DIR/spark_performance.txt
        # Because Spark and 'time' both output in STDERR, we discard STDOUT and tail only the last 3 lines of STDERR (output of 'time')
        { time -p ./bin/run-example JavaWordCount ~/inputs/$1 > /dev/null ; } 2> $WORKING_DIR/temp.txt
        cat $WORKING_DIR/temp.txt | tail -3 >> $WORKING_DIR/spark_performance.txt
        rm $WORKING_DIR/temp.txt
    done
}

cd /usr/local/spark/
touch $WORKING_DIR/spark_performance.txt

testSpark "buchanj-midwinter-00-t.txt"
testSpark "carman-farhorizons-00-t.txt"
testSpark "charlesworth-scene-00-t.txt"
testSpark "cheyneyp-darkbahama-00-t.txt"
testSpark "colby-champlain-00-t.txt"
testSpark "delamare-bumps-00-t.txt"
testSpark "delamare-lucy-00-t.txt"
testSpark "delamare-myfanwy-00-t.txt"
testSpark "delamare-penny-00-t.txt"

cat $WORKING_DIR/spark_performance.txt
echo "Spark performance saved in: $WORKING_DIR/spark_performance.txt"