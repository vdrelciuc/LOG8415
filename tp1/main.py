from datetime import date, datetime, timedelta
import boto3
import requests
import threading
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import subprocess
import multiprocessing
import json

from matplotlib.dates import (DateFormatter)

# Metrics selected from https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
TARGET_GROUP_CLOUDWATCH_METRICS = ['RequestCountPerTarget']
ELB_CLOUDWATCH_METRICS = ['NewConnectionCount', 'ProcessedBytes', 'TargetResponseTime']

elb_metrics_count = len(ELB_CLOUDWATCH_METRICS)
tg_metrics_count = len(TARGET_GROUP_CLOUDWATCH_METRICS)

# DEFINE FUNCTIONS HERE

def create_instances(ec2_resource, instanceType, count, imageId, keyName):
    user_data = open('flask_startup.sh', 'r')
    return ec2_resource.create_instances(
        InstanceType = instanceType,
        MinCount = count,
        MaxCount = count,
        ImageId = imageId,
        KeyName = keyName,
        UserData = user_data.read(),
        SecurityGroups = ['custom-sec-group']
    )

def create_security_group(ec2_resource):
    response_vpcs = ec2_client.describe_vpcs()
    vpc_id = response_vpcs.get('Vpcs', [{}])[0].get('VpcId', '')
    response_sg = ec2_client.create_security_group(GroupName='custom-sec-group',
        Description='Security group for our instances',
        VpcId=vpc_id)
    sg_id = response_sg['GroupId']
    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
        {'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        {'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    ])
    return ec2_resource.SecurityGroup(response_sg['GroupId'])

def create_load_balancer(client, name, sg, ec2_client):
    subnets = []
    sn_all = ec2_client.describe_subnets()
    for sn in sn_all['Subnets'] :
        subnets.append(sn['SubnetId'])

    return client.create_load_balancer(
        Name=name,
        SecurityGroups=[
            sg.id
        ],
        IpAddressType='ipv4',
        Subnets= subnets
    )

def create_target_group(client, name, ec2_client):
    response_vpcs = ec2_client.describe_vpcs()
    vpc_id = response_vpcs.get('Vpcs', [{}])[0].get('VpcId', '')
    return client.create_target_group(
        Name=name,
        Protocol='HTTP',
        Port=80,
        VpcId=vpc_id
    )

def register_targets(client, targetGroup, targets):
    return client.register_targets(
        TargetGroupArn=targetGroup['TargetGroups'][0]['TargetGroupArn'],
        Targets=targets
    )

def create_listener(client, targetGroup, loadBalancer):
    return client.create_listener(
        DefaultActions=[
            {
                'TargetGroupArn': targetGroup['TargetGroups'][0]['TargetGroupArn'],
                'Type': 'forward',
            },
        ],
        LoadBalancerArn=loadBalancer['LoadBalancers'][0]['LoadBalancerArn'],
        Port=80,
        Protocol='HTTP',
    )

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

def initialize_cloudwatch():
    return boto3.client('cloudwatch')

def build_cloudwatch_query():
    # from doc https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data
    targetgroup_val_1, targetgroup_val_2 = "targetgroup/cluster1-tg", "targetgroup/cluster2-tg"
    loadbal_val_1, loadbal_val_2 = "app/cluster1-elb", "app/cluster2-elb"
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
    dimension_tg_1 = dimension_tg_2 = dimension_lb_1 = dimension_lb_2 = None
    
    for response in response_elb["Metrics"]:
        dimension = response["Dimensions"][0]
        if targetgroup_val_1 in dimension["Value"]:
            dimension_tg_1 = dimension
        elif targetgroup_val_2 in dimension["Value"]:
            dimension_tg_2 = dimension

    for response in response_tg["Metrics"]:
        dimension = response["Dimensions"][1]
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
            "Id": (metric + dimension["Name"] + str(cluster_id)).lower(),
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
    print('Started querying CloudWatch.')
    return cw_client.get_metric_data(
        MetricDataQueries=query,
        StartTime=datetime.utcnow() - timedelta(minutes=30), # metrics from the last 30 mins (estimated max workload time)
        EndTime=datetime.utcnow(),
    )

def parse_data(response):
    global elb_metrics_count, tg_metrics_count
    results = response["MetricDataResults"]

    tg_metrics_cluster1 = results[:tg_metrics_count]
    tg_metrics_cluster2 = results[tg_metrics_count:tg_metrics_count * 2]
    elb_metrics_cluster1 = results[tg_metrics_count * 2:tg_metrics_count * 2 + elb_metrics_count]
    elb_metrics_cluster2 = results[tg_metrics_count * 2 + elb_metrics_count:]

    cluster1_data = elb_metrics_cluster1 + tg_metrics_cluster1
    cluster2_data = elb_metrics_cluster2 + tg_metrics_cluster2
    return cluster1_data, cluster2_data


class MetricData:
    def __init__(self, metric):
        # "app/t2-app-load-balancer/4db0b61e07b90a45 ActiveConnectionCount"
        label = metric["Label"].split("/")  # ["app", "t2-app-load-balancer", "4db0b61e07b90a45 ActiveConnectionCount"]
        label[2] = label[2].split()[1]      # ["app", "t2-app-load-balancer", "ActiveConnectionCount"]
        label.pop(1)                        # ["app", "ActiveConnectionCount"]

        self.label = ":".join(label)
        self.timestamps = metric["Timestamps"]
        self.values = metric["Values"]


def generate_graphs(metrics_cluster1, metrics_cluster2):
    print('Generating graphs under graphs/.')
    for i in range(len(metrics_cluster1)):
        data_cluster1 = MetricData(metrics_cluster1[i])
        data_cluster2 = MetricData(metrics_cluster2[i])
        formatter = DateFormatter("%H:%M:%S")
        label = data_cluster1.label

        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(formatter)
        plt.xlabel("Timestamps")
        plt.plot(data_cluster1.timestamps, data_cluster1.values, label="Cluster 1")
        plt.plot(data_cluster2.timestamps, data_cluster2.values, label="Cluster 2")
        plt.title(label)
        plt.legend(loc='best')
        plt.savefig(f"graphs/{label}")

def initialize_infra(ec2_client, ec2_resource, elb_client):
    print('Started initializing infrastructure.')
    sg = create_security_group(ec2_resource)
    m4Instances = create_instances(ec2_resource, 'm4.large', 5, 'ami-08c40ec9ead489470', 'vockey')
    t2Instances = create_instances(ec2_resource, 't2.large', 4, 'ami-08c40ec9ead489470', 'vockey')

    cluster1_elb = create_load_balancer(elb_client, 'cluster1-elb', sg, ec2_client)
    cluster2_elb = create_load_balancer(elb_client, 'cluster2-elb', sg, ec2_client)

    cluster1_tg = create_target_group(elb_client, 'cluster1-tg', ec2_client)
    cluster2_tg = create_target_group(elb_client, 'cluster2-tg', ec2_client)

    m4targets = []
    for ins in m4Instances:
        m4targets.append({
            "Id": ins.id
        })

    t2targets = []
    for ins in t2Instances:
        t2targets.append({
            "Id": ins.id
        })

    for instance in m4Instances:
        instance.wait_until_running()

    for instance in t2Instances:
        instance.wait_until_running()

    register_targets(elb_client, cluster1_tg, m4targets)
    register_targets(elb_client, cluster2_tg, t2targets)

    listener_cluster1 = create_listener(elb_client, cluster1_tg, cluster1_elb)
    listener_cluster2 = create_listener(elb_client, cluster2_tg, cluster2_elb)

    print('Finished initializing infrastructure.')

    return cluster1_elb, cluster2_elb, sg, m4Instances, t2Instances, listener_cluster1, listener_cluster2, cluster1_tg, cluster2_tg

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def print_response(response):
    print('Saving query result in graphs/response.json.')
    with open("graphs/response.json", "w") as data_file:
        json.dump(response, data_file, indent=4, sort_keys=True, default=json_serial)

# PROGRAM EXECUTION

# # 1. Initialize AWS clients
ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')
elb_client = boto3.client('elbv2')
cw_client = boto3.client('cloudwatch')

# 2. Generate infrastructure (EC2 instances, load balancers and target groups)
cluster1_elb, cluster2_elb, sg, m4Instances, t2Instances, listener_cluster1, listener_cluster2, cluster1_tg, cluster2_tg = initialize_infra(ec2_client=ec2_client, ec2_resource=ec2_resource, elb_client=elb_client)
time.sleep(90)

# 3. Run workloads
run_workloads(cluster1_elb, cluster2_elb)

# 4. Build query to collect desired metrics from the last 30 minutes (estimated max workload time)
query = build_cloudwatch_query()

# 5. Query CloudWatch client using built query
response = get_data(cw_client=cw_client, query=query)

# 6. Save output to response.json
print_response(response)

# 7. Parse MetricDataResults and store metrics
(metrics_cluster1, metrics_cluster2) = parse_data(response)

# 8. Generate graphs and save under /metrics folder
generate_graphs(metrics_cluster1, metrics_cluster2)

print('Done.')
