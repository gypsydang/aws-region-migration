#!/usr/bin/python
# -*- coding: utf8 -*-

import boto3
import json
import sys

target_region_name='cn-northwest-1'

session = boto3.Session(profile_name=sys.argv[1])
client = session.client('ec2', region_name=target_region_name)
ec2 = session.resource('ec2', region_name=target_region_name)


'''
settings2=json.load(open("vpcs_subnets.json"))
settings3=json.load(open("sg_groups.json"))


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

'''

def print_tags(tag_list):
    tag_str='Tags( '
    for tag in tag_list:
        tag_str += '{key}/{value} '.format(key=tag['Key'], value=tag['Value'])

    tag_str += ')'

    return tag_str

def import_vpcs():
    vpcs=json.load(open("vpcs_export.json"))
    
    for vpc in vpcs['Vpcs']:
        print('{cidr} {tags} IsDefault({IsDefault})'.format(cidr=vpc['CidrBlock'], tags=print_tags(vpc['Tags']), IsDefault=vpc['IsDefault']))
        
def import_subnets(vpc_id=None):
    if vpc_id is None:
        print("Please input VPC ID")
        return

    subnets=json.load(open("vpcs_subnets.json"))

    for subnet in subnets['Subnets']:
        print('{az} {cidr} {tags})'.format(az=subnet['AvailabilityZone'], cidr=subnet['CidrBlock'], tags=print_tags(subnet['Tags'])))

        # TODO cn-north-1 => cn-northwest-1
        response = client.create_subnet(
            AvailabilityZone=subnet['AvailabilityZone'].replace('cn-north-1', 'cn-northwest-1'),
            CidrBlock=subnet['CidrBlock'],
            VpcId=vpc_id,
            DryRun=False
        )
        print(response)
    
        # Adding tags
        new_subnet = ec2.Subnet(response['Subnet']['SubnetId'])
        tag = new_subnet.create_tags(
            Tags=subnet['Tags']
        )
        print(tag)
        


def import_sg():
    pass



if __name__ == '__main__':
    #import_vpcs()
    import_subnets(vpc_id='vpc-xxxxx')
    #import_sg()


