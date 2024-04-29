from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
import requests
import os
import json

def azure_alert_on_network_security_group():
    
  current_script_name = "azure_alert_on_network_security_group"
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

  comparison_list = [
    'Microsoft.ClassicNetwork/networkSecurityGroups/write',
    'Microsoft.ClassicNetwork/networkSecurityGroups/delete',
    'Microsoft.Network/networkSecurityGroups/delete',
    'Microsoft.Network/networkSecurityGroups/write',
    'Microsoft.Network/networkSecurityGroups/securityRules/write',
    'Microsoft.ClassicNetwork/networkSecurityGroups/securityRules/write',
    'Microsoft.Network/networkSecurityGroups/securityRules/delete',
    'Microsoft.ClassicNetwork/networkSecurityGroups/securityRules/delete'
  ]

  items_list = []
  existent_list = []
  non_existent_list = []

  #iterate all subscriptions
  for subscription in subscriptions:
      subscription_id = subscription.subscription_id
      diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Insights/activitylogalerts?api-version=2017-04-01"
      headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
      response = requests.get(diagnostic_settings_endpoint, headers=headers)
      data = response.json()

      for comp in comparison_list:
        check_rule = comp
        exists = False
        for item in data.get('value', []):
            rule_name=item.get("name",{})
            rule_state=item.get("properties",{}).get("enabled",{})
            operation_name = item.get("properties", {}).get("condition", {}).get("allOf", [{}])[1].get("equals", "")

            if operation_name == check_rule:
                existent_list.append(check_rule)
                exists = True
                items_list.append({"name":rule_name,"operation_name":operation_name,"enabled":rule_state})
                break

        if not exists:
            non_existent_list.append(check_rule)
      if len(existent_list) > 0:
        existent_list.append({"Find below the details of the existing alerts": items_list})
  result_list.append({"Alerts for these activities exist : ": existent_list, "Alerts for these activities do not exist : ": non_existent_list})


  with open(output_file, 'w') as outfile:
      json.dump(result_list, outfile, indent=4)