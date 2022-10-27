from datetime import date, datetime, timedelta
from metric_data import MetricData

import boto3
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import (DateFormatter)

# Metrics selected from https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
TARGET_GROUP_CLOUDWATCH_METRICS = ['RequestCountPerTarget']
ELB_CLOUDWATCH_METRICS = ['NewConnectionCount', 'ProcessedBytes', 'TargetResponseTime']
EC2_CLOUDWATCH_METRICS = ['CPUUtilization', 'NetworkIn', 'NetworkOut']

elb_metrics_count = len(ELB_CLOUDWATCH_METRICS)
tg_metrics_count = len(TARGET_GROUP_CLOUDWATCH_METRICS)
ecs_metrics_count = len(EC2_CLOUDWATCH_METRICS)

class CloudWatchMonitor:

    def __init__(self):
        self.cw_client = boto3.client('cloudwatch')

    def appendMetricDataQy(self, container, cluster_id, metrics, dimension):
        for metric in metrics:
            if metric in EC2_CLOUDWATCH_METRICS:
                namespace = 'AWS/EC2'
            else:
                namespace = 'AWS/ApplicationELB'
            container.append({
                "Id": (metric + dimension["Name"] + cluster_id).lower(),
                "MetricStat": {
                    "Metric": {
                        "Namespace": namespace,
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

    def build_cloudwatch_query(self, instances):
        # from doc https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data
        targetgroup_val_1, targetgroup_val_2 = "targetgroup/cluster1", "targetgroup/cluster2"
        loadbal_val = "app/elb"
        response_elb = self.cw_client.list_metrics(Namespace= 'AWS/ApplicationELB', MetricName= 'RequestCount', Dimensions=[
            {
                'Name': 'LoadBalancer',
            },
        ])
        response_tg = self.cw_client.list_metrics(Namespace= 'AWS/ApplicationELB', MetricName= 'RequestCount', Dimensions=[
            {
                'Name': 'TargetGroup',
            },
        ])
        dimension_tg_1 = dimension_tg_2 = dimension_lb = None
        for response in response_elb["Metrics"]:
            dimension = response["Dimensions"][0]
            if loadbal_val in dimension["Value"]:
                dimension_lb = dimension

        for response in response_tg["Metrics"]:
            dimension = response["Dimensions"][0]
            if targetgroup_val_1 in dimension["Value"]:
                dimension_tg_1 = dimension
            elif targetgroup_val_2 in dimension["Value"]:
                dimension_tg_2 = dimension

        metricDataQy = []
        metric_pipeline = [('1', dimension_tg_1, TARGET_GROUP_CLOUDWATCH_METRICS), ('2', dimension_tg_2, TARGET_GROUP_CLOUDWATCH_METRICS),
            ('', dimension_lb, ELB_CLOUDWATCH_METRICS)]
        metric_pipeline += [(instance.id.split('-')[1], { 'Name': 'InstanceId', 'Value': instance.id }, EC2_CLOUDWATCH_METRICS) for instance in instances]
        for metric_action in metric_pipeline:
            self.appendMetricDataQy(metricDataQy, metric_action[0], metric_action[2], metric_action[1])
        return metricDataQy

    def get_data(self, query):
        print('Started querying CloudWatch.')
        return self.cw_client.get_metric_data(
            MetricDataQueries=query,
            StartTime=datetime.utcnow() - timedelta(minutes=30), # metrics from the last 30 mins (estimated max workload time)
            EndTime=datetime.utcnow(),
        )

    def parse_data(self, response):
        global elb_metrics_count, tg_metrics_count
        results = response["MetricDataResults"]
        tg_metrics_cluster1 = results[:tg_metrics_count]
        tg_metrics_cluster2 = results[tg_metrics_count:tg_metrics_count * 2]
        elb_metrics = results[tg_metrics_count * 2:tg_metrics_count * 2 + elb_metrics_count]
        ecs_metrics = results[tg_metrics_count * 2 + elb_metrics_count:]
        print('tg_metrics_cluster1', tg_metrics_cluster1)
        print('tg_metrics_cluster2', tg_metrics_cluster2)
        print('elb_metrics', elb_metrics)
        print('ecs_metrics', ecs_metrics)
        return tg_metrics_cluster1, tg_metrics_cluster2, elb_metrics, ecs_metrics

    def generate_graphs(self, metrics_cluster1, metrics_cluster2):
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

    