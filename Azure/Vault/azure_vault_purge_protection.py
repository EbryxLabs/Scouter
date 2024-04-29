from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
import requests
import os
import json

def azure_vault_purge_protection():
    
  current_script_name = "azure_vault_purge_protection"
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
      diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/resources?$filter=resourceType eq 'Microsoft.KeyVault/vaults'&api-version=2015-11-01"
      headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
      response = requests.get(diagnostic_settings_endpoint, headers=headers)
      if response.status_code == 200:
        data = response.json()
      for item in data.get("value", []):
          vault_name=item.get("name", {})
          vault_id=item.get("id", {})

          diagnostic_settings_endpoint = f"https://management.azure.com/{vault_id}/privateEndpointConnections?api-version=2022-07-01"
          headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
          response = requests.get(diagnostic_settings_endpoint, headers=headers)
          print(response)
          data = response.json()
          print(data)


  with open(output_file, 'w') as outfile:
      json.dump(result_list, outfile, indent=4)
azure_vault_purge_protection()
