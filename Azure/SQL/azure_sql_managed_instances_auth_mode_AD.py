from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
import requests

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

print(result_list)