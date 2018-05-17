#!/bin/bash


REGION_LIST="cn-north-1"
PROFILE=$1

[ "_$PROFILE" = "_" ] && PROFILE=default

for R in ${REGION_LIST}; do
	#echo "AvailabilityZone,State,InstanceId,InstanceType,Platform,Name"
	#aws --profile $PROFILE ec2 --region $R describe-instances --query 'Reservations[*].Instances[*].[Placement.AvailabilityZone, State.Name, InstanceId, InstanceType, Platform, Tags[0].Value]' --filter Name=instance-state-code,Values=16,80 --output text | awk '{print $1","$2","$3","$4","$5}'
	aws --profile $PROFILE ec2 describe-vpcs
done



aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-dc2ddeb5" --output json


exit 0
