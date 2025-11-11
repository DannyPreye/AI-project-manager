"""
Example: Using Trello Tools with CrewAI Agents

This example shows how to use the Trello tools to create a project management workflow.
"""

from crewai import Agent, Task, Crew, LLM
from integrations import get_all_trello_tools, get_essential_trello_tools
import os
from dotenv import load_dotenv

load_dotenv()

# Create LLM
llm = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)


# ================================ Example 1: Essential Tools Only ================================

def example_essential_tools():
    """
    Use only essential Trello tools for basic project setup.
    """

    trello_manager = Agent(
        role="Trello Project Setup Manager",
        goal="Set up a complete Trello board with lists and cards for a project",
        backstory="""You are an expert project manager who uses Trello to organize work.
        You create well-structured boards with clear lists and detailed cards for each task.
        You always break down tasks into manageable sub-tasks using checklists.""",
        tools=get_essential_trello_tools(),  # Only board, list, card, move, and checklist tools
        llm=llm,
        verbose=True
    )

    task = Task(
        description="""
        Set up a Trello board for a 'Website Redesign' project.

        1. Create a board called 'Website Redesign Project'
        2. Create these lists: 'Backlog', 'To Do', 'In Progress', 'Review', 'Done'
        3. Create these cards in the 'To Do' list:
           - 'Design new homepage mockup' (due 2025-12-15, with checklist: 'Research competitors', 'Create wireframe', 'Design mockup')
           - 'Implement responsive navigation' (due 2025-12-20, with checklist: 'HTML structure', 'CSS styling', 'JavaScript interactions')
           - 'Set up contact form' (due 2025-12-25, with checklist: 'Form HTML', 'Validation', 'Backend integration')

        Provide a summary with all IDs created.
        """,
        agent=trello_manager,
        expected_output="Summary of created board, lists, and cards with their IDs"
    )

    crew = Crew(
        agents=[trello_manager],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()
    print("\n" + "="*80)
    print("EXAMPLE 1 RESULT:")
    print(result)
    print("="*80)
    return result


# ================================ Example 2: All Tools ================================

def example_all_tools():
    """
    Use all Trello tools for comprehensive project management with labels and advanced features.
    """

    advanced_manager = Agent(
        role="Advanced Trello Project Manager",
        goal="Create a sophisticated project board with labels, checklists, and proper categorization",
        backstory="""You are a senior project manager who uses all of Trello's features.
        You use labels to categorize tasks by priority and type, create detailed checklists,
        and organize everything systematically.""",
        tools=get_all_trello_tools(),  # All available tools
        llm=llm,
        verbose=True
    )

    task = Task(
        description="""
        Set up a comprehensive Trello board for an 'E-commerce Platform Development' project.

        1. Create a board called 'E-commerce Platform Dev'
        2. Create workflow lists: 'Sprint Planning', 'Development', 'Code Review', 'Testing', 'Deployed'
        3. Create cards with appropriate labels:
           - 'User Authentication System' in 'Development' (Priority: High, Type: Feature)
           - 'Shopping Cart Functionality' in 'Development' (Priority: High, Type: Feature)
           - 'Payment Gateway Integration' in 'Sprint Planning' (Priority: Critical, Type: Feature)
           - 'Fix checkout page styling' in 'Testing' (Priority: Medium, Type: Bug)

        4. Add checklists to break down complex tasks
        5. Use labels to categorize:
           - Red label for 'Critical'
           - Orange for 'High Priority'
           - Yellow for 'Medium Priority'
           - Green for 'Feature'
           - Blue for 'Bug'

        Provide complete summary with all IDs.
        """,
        agent=advanced_manager,
        expected_output="Detailed summary of board structure with all IDs and labels"
    )

    crew = Crew(
        agents=[advanced_manager],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()
    print("\n" + "="*80)
    print("EXAMPLE 2 RESULT:")
    print(result)
    print("="*80)
    return result


# ================================ Example 3: Integration with Research & Planning ================================

def example_with_planning_output(planning_output: str, team_members: list):
    """
    Create Trello board from planning crew output.
    This integrates with your existing research and planning crews.

    Args:
        planning_output: The JSON output from your planning crew
        team_members: List of team member dictionaries
    """

    execution_manager = Agent(
        role="Trello Execution Manager",
        goal="Convert project plans into actionable Trello boards with proper task distribution",
        backstory="""You are an expert at translating project plans into well-organized Trello boards.
        You understand how to break down complex plans into boards, lists, and cards. You assign
        tasks to appropriate team members and set realistic due dates.""",
        tools=get_all_trello_tools(),
        llm=llm,
        verbose=True
    )

    task = Task(
        description=f"""
        Based on this planning output, create a complete Trello board:

        {planning_output}

        Team Members:
        {team_members}

        Your tasks:
        1. Create a board with project name from the plan
        2. Create lists for each sprint/phase identified in the plan
        3. Create cards for each task in the plan with:
           - Task title and description
           - Due date from the timeline
           - Checklist with acceptance criteria
           - Labels for priority level
        4. Organize cards into appropriate lists based on sprint/phase

        Provide summary of created structure with all IDs.
        """,
        agent=execution_manager,
        expected_output="Complete Trello board structure with all IDs"
    )

    crew = Crew(
        agents=[execution_manager],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()
    return result


# ================================ Example 4: Specific Tools for Specific Agents ================================

def example_specialized_agents():
    """
    Create multiple agents with specific tool subsets for different responsibilities.
    """

    # Agent 1: Only creates boards and lists
    setup_agent = Agent(
        role="Board Setup Specialist",
        goal="Create and configure Trello boards and lists",
        backstory="Expert at setting up project structures",
        tools=[
            TrelloCreateBoardTool(),
            TrelloCreateListTool(),
            TrelloUpdateListTool(),
        ],
        llm=llm,
        verbose=True
    )

    # Agent 2: Only manages cards and checklists
    task_agent = Agent(
        role="Task Management Specialist",
        goal="Create and manage task cards with checklists",
        backstory="Expert at breaking down work into actionable tasks",
        tools=[
            TrelloCreateCardTool(),
            TrelloUpdateCardTool(),
            TrelloCreateChecklistTool(),
            TrelloAddChecklistItemTool(),
            TrelloMoveCardTool(),
        ],
        llm=llm,
        verbose=True
    )

    # Agent 3: Only manages labels
    categorization_agent = Agent(
        role="Categorization Specialist",
        goal="Organize tasks with labels and categories",
        backstory="Expert at task categorization and prioritization",
        tools=[
            TrelloCreateLabelTool(),
            TrelloAddLabelToCardTool(),
        ],
        llm=llm,
        verbose=True
    )

    setup_task = Task(
        description="Create a board called 'Q1 Marketing Campaign' with lists: 'Planning', 'Execution', 'Review'",
        agent=setup_agent,
        expected_output="Board and list IDs"
    )

    task_task = Task(
        description="Create 3 marketing task cards in 'Planning' list with checklists",
        agent=task_agent,
        expected_output="Card IDs with checklists",
        context=[setup_task]
    )

    label_task = Task(
        description="Add priority labels (High, Medium, Low) to the created cards",
        agent=categorization_agent,
        expected_output="Label assignments",
        context=[task_task]
    )

    crew = Crew(
        agents=[setup_agent, task_agent, categorization_agent],
        tasks=[setup_task, task_task, label_task],
        verbose=True
    )

    result = crew.kickoff()
    print("\n" + "="*80)
    print("SPECIALIZED AGENTS RESULT:")
    print(result)
    print("="*80)
    return result


# ================================ Main ================================

if __name__ == "__main__":
    print("Trello Tools Example\n")
    print("Choose an example to run:")
    print("1. Essential Tools - Basic board setup")
    print("2. All Tools - Advanced board with labels")
    print("3. Specialized Agents - Multiple agents with specific tools")
    print("4. Exit")

    choice = input("\nEnter choice (1-4): ")

    if choice == "1":
        example_essential_tools()
    elif choice == "2":
        example_all_tools()
    elif choice == "3":
        example_specialized_agents()
    else:
        print("Exiting...")


# ================================ Import Needed for Example 4 ================================

if __name__ == "__main__":
    from integrations import (
        TrelloCreateBoardTool,
        TrelloCreateListTool,
        TrelloUpdateListTool,
        TrelloCreateCardTool,
        TrelloUpdateCardTool,
        TrelloCreateChecklistTool,
        TrelloAddChecklistItemTool,
        TrelloMoveCardTool,
        TrelloCreateLabelTool,
        TrelloAddLabelToCardTool,
    )

