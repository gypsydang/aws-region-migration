import json
import boto3

client = boto3.client('iam')
settings=json.load(open("iam_export.json"))


for g in settings['GroupDetailList']:
    client.create_group(Path=g['Path'],GroupName=g['GroupName'])

for u in settings['UserDetailList']:
    client.create_user(Path=u['Path'],UserName=u['UserName'])
    for ug in u['GroupList']:
        client.add_user_to_group(GroupName=ug,UserName=u['UserName'])

for r in settings['RoleDetailList']:
    if r['Path'].startswith('/aws-service-role/'):
        client.create_service_linked_role(AWSServiceName=r['Path'][18:-1])
    else:
        client.create_role(Path=r['Path'],RoleName=r['RoleName'],AssumeRolePolicyDocument=json.dumps(r['AssumeRolePolicyDocument']),MaxSessionDuration=3600)

for q in settings['RoleDetailList']:
    for uq in q['InstanceProfileList']:
        client.add_role_to_instance_profile(RoleName=q['RoleName'],InstanceProfileName=client.create_instance_profile(InstanceProfileName=uq['InstanceProfileName'])['InstanceProfile']['InstanceProfileName'])

for q in settings['UserDetailList']:
    if 'UserPolicyList' in q:
        for uq in q['UserPolicyList']:
            client.attach_user_policy(PolicyArn=client.create_policy(PolicyName=uq['PolicyName'],Path=q['Path'],PolicyDocument=json.dumps(uq['PolicyDocument']))['Policy']['Arn'],UserName=q['UserName'])

for q in settings['UserDetailList']:
    for uq in q['AttachedManagedPolicies']:
         client.attach_user_policy(PolicyArn=uq['PolicyArn'],UserName=q['UserName'])

for q in settings['GroupDetailList']:
    for uq in q['GroupPolicyList']:
        client.attach_group_policy(PolicyArn=client.create_policy(PolicyName=uq['PolicyName'],Path=q['Path'],PolicyDocument=json.dumps(uq['PolicyDocument']))['Policy']['Arn'],GroupName=q['GroupName'])

for q in settings['GroupDetailList']:
    for uq in q['AttachedManagedPolicies']:
         client.attach_group_policy(PolicyArn=uq['PolicyArn'],GroupName=q['GroupName'])

for q in settings['RoleDetailList']:
    if not q['Path'].startswith('/aws-service-role/'):    
        if 'RolePolicyList' in q:
            for uq in q['RolePolicyList']:
                client.attach_role_policy(PolicyArn=client.create_policy(PolicyName=uq['PolicyName'],Path=q['Path'],PolicyDocument=json.dumps(uq['PolicyDocument']))['Policy']['Arn'],RoleName=q['RoleName'])

for q in settings['RoleDetailList']:
    if not q['Path'].startswith('/aws-service-role/'):
        for uq in q['AttachedManagedPolicies']:
            if not q['Path'].startswith('/service-role/'):
                client.attach_role_policy(PolicyArn=uq['PolicyArn'],RoleName=q['RoleName'])

