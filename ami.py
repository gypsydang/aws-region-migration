

import boto3
import json

client = boto3.client('ec2')

settings=json.load(open("ec2_list.json"))

amilist=[]
for i in settings['Reservations']:
    for ii in i['Instances']:
        amilist.append({'ImageId':client.create_image(InstanceId=ii['InstanceId'],Name=ii['InstanceId'],NoReboot=True)['ImageId'],'ImageName':ii['InstanceId']})

with open("ami.json",'w') as f_obj:
    json.dump(amilist, f_obj)





