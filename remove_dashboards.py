import boto3

client = boto3.client('cloudwatch')

response = client.list_dashboards()

dashboard_list = [dashboard['DashboardName'] for dashboard in response['DashboardEntries']]

client.delete_dashboards(
    DashboardNames = dashboard_list
)