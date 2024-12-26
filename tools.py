import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def launch_ec2_instance(name, image_id, architecture, instance_type, key_pair):
    """
    Launch a new EC2 instance with specified parameters.

    Parameters
    ----------
    name : str
        The name of the EC2 instance.
    image_id : str
        The Amazon Machine Image (AMI) ID.
    architecture : str
        The architecture of the instance (e.g., 'x86_64', 'arm64').
    instance_type : str
        The type of the EC2 instance (e.g., 't2.micro').
    key_pair : str
        The name of the key pair to associate with the instance.

    Returns
    -------
    dict
        A dictionary containing details about the launched instance, or an error message if the operation fails.
    """
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    try:
        print(f"Launching EC2 instance with the following details:\n"
              f"Name: {name}, Image ID: {image_id}, Architecture: {architecture}, "
              f"Instance Type: {instance_type}, Key Pair: {key_pair}")
        
        # Launch EC2 instance
        response = ec2_client.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            KeyName=key_pair,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': name},
                        {'Key': 'Architecture', 'Value': architecture}
                    ]
                }
            ]
        )
        
        # Extract instance details
        instance = response['Instances'][0]
        instance_id = instance['InstanceId']
        print(f"EC2 instance launched successfully! Instance ID: {instance_id}")
        
        return {
            "InstanceId": instance_id,
            "State": instance['State']['Name'],
            "PublicIpAddress": instance.get('PublicIpAddress', 'N/A'),
            "InstanceType": instance['InstanceType']
        }
    
    except (NoCredentialsError, PartialCredentialsError):
        return {"Error": "AWS credentials not found or incomplete!"}
    except Exception as e:
        return {"Error": str(e)}



def get_ec2_info():
    """
    This function retrieves information about existing EC2 instances.

    Parameters
    ----------
    None

    Returns
    -------
    string
        Information about existing EC2 instances, including instance IDs, types, states, and more.
    """
    try:
        # Initialize the EC2 client
        ec2_client = boto3.client('ec2' , region_name='us-east-1')

        print("EC2 CLIENT IS : " , ec2_client)
        
        # Retrieve information about all instances
        response = ec2_client.describe_instances()

        # Parse and extract useful information
        instances_info = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance.get('InstanceId', 'N/A')
                instance_type = instance.get('InstanceType', 'N/A')
                state = instance['State'].get('Name', 'N/A')
                public_ip = instance.get('PublicIpAddress', 'N/A')
                private_ip = instance.get('PrivateIpAddress', 'N/A')

                instances_info.append(
                    f"Instance ID: {instance_id}, Type: {instance_type}, "
                    f"State: {state}, Public IP: {public_ip}, Private IP: {private_ip}"
                )

        if not instances_info:
            return "No EC2 instances found in the current AWS account."
        
        return "\n".join(instances_info)

    except Exception as e:
        return f"An error occurred while retrieving EC2 information: {str(e)}"

# # Example usage
# response = launch_ec2_instance(
#     name="MyTestInstance",
#     image_id="ami-01816d07b1128cd2d",  
#     architecture="x86_64",
#     instance_type="t2.micro",
#     key_pair="mykey"  
# )

# print(response)
