#!/bin/bash

# Assumes hadoop_setup.sh and spark_setup.sh have been run before

# Download input files
mkdir ~/inputs
cd ~/inputs
wget http://www.gutenberg.ca/ebooks/buchanj-midwinter/buchanj-midwinter-00-t.txt -o buchanj-midwinter-00-t.txt
wget http://www.gutenberg.ca/ebooks/carman-farhorizons/carman-farhorizons-00-t.txt -o carman-farhorizons-00-t.txt
wget http://www.gutenberg.ca/ebooks/colby-champlain/colby-champlain-00-t.txt -o colby-champlain-00-t.txt
wget http://www.gutenberg.ca/ebooks/cheyneyp-darkbahama/cheyneyp-darkbahama-00-t.txt -o cheyneyp-darkbahama-00-t.txt
wget http://www.gutenberg.ca/ebooks/delamare-bumps/delamare-bumps-00-t.txt -o delamare-bumps-00-t.txt
wget http://www.gutenberg.ca/ebooks/charlesworth-scene/charlesworth-scene-00-t.txt -o harlesworth-scene-00-t.txt
wget http://www.gutenberg.ca/ebooks/delamare-lucy/delamare-lucy-00-t.txt -o delamare-lucy-00-t.txt
wget http://www.gutenberg.ca/ebooks/delamare-myfanwy/delamare-myfanwy-00-t.txt -o delamare-myfanwy-00-t.txt
wget http://www.gutenberg.ca/ebooks/delamare-penny/delamare-penny-00-t.txt -o delamare-penny-00-t.txt

# Time Hadoop execution (repeat 3 times each)
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount inputs/buchanj-midwinter-00-t.txt output1
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount inputs/carman-farhorizons-00-t.txt output2
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount inputs/colby-champlain-00-t.txt output3
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount inputs/cheyneyp-darkbahama-00-t.txt output4
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount inputs/delamare-bumps-00-t.txt output5
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount inputs/harlesworth-scene-00-t.txt output6
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount inputs/delamare-lucy-00-t.txt output7
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount inputs/delamare-myfanwy-00-t.txt output8
time hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount inputs/delamare-penny-00-t.txt output9

cd /usr/local/spark/

# Tiem Spark execution (repeat 3 times each)
time ./bin/run-example JavaWordCount ~/inputs/buchanj-midwinter-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/carman-farhorizons-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/colby-champlain-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/cheyneyp-darkbahama-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/delamare-bumps-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/harlesworth-scene-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/delamare-lucy-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/delamare-myfanwy-00-t.txt
time ./bin/run-example JavaWordCount ~/inputs/delamare-penny-00-t.txt