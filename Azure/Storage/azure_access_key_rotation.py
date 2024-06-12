from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from datetime import datetime, timedelta
import json

credential = DefaultAzureCredential()
subscription_client = SubscriptionClient(credential)

subscriptions = subscription_client.subscriptions.list()
storage_details = []
key_details = []
key_number = 1

for subscription in subscriptions:
    storage_client = StorageManagementClient(credential, subscription.subscription_id)

    storage_accounts = storage_client.storage_accounts.list()
    for storage in storage_accounts:

        SAS_key = storage_client.storage_accounts.list_keys(storage.id.split("/")[4], storage.name)
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
with open('azure_storage_accesskey_rotation.json', 'w') as f:
    json.dump(data, f, indent=4)

print("All details have been saved to 'azure_storage_accesskey_rotation.json'")
