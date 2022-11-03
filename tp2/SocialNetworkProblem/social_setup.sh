#!/bin/bash

# Assumes hadoop_setup.sh has been run before
# Assumes the source code is available on the target VM (under ~/SocialNetworkProblem) 
# Assumes Maven is installed on the target VM

# Generate JAR file from project
cd ~/SocialNetworkProblem
mvn clean install / # or whatever other command

# Execute our app in Hadoop
hadoop jar SocialNetworkProblem.jar src/com/log8415/resources/soc-LiveJournal1Adj.txt ConnectionRecommendations.txt