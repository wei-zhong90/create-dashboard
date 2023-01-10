import boto3

client = boto3.client('cloudwatch')

paginator = client.get_paginator('list_dashboards')

# response = client.list_dashboards()

response_iterator = paginator.paginate(
    PaginationConfig={
        'MaxItems': 200
    }
)

dashboard_list = []

for page in response_iterator:
    dashboard_list.extend(da['DashboardName'] for da in page['DashboardEntries'])
# dashboard_list = [dashboard['DashboardName'] for dashboard in response['DashboardEntries']]

client.delete_dashboards(
    DashboardNames = dashboard_list
)
