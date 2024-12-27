from agents import userAgent
from openai import OpenAI
import json
from swarm import Swarm

ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",        
    api_key="ollama"            
)

def process_and_print_streaming_response(response):
    """Process and print the output from a streaming response.

    This function takes a generator of response chunks and prints the output in a
    human-readable format. It preserves the order of the chunks and handles the
    following chunk types:

    - sender: sets the last sender name
    - content: prints the content as part of the conversation
    - tool_calls: prints the tool calls with function name and arguments
    - delim: prints a newline when the delimiter is "end"
    - response: returns the response when found

    :param response: a generator of response chunks
    :return: the response when found, or None
    """
    
    content = ""
    last_sender = ""

    for chunk in response:
        if "sender" in chunk:
            last_sender = chunk["sender"]

        if "content" in chunk and chunk["content"] is not None:
            if not content and last_sender:
                print(f"\033[94m{last_sender}:\033[0m", end=" ", flush=True)
                last_sender = ""
            print(chunk["content"], end="", flush=True)
            content += chunk["content"]

        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                print(f"\033[94m{last_sender}: \033[95m{name}\033[0m()")

        if "delim" in chunk and chunk["delim"] == "end" and content:
            print() 
            content = ""

        if "response" in chunk:
            return chunk["response"]

def pretty_print_messages(messages) -> None:
    """
    Pretty print the messages from an assistant, displaying the sender's name,
    response content, and any tool calls in a formatted manner.

    Each message from the assistant is printed with the sender's name in blue.
    If the message contains content, it is printed immediately after the sender's name.
    Tool calls, if present, are printed in purple with function names and arguments.

    :param messages: A list of message dictionaries, where each dictionary contains
                     the keys 'role', 'sender', 'content', and optionally 'tool_calls'.
    """

    for message in messages:
        if message["role"] != "assistant":
            continue

        # print agent name in blue
        print(f"\033[94m{message['sender']}\033[0m:", end=" ")

        # print response, if any
        if message["content"]:
            print(message["content"])

        # print tool calls in purple, if any
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print()
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            print(f"\033[95m{name}\033[0m({arg_str[1:-1]})")


def run_demo_loop(
    starting_agent, context_variables=None, stream=False, debug=False
) -> None:
    
    """
    Runs an interactive demo loop for an Ollama Swarm CLI, using the provided
    starting agent and optionally a set of context variables.

    :param starting_agent: The starting agent to use in the demo loop.
    :param context_variables: Optional dictionary of context variables to
        pass to the client.
    :param stream: If True, the demo loop will stream responses from the
        client. If False, the demo loop will wait for the client to return
        a full response before printing it.
    :param debug: If True, the demo loop will print debug information about
        the client's responses.

    The demo loop will print the user's input in gray, the agent's responses in
    blue, and any tool calls in purple. If the client returns a response with
    multiple messages, the demo loop will print each message individually.
    """
    client = Swarm(client=ollama_client)
    print("Starting Ollama Swarm CLI:")

    messages = []
    agent = starting_agent

    while True:
        user_input = input("\033[90mUser\033[0m: ")
        messages.append({"role": "user", "content": user_input})

        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables or {},
            stream=stream,
            debug=debug,
        )

        print("THE RESPONSE IS : ", response)

        if stream:
            response = process_and_print_streaming_response(response)
        else:
            pretty_print_messages(response.messages)

        messages.extend(response.messages)
        agent = response.agent


if __name__ == "__main__":
    run_demo_loop(userAgent, stream=True)