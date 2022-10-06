#!/bin/bash

sudo apt-get update
sudo apt-get -y install python3-pip
sudo pip3 install flask
mkdir flask_app
cd flask_app
instance_id=$(ec2metadata --instance-id)
echo "from flask import Flask
app = Flask(__name__)
@app.route('/')
def myFlaskApp():

        return \""$instance_id" is responding now! \"

if __name__ == \"__main__\":
       app.run(host='0.0.0.0', port=80) " | sudo tee app.py
echo "DONE"
exit