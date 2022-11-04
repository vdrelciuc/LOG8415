#!/bin/bash

# How to use:
# `./run.sh <ip> <path-to-pem> <path-to-dataset>
# <path-to-dataset> is optional

if [ $# -lt 2 ]; then
  echo "Missing ip and path to pem file arguments"
  exit 1
fi

ip=$1
pem_path=$2
dataset_path="${3:-src/main/resources/dataset.txt}"
dataset_name=$(basename "$dataset_path")
output_path="output/$dataset_name"

cd "$(dirname "$0")" || exit

printf "Copying source files to VM...\n\n"

scp -i "$pem_path" -r src pom.xml ubuntu@"$ip:~/SocialNetworkProblem/"

printf "\nSuccess!\n"

printf "Compiling source files and starting hadoop...\n\n"

ssh -i "$pem_path" ubuntu@"$ip" "source ~/.profile && \
  cd SocialNetworkProblem && \
  rm -rf $output_path && \
  mvn clean install && \
  hadoop jar target/SocialNetworkProblem.jar $dataset_path $output_path"

printf "\nSuccess!\n"

printf "Downloading results to \"%s\"...\n\n" "$(pwd)/$dataset_path"

mkdir -p output
scp -ri "$pem_path" ubuntu@"$ip:~/SocialNetworkProblem/$output_path" "output/$dataset_name"

printf "\nDone!\""
