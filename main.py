import boto3
import json
import re

session = boto3.session.Session()
region = session.region_name
ec2 = boto3.resource('ec2')
CW_client = boto3.client('cloudwatch')

metrics_source = """
{
    "metrics": [
        [ { "expression": "(m2+m3)/(FLOOR((PERIOD(m1)-m1))+1)",
                            "label": "%s", "id": "e1", "period": 60 } ],
        [ "AWS/EBS", "VolumeIdleTime", "VolumeId",
            "%s", { "id": "m1", "visible": false } ],
        [ ".", "%s", ".", ".", { "id": "m2", "visible": false } ],
        [ ".", "%s", ".", ".", { "id": "m3", "visible": false } ]
    ],
    "view": "timeSeries",
    "stacked": false,
    "region": "%s",
    "stat": "Sum",
    "period": 300,
    "title": "%s"
}
"""

# dashboard_body = """
# {
#     "widgets": [
#         {
#             "type": "metric",
#             "x": %d,
#             "y": %d,
#             "width": 12,
#             "height": 6,
#             "properties": %s
#         }
#     ]
# }
# """

# response = CW_client.put_dashboard(DashboardName='test', DashboardBody=dashboard_body)


def sanitize(s):
    return re.sub(r'\W+', '_', s)


def tag_volumes(device_mappings, instance_name, instance_id):
    volumes_list = []
    for block in device_mappings:
        volume_id = block['Ebs']['VolumeId']
        volumes_list.append(volume_id)
        volume = ec2.Volume(volume_id)
        volume.create_tags(
            Tags=[
                {
                    'Key': 'instance_name',
                    'Value': sanitize(instance_name)
                },
                {
                    'Key': 'instance_id',
                    'Value': sanitize(instance_id)
                },
            ]
        )
    return volumes_list


# sourcery skip: hoist-statement-from-loop
# Get full list
print("Collecting instance list...")
instances = ec2.instances.all()

# Iterate over the list.Note the use of instance as a resource with attribute here.
for instance in instances:

    print(f"Start processing {instance.instance_id}...")

    widget_list=[]
    y_count=0
    instance_name=''
    for tag in instance.tags:
        if tag['Key'] == 'Name':
            instance_name=tag['Value']
    instance_id=instance.instance_id
    block_devices=instance.block_device_mappings
    volumes_list=tag_volumes(block_devices, instance_name, instance_id)
    for volume in volumes_list:
        iops_metric=metrics_source % (
            volume, volume, 'VolumeReadOps', 'VolumeWriteOps', region, f'{volume}_iops')
        iops_widget={
            "type": "metric",
            "x": 0,
            "y": y_count,
            "width": 12,
            "height": 6,
            "properties": json.loads(iops_metric)
        }
        widget_list.append(iops_widget)
        throughput_metric = metrics_source % (
            volume, volume, 'VolumeReadBytes', 'VolumeWriteBytes', region, f'{volume}_throughput')
        throughput_widget = {
            "type": "metric",
            "x": 13,
            "y": y_count,
            "width": 12,
            "height": 6,
            "properties": json.loads(throughput_metric)
        }
        widget_list.append(throughput_widget)
        y_count += 7

    dashboard_body = {
        'widgets': widget_list
    }

    response = CW_client.put_dashboard(DashboardName=sanitize(
        f"{instance_name}_ebs_performance"), DashboardBody=json.dumps(dashboard_body))
    print(f"Finish generating dashboard for {instance_name}")
    print("*"*20)
