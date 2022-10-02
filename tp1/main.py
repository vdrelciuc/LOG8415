from datetime import datetime 
from datetime import timedelta
import boto3
import requests
import threading
import time

# Metrics selected from https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
TARGET_GROUP_CLOUDWATCH_METRICS = ['HealthyHostCount', 'HTTPCode_Target_4XX_Count','HTTPCode_Target_2XX_Count', 'RequestCount', 'RequestCountPerTarget', 'TargetResponseTime','UnHealthyHostCount'] 
ELB_CLOUDWATCH_METRICS = ['ActiveConnectionCount', 'ConsumedLCUs', 'RequestCount', 'HTTPCode_ELB_5XX_Count', 'HTTPCode_ELB_503_Count', 'HTTPCode_Target_2XX_Count', 'NewConnectionCount', 'ProcessedBytes', 'TargetResponseTime'] 

# DEFINE FUNCTIONS HERE

def initialize_infra():
    # TODO: implement
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
    targetgroup_val_1, targetgroup_val_2 = "targetgroup/t2-app-load", "targetgroup/m4-app-load-balancer"
    loadbal_val_1, loadbal_val_2 = "app/t2-app-load", "app/m4-app-load-balancer"
    response_elb = cw_client.list_metrics(Namespace= 'AWS/ApplicationELB', MetricName= 'RequestCount', Dimensions=[
        {
            'Name': 'LoadBalancer',
        },
    ])
    response_tg = cw_client.list_metrics(Namespace= 'AWS/ApplicationELB', MetricName= 'RequestCount', Dimensions=[
        {
            'Name': 'TargetGroup',
        },
    ])
    for response in response_elb["Metrics"]:
        dimension = response["Dimensions"][0]
        if targetgroup_val_1 in dimension["Value"]:
            dimension_tg_1 = dimension
        elif targetgroup_val_2 in dimension["Value"]:
            dimension_tg_2 = dimension
    
    for response in response_tg["Metrics"]:
        dimension = response["Dimensions"][0]
        if loadbal_val_1 in dimension["Value"]:
            dimension_lb_1 = dimension
        elif loadbal_val_2 in dimension["Value"]:
            dimension_lb_2 = dimension

    metricDataQy = []
    metric_pipeline = [(1, dimension_tg_1, TARGET_GROUP_CLOUDWATCH_METRICS), (2, dimension_tg_2, TARGET_GROUP_CLOUDWATCH_METRICS), 
        (1, dimension_lb_1, ELB_CLOUDWATCH_METRICS), (2, dimension_lb_2, ELB_CLOUDWATCH_METRICS)]
    for metric_action in metric_pipeline:
        appendMetricDataQy(metricDataQy, metric_action[0], metric_action[2], metric_action[1])
    return metricDataQy

def appendMetricDataQy(container, cluster_id, metrics, dimension):
    for metric in metrics:
        container.append({
            "Id": metric + dimension["Name"] + cluster_id,
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/ApplicationELB",
                    "MetricName": metric,
                    "Dimensions": [
                        {
                            "Name": dimension["Name"],
                            "Value": dimension["Value"]
                        }
                    ]
                },
                "Period": 60,
                "Stat": "Average",
            }
        })
    

def get_data(cw_client, query):
    return cw_client.get_metric_data(
        MetricDataQueries=query,
        StartTime=datetime.utcnow() - timedelta(minutes=30), # metrics from the last 30 mins (estimated max workload time)
        EndTime=datetime.utcnow(),
    )

def parse_data(response):
    # from doc https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data
    # TODO: implement using template in doc
    return {}

def generate_graphs(metrics):
    # TODO: implement using matplotlib.pyplot
    return {} # delete return after implement

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

'''
# 5. Query CloudWatch client using built query 
response = get_data(cw_client=cw_client, query=query)

# 6. Parse MetricDataResults and store metrics
metrics = parse_data(response)

# 7. Generate graphs and save under /metrics folder
generate_graphs(metrics)
'''
print('Done')
