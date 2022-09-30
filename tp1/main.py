import json
import requests

def call_endpoint_http():
    url = 'http://ec2-54-144-178-229.compute-1.amazonaws.com'
    headers = {'content-type': 'application/json'}
    request = requests.get(url, headers=headers)
    print(request.status_code)
    print(request.text)

call_endpoint_http()

