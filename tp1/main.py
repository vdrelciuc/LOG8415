from datetime import datetime, timedelta
import boto3
import requests
import threading
import time
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import (DateFormatter)
matplotlib.use('TkAgg')

# Metrics selected from https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
TARGET_GROUP_CLOUDWATCH_METRICS = ['HealthyHostCount', 'HTTPCode_Target_4XX_Count','HTTPCode_Target_2XX_Count', 'RequestCount', 'RequestCountPerTarget', 'TargetResponseTime','UnHealthyHostCount']
ELB_CLOUDWATCH_METRICS = ['ActiveConnectionCount', 'ConsumedLCUs', 'RequestCount', 'HTTPCode_ELB_5XX_Count', 'HTTPCode_ELB_503_Count', 'HTTPCode_Target_2XX_Count', 'NewConnectionCount', 'ProcessedBytes', 'TargetResponseTime']

elb_metrics_count = len(ELB_CLOUDWATCH_METRICS)
tg_metrics_count = len(TARGET_GROUP_CLOUDWATCH_METRICS)

# DEFINE FUNCTIONS HERE

def initialize_infra():
    # TODO: implement

    #create instances
    ec2_client = boto3.client('ec2')
    
    ec2_client.run_instances(
        InstanceType='m4.large',
        MinCount=1,
        MaxCount=2,
        ImageId='ami-08c40ec9ead489470',
        KeyName='vockey'
        )

    ec2_client.run_instances(
        InstanceType='t2.large',
        MinCount=1,
        MaxCount=5,
        ImageId='ami-08c40ec9ead489470',
        KeyName='vockey'
        )

    #create target groups
    elbv2_client = boto3.client('elbv2')
    elbv2_client.create_target_group(name="m4-target-group")
    elbv2_client.create_target_group(name="t2-target-group")

   

    return {}

def call_endpoint_http(cluster):
    headers = {'content-type': 'application/json'}
    url = 'http://' + cluster
    request = requests.get(url, headers=headers)
    # print(request.text) # uncomment to see individual instance_id

def run_first_workload(t2_cluster, m4_cluster):
    # 1000 GET requests sequentially
    print('Starting first workload...')
    for _ in range(10): # TODO: update with real values
        call_endpoint_http(t2_cluster)
        call_endpoint_http(m4_cluster)
    print('Finishing first workload...')

def run_second_workload(t2_cluster, m4_cluster):
    # 500 GET requests, then one minute sleep, followed by 1000 GET requests
    print('Starting second workload...')
    for _ in range(5): # TODO: update with real values
        call_endpoint_http(t2_cluster)
        call_endpoint_http(m4_cluster)

    time.sleep(6) # TODO: update with real values

    for _ in range(10): # TODO: update with real values
        call_endpoint_http(t2_cluster)
        call_endpoint_http(m4_cluster)
    print('Finishing second workload...')

def run_workloads(elb_client):
    response = elb_client.describe_load_balancers()
    t2_cluster = response['LoadBalancers'][0]['DNSName'] # TODO: update hardcoded cluster
    m4_cluster = response['LoadBalancers'][1]['DNSName'] # TODO: update hardcoded cluster

    first_workload_thread = threading.Thread(target=run_first_workload, args=(t2_cluster,m4_cluster))
    second_workload_thread = threading.Thread(target=run_second_workload, args=(t2_cluster,m4_cluster))

    first_workload_thread.start()
    second_workload_thread.start()

    first_workload_thread.join()
    second_workload_thread.join()

def initialize_cloudwatch():
    return boto3.client('cloudwatch')

def build_cloudwatch_query():
    # from doc https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data
    # TODO: implement using template in doc
    return {}

def get_data(cw_client, query):
    return cw_client.get_metric_data(
        MetricDataQueries=query,
        StartTime=datetime.utcnow() - timedelta(minutes=30), # metrics from the last 30 mins (estimated max workload time)
        EndTime=datetime.utcnow(),
    )

def parse_data(response):
    global elb_metrics_count, tg_metrics_count
    results = response["MetricDataResults"]

    elb_metrics_cluster1 = results[:elb_metrics_count]
    elb_metrics_cluster2 = results[elb_metrics_count:elb_metrics_count * 2]
    tg_metrics_cluster1 = results[elb_metrics_count * 2:elb_metrics_count * 2 + tg_metrics_count]
    tg_metrics_cluster2 = results[elb_metrics_count * 2 + tg_metrics_count:]

    cluster1_data = elb_metrics_cluster1 + tg_metrics_cluster1
    cluster2_data = elb_metrics_cluster2 + tg_metrics_cluster2
    return cluster1_data, cluster2_data


class MetricData:
    def __init__(self, metric):
        self.label = metric["Label"]
        self.timestamps = metric["Timestamps"]
        self.values = metric["Values"]


def generate_graphs(metrics_cluster1, metrics_cluster2):
    for i in range(len(metrics_cluster1)):
        data_cluster1 = MetricData(metrics_cluster1[i])
        data_cluster2 = MetricData(metrics_cluster2[i])
        formatter = DateFormatter("%H:%M:%S")

        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(formatter)
        plt.xlabel("Timestamps")
        plt.plot(data_cluster1.timestamps, data_cluster1.values, label="Cluster 1")
        plt.plot(data_cluster2.timestamps, data_cluster2.values, label="Cluster 2")
        plt.title(data_cluster1.label)
        plt.legend(loc='best')
        plt.savefig(f"graphs/{data_cluster1.label}")

# PROGRAM EXECUTION

# 1. Initialize AWS clients
elb_client = boto3.client('elbv2')
cw_client = boto3.client('cloudwatch')

# 2. Generate infrastructure (EC2 instances, load balancers and target groups)
initialize_infra()

# 3. Run workloads
run_workloads(elb_client)

# 4. Build query to collect desired metrics from the last 30 minutes (estimated max workload time)
query = build_cloudwatch_query()

# 5. Query CloudWatch client using built query
response = get_data(cw_client=cw_client, query=query)

# 6. Parse MetricDataResults and store metrics
(metrics_cluster1, metrics_cluster2) = parse_data(response)

# 7. Generate graphs and save under /metrics folder
generate_graphs(metrics_cluster1, metrics_cluster2)
print('Done')
