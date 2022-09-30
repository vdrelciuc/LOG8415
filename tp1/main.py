import requests
import time

T2_CLUSTER_ELB = 'http://t2-app-load-balancer-865787253.us-east-1.elb.amazonaws.com/'
M4_CLUSTER_ELB = 'http://m4-app-load-balancer-41265058.us-east-1.elb.amazonaws.com/'
AWS_ACCESS_KEY_ID = 'XXX'
AWS_SECRET_ACCESS_KEY = 'YYY'
AWS_SESSION_TOKEN = 'ZZZ'

def call_endpoint_http(cluster):
    headers = {'content-type': 'application/json'}
    request = requests.get(cluster, headers=headers)
    # print(request.text) # uncomment to see individual instance_id

def run_first_workload():
    # 1000 GET requests sequentially
    print('Starting first workload...')
    for _ in range(1000):
        call_endpoint_http(T2_CLUSTER_ELB)
        call_endpoint_http(M4_CLUSTER_ELB)
    print('Finishing first workload...')

def run_second_workload():
    # 500 GET requests, then one minute sleep, followed by 1000 GET requests
    print('Starting second workload...')
    for _ in range(500):
        call_endpoint_http(T2_CLUSTER_ELB)
        call_endpoint_http(M4_CLUSTER_ELB)

    time.sleep(60)

    for _ in range(1000):
        call_endpoint_http(T2_CLUSTER_ELB)
        call_endpoint_http(M4_CLUSTER_ELB)
    print('Finishing second workload...')

run_first_workload()
run_second_workload()
