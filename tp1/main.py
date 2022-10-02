from datetime import datetime 
from datetime import timedelta
import boto3
import requests
import time

T2_CLUSTER_ELB = 'http://t2-app-load-balancer-865787253.us-east-1.elb.amazonaws.com/'
M4_CLUSTER_ELB = 'http://m4-app-load-balancer-41265058.us-east-1.elb.amazonaws.com/'
AWS_ACCESS_KEY_ID = 'ASIAY66MJR2U4XF6UEEJ'
AWS_SECRET_ACCESS_KEY = 'ay3MA1ep8BL8VfB4oEyabetu/AUcWnpBiby3FE1E'
AWS_SESSION_TOKEN = 'FwoGZXIvYXdzEOv//////////wEaDNeUebVcXeb9BkVOWyLDAdnNimCUhv7s3OFRP9QEVcp5cixFhW+wwh0B+mlTTyRJWeoyPILwWoiN+FLRWM3saBQbhl4AVofPFINMjm+KTmKRjFMnCVpz1T6iskCHeckNL9DY61EPAFBs/GO+3i2ECk4PmtcpJzSDtxPkv/yYBQ7IcxE1hwnuSqhyIezs3QvJrARW61yLu2VG8ToJh4UXsrxa4FQxEFQ3IhZjbxCArnHyV43oQCCgNebj5rRDlS0FPlIX98Q7Nc91OcjUL6MkBeJjSiiml+eZBjItPtJeXMP0/uVUqKahN8Zxri3ja/tR8I3M4UJF59frn7tCjIySVFfHlrJ4zt4V'

# Metrics selected from https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html
TARGET_GROUP_CLOUDWATCH_METRICS = ['HealthyHostCount', 'HTTPCode_Target_4XX_Count','HTTPCode_Target_2XX_Count', 'RequestCount', 'RequestCountPerTarget', 'TargetResponseTime','UnHealthyHostCount'] 
ELB_CLOUDWATCH_METRICS = ['ActiveConnectionCount', 'ConsumedLCUs', 'RequestCount', 'HTTPCode_ELB_5XX_Count', 'HTTPCode_ELB_503_Count', 'HTTPCode_Target_2XX_Count', 'NewConnectionCount', 'ProcessedBytes', 'TargetResponseTime'] 

# DEFINE FUNCTIONS HERE

def initialize_infra():
    # TODO: implement
    return {}

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

def initialize_cloudwatch():
    return boto3.client(
        'cloudwatch', 
        region_name='us-east-1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN)

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
    # from doc https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data
    # TODO: implement using template in doc
    return {}

def generate_graphs(metrics):
    # TODO: implement using matplotlib.pyplot
    return {} # delete return after implement

# PROGRAM EXECUTION

# 1. Generate infrastructure (EC2 instances, load balancers and target groups)
initialize_infra()

# 2. Run first workload
# run_first_workload() # uncomment to execute workload (takes ~1 min)

# 3. Run second workload
# run_second_workload() # uncomment to execute workload (takes ~ 3 min)

# 4. Create CloudWatch client using boto3
cw_client = initialize_cloudwatch()

# 5. Build query to collect desired metrics from the last 30 minutes (estimated max workload time)
query = build_cloudwatch_query()

# 6. Query CloudWatch client using built query 
response = get_data(cw_client=cw_client, query=query)

# 7. Parse MetricDataResults and store metrics
metrics = parse_data(response)

# 8. Generate graphs and save under /metrics folder
generate_graphs(metrics)
