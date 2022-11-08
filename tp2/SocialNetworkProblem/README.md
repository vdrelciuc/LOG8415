# How to run?

You need the ip of your vm and the .pem file.

```bash
# `./run.sh <ip> <path-to-pem> <path-to-dataset>
# <vm_address> is the ip of the vm that will be used to connect via ssh. Should be formatted as "<user>@<ip>"
# <path-to-dataset> is optional

./run.sh ubuntu@20.124.97.80 ubuntu_v2.pem 
```

You can specify a custom dataset using:

```bash
./run.sh ubuntu@20.124.97.80 ubuntu_v2.pem src/main/resources/test.txt
```
