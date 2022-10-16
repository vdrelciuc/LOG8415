import boto3

TARGET_GROUP_CLOUDWATCH_METRICS = ['RequestCountPerTarget']
ELB_CLOUDWATCH_METRICS = ['NewConnectionCount', 'ProcessedBytes', 'TargetResponseTime']

class QueryBuilder:

    def __init__(self):
        self.cw_client = boto3.client('cloudwatch')

    def appendMetricDataQy(self, container, cluster_id, metrics, dimension):
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

    def build_cloudwatch_query(self):
        # from doc https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data
        targetgroup_val_1, targetgroup_val_2 = "targetgroup/cluster1-tg", "targetgroup/cluster2-tg"
        loadbal_val_1, loadbal_val_2 = "app/cluster1-elb", "app/cluster2-elb"
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
            self.appendMetricDataQy(metricDataQy, metric_action[0], metric_action[2], metric_action[1])

        return metricDataQy