import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os

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


def get_available_files_to_upload():
    try:
        files = os.listdir('samplefiles')
        return '\n'.join(files)
    except Exception as e:
        return f"An error occurred while retrieving available files: {str(e)}"


def upload_file_to_s3(file_name, bucket_name, object_name=None):
    """
    Uploads a file to an S3 bucket.

    Parameters
    ----------
    file_name : str
        The name of the file to upload.
    bucket_name : str
        The name of the S3 bucket to upload the file to.
    object_name : str, optional
        The name of the object in the S3 bucket to store the file as. If not provided, the file_name is used.

    Returns
    -------
    str
        A message indicating the success or failure of the upload operation.

    Raises
    ------
    FileNotFoundError
        If the file is not found.
    NoCredentialsError
        If AWS credentials are not available.
    PartialCredentialsError
        If incomplete AWS credentials are provided.
    Exception
        If any other error occurs during upload.
    """
    s3_client = boto3.client('s3')

    file_name = "./samplefiles/" + file_name

    # If the object name is not provided, use the file name
    if object_name is None:
        object_name = file_name

    try:
        # Upload the file
        s3_client.upload_file(file_name, bucket_name, object_name)
        return (f"File '{file_name}' uploaded successfully to '{bucket_name}/{object_name}'")
    except FileNotFoundError:
        return (f"File '{file_name}' not found.")
    except NoCredentialsError:
        return ("Credentials not available.")
    except PartialCredentialsError:
        return ("Incomplete credentials provided.")
    except Exception as e:
        return (f"Error occurred: {e}")

# # Example usage
# file_name = "jaguar.webp"
# bucket_name = "com.visheshpandey"
# response = upload_file_to_s3(file_name, bucket_name)
# print(response)


# files = get_available_files_to_upload()

# print(files)