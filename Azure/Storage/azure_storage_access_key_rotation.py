from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from datetime import datetime, timedelta
import json
import os




def azure_storage_access_key_rotation():
    current_script_name = "azure_storage_access_key_rotation"
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

# Create Resource Management Client & List subscriptions
    subscriptions = subscription_client.subscriptions.list()
    storage_details = []
    key_details = []
    key_number = 1

    for subscription in subscriptions:
        storage_client = StorageManagementClient(credential, subscription.subscription_id)

# Retrieve the list of stoage accounts
        storage_accounts = storage_client.storage_accounts.list()
        for storage in storage_accounts:

            SAS_key = storage_client.storage_accounts.list_keys(storage.id.split("/")[4], storage.name)
# Retrieve the details of SAS keys
            for key in SAS_key.keys:
                CreationTime = key.creation_time
                datetime_obj = datetime.fromisoformat(str(CreationTime))
                date = datetime_obj.date()
                current_date = datetime.now().date()
                difference = current_date - date

                if difference > timedelta(days=90):
                    KeyRotation = "False"
                else:
                    KeyRotation = "True"

                key_info = {
                    "Subscription ID": subscription.subscription_id,
                    "Last Rotation Time": datetime_obj.isoformat(),  # Converting datetime to ISO 8601 string
                    "Key": key_number,
                    "Key Rotation (90 Days)": KeyRotation
                }

                key_details.append(key_info)
                key_number += 1

            storage_info = {
                "Subscription ID": subscription.subscription_id,
                "Resource": storage.id.split("/")[4],
                "Storage": storage.name,
                "Location": storage.location,
                "Last Rotation Time": datetime_obj.isoformat()  # Converting datetime to ISO 8601 string
          }

            storage_details.append(storage_info)

  # Organizing storage and key details in a single dictionary
    data = {
        "StorageDetails": storage_details,
        "KeyDetails": key_details
  }

  # Saving all details to a single JSON file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

    print("All details have been saved to 'azure_storage_accesskey_rotation.json'")
