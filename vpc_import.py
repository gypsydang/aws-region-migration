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
    if 'Tags' in v:
        vpc.create_tags(Tags=v['Tags'])
    vpc.load()

subnetdict={}
for n in settings2['Subnets']:
    subnetdict[n['SubnetId']]=client.create_subnet(AvailabilityZone=n['AvailabilityZone'].replace('north','northwest'),CidrBlock=n['CidrBlock'],VpcId=vpcdict[n['VpcId']])['Subnet']['SubnetId']
    subnet = ec2.Subnet(subnetdict[n['SubnetId']])
    if 'Tags' in n:
       subnet.create_tags(Tags=n['Tags'])
    subnet.load()
  
groupdict={}
for s in settings3['SecurityGroups']:
    if not (s['GroupName'] == 'default' or s['GroupName'].startswith('launch-wizard')):
        if s['VpcId'] in vpcdict:
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



settings4=json.load(open("ec2_list.json"))

amilist=json.load(open("ami.json"))

newlist=[]
for i in amilist:
    newlist.append({'ImageId':client.copy_image(Name=i['ImageName'],SourceImageId=i['ImageId'],SourceRegion='cn-north-1')['ImageId'],'ImageName':i['ImageName']})

imagedict={}
for i in newlist:
    imagedict[i['ImageName']]=i['ImageId']

for i in settings4['Reservations']:
    for ii in i['Instances']:
        for iii in ii['SecurityGroups']:
            SGIds=[]
            if iii['GroupId'] in groupdict:
                SGIds.append(groupdict[iii['GroupId']])
        if not len(SGIds)==0:
            ec2.create_instances(MaxCount=1,MinCount=1,ImageId=imagedict[ii['InstanceId']],InstanceType=ii['InstanceType'],SecurityGroupIds=SGIds,SubnetId=subnetdict[ii['SubnetId']],PrivateIpAddress=ii['PrivateIpAddress'])





    





