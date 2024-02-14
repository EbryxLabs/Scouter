from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
import requests
import json
import sys
import os

current_script_name = sys.argv[0]
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

    resource_client = ResourceManagementClient(credentials, subscription_id)
    
    group_list = resource_client.resource_groups.list()
    for group in list(group_list):
        resource_group_name = group.name

        # Define the request to fetch all SQL managed instances from each subscription
        diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Sql/managedInstances?api-version=2021-11-01"
        headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
        response = requests.get(diagnostic_settings_endpoint, headers=headers)

        data=response.json()

        for item in data.get("value", []):
            instance_name=item.get("name")
            instance_id=item.get("id")

            diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Sql/managedInstances/{instance_name}/vulnerabilityAssessments?api-version=2021-11-01"
            headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
            response = requests.get(diagnostic_settings_endpoint, headers=headers)

            vuln_data = response.json()
            print(vuln_data)
            for vuln_info in vuln_data.get("value",[]):
              policy_name=vuln_info.get("name",{})
              retention_days = vuln_info.get('properties', {}).get('retentionDays')
              state = vuln_info.get('properties', {}).get('state')
              recurringScans_enabled = vuln_info.get('properties', {}).get('recurringScans', {}).get('isEnabled')
              emailSubscriptionAdmins = vuln_info.get('properties', {}).get('recurringScans', {}).get('emailSubscriptionAdmins')
              result_list.append({"instance_id": instance_id, "policy_name":policy_name, "recurringScans_enabled":recurringScans_enabled})
              if recurringScans_enabled==True:
                  email_list=[]
                  for email in vuln_info.get('properties', {}).get('recurringScans', {}).get('emails',[]):
                      email_list.append({email})

                  result_list.append({"emails":email_list})

print(json.dumps(result_list,indent=4))

with open(output_file, 'w') as outfile:
    json.dump(result_list, outfile, indent=4)