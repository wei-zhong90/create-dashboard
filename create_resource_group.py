import boto3
import json
import re

client = boto3.client('resource-groups')
ec2 = boto3.resource('ec2')

instances = ec2.instances.all()

def sanitize(s):
    return re.sub(r'\W+', '_', s)

for instance in instances:
    instance_name = ''
    for tag in instance.tags:
        if tag['Key'] == 'Name':
            instance_name = tag['Value']
    response = client.create_group(
        Name = f'{sanitize(instance_name)}-group',
        Description = 'instanceVolumeGroup',
        ResourceQuery = {
            'Type': 'TAG_FILTERS_1_0',
            'Query': json.dumps({
                'ResourceTypeFilters': ['AWS::AllSupported'],
                'TagFilters': [{
                    'Values': [sanitize(instance_name)],
                    'Key': 'instance_name'
                }]
            })
        }
    )
