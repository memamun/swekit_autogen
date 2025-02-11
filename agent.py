"""AutoGen SWE Agent"""

import os
import sys
import platform
import dotenv
import subprocess
import logging
import warnings
from autogen import UserProxyAgent
from autogen.agentchat.contrib.captainagent import CaptainAgent
from composio_autogen import App, ComposioToolSet, WorkspaceType
from prompts import ROLE, GOAL, BACKSTORY, DESCRIPTION, EXPECTED_OUTPUT
from typing import Optional, Dict, Any, Union, List
from pydantic import BaseModel, Field

# Suppress all warnings
warnings.filterwarnings("ignore")

# Suppress specific Composio warnings
os.environ["COMPOSIO_SUPPRESS_WARNINGS"] = "1"
os.environ["COMPOSIO_IGNORE_RETURN_TYPE_WARNINGS"] = "1"
os.environ["COMPOSIO_LOGGING_LEVEL"] = "ERROR"

class FileToolResponse(BaseModel):
    """Response model for file operations"""
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    path: Optional[str] = Field(None, description="File path")
    content: Optional[str] = Field(None, description="File content")

class GitToolResponse(BaseModel):
    """Response model for git operations"""
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    patch: Optional[str] = Field(None, description="Git patch")
    branch: Optional[str] = Field(None, description="Git branch")

class ShellToolResponse(BaseModel):
    """Response model for shell operations"""
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    output: Optional[str] = Field(None, description="Command output")
    error: Optional[str] = Field(None, description="Error message")

class GithubToolResponse(BaseModel):
    """Response model for GitHub operations"""
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    url: Optional[str] = Field(None, description="GitHub URL")

def setup_logging():
    """Configure logging settings programmatically"""
    try:
        # Disable all loggers except critical
        logging.getLogger().setLevel(logging.CRITICAL)
        logging.getLogger('composio').setLevel(logging.CRITICAL)
        logging.getLogger('composio.client').setLevel(logging.CRITICAL)
        
        # Disable specific loggers
        for logger_name in ['urllib3', 'docker', 'git', 'requests']:
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)
        
        # Create our logger with minimal output
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.CRITICAL)
        
        # Set environment variables silently
        if platform.system().lower() == 'windows':
            subprocess.run(
                ['setx', 'COMPOSIO_LOGGING_LEVEL', 'ERROR'],
                check=True,
                capture_output=True,
                text=True
            )
        
        return logger
        
    except Exception as e:
        sys.exit(1)

# Initialize logging silently
logger = setup_logging()

def set_windows_env_vars():
    """Set Windows environment variables from .env file using setx"""
    try:
        # Load environment variables from .env
        env_vars = dotenv.dotenv_values()
        
        if not env_vars:
            logger.warning("No variables found in .env file")
            return
        
        # Set each variable using setx
        for key, value in env_vars.items():
            try:
                subprocess.run(['setx', key, value], check=True, capture_output=True)
                logger.info(f"Successfully set {key}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error setting {key}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error setting {key}: {e}")
                
    except FileNotFoundError:
        logger.error("Error: .env file not found")
    except Exception as e:
        logger.error(f"Error loading environment variables: {e}")

def set_unix_env_vars():
    """Set Unix environment variables from .env file"""
    try:
        dotenv.load_dotenv()
        logger.info("Successfully loaded environment variables")
    except Exception as e:
        logger.error(f"Error loading environment variables: {e}")

# Initialize environment based on platform silently
try:
    system = platform.system().lower()
    dotenv.load_dotenv(override=True)

    # Initialize Composio toolset with specific configuration
    composio_toolset = ComposioToolSet(
        workspace_config=WorkspaceType.Docker(
            silent=True,  # Suppress Docker output
            environment={
                "COMPOSIO_SUPPRESS_WARNINGS": "1",
                "COMPOSIO_IGNORE_RETURN_TYPE_WARNINGS": "1",
                "COMPOSIO_LOGGING_LEVEL": "ERROR",
                "PYTHONWARNINGS": "ignore"
            }
        )
    )

    # Define CaptainAgent configuration
    llm_config = {
        "config_list": [
            {"model": "gpt-4-turbo", "api_key": os.environ.get("OPENAI_API_KEY")},
        ],
        "temperature": 0.7,
        "request_timeout": 120,
        "seed": 42
    }

    # Create CaptainAgent
    captain = CaptainAgent(
        name="SWE_Captain",
        llm_config=llm_config,
        code_execution_config={
            "use_docker": False,
            "work_dir": "groupchat",
            "timeout": 60,
            "last_n_messages": 3
        },
        agent_lib="captainagent_expert_library.json",
        tool_lib=composio_toolset.get_tools(),
        system_message=f"""
        Role: {ROLE}
        Goal: {GOAL}
        Backstory: {BACKSTORY}
        Description: {DESCRIPTION}
        Expected Output: {EXPECTED_OUTPUT}
        
        When the task is complete, reply with TERMINATE.
        """,
        max_consecutive_auto_reply=5
    )

    # Define user proxy agent
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x is not None and isinstance(x.get("content"), str) and "TERMINATE" in x.get("content", ""),
        code_execution_config={
            "use_docker": False,
            "work_dir": "workspace",
            "timeout": 60
        },
        system_message="""You are a user proxy that helps interact with the CaptainAgent.
        You can:
        1. Execute code provided by the CaptainAgent
        2. Provide feedback and additional instructions
        3. Help guide the conversation towards solving the task
        4. Handle errors and provide debugging information
        
        When you receive input from the human user, pass it along to the CaptainAgent.
        When encountering errors, provide clear feedback and suggestions.
        """
    )

    # Register tools silently
    composio_toolset.register_tools(
        apps=[App.FILETOOL, App.SHELLTOOL, App.GITHUB],
        caller=captain,
        executor=user_proxy
    )

except Exception as e:
    sys.exit(1)
