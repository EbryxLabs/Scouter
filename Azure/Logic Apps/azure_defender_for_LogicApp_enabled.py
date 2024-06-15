from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.logic import LogicManagementClient
from azure.mgmt.resource import SubscriptionClient
from azure.core.exceptions import HttpResponseError
import requests
import json
import os 


def azure_defender_for_LogicApp_enabled():
    current_script_name = "azure_defender_for_LogicApp_enabled"
    print("Running ",current_script_name," . . . ")

    output_file_name = os.path.splitext(os.path.basename(current_script_name))[0]

    script_directory = os.path.dirname(os.path.abspath(__file__))

    output_directory = os.path.join(script_directory, "outputs")
    output_file = os.path.join(output_directory, output_file_name)


    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    result_list = []

    def authenticate_azure():
        # Authenticate using default Azure credentials
        credentials = DefaultAzureCredential()
        return credentials


    def list_subscriptions(credentials):
        # Create Resource Management Client & List subscriptions
        subscription_client = SubscriptionClient(credentials)
        subscriptions = list(subscription_client.subscriptions.list())
        return subscriptions


    def list_resource_groups(credentials, subscription_id):
        # Create Resource Management Client
        resource_client = ResourceManagementClient(credentials, subscription_id)

        # List resource groups
        resource_groups = list(resource_client.resource_groups.list())
        return resource_groups


    def check_diagnostic_settings(subscription_id, resource_group_name, logic_app_name):
        # Authenticate Azure account
        credentials = authenticate_azure()

        # Define the Azure Resource Manager API endpoint for diagnostic settings & Make a request to the Azure Resource Manager API

        diagnostic_settings_endpoint = f"https://management.azure.com{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Logic/workflows/{logic_app_name}/providers/Microsoft.Insights/diagnosticSettings?api-version=2021-05-01-preview"
        
        headers = {"Authorization": f"Bearer {credentials.get_token('https://management.azure.com').token}"}
        response = requests.get(diagnostic_settings_endpoint, headers=headers)


        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            diagnostic_settings = response.json().get("value", [])
            return len(diagnostic_settings) > 0  # Check if there are diagnostic settings configured
        else:
            return False  # Unable to retrieve diagnostic settings


    def list_logic_apps(logic_client, resource_group_name, subscription_id):
        try:
            # List Logic Apps in the current resource group
            logic_apps = list(logic_client.workflows.list_by_resource_group(resource_group_name))

            print(f"    Logic Apps in Resource Group '{resource_group_name}':")
            for logic_app in logic_apps:
                print(f"      - Logic App: {logic_app.name}")
                result_list.append({"resource_group": resource_group_name, "logic_app": logic_app.name})
                print(result_list)

                # Check if diagnostic settings are enabled
                if check_diagnostic_settings(subscription_id, resource_group_name, logic_app.name):
                    print("Diagnostic settings are enabled for the Logic App.")
                else:
                    print("Diagnostic settings are not configured as expected.")
        except HttpResponseError as ex:
            print(f"An error occurred while listing Logic Apps in resource group '{resource_group_name}': {ex}")


    if __name__ == "__main__":
        # Authenticate Azure account
        credentials = authenticate_azure()

        # List subscriptions
        subscriptions = list_subscriptions(credentials)

        for subscription in subscriptions:
            print(f"Subscription ID: {subscription.subscription_id}")
            print("Resource Groups:")

            # List resource groups for each subscription
            resource_groups = list_resource_groups(credentials, subscription.subscription_id)

            for resource_group in resource_groups:
                print(f"  - Resource Group: {resource_group.name}")

                # Create Logic Management Client for the current subscription
                logic_client = LogicManagementClient(credentials, subscription.subscription_id)

                # List Logic Apps in the current resource group
                list_logic_apps(logic_client, resource_group.name, subscription.subscription_id)
                
                print()  # Add a newline between resource groups
            print()  # Add a newline between subscriptions

    # Write data to a JSON file
    with open(output_file, 'w') as jsonfile:
        json.dump(result_list, jsonfile, indent=4)

    print(f"Logic Apps diagnostic details have been saved to {output_file}")
