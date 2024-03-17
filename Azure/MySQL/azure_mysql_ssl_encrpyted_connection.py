from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
import requests
import json
import sys
import os

def azure_mysql_ssl_encrpyted_connection():
    current_script_name = "azure_mysql_ssl_encrpyted_connection"
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
            
            # Define the request to fetch all single SQL servers from each resource group
            diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.DBforMySQL/servers?api-version=2021-05-01"
            headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
            response = requests.get(diagnostic_settings_endpoint, headers=headers)
            
            if response.status_code == 200:
                data = response.json()

                for item in data.get("value",[]):
                    server_id = item.get("id",{})
                    server_name = item.get("name",{})

                    diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.DBforMySQL/servers/{server_name}/configurations?api-version=2017-12-01"
                    headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
                    response = requests.get(diagnostic_settings_endpoint, headers=headers)
                    data = response.json()

                    for item in data.get("value",[]):
                        if item["name"] == "require_secure_transport":
                            result_list.append({f"SSL connection requirement results for {server_name}: ":item})

            
            # Define the request to fetch all flexible SQL servers from each resource group
            diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.DBforMySQL/flexibleServers?api-version=2021-05-01"
            headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
            response = requests.get(diagnostic_settings_endpoint, headers=headers)
            if response.status_code == 200:
                data = response.json()

                for item in data.get("value",[]):
                    server_id = item.get("id",{})
                    server_name = item.get("name",{})

                    diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.DBforMySQL/flexibleServers/{server_name}/configurations?api-version=2023-06-30"
                    headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
                    response = requests.get(diagnostic_settings_endpoint, headers=headers)

                    data = response.json()

                    for item in data.get("value",[]):
                        if item["name"] == "require_secure_transport":
                            result_list.append({f"SSL connection requirement results for {server_name}: ":item})

    with open(output_file, 'w') as outfile:
        json.dump(result_list, outfile, indent=4)