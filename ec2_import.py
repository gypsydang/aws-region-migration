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
    'instance-ami': {},
    'security_group':{}
} 

session = boto3.Session(profile_name=sys.argv[1])
ec2_client_handler = session.client('ec2', region_name=transform_map['region']['from'])
ec2_resource_handler = session.resource('ec2', region_name=transform_map['region']['from'])

def print_tags(tag_list):
    tag_str='Tags( '
    for tag in tag_list:
        tag_str += '{key}/{value} '.format(key=tag['Key'], value=tag['Value'])

    tag_str += ')'

    return tag_str

def import_sg():

    transform_map = load_json_from_file('transform.json')
    sg_groups = load_json_from_file('sg_groups.json')

    for sg_group in sg_groups['SecurityGroups']:
        if sg_group['VpcId'] not in transform_map['vpc'].keys():
            continue

        if sg_group['GroupName'] == 'default':
            continue

        response = client.create_security_group(
            Description=sg_group['Description'],
            GroupName=sg_group['GroupName'],
            VpcId=transform_map['vpc'][sg_group['VpcId']]
        )

        print(response)
        sg_id = response['GroupId']
        security_group = ec2.SecurityGroup(sg_id)
        # Adding Ingress/Egress rules
        response = security_group.authorize_ingress(
            IpPermissions=sg_group['IpPermissions']
        )
        ## TODO: Skip just here, later will clear the egress
        #response = security_group.authorize_egress(
            #IpPermissions=sg_group['IpPermissionsEgress']
        #)

        # Adding tags
        tag = security_group.create_tags(
            Tags=sg_group['Tags']
        )

        print(tag)

        transform_map['security_group'][sg_group['GroupId']] = sg_id

        write_json_to_file('transform.json', transform_map)


def create_image(ec2)
    '''
    response = client.create_image(
        BlockDeviceMappings=[
            {
                'DeviceName': 'string',
                'VirtualName': 'string',
                'Ebs': {
                    'Encrypted': True|False,
                    'DeleteOnTermination': True|False,
                    'Iops': 123,
                    'KmsKeyId': 'string',
                    'SnapshotId': 'string',
                    'VolumeSize': 123,
                    'VolumeType': 'standard'|'io1'|'gp2'|'sc1'|'st1'
                },
                'NoDevice': 'string'
            },
        ],
        Description='string',
        DryRun=True|False,
        InstanceId='string',
        Name='string',
        NoReboot=True
    )
    '''
    pass



def import_ec2():

    ec2_list = load_json_from_file('ec2_list.json')

    for reservation in ec2_list['Reservations']:
        for ec2 in reservation['Instances']:
            # Skip Terminated
            if ec2['State']['Name'] == 'terminated':
                continue

            if ec2['VpcId'] not in transform_map['vpc'].keys():
                continue

            #ami_

            res = create_image(ec2)

            ami_id = res['ImageId']
            
            print('{} {} EC2 interfaces({}) ami_id({})'.format(ec2['VpcId'], ec2['InstanceId'], len(ec2['NetworkInterfaces']), ami_id))

            transform_map['instance_ami'][ec2['InstanceId']] = ami_id

if __name__ == '__main__':
    transform_map = load_json_from_file('transform.json')

    import_ec2()

    write_json_to_file('transform.json', transform_map)
