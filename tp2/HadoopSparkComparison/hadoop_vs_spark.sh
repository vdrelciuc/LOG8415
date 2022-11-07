#!/bin/bash

# Assumes Hadoop and Spark are already installed on the machine
# Otherwise, please run hadoop_setup.sh and spark_setup.sh first

# Also assumes the input files already exist in ~/inputs
# Otherwise, please download using: wget http://www.gutenberg.ca/ebooks/buchanj-midwinter/buchanj-midwinter-00-t.txt -o ~/inputs/buchanj-midwinter-00-t.txt

# Cleanup any existing Hadoop output folders
if [ -d "~/outputs" ]; then
  rm -rf ~/outputs
fi

# Create Hadoop outputs parent folder
mkdir ~/outputs

# Time Hadoop execution
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/buchanj-midwinter-00-t.txt ~/outputs/output1
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/carman-farhorizons-00-t.txt ~/outputs/output2
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/colby-champlain-00-t.txt ~/outputs/output3
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/cheyneyp-darkbahama-00-t.txt ~/outputs/output4
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/delamare-bumps-00-t.txt ~/outputs/output5
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/charlesworth-scene-00-t.txt ~/outputs/output6
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/delamare-lucy-00-t.txt ~/outputs/output7
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/delamare-myfanwy-00-t.txt ~/outputs/output8
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/inputs/delamare-penny-00-t.txt ~/outputs/output9

cd /usr/local/spark/

# Tiem Spark execution
time ./bin/run-example JavaWordCount ~/inputs/buchanj-midwinter-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/carman-farhorizons-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/colby-champlain-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/cheyneyp-darkbahama-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/delamare-bumps-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/charlesworth-scene-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/delamare-lucy-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/delamare-myfanwy-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/delamare-penny-00-t.txt