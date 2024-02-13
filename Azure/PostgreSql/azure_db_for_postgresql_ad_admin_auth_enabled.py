from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
import requests

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
        
        # Define the request to fetch all SQL servers from each resource group
        diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.DBforPostgreSQL/flexibleServers?api-version=2022-12-01"
        headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
        response = requests.get(diagnostic_settings_endpoint, headers=headers)

        if response.status_code == 200:
            data = response.json()
            for item in data.get("value",[]):
                server_id = item.get("id",{})
                server_name=item.get("name",{})
                server_type=item.get("type",{})
                ad_auth = item.get("properties",{}).get("authConfig",{}).get("activeDirectoryAuth",{})

                result_list.append({"server_id":server_id,"server_name":server_name,"server_type":server_type,"ad_auth":ad_auth})


        diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.DBforPostgreSQL/servers?api-version=2017-12-01"
        headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
        response = requests.get(diagnostic_settings_endpoint, headers=headers)

        if response.status_code == 200:
            data = response.json()
            for item in data.get("value",[]):
                server_id = item.get("id",{})
                server_name=item.get("name",{})
                server_type=item.get("type",{})
                ad_auth = item.get("properties",{}).get("authConfig",{}).get("activeDirectoryAuth",{})

                result_list.append({"server_id":server_id,"server_name":server_name,"server_type":server_type,"ad_auth":ad_auth})

print(result_list)