"""AutoGen SWE Agent"""
import os
import sys
from autogen import UserProxyAgent
from autogen.agentchat.contrib.captainagent import CaptainAgent
from composio_autogen import ComposioToolSet, App, Action, WorkspaceType
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import logging
import warnings
import shutil
from dotenv import load_dotenv

# Suppress warnings
logging.getLogger().setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Define workspace path
WORKSPACE_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")

# Create workspace directory first
if os.path.exists(WORKSPACE_ROOT):
    shutil.rmtree(WORKSPACE_ROOT)  # Clean existing workspace
os.makedirs(WORKSPACE_ROOT)

# Base response models
class GitHubResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

# Initialize Composio toolset with Host workspace
composio_toolset = ComposioToolSet(
    workspace_config=WorkspaceType.Host(
        environment={
            "COMPOSIO_LOGGING_LEVEL": "INFO",
            "PYTHONWARNINGS": "ignore",
            "ALLOW_CLONE_WITHOUT_REPO": "true",
            "GITHUB_ACCESS_TOKEN": os.getenv("GITHUB_ACCESS_TOKEN"),
            "COMPOSIO_WORKSPACE_PATH": WORKSPACE_ROOT,
            "GIT_PYTHON_GIT_EXECUTABLE": "git",
            "GIT_PYTHON_REFRESH": "quiet",
            "GIT_COMMITTER_NAME": "SWE Assistant",
            "GIT_COMMITTER_EMAIL": "swe.assistant@example.com"
        }
    ),
    api_key=os.getenv("COMPOSIO_API_KEY")
)

# Get SWE tools
swe_tools = composio_toolset.get_tools(actions=[
    Action.FILETOOL_OPEN_FILE,
    Action.FILETOOL_EDIT_FILE,
    Action.FILETOOL_CREATE_FILE,
    Action.FILETOOL_LIST_FILES,
    Action.FILETOOL_GIT_CLONE,
    Action.FILETOOL_GIT_REPO_TREE,
    Action.FILETOOL_GIT_PATCH,
    Action.CODE_ANALYSIS_TOOL_CREATE_CODE_MAP,
    Action.SHELLTOOL_EXEC_COMMAND,
    Action.SHELLTOOL_TEST_COMMAND
])

# Initialize LLM configs
llm_config = {
    "config_list": [
        {
            "model": "gpt-4-turbo",
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    ],
    "temperature": 0
}

# Initialize CaptainAgent
captain = CaptainAgent(
    name="captain",
    llm_config=llm_config,
    code_execution_config={
        "use_docker": False,
        "work_dir": WORKSPACE_ROOT,
        "timeout": 300
    },
    tool_lib="[ag2_tool,swe_tools]",
    agent_config_save_path=None
)

# Initialize UserProxy
user_proxy = UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
    human_input_mode="NEVER",
    code_execution_config={
        "use_docker": False,
        "work_dir": WORKSPACE_ROOT,
        "timeout": 300
    }
)

# Register tools
composio_toolset.register_tools(
    apps=[App.GITHUB, App.FILETOOL, App.SHELLTOOL],
    caller=captain,
    executor=user_proxy
)