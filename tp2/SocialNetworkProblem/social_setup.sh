#!/bin/bash

# Assumes hadoop_setup.sh has been run before
# Assumes the source code is available on the target VM (under ~/SocialNetworkProblem)

# Install maven if not already installed
if ! command -v mvn
then
  echo "Maven not found. Installing..."
  sudo apt install -y maven
fi


# Generate JAR file from project
cd ~/SocialNetworkProblem

# Remove the ConnectionRecommendations directory if it exists
if [ -d "output/dataset" ]; then
  rm -rf output/dataset
fi

mvn clean install

# Execute our app in Hadoop
hadoop jar target/SocialNetworkProblem.jar src/main/resources/dataset.txt output/dataset
