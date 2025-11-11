from crewai import Crew, Agent, Task, LLM
from dotenv import load_dotenv
from integrations.trello_tool import get_all_trello_tools
import os

load_dotenv()

llm = LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Get all Trello tools
trello_tools = get_all_trello_tools()

# ================================ Agents ================================

trello_board_manager = Agent(
    role="Trello Board Setup Manager",
    goal="Create and organize Trello boards with proper list structure for project workflow",
    backstory="""You are an expert at setting up Trello boards for software projects.
    You create well-organized board structures with clear workflow stages. You understand
    that a good board structure helps teams visualize progress and manage work efficiently.
    You always create at least these standard lists: Backlog, To Do, In Progress, Review,
    Testing, and Done.""",
    tools=trello_tools,
    llm=llm,
    verbose=True
)

trello_task_manager = Agent(
    role="Trello Task Creation Specialist",
    goal="Transform project tasks into detailed Trello cards with checklists, labels, and proper assignments",
    backstory="""You are a meticulous task manager who excels at breaking down project plans
    into actionable Trello cards. You create detailed card descriptions, add comprehensive
    checklists with acceptance criteria, assign appropriate team members, and set realistic
    due dates. You use labels effectively to categorize tasks by priority and type. You never
    create vague cards - every card has clear deliverables and success criteria.""",
    tools=trello_tools,
    llm=llm,
    verbose=True
)

trello_workflow_organizer = Agent(
    role="Trello Workflow Organizer",
    goal="Organize cards into appropriate lists and ensure proper task flow through the board",
    backstory="""You understand project workflows and task dependencies. You organize cards
    into the right lists based on their current status and dependencies. You ensure that
    tasks flow logically through the board stages, and you move cards to appropriate lists
    based on project phases and sprint planning.""",
    tools=trello_tools,
    llm=llm,
    verbose=True
)


# ================================ Tasks ================================

create_board_structure_task = Task(
    description="""
    Based on the project plan, create a comprehensive Trello board structure.

    Project Information: {project_name}
    Board ID (already created): {board_id}

    Your tasks:
    1. Create workflow lists on the board in this exact order:
       - Backlog (for future work and ideas)
       - To Do (ready to start)
       - In Progress (actively being worked on)
       - Code Review (awaiting review)
       - Testing (QA in progress)
       - Done (completed)

    2. If the project has sprints or phases, create additional lists for:
       - Sprint Planning
       - Sprint 1, Sprint 2, etc. (if mentioned in the plan)

    Return ALL list IDs in a structured format:
    {{
        "backlog_list_id": "...",
        "todo_list_id": "...",
        "in_progress_list_id": "...",
        "review_list_id": "...",
        "testing_list_id": "...",
        "done_list_id": "..."
    }}
    """,
    agent=trello_board_manager,
    expected_output="JSON object with all created list IDs and their names"
)

create_tasks_cards_task = Task(
    description="""
    Transform the project planning output into detailed Trello cards.

    Planning Output: {planning_output}
    Team Members: {team_members}
    List IDs: list ids from the previous task

    For EACH task in the planning output, create a Trello card with:

    1. **Card Name**: Clear, action-oriented task title

    2. **Description**: Include:
       - Detailed task description
       - Technical requirements
       - Acceptance criteria (from planning output)
       - Dependencies (mention which other tasks must be done first)
       - Estimated effort

    3. **Checklist**: Create a checklist named "Acceptance Criteria" with items for:
       - Each acceptance criterion from the planning output
       - Testing requirements
       - Documentation requirements

    4. **Due Date**: Set the due date based on the timeline in the planning output

    5. **Assign**: Assign to appropriate team member based on:
       - Skills match (from team_members)
       - The "assigned_to" field in the planning output

    6. **Labels**: Create and add labels for:
       - Priority level (Critical=red, High=orange, Medium=yellow, Low=green)
       - Task type (Feature=blue, Bug=purple, Documentation=sky)

    7. **List Placement**:
       - High priority tasks that should start immediately → "To Do" list
       - Lower priority or later phase tasks → "Backlog" list
       - Tasks with unmet dependencies → "Backlog" list

    IMPORTANT: Process ALL tasks from the planning output. Don't skip any.

    Return a summary with:
    - Total cards created
    - Cards in each list
    - Any issues encountered
    """,
    agent=trello_task_manager,
    expected_output="""Detailed summary of all created cards including:
    - Total number of cards created
    - Breakdown by list (how many in each)
    - Breakdown by priority
    - Any team member without assignments
    - List of card IDs created""",
    context=[create_board_structure_task]
)

organize_workflow_task = Task(
    description="""
    Review and organize the created Trello board for optimal workflow.

    List IDs: list ids from the previous task
    Created Cards Summary: [from previous task]

    Your tasks:

    1. **Review Card Distribution**:
       - Check that high-priority, no-dependency tasks are in "To Do"
       - Ensure dependent tasks are in "Backlog" until dependencies are met
       - Verify cards are not overloaded in any single list

    2. **Verify Assignments**:
       - Check that workload is balanced across team members
       - Identify any team members with no tasks
       - Identify any team members with too many tasks

    3. **Check Dependencies**:
       - Review cards in "To Do" and ensure they have no blocking dependencies
       - Move any blocked tasks back to "Backlog"

    4. **Add Sprint Organization** (if applicable):
       - If the project has sprints, organize tasks into sprint lists
       - Move Sprint 1 tasks to "To Do" or "In Progress" as appropriate

    5. **Final Verification**:
       - Ensure all cards have checklists
       - Ensure all cards have due dates
       - Ensure all cards have assignees
       - Ensure all cards have appropriate labels

    Provide a final board summary report with:
    - Total cards per list
    - Total cards per team member
    - Any issues or recommendations
    - Board URL or board ID for easy access
    """,
    agent=trello_workflow_organizer,
    expected_output="""Complete board organization report with:
    - Cards per list breakdown
    - Team member workload summary
    - Any issues or warnings
    - Recommendations for board usage
    - Board access information""",
    context=[create_board_structure_task, create_tasks_cards_task]
)


# ================================ Crew ================================

execution_crew = Crew(
    agents=[trello_board_manager, trello_task_manager, trello_workflow_organizer],
    tasks=[create_board_structure_task, create_tasks_cards_task, organize_workflow_task],
    verbose=True
)

