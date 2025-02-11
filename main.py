from composio import Action
import uuid
from agent import composio_toolset, captain, user_proxy

def main() -> None:
    """Run the agent with interactive user input."""
    print("Welcome to the Interactive SWE Agent!")
    print("You can interact with the agent by providing:")
    print("1. Repository information (owner/repo)")
    print("2. Issue description or number")
    print("Type 'exit' at any time to quit\n")

    while True:
        # Get repository information
        repo = input("Enter repository (format: owner/repo): ")
        if repo.lower() == 'exit':
            break
            
        # Get issue information
        issue = input("Enter issue description or number: ")
        if issue.lower() == 'exit':
            break

        try:
            owner, repo_name = repo.split("/")
            
            # Initiate chat with CaptainAgent
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

            # Process the results
            composio_toolset.execute_action(
                action=Action.FILETOOL_CHANGE_WORKING_DIRECTORY,
                params={"path": f"/home/user/{repo_name}"},
            )
            
            # Get the patch
            response = composio_toolset.execute_action(
                action=Action.FILETOOL_GIT_PATCH,
                params={},
            )

            # Create and push changes
            branch_name = "fix-" + str(uuid.uuid4())[:8]
            git_commands = [
                f"checkout -b {branch_name}",
                "add -u",
                "config --global user.email 'random@gmail.com'",
                "config --global user.name 'random'",
                f"commit -m 'Fix: {issue}'",
                f"push --set-upstream origin {branch_name}",
            ]
            
            for command in git_commands:
                composio_toolset.execute_action(
                    action=Action.FILETOOL_GIT_CUSTOM,
                    params={"cmd": command},
                )

            # Create pull request
            pr_response = composio_toolset.execute_action(
                action=Action.GITHUB_CREATE_A_PULL_REQUEST,
                params={
                    "owner": owner,
                    "repo": repo_name,
                    "head": branch_name,
                    "base": "master",
                    "title": f"Fix: {issue}",
                },
            )

            # Show results
            print("\n=== Results ===")
            if response.get("data", {}).get("patch"):
                print("Changes made:")
                print(response["data"]["patch"])
            print(f"\nPull request created: {pr_response.get('data', {}).get('html_url', 'N/A')}")

        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again with valid input")

        # Ask if user wants to continue
        if input("\nWould you like to process another issue? (y/n): ").lower() != 'y':
            break

    print("Thank you for using the Interactive SWE Agent!")

if __name__ == "__main__":
    main()
