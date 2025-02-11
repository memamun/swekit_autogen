from composio import Action
import uuid
from agent import composio_toolset, captain, user_proxy

def main() -> None:
    """Run the agent with interactive user input."""
    print("Welcome to the Full-Stack Development Agent!")
    print("\nAvailable Operations:")
    print("1. Create new repository")
    print("2. Work on existing repository")
    print("3. Fix issues")
    print("4. Review pull requests")
    print("Type 'exit' at any time to quit\n")

    while True:
        operation = input("Select operation (1-4): ")
        if operation.lower() == 'exit':
            break

        try:
            if operation == "1":
                # Create new repository
                repo_name = input("Enter new repository name: ")
                description = input("Enter repository description: ")
                
                # Create repository
                repo_response = composio_toolset.execute_action(
                    action=Action.GITHUB_CREATE_A_REPOSITORY,
                    params={
                        "name": repo_name,
                        "description": description,
                        "private": False
                    }
                )
                
                # Initialize with project structure
                chat_result = user_proxy.initiate_chat(
                    captain,
                    message=f"""
                    Repository: {repo_response['data']['full_name']}
                    Task: Initialize repository with a full-stack project structure
                    
                    Please:
                    1. Set up the basic project structure
                    2. Initialize frontend and backend
                    3. Set up CI/CD configuration
                    4. Create initial documentation
                    """
                )

            elif operation == "2":
                # Work on existing repository
                repo = input("Enter repository (format: owner/repo): ")
                task = input("Enter development task description: ")
                
                chat_result = user_proxy.initiate_chat(
                    captain,
                    message=f"""
                    Repository: {repo}
                    Task: {task}
                    
                    Please:
                    1. Analyze the existing codebase
                    2. Plan the implementation
                    3. Make necessary changes
                    4. Add tests
                    5. Create a pull request
                    """
                )

            elif operation == "3":
                # Fix issues (existing functionality)
                repo = input("Enter repository (format: owner/repo): ")
                issue = input("Enter issue number or description: ")
                
                # Existing issue handling code...
                
            elif operation == "4":
                # Review pull requests
                repo = input("Enter repository (format: owner/repo): ")
                pr_number = input("Enter PR number: ")
                
                chat_result = user_proxy.initiate_chat(
                    captain,
                    message=f"""
                    Repository: {repo}
                    PR: {pr_number}
                    
                    Please:
                    1. Review the changes
                    2. Check code quality
                    3. Verify tests
                    4. Provide feedback
                    """
                )

            # Show results and handle continuation
            print("\n=== Operation Complete ===")
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again with valid input")

        if input("\nWould you like to perform another operation? (y/n): ").lower() != 'y':
            break

    print("Thank you for using the Full-Stack Development Agent!")

if __name__ == "__main__":
    main()
