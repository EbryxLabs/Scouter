from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
import requests
import json
import sys
import os

def flow_log_retention_period():
    current_script_name = "flow_log_retention_period"
    print("Running ",current_script_name," . . . ")
    output_file_name = os.path.splitext(os.path.basename(current_script_name))[0]

    script_directory = os.path.dirname(os.path.abspath(__file__))

    output_directory = os.path.join(script_directory, "outputs")
    output_file = os.path.join(output_directory, output_file_name)


    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    result_list = []

    # Authenticate using default Azure credentials
    credentials = DefaultAzureCredential()

    # Create Resource Management Client & List subscriptions
    subscription_client = SubscriptionClient(credentials)
    subscriptions = list(subscription_client.subscriptions.list())

    #iterate all subscriptions
    for subscription in subscriptions:
        subscription_id = subscription.subscription_id

        resource_client = ResourceManagementClient(credentials, subscription_id)

        # Retrieve the list of resource groups
        group_list = resource_client.resource_groups.list()
        for group in list(group_list):
            resource_group_name = group.name
            
            # get all the network watchers
            diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/networkWatchers?api-version=2023-09-01"
            headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
            response = requests.get(diagnostic_settings_endpoint, headers=headers)
            data=response.json()
            for item in data.get("value",[]):
                network_watcher_id = item.get("id",{})

                # Define the request to fetch all flow logs from each network watcher
                diagnostic_settings_endpoint = f"https://management.azure.com{network_watcher_id}/flowLogs?api-version=2023-09-01"
                headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
                response = requests.get(diagnostic_settings_endpoint, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(data)

                    for item in data.get("value",[]):
                        flow_log_id = item.get("id",{})
                        flow_log_name = item.get("name",{})
                        flow_logs_state = item.get("properties",{}).get("enabled",{})
                        flow_log_retention_policy=item.get("properties",{}).get("retentionPolicy",{})

                        result_list.append({"flow_log_id":flow_log_id,"flow_log_name":flow_log_name,"flow_logs_enabled":flow_logs_state,"flow_log_retention_policy":flow_log_retention_policy})

    with open(output_file, 'w') as outfile:
        json.dump(result_list, outfile, indent=4)
