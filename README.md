# This script is developed for LFL to build ebs dashboards in one batch

## Deployment instruction

Use the *main.py* script to tag all ebs volumes with their corresponding instance id and instance name and then generate dashboards for each of the instance to demonstrate calculated **iops** and **throughput**

```sh
python3 -m pip install -r requirements.txt
python3 main.py
```

The other script named *create_resource_group.py* is optional, which is for creating resource group to group ebs volumes that belong to the same instance together. Resource group will provide a more convenient way to check all metrics related to EBS volumes.

```bash
python3 create_resource_group.py
```

The last script is for cleaning up all the dashboards if they are not intended or do not meet the requirements.
But please be careful when using this script. It will indifferently remove all the dashboards even if they are not created by the previous *main.py* script.

```bash
python3 remove_dashboards.py
```
