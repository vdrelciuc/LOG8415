import requests
import time
import threading

def call_endpoint_http(cluster):
    headers = {'content-type': 'application/json'}
    url = 'http://' + cluster
    request = requests.get(url, headers=headers, verify=False)
    return request

def run_first_workload(t2_cluster, m4_cluster):
    # 1000 GET requests sequentially
    print('Started first workload.')
    for _ in range(1000):
        call_endpoint_http(t2_cluster)
        call_endpoint_http(m4_cluster)
    print('Finished first workload.')

def run_second_workload(t2_cluster, m4_cluster):
    # 500 GET requests, then one minute sleep, followed by 1000 GET requests
    print('Started second workload.')
    for _ in range(500):
        call_endpoint_http(t2_cluster)
        call_endpoint_http(m4_cluster)

    time.sleep(60)

    for _ in range(1000):
        call_endpoint_http(t2_cluster)
        call_endpoint_http(m4_cluster)
    print('Finished second workload.')

def run_workloads(cluster1_elb, cluster2_elb):
    m4_cluster = cluster1_elb['LoadBalancers'][0]['DNSName']
    t2_cluster = cluster2_elb['LoadBalancers'][0]['DNSName']

    t2_code, m4_code = 0, 0
    while (t2_code != 200) and (m4_code != 200):
        t2_code = call_endpoint_http(t2_cluster).status_code
        m4_code = call_endpoint_http(m4_cluster).status_code
        time.sleep(2)

    first_workload_thread = threading.Thread(target=run_first_workload, args=(t2_cluster,m4_cluster))
    second_workload_thread = threading.Thread(target=run_second_workload, args=(t2_cluster,m4_cluster))

    first_workload_thread.start()
    second_workload_thread.start()

    first_workload_thread.join()
    second_workload_thread.join()
