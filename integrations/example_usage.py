"""
Example: Integrating Trello with Project Manager Crew
"""

from crewai import Agent, Task, Crew, LLM
from integrations import create_trello_tools
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Trello tools
create_board_tool, create_list_tool, create_card_tool = create_trello_tools()

# Create LLM
llm = LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Create an agent that can use Trello
trello_manager = Agent(
    role="Trello Project Manager",
    goal="Set up Trello boards and organize project tasks",
    backstory="""You are an expert project manager who uses Trello to organize work. 
    You create well-structured boards with clear lists and detailed cards for each task.""",
    tools=[create_board_tool, create_list_tool, create_card_tool],
    llm=llm,
    verbose=True,
)


# Example 1: Simple board creation
def example_simple_board():
    task = Task(
        description="""
        Create a Trello board called 'Website Redesign Project'.
        Create three lists: 'Backlog', 'In Progress', and 'Completed'.
        Add a card in the Backlog for 'Design new homepage mockup' due on 2025-12-15.
        Assign it to John Doe (john@example.com).
        """,
        agent=trello_manager,
        expected_output="Summary of created board, lists, and cards with their IDs",
    )

    crew = Crew(agents=[trello_manager], tasks=[task], verbose=True)

    result = crew.kickoff()
    print("\n" + "=" * 50)
    print("RESULT:")
    print(result)
    print("=" * 50)


# Example 2: Integration with research output
def example_with_research_output(research_findings: str, team_members: list):
    """
    This shows how to use Trello tools with research crew output.

    Args:
        research_findings: The output from your research crew
        team_members: List of team member dictionaries
    """

    task = Task(
        description=f"""
        Based on the following research findings, create a Trello board to manage the project:
        
        {research_findings}
        
        Team Members:
        {team_members}
        
        Your tasks:
        1. Create a Trello board with an appropriate name based on the project
        2. Create lists for different phases of work (e.g., 'Planning', 'Design', 'Development', 'Testing', 'Deployment')
        3. Create cards for the key deliverables and tasks identified in the research
        4. Assign cards to appropriate team members based on their skills
        5. Set due dates based on the project timeline
        
        Provide a summary of what you created with all IDs.
        """,
        agent=trello_manager,
        expected_output="Complete summary of the Trello board structure with IDs for all created items",
    )

    crew = Crew(agents=[trello_manager], tasks=[task], verbose=True)

    result = crew.kickoff()
    return result


# Example 3: Creating sprint boards
def example_sprint_board():
    task = Task(
        description="""
        Create a Trello board for 'Sprint 1 - User Authentication'.
        
        Create these lists:
        - Sprint Backlog
        - To Do
        - In Progress
        - Code Review
        - Testing
        - Done
        
        Add these cards to Sprint Backlog:
        1. 'Set up authentication database schema' - due 2025-11-15 - assign to Alice Smith
        2. 'Implement JWT token generation' - due 2025-11-18 - assign to Bob Johnson
        3. 'Create login/signup UI' - due 2025-11-20 - assign to Carol White
        4. 'Write authentication tests' - due 2025-11-22 - assign to Alice Smith
        """,
        agent=trello_manager,
        expected_output="Summary of sprint board with all created items",
    )

    crew = Crew(agents=[trello_manager], tasks=[task], verbose=True)

    result = crew.kickoff()
    print("\n" + "=" * 50)
    print("SPRINT BOARD CREATED:")
    print(result)
    print("=" * 50)


if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Simple board creation")
    print("2. Sprint board creation")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ")

    if choice == "1":
        example_simple_board()
    elif choice == "2":
        example_sprint_board()
    else:
        print("Exiting...")
