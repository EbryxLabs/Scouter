from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
import requests

result_list = []
disabledAlerts_list=[]

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

        # Retrieve the list of databases in each server
        for item in data.get("value", []):
            server_name=item.get("name", {})
            diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Sql/servers/{server_name}/databases?api-version=2021-11-01"
            headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
            response = requests.get(diagnostic_settings_endpoint, headers=headers)
            if response.status_code == 200:
              dbs  = response.json()

            # Retrieve the security alerting policies of all 
            for item in dbs.get("value",[]):
              db_name=item.get("name",{})
              db_id=item.get("id",{})
              diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Sql/servers/{server_name}/databases/{db_name}/securityAlertPolicies?api-version=2021-11-01"
              headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
              response = requests.get(diagnostic_settings_endpoint, headers=headers)
              db_info=response.json()

              for info in db_info.get("value",[]):
                alerting_policy_state=info.get("properties",{}).get("state",{})
                retention_days=info.get("properties",{}).get("retentionDays",{})
                emailAccountAdmins = info.get('properties', {}).get('emailAccountAdmins')
                disabledAlerts=info.get('properties', {}).get('disabledAlerts')

                disabledAlerts_is_empty = all(element == '' for element in disabledAlerts)
                if disabledAlerts_is_empty:
                  result_list.append({"db_id": db_id, "alerting_policy_state":alerting_policy_state, "retention_period": retention_days, "emailAccountAdmins": emailAccountAdmins,"disabledAlerts":"None"})
                else:
                  result_list.append({"db_id": db_id, "alerting_policy_state":alerting_policy_state, "retention_period": retention_days, "emailAccountAdmins": emailAccountAdmins,"disabledAlerts":disabledAlerts})

                # if len(disabledAlerts)>0:
                #   for item in disabledAlerts:
                #     disabledAlerts_list.append({item})                      
                #   result_list.append({"disabledAlerts":disabledAlerts_list})

                #append the output of the checks to a list

print(result_list)