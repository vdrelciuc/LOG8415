from datetime import date, datetime, timedelta

from infrastructure_builder import InfrastructureBuilder
from metric_data import MetricData
from workloads import run_workloads
from cloudwatch_monitor import CloudWatchMonitor

import boto3
import time
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import subprocess
import multiprocessing
import json

from matplotlib.dates import (DateFormatter)

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

# 1. Generate infrastructure (EC2 instances, load balancers and target groups)
ib = InfrastructureBuilder()
cluster1_elb, cluster2_elb, sg, m4Instances, t2Instances, listener_cluster1, listener_cluster2, cluster1_tg, cluster2_tg = initialize_infra(infra_builder=ib)
time.sleep(90)

# 2. Run workloads
run_workloads(cluster1_elb, cluster2_elb)

# 3. Build query to collect desired metrics from the last 30 minutes (estimated max workload time)
cloudwatch_monitor = CloudWatchMonitor()
query = cloudwatch_monitor.build_cloudwatch_query()

# 4. Query CloudWatch client using built query
response = cloudwatch_monitor.get_data(query)

# 5. Save output to response.json
print_response(response)

# 6. Parse MetricDataResults and store metrics
(metrics_cluster1, metrics_cluster2) = cloudwatch_monitor.parse_data(response)

# 7. Generate graphs and save under /metrics folder
generate_graphs(metrics_cluster1, metrics_cluster2)

print('Done.')
