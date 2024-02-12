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
        diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Sql/servers?api-version=2021-11-01"
        headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
        response = requests.get(diagnostic_settings_endpoint, headers=headers)
        if response.status_code == 200:
          data = response.json()
        for item in data.get("value", []):
            server_name=item.get("name", {})
            server_id=item.get("id", {})
            diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Sql/servers/{server_name}/securityAlertPolicies?api-version=2021-11-01"
            headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
            response = requests.get(diagnostic_settings_endpoint, headers=headers)
            audit_data = response.json()
            for audit_info in audit_data.get("value",[]):
              policy_name=audit_info.get("name",{})
              retention_days = audit_info.get('properties', {}).get('retentionDays')
              state = audit_info.get('properties', {}).get('state')
              emailAccountAdmins = audit_info.get('properties', {}).get('emailAccountAdmins')


              result_list.append({"server_id": server_id, "policy_name":policy_name, "auditing_state":state, "retention_period": retention_days, "emailAccountAdmins": emailAccountAdmins})

print(result_list)