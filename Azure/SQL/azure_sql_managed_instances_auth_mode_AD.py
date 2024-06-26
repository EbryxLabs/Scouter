from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
import requests
import json
import sys
import os

def azure_sql_managed_instances_auth_mode_AD():
    current_script_name = "azure_sql_managed_instances_auth_mode_AD"
    print("Running ",current_script_name," . . . ")
    output_file_name = os.path.splitext(os.path.basename(current_script_name))[0]

    script_directory = os.path.dirname(os.path.abspath(__file__))

    output_directory = os.path.join(script_directory, "outputs")
    output_file = os.path.join(output_directory, output_file_name)


    if not os.path.exists(output_directory):
        os.makedirs(output_directory)


    # Authenticate using default Azure credentials
    credentials = DefaultAzureCredential()

    # Create Resource Management Client & List subscriptions
    subscription_client = SubscriptionClient(credentials)
    subscriptions = list(subscription_client.subscriptions.list())

    result_list = []

    for subscription in subscriptions:
        subscription_id = subscription.subscription_id

        # Define the request to fetch all SQL managed instances from each subscription
        diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Sql/managedInstances?api-version=2021-11-01"
        headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
        response = requests.get(diagnostic_settings_endpoint, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # traverse through the response to find the required information
            for item in data.get("value", []):
                server_id=item.get("id", {})
                administrators = item.get("properties", {}).get("administrators", {})
                azureADOnlyAuthentication = administrators.get("azureADOnlyAuthentication")
                if administrators and "azureADOnlyAuthentication" in administrators:
                    result_list.append({"id": server_id, "azureADOnlyAuthentication": azureADOnlyAuthentication})
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")



    with open(output_file, 'w') as outfile:
        json.dump(result_list, outfile, indent=4)