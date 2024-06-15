from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
import json
import os


def azure_storage_versioning_enabled():
  current_script_name = "azure_storage_versioning_enabled"
  print("Running ",current_script_name," . . . ")
  output_file_name = os.path.splitext(os.path.basename(current_script_name))[0]

  script_directory = os.path.dirname(os.path.abspath(__file__))

  output_directory = os.path.join(script_directory, "outputs")
  output_file = os.path.join(output_directory, output_file_name)


  if not os.path.exists(output_directory):
      os.makedirs(output_directory)

 # Authenticate using default Azure credentials
  credential = DefaultAzureCredential()
  subscription_client = SubscriptionClient(credential)

# iterate all subscriptions
  subscriptions = subscription_client.subscriptions.list()

  blob_details = []

  for subscription in subscriptions:
      storage_client = StorageManagementClient(credential, subscription.subscription_id)
      storage_accounts = storage_client.storage_accounts.list()
  
# Retrive Blob details  
      for storage in storage_accounts:
          blob_service_list = storage_client.blob_services.list(storage.id.split("/")[4], storage.name)
          for items in blob_service_list:
              blob_info = {
                  "Subscription ID": subscription.subscription_id,
                  "Resource Group": items.id.split("/")[4],
                  "Storage Account": items.id.split("/")[8],
                  "Name": items.name,
                  "Versioning Enabled": items.is_versioning_enabled
              }
              blob_details.append(blob_info)

  # Print details to console
  for i, blob_info in enumerate(blob_details, start=1):
      print(f"Blob {i} Details:")
      for key, value in blob_info.items():
          print(f"{key}: {value}")
      print("-------------------------------------------")

 
  # Write data to a JSON file
  with open(output_file, 'w') as jsonfile:
      json.dump(blob_details, jsonfile, indent=4)

  print(f"Storage Versioning details have been saved to {output_file}")
