from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from dotenv import load_dotenv
import os

def deploy_azure_vm(resource_group_name, location, vm_name, username, password):
    """
    Function to deploy an Azure VM.

    Parameters:
        resource_group_name (str): Name of the resource group.
        location (str): Azure region for the resources.
        vm_name (str): Name of the virtual machine.
        username (str): Admin username for the VM.
        password (str): Admin password for the VM.
    """
    load_dotenv()  # Load environment variables
    credential = DefaultAzureCredential()
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    
    if not subscription_id:
        raise ValueError("AZURE_SUBSCRIPTION_ID environment variable is not set.")
    
    # Step 1: Provision a resource group
    resource_client = ResourceManagementClient(credential, subscription_id)
    rg_result = resource_client.resource_groups.create_or_update(
        resource_group_name, {"location": location}
    )
    
    print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")
    
    # Step 2: Provision a virtual network
    network_client = NetworkManagementClient(credential, subscription_id)
    vnet_name = f"{vm_name}-vnet"
    subnet_name = f"{vm_name}-subnet"
    ip_name = f"{vm_name}-ip"
    nic_name = f"{vm_name}-nic"
    ip_config_name = f"{vm_name}-ip-config"
    
    poller = network_client.virtual_networks.begin_create_or_update(
        resource_group_name,
        vnet_name,
        {
            "location": location,
            "address_space": {"address_prefixes": ["10.0.0.0/16"]},
        },
    )
    vnet_result = poller.result()
    
    print(f"Provisioned virtual network {vnet_result.name}")
    
    # Step 3: Provision a subnet
    poller = network_client.subnets.begin_create_or_update(
        resource_group_name,
        vnet_name,
        subnet_name,
        {"address_prefix": "10.0.0.0/24"},
    )
    subnet_result = poller.result()
    
    print(f"Provisioned subnet {subnet_result.name}")
    
    # Step 4: Provision a public IP address
    poller = network_client.public_ip_addresses.begin_create_or_update(
        resource_group_name,
        ip_name,
        {
            "location": location,
            "sku": {"name": "Standard"},
            "public_ip_allocation_method": "Static",
            "public_ip_address_version": "IPV4",
        },
    )
    ip_address_result = poller.result()
    
    print(f"Provisioned public IP address {ip_address_result.name}")
    
    # Step 5: Provision a network interface
    poller = network_client.network_interfaces.begin_create_or_update(
        resource_group_name,
        nic_name,
        {
            "location": location,
            "ip_configurations": [
                {
                    "name": ip_config_name,
                    "subnet": {"id": subnet_result.id},
                    "public_ip_address": {"id": ip_address_result.id},
                }
            ],
        },
    )
    nic_result = poller.result()
    
    print(f"Provisioned network interface {nic_result.name}")
    
    # Step 6: Provision the virtual machine
    compute_client = ComputeManagementClient(credential, subscription_id)
    
    poller = compute_client.virtual_machines.begin_create_or_update(
        resource_group_name,
        vm_name,
        {
            "location": location,
            "storage_profile": {
                "image_reference": {
                    "publisher": "Canonical",
                    "offer": "UbuntuServer",
                    "sku": "16.04.0-LTS",
                    "version": "latest",
                }
            },
            "hardware_profile": {"vm_size": "Standard_DS1_v2"},
            "os_profile": {
                "computer_name": vm_name,
                "admin_username": username,
                "admin_password": password,
            },
            "network_profile": {
                "network_interfaces": [
                    {
                        "id": nic_result.id,
                    }
                ]
            },
        },
    )
    
    vm_result = poller.result()
    print(f"Provisioned virtual machine {vm_result.name}")



