"""AutoGen SWE Agent"""

import os
import dotenv
from autogen import UserProxyAgent
from autogen.agentchat.contrib.captainagent import CaptainAgent
from composio_autogen import App, ComposioToolSet, WorkspaceType
from prompts import ROLE, GOAL, BACKSTORY, DESCRIPTION, EXPECTED_OUTPUT

# Load environment variables from .env
dotenv.load_dotenv()

# Initialize Composio toolset
composio_toolset = ComposioToolSet(workspace_config=WorkspaceType.Docker())

# Define CaptainAgent configuration
llm_config = {
    "config_list": [
        {"model": "gpt-4-turbo", "api_key": os.environ["OPENAI_API_KEY"]},
    ]
}

# Create CaptainAgent
captain = CaptainAgent(
    name="SWE_Captain",
    llm_config=llm_config,
    code_execution_config={"use_docker": False, "work_dir": "groupchat"},
    agent_lib="captainagent_expert_library.json",  # Path to your expert library
    tool_lib=composio_toolset.get_tools(),  # Integrate Composio tools
    system_message=f"""
    Role: {ROLE}
    Goal: {GOAL}
    Backstory: {BACKSTORY}
    Description: {DESCRIPTION}
    Expected Output: {EXPECTED_OUTPUT}
    
    When the task is complete, reply with TERMINATE.
    """
)

# Define user proxy agent
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x is not None and isinstance(x.get("content"), str) and "TERMINATE" in x.get("content", ""),
    code_execution_config={"use_docker": False},
)

# Register tools
composio_toolset.register_tools(
    apps=[App.FILETOOL, App.SHELLTOOL, App.GITHUB],
    caller=captain,
    executor=user_proxy
)
