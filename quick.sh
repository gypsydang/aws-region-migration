#!/bin/bash


do_export() {
	P=$1
	R=$2
	aws --profile $P --region $R iam get-account-authorization-details --output json > iam_export.json
	aws --profile $P --region $R ec2 describe-vpcs --output json > vpcs_export.json
	aws --profile $P --region $R ec2 describe-subnets --output json > vpcs_subnets.json
	aws --profile $P --region $R ec2 describe-security-groups --output json  > sg_groups.json
	aws --profile $P --region $R ec2 describe-instances --output json > ec2_list.json
}

do_import() {

# 1. 手工确认IAM部分

# 2. 手工建立工作VPC(1个)，和igw

# 3. 自动导入指定vpc的Subnet定义及其路由表

# 4. 手工操作NAT Gateway

# 5. 自动导入指定vpc的sg

# 6. 基于当前运行EC2，全部制作镜像

	return

}


# Main
do_export default cn-north-1
#do_import chinakb 
