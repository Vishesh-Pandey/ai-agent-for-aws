from swarm import Agent
from aws_tools import  get_ec2_info , launch_ec2_instance , upload_file_to_s3,get_available_files_to_upload
from azure_tools import deploy_azure_vm
from azure_tools import create_azure_vnet

launchInstanceAgent = Agent(
    name="Launch AWS Instance Agent",
    model = "llama3.2:3b",
    instructions=(
    "You are responsible only for launching EC2 instances using launch_ec2_instance function tool based on user-provided inputs. If the user asks about existing EC2 instances or general AWS topics, return control to the `router agent`."
),
    functions=[launch_ec2_instance],
)

awsS3Agent = Agent(
    name="AWS S3 Agent",
    model = "llama3.2:3b",
    instructions=(
    "You are responsible only for uploading files to AWS S3. Tell user about available files to upload using get_available_files_to_upload function. Once user provides the file name, bucket name and object name then call upload_file_to_s3 function tool. If the user asks about existing EC2 instances or general AWS topics, return control to the `router agent`."
),
    functions=[upload_file_to_s3, get_available_files_to_upload],
)

ec2InfoAgent = Agent(
    name="AWS EC2 Info Agent",
    model = "llama3.2:3b",
    instructions=(
    "You retrieve information about existing EC2 instances. If the user asks to launch a new instance or perform any other task, return control to the `router agent`."
),
    functions=[get_ec2_info],
)

azureVMAgent = Agent(
    name="Azure VM Agent",
    model = "llama3.2:3b",
    instructions=
    "Your task is to deploy azure vm asking required question to the user. You need to ask resource_group_name, location , vm_name, username and password. Once you get the resource group name, location, vm_name, username and password then call the function deploy_azure_vm. If the user asks about existing EC2 instances or general AWS topics, return control to the `router agent`.",
    functions=[deploy_azure_vm],
)

azureVNETAgent = Agent(
    name="Azure VNET Agent",
    model = "llama3.2:3b",
    instructions="Your task is to create azure vnet. You need to ask resource_group_name, location , vnet_name, subnet_name. Once you get the resource group name, location, vnet_name and subnet_name then call the function create_azure_vnet. If the user asks about existing EC2 instances or general AWS topics, return control to the `router agent`.",
    functions=[create_azure_vnet],
)

routerAgent = Agent(
    name="Router Agent",
    model = "llama3.2:3b",
    instructions=
    "Your job is to understand user requests and delegate tasks to either the `Launch AWS Instance Agent` or the `AWS S3 Agent` or the `AWS EC2 Info Agent` or the `Azure VM Agent` or the `Azure VNET Agent` based on the request. If the user query is unclear, ask follow-up questions to clarify their intent before delegating."
,
)

def transfer_back_to_router_agent():
    '''
    Call this function if a user is aksing about ec2 that can not be handled by current agent
    '''
    return routerAgent


def transfer_to_launch_instance_agent():
    '''
    Call this function if a user is asking to launch a new instance, to transfer control to the `Launch Instance Agent`
    '''
    return launchInstanceAgent

def transfer_to_ec2_info_agent():
    """
    Transfers control to the EC2 Info Agent.

    Call this function when a user requests information about existing EC2 instances.
    The EC2 Info Agent is responsible for retrieving details about existing 
    EC2 instances such as instance IDs, types, states, and IP addresses.
    
    Returns
    -------
    Agent
        The EC2 Info Agent to handle the user's request.
    """

    return ec2InfoAgent

def transfer_to_azure_vm_agent():
    """
    Transfers control to the Azure Agent.

    Call this function when a user requests information about Azure 
    such as deploying a new VM.
    
    Returns
    -------
    Agent
        The Azure Agent to handle the user's request.
    """
    return azureVMAgent

def transfer_to_azure_vnet_agent():
    """
    Transfers control to the Azure Agent.

    Call this function when a user requests information about Azure 
    such as creating a new VNET.
    
    Returns
    -------
    Agent
        The Azure Agent to handle the user's request.
    """
    return azureVNETAgent

def transfer_to_aws_s3_agent():
    """
    Transfers control to the AWS S3 Agent.

    Call this function when a user requests actions related to AWS S3,
    such as uploading files to an S3 bucket or inquiring about available files
    for upload.

    Returns
    -------
    Agent
        The AWS S3 Agent to handle the user's request.
    """
    return awsS3Agent

routerAgent.functions = [transfer_to_azure_vm_agent, transfer_to_launch_instance_agent, transfer_to_ec2_info_agent, transfer_to_azure_vnet_agent, transfer_to_aws_s3_agent]

launchInstanceAgent.functions.append(transfer_back_to_router_agent)
ec2InfoAgent.functions.append(transfer_back_to_router_agent)
