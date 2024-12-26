from swarm import Agent
from tools import  get_ec2_info , launch_ec2_instance

launchInstanceAgent = Agent(
    name="Launch Instance Agent",
    model = "llama3.2:1b",
    instructions=(
    "You are responsible only for launching EC2 instances using launch_ec2_instance function tool based on user-provided inputs. If the user asks about existing EC2 instances or general AWS topics, return control to the `User Agent`."
),
    functions=[launch_ec2_instance],
)

ec2InfoAgent = Agent(
    name="EC2 Info Agent",
    model = "llama3.2:1b",
    instructions=(
    "You retrieve information about existing EC2 instances. If the user asks to launch a new instance or perform any other task, return control to the `User Agent`."
),
    functions=[get_ec2_info],
)

userAgent = Agent(
    name="User Agent",
    model = "llama3.2:1b",
    instructions=
    "Your job is to understand user requests and delegate tasks to either the `Launch Instance Agent` or the `EC2 Info Agent` based on the request. If the user query is unclear, ask follow-up questions to clarify their intent before delegating."
,
)

def transfer_back_to_user_agent():
    '''
    Call this function if a user is aksing about ec2 that can not be handled by current agent
    '''
    return userAgent


def transfer_to_launch_instance_agent():
    return launchInstanceAgent

def transfer_to_ec2_info_agent():
    return ec2InfoAgent

userAgent.functions = [transfer_to_launch_instance_agent, transfer_to_ec2_info_agent]

launchInstanceAgent.functions.append(transfer_back_to_user_agent)
ec2InfoAgent.functions.append(transfer_back_to_user_agent)
