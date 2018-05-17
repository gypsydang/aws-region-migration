#!/bin/bash


aws iam get-account-authorization-details --output json > iam_export.json
aws ec2 describe-vpcs --output json > vpcs_export.json
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-111111" --output json > vpcs_subnets.json
aws ec2 describe-security-groups --output json  > sg_groups.json
aws ec2 describe-instances --output json > ec2_list.json
