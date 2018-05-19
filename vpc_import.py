import boto3
import json
settings1=json.load(open("vpcs_export.json"))
settings2=json.load(open("vpcs_subnets.json"))
settings3=json.load(open("sg_groups.json"))

client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

vpcdict={}
for v in settings1['Vpcs']:
    vpcdict[v['VpcId']]=client.create_vpc(CidrBlock=v['CidrBlock'])['Vpc']['VpcId']
    vpc = ec2.Vpc(vpcdict[v['VpcId']])
    vpc.create_tags(Tags=v['Tags'])
    vpc.load()

subnetdict={}
for n in settings2['Subnets']:
    subnetdict[n['SubnetId']]=client.create_subnet(AvailabilityZone=n['AvailabilityZone'].replace('north','northwest'),CidrBlock=n['CidrBlock'],VpcId=vpcdict[n['VpcId']])['Subnet']['SubnetId']
    subnet = ec2.Subnet(subnetdict[n['SubnetId']])
    subnet.create_tags(Tags=n['Tags'])
    subnet.load()
    
groupdict={}
for s in settings3['SecurityGroups']:
    if not (s['GroupName'] == 'default' or s['GroupName'].startswith('launch-wizard')):
        groupdict[s['GroupId']]=client.create_security_group(Description=s['Description'],GroupName=s['GroupName'],VpcId=vpcdict[s['VpcId']])['GroupId']
        security_group = ec2.SecurityGroup(groupdict[s['GroupId']])
        security_group.authorize_ingress(IpPermissions=s['IpPermissions'])
        FPermissions=[]
        for q in s['IpPermissionsEgress']:
            if not (q['IpProtocol']=='-1'):
                FPermissions.append(q)
        if not len(FPermissions)==0:
            security_group.authorize_egress(IpPermissions=FPermissions)
        if 'Tags' in s:
            security_group.create_tags(Tags=s['Tags'])
        security_group.load()





    





