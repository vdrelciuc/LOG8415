import boto3

class InfrastructureBuilder:

    def __init__(self):
        self.ec2_client = boto3.client('ec2')
        self.ec2_resource = boto3.resource('ec2')
        self.elb_client = boto3.client('elbv2')

    def create_security_group(self, name):
        response_vpcs = self.ec2_client.describe_vpcs()
        vpc_id = response_vpcs.get('Vpcs', [{}])[0].get('VpcId', '')

        response_security_group = self.ec2_client.create_security_group(
            GroupName=name,
            Description='Security group for our instances',
            VpcId=vpc_id)

        security_group_id = response_security_group['GroupId']
        
        self.ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
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
        
        return self.ec2_resource.SecurityGroup(response_security_group['GroupId'])
