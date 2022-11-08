#!/bin/bash

set -e

# Assumes Hadoop and Maven are already installed on the remote machine
# Otherwise, please run hadoop_setup.sh on the remote machine

# How to use:
# `./run.sh <vm_address> <path-to-pem> <path-to-dataset>
# <vm_address> is the ip of the vm that will be used to connect via ssh. Should be formatted as "<user>@<ip>"
# <path-to-dataset> is optional

if [ $# -lt 2 ]; then
  echo "Missing ip and path to pem file arguments"
  exit 1
fi

vm_address=$1
pem_path=$2
dataset_path="${3:-src/main/resources/dataset.txt}"
dataset_name=$(basename "$dataset_path")
output_path="output/$dataset_name"

cd "$(dirname "$0")" || exit

printf "Copying source files to VM...\n\n"

scp -i "$pem_path" -r src pom.xml "$vm_address:~/SocialNetworkProblem/"

printf "\nSuccess!\n"

printf "Compiling source files and starting hadoop...\n\n"

ssh -i "$pem_path" "$vm_address" "source ~/.profile && \
  cd SocialNetworkProblem && \
  rm -rf $output_path && \
  mvn clean install && \
  hadoop jar target/SocialNetworkProblem.jar $dataset_path $output_path"

printf "\nSuccess!\n"

printf "Downloading results to \"%s\"...\n\n" "$(pwd)/$output_path"

mkdir -p output
scp -ri "$pem_path" "$vm_address:~/SocialNetworkProblem/$output_path" "$output_path"

printf "\nDone!\""
