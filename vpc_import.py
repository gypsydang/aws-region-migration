#!/usr/bin/python
# -*- coding: utf8 -*-

import boto3
from botocore.exceptions import ClientError

import json
import sys
from utils import *

target_region_name='cn-northwest-1'


# 用于记录源数据到目标数据的ID转换, 例如 subnet_id, sg_id
transform_map = {
    'region': { 'from':'cn-north-1', 'to':'cn-northwest-1'},
    'vpc':{},
    'subnet':{},
    'security_group':{}
} 

session = boto3.Session(profile_name=sys.argv[1])
client = session.client('ec2', region_name=transform_map['region']['to'])
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
        if 'Tags' not in vpc:
            vpc['Tags'] = [
                {
                    'Key': 'Name',
                    'Value': ''
                }
            ]
        print('{cidr} {tags} IsDefault({IsDefault})'.format(cidr=vpc['CidrBlock'], tags=print_tags(vpc['Tags']), IsDefault=vpc['IsDefault']))
        
def import_subnets():
    subnets = load_json_from_file('vpcs_subnets.json')

    for subnet in subnets['Subnets']:
        if 'Tags' not in subnet:
            subnet['Tags'] = [
                {
                    'Key': 'Name',
                    'Value': ''
                }
            ]
        print('{az} {cidr} {tags})'.format(az=subnet['AvailabilityZone'], cidr=subnet['CidrBlock'], tags=print_tags(subnet['Tags'])))

        if subnet['VpcId'] not in transform_map['vpc'].keys():
            continue

        response = client.create_subnet(
            AvailabilityZone=subnet['AvailabilityZone'].replace(transform_map['region']['from'], transform_map['region']['to']),
            CidrBlock=subnet['CidrBlock'],
            VpcId=transform_map['vpc'][subnet['VpcId']],
            DryRun=False
        )
        #print(response)
    
        # Adding tags
        dst_subnet_id = response['Subnet']['SubnetId']
        new_subnet = ec2.Subnet(dst_subnet_id)
        tag = new_subnet.create_tags(
            Tags=subnet['Tags']
        )

        transform_map['subnet'][subnet['SubnetId']] = dst_subnet_id

        write_json_to_file('transform.json', transform_map)

        #print(tag)
        

def tranform_IpPermissions(permissions):
    transformed_list=[]
    for permission in permissions:
        group_list=[]
        if 'UserIdGroupPairs' in permission:
            for group in permission['UserIdGroupPairs']:
                print group
                print transform_map['security_group'][group['GroupId']]
            
                group_list.append({
                        'GroupId': transform_map['security_group'][group['GroupId']],
                        'UserId': transform_map['account']['to']
                    }
                )
            permission['UserIdGroupPairs']=group_list
        transformed_list.append(permission)
                
    print transformed_list
    return transformed_list


def import_sg(Type='Group'):
    sg_groups = load_json_from_file('sg_groups.json')

    for sg_group in sg_groups['SecurityGroups']:
        if sg_group['VpcId'] not in transform_map['vpc'].keys():
            continue

        if sg_group['GroupName'] == 'default':
            continue

        if Type == 'Group':
            response = client.create_security_group(
                Description=sg_group['Description'],
                GroupName=sg_group['GroupName'],
                VpcId=transform_map['vpc'][sg_group['VpcId']]
            )

            print(response)
            sg_id = response['GroupId']

            transform_map['security_group'][sg_group['GroupId']] = sg_id

            print(sg_id)

            # Adding tags
            security_group = ec2.SecurityGroup(sg_id)
            if 'Tags' in sg_group:
                tag = security_group.create_tags(
                    Tags=sg_group['Tags']
                )
                print(tag)
        elif Type == 'Rule':
            # Adding Ingress/Egress rules
            # TODO: Src ... sg mapping
            security_group = ec2.SecurityGroup(transform_map['security_group'][sg_group['GroupId']])
            response = security_group.authorize_ingress(
                IpPermissions=tranform_IpPermissions(sg_group['IpPermissions'])
            )
            ## TODO: Skip just here, later will clear the egress
            #response = security_group.authorize_egress(
                #IpPermissions=sg_group['IpPermissionsEgress']
            #)

    write_json_to_file('transform.json', transform_map)

if __name__ == '__main__':
    transform_map = load_json_from_file('transform.json')

    import_vpcs()
    import_subnets()
    import_sg(Type='Group')
    import_sg(Type='Rule')

    write_json_to_file('transform.json', transform_map)

