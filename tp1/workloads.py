import requests
import time
import threading

def call_endpoint_http(cluster):
    headers = {'content-type': 'application/json'}
    url = 'http://' + cluster
    request = requests.get(url, headers=headers, verify=False)
    return request

def run_first_workload(elb_dns):
    # 1000 GET requests sequentially
    print('Started first workload.')
    for _ in range(1000):
        call_endpoint_http(elb_dns)
    print('Finished first workload.')

def run_second_workload(elb_dns):
    # 500 GET requests, then one minute sleep, followed by 1000 GET requests
    print('Started second workload.')
    for _ in range(500):
        call_endpoint_http(elb_dns)

    time.sleep(60)

    for _ in range(1000):
        call_endpoint_http(elb_dns)
    print('Finished second workload.')

def run_workloads(elb):
    elb_dns = elb['LoadBalancers'][0]['DNSName']

    first_workload_thread = threading.Thread(target=run_first_workload, args=(elb_dns))
    second_workload_thread = threading.Thread(target=run_second_workload, args=(elb_dns))

    first_workload_thread.start()
    second_workload_thread.start()

    first_workload_thread.join()
    second_workload_thread.join()
