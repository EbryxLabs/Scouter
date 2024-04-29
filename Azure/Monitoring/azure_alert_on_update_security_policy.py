from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
import requests
import os
import json

def azure_alert_on_update_security_policy():
    
  current_script_name = "azure_alert_on_update_security_policy"
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
      diagnostic_settings_endpoint = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Insights/activitylogalerts?api-version=2017-04-01"
      headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
      response = requests.get(diagnostic_settings_endpoint, headers=headers)
      data = response.json()

      found = False
      for item in data['value']:
        if 'properties' in item and 'condition' in item['properties'] and 'allOf' in item['properties']['condition']:
          for inner_item in item['properties']['condition']['allOf']:
            if inner_item['field'] == 'operationName' and inner_item['equals'] == 'Microsoft.Security/policies/write':
              found = True
              rule_name=item.get("name",{})
              operation_name = item.get("properties", {}).get("condition", {}).get("allOf", [{}])[1].get("equals", "")
              rule_state=item.get("properties",{}).get("enabled",{})

              result_list.append({"Result":"The required rule exists, details are as follows","name":rule_name,"operation_name":operation_name,"enabled":rule_state})
              break  # Exit the inner loop if found

      if not found:
        result_list.append({"Result":"The required rule does not exist, please create alert rule through Azure Monitor to notify on rule creation"})


  with open(output_file, 'w') as outfile:
      json.dump(result_list, outfile, indent=4)