from inputs import from_github
from composio import Action
import uuid
import os
from agent import composio_toolset, captain, user_proxy

def main() -> None:
    """Run the agent."""
    repo, issue = from_github()
    owner, repo_name = repo.split("/")
    
    # Create platform-independent path
    work_dir = os.path.join(os.path.expanduser("~"), repo_name)
    
    # Initiate the chat with CaptainAgent
    chat_result = user_proxy.initiate_chat(
        captain,
        message=f"""
        Repository: {repo}
        Issue: {issue}
        
        Please analyze this issue and create a fix following these steps:
        1. Analyze the codebase and understand the issue
        2. Develop a solution strategy
        3. Implement the fix
        4. Test the changes
        5. Create a pull request
        """
    )

    composio_toolset.execute_action(
        action=Action.FILETOOL_CHANGE_WORKING_DIRECTORY,
        params={"path": work_dir},
    )
    # Get the patch after the chat is complete
    response = composio_toolset.execute_action(
        action=Action.FILETOOL_GIT_PATCH,
        params={},
    )
    branch_name = "test-branch-" + str(uuid.uuid4())[:4]
    git_commands = [
        f"checkout -b {branch_name}",
        "add -u",
        "config --global user.email 'random@gmail.com'",
        "config --global user.name 'random'",
        f"commit -m '{issue}'",
        f"push --set-upstream origin {branch_name}",
    ]
    for command in git_commands:
        composio_toolset.execute_action(
            action=Action.FILETOOL_GIT_CUSTOM,
            params={"cmd": command},
        )
    composio_toolset.execute_action(
        action=Action.GITHUB_CREATE_A_PULL_REQUEST,
        params={
            "owner": owner,
            "repo": repo_name,
            "head": branch_name,
            "base": "master",
            "title": "Test-Title",
        },
    )

    data = response.get("data")
    if data.get("error") and len(data["error"]) > 0:
        print("Error:", response["error"])
    elif data.get("patch"):
        print("=== Generated Patch ===\n" + data["patch"])
    else:
        print("No output available")

if __name__ == "__main__":
    main()
