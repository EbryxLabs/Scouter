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

    # Define the request to fetch all SQL servers from each resource group
    diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Storage/storageAccounts?api-version=2023-01-01"
    headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
    response = requests.get(diagnostic_settings_endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()

    for item in data.get("value", []):
        storage_account_id=item.get("id", {})
        storage_account_name=item.get("name", {})
        
        diagnostic_settings_endpoint = f"https://management.azure.com/{storage_account_id}/providers/Microsoft.Security/defenderForStorageSettings/current?api-version=2022-12-01-preview"
        headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
        response = requests.get(diagnostic_settings_endpoint, headers=headers)
        data = response.json()

        setting_name = data.get("name",{})
        state=data.get("properties",{}).get("isEnabled",{})
        
        result_list.append({"storage_account_id":storage_account_id,"storage_account_name":storage_account_name,"setting_name":setting_name,"state":state})

print(result_list)         