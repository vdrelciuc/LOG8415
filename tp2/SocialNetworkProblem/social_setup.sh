#!/bin/bash

# Assumes hadoop_setup.sh has been run before
# Assumes the source code is available on the target VM (under ~/SocialNetworkProblem)

# Install maven if not already installed
if ! command -v mvn &> /dev/null
then
  echo "Maven not found. Installing..."
  sudo apt install -y maven
fi


# Generate JAR file from project
cd ~/SocialNetworkProblem
mvn clean install

# Execute our app in Hadoop
hadoop jar target/SocialNetworkProblem.jar src/main/resources/soc-LiveJournal1Adj.txt ConnectionRecommendations.txt
