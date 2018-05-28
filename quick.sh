#!/bin/bash


do_export() {
	aws iam get-account-authorization-details --output json > iam_export.json
	aws ec2 describe-vpcs --output json > vpcs_export.json
	aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-111111" --output json > vpcs_subnets.json
	aws ec2 describe-security-groups --output json  > sg_groups.json
	aws ec2 describe-instances --output json > ec2_list.json
}

do_import() {

# 1. 手工确认IAM部分

# 2. 手工建立工作VPC(1个)，和igw

# 3. 自动导入指定vpc的Subnet定义及其路由表

# 4. 手工操作NAT Gateway

# 5. 自动导入指定vpc的sg

# 6. 基于当前运行EC2，全部制作镜像


}


# Main
#do_export
do_import
