from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
import json 
import os

def azure_storage_encryption_enabled():
  current_script_name = "azure_storage_encryption_enabled"
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
  storage_details = []


# Retrieve Storage encryption details
  for subscription in subscriptions:
      storage_client = StorageManagementClient(credential, subscription.subscription_id)
      storage_accounts = storage_client.storage_accounts.list()
      for storage in storage_accounts:
          storage_info = {
              "Subscription ID": subscription.subscription_id,
              "Resource Group": storage.id.split("/")[4],
              "Storage Name": storage.name,
              "Location": storage.location,
              "Encryption": storage.encryption.services.blob.enabled if storage.encryption and storage.encryption.services and storage.encryption.services.blob else None
          }
          storage_details.append(storage_info)

  # Print details to console
  for i, storage_info in enumerate(storage_details, start=1):
      print(f"Storage {i} Details:")
      for key, value in storage_info.items():
          print(f"{key}: {value}")
      print("-------------------------------------------")


  # Write data to a JSON file
  with open(output_file, 'w') as jsonfile:
      json.dump(storage_details, jsonfile, indent=4)

  print(f"Storage Encryption details have been saved to {output_file}")

