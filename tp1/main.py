from datetime import date, datetime, timedelta

from infrastructure_builder import InfrastructureBuilder
from metric_data import MetricData
from workloads import run_workloads

import boto3
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
                "Stat": "Sum",
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

def initialize_infra(infra_builder):
    print('Started initializing infrastructure.')

    security_group = infra_builder.create_security_group('custom-sec-group-2')

    user_data = open('flask_startup.sh', 'r').read()
    m4_Instances = infra_builder.create_instances('m4.large', 5, 'ami-08c40ec9ead489470', 'vockey', user_data, security_group.group_name)
    t2_Instances = infra_builder.create_instances('t2.large', 4, 'ami-08c40ec9ead489470', 'vockey', user_data, security_group.group_name)

    cluster1_elb = infra_builder.create_load_balancer('cluster1-elb', security_group.id)
    cluster2_elb = infra_builder.create_load_balancer('cluster2-elb', security_group.id)

    cluster1_tg = infra_builder.create_target_group('cluster1-tg')
    cluster2_tg = infra_builder.create_target_group('cluster2-tg')

    infra_builder.register_targets(cluster1_tg, m4_Instances)
    infra_builder.register_targets(cluster2_tg, t2_Instances)

    listener_cluster1 = infra_builder.create_listener(cluster1_tg, cluster1_elb)
    listener_cluster2 = infra_builder.create_listener(cluster2_tg, cluster2_elb)

    print('Finished initializing infrastructure.')

    return cluster1_elb, cluster2_elb, security_group, m4_Instances, t2_Instances, listener_cluster1, listener_cluster2, cluster1_tg, cluster2_tg

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
cw_client = boto3.client('cloudwatch')

# 2. Generate infrastructure (EC2 instances, load balancers and target groups)
ib = InfrastructureBuilder()
cluster1_elb, cluster2_elb, sg, m4Instances, t2Instances, listener_cluster1, listener_cluster2, cluster1_tg, cluster2_tg = initialize_infra(infra_builder=ib)
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
