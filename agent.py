"""AutoGen SWE Agent"""

import os
import sys
import platform
import dotenv
import subprocess
from autogen import UserProxyAgent
from autogen.agentchat.contrib.captainagent import CaptainAgent
from composio_autogen import App, ComposioToolSet, WorkspaceType
from prompts import ROLE, GOAL, BACKSTORY, DESCRIPTION, EXPECTED_OUTPUT

def set_windows_env_vars():
    """Set Windows environment variables from .env file using setx"""
    try:
        # Load environment variables from .env
        env_vars = dotenv.dotenv_values()
        
        if not env_vars:
            print("Warning: No variables found in .env file")
            return
        
        # Set each variable using setx
        for key, value in env_vars.items():
            try:
                subprocess.run(['setx', key, value], check=True, capture_output=True)
                print(f"Successfully set {key}")
            except subprocess.CalledProcessError as e:
                print(f"Error setting {key}: {e}")
            except Exception as e:
                print(f"Unexpected error setting {key}: {e}")
                
    except FileNotFoundError:
        print("Error: .env file not found")
    except Exception as e:
        print(f"Error loading environment variables: {e}")

def set_unix_env_vars():
    """Set Unix environment variables from .env file"""
    try:
        # Load and set environment variables
        dotenv.load_dotenv()
        print("Successfully loaded environment variables")
    except Exception as e:
        print(f"Error loading environment variables: {e}")

# Determine OS and set environment variables accordingly
try:
    system = platform.system().lower()
    
    if system == 'windows':
        print("Detected Windows system")
        set_windows_env_vars()
    elif system in ['linux', 'darwin']:
        print(f"Detected Unix-like system ({system})")
        set_unix_env_vars()
    else:
        print(f"Warning: Unknown operating system: {system}")
        # Try to load env vars anyway
        dotenv.load_dotenv()
        
except Exception as e:
    print(f"Error detecting system type: {e}")
    sys.exit(1)

try:
    # Initialize Composio toolset
    composio_toolset = ComposioToolSet(workspace_config=WorkspaceType.Docker())

    # Define CaptainAgent configuration
    llm_config = {
        "config_list": [
            {"model": "gpt-4-turbo", "api_key": os.environ.get("OPENAI_API_KEY")},
        ]
    }

    # Create CaptainAgent
    captain = CaptainAgent(
        name="SWE_Captain",
        llm_config=llm_config,
        code_execution_config={"use_docker": False, "work_dir": "groupchat"},
        agent_lib="captainagent_expert_library.json",
        tool_lib=composio_toolset.get_tools(),
        system_message=f"""
        Role: {ROLE}
        Goal: {GOAL}
        Backstory: {BACKSTORY}
        Description: {DESCRIPTION}
        Expected Output: {EXPECTED_OUTPUT}
        
        When the task is complete, reply with TERMINATE.
        """
    )

    # Define interactive user proxy agent
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x is not None and isinstance(x.get("content"), str) and "TERMINATE" in x.get("content", ""),
        code_execution_config={"use_docker": False},
        system_message="""You are a user proxy that helps interact with the CaptainAgent.
        You can:
        1. Execute code provided by the CaptainAgent
        2. Provide feedback and additional instructions
        3. Help guide the conversation towards solving the task
        
        When you receive input from the human user, pass it along to the CaptainAgent.
        """
    )

    # Register tools
    composio_toolset.register_tools(
        apps=[App.FILETOOL, App.SHELLTOOL, App.GITHUB],
        caller=captain,
        executor=user_proxy
    )

except Exception as e:
    print(f"Error initializing agents and tools: {e}")
    sys.exit(1)
