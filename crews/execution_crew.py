from crewai import Crew, Agent, Task, LLM
from dotenv import load_dotenv
from integrations.trello_tool import get_all_trello_tools
import os

load_dotenv()

llm = LLM(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

# Get all Trello tools
trello_tools = get_all_trello_tools()

# ================================ Agents ================================

trello_board_manager = Agent(
    role="Trello Board Setup Manager",
    goal="Create and organize Trello boards with proper list structure for project workflow",
    backstory="""You are an expert at setting up Trello boards for software projects.
    You create well-organized board structures with clear workflow stages. You understand
    that a good board structure helps teams visualize progress and manage work efficiently.

    IMPORTANT: After creating each list, you MUST extract and save the list ID from the
    success message for use in subsequent tasks.""",
    tools=trello_tools,
    llm=llm,
    verbose=True,
    allow_delegation=False
)

trello_task_manager = Agent(
    role="Trello Task Creation Specialist",
    goal="Transform ALL project tasks into Trello cards with exact dates from planning",
    backstory="""You are a meticulous task manager who creates Trello cards for EVERY
    task in the project plan. You NEVER skip tasks and you ALWAYS use the exact dates
    provided in the planning output.

    CRITICAL RULES:
    1. Create a card for EVERY task in the planning output
    2. Use the EXACT start_date and end_date from each task
    3. DO NOT generate new dates - use what's in the plan
    4. Work through tasks ONE AT A TIME
    5. Keep count of tasks created vs total tasks
    6. Complete each card fully (card → checklist → labels) before moving to next

    You are thorough and never give up until ALL tasks are created.""",
    tools=trello_tools,
    llm=llm,
    verbose=True,
    allow_delegation=False
)

trello_workflow_organizer = Agent(
    role="Trello Workflow Organizer",
    goal="Verify all tasks were created and provide summary",
    backstory="""You verify that the Trello board is complete and matches the plan.
    You check that all tasks were created and provide a detailed report.""",
    tools=trello_tools,
    llm=llm,
    verbose=True,
    allow_delegation=False
)


# ================================ Tasks ================================

create_board_structure_task = Task(
    description="""
    Create a Trello board structure by creating these lists in order:

    Board ID: {board_id}

    Use the "Create Trello List" tool to create each list with EXACT parameters:

    1. board_id="{board_id}", list_name="Backlog", position=1
    2. board_id="{board_id}", list_name="To Do", position=2
    3. board_id="{board_id}", list_name="In Progress", position=3
    4. board_id="{board_id}", list_name="Code Review", position=4
    5. board_id="{board_id}", list_name="Testing", position=5
    6. board_id="{board_id}", list_name="Done", position=6

    AFTER creating ALL lists, extract each list ID from the success messages.

    Success message format: "✅ Successfully created list 'To Do' (ID: 6731abc123456789)"
    Extract: 6731abc123456789

    Return ONLY a JSON object with the list IDs:
    {{
        "backlog_list_id": "extracted_id_1",
        "todo_list_id": "extracted_id_2",
        "in_progress_list_id": "extracted_id_3",
        "review_list_id": "extracted_id_4",
        "testing_list_id": "extracted_id_5",
        "done_list_id": "extracted_id_6"
    }}

    DO NOT add explanatory text. ONLY return the JSON object.
    """,
    agent=trello_board_manager,
    expected_output="JSON object containing all 6 list IDs with no additional text"
)

create_tasks_cards_task = Task(
    description="""
    Create Trello cards for EVERY task in the planning output. You MUST create ALL tasks.

    Planning Output: {planning_output}
    List IDs from previous task: {{output from previous task}}

    STEP 1: PARSE THE PLANNING OUTPUT

    Extract the "tasks" array from the planning JSON. Count how many tasks there are.
    Example: If planning has 20 tasks, you MUST create 20 cards.

    STEP 2: GET LIST IDs

    From the previous task output, extract:
    - todo_list_id (for high priority tasks)
    - backlog_list_id (for other tasks)

    STEP 3: CREATE EACH CARD (DO THIS FOR EVERY TASK)

    For task number 1 of X:

    A) CREATE CARD
       Tool: "Create Trello Card"
       - list_id: Use todo_list_id if priority is "Critical" or "High", else backlog_list_id
       - card_name: Use task "title" field from planning
       - description: Use task "description" field from planning
       - team_member_ids: "[]" (empty for now)
       - start_date: Use EXACT "start_date" from task (format: "YYYY-MM-DD")
       - end_date: Use EXACT "end_date" from task (format: "YYYY-MM-DD")

       CRITICAL: DO NOT make up dates. Use the dates from the planning output.

    B) EXTRACT CARD ID
       Success message: "✅ Successfully created card 'Task Name' (ID: 673abc123)"
       Card ID: 673abc123
       WRITE THIS DOWN

    C) CREATE CHECKLIST
       Tool: "Create Checklist on Card"
       - card_id: The ID from step B
       - checklist_name: "Acceptance Criteria"

    D) EXTRACT CHECKLIST ID
       Success message: "✅ Successfully created checklist 'Acceptance Criteria' (ID: abc123)"
       Checklist ID: abc123

    E) ADD CHECKLIST ITEMS
       For EACH item in task's "acceptance_criteria" array:
       Tool: "Add Item to Checklist"
       - checklist_id: The ID from step D
       - item_name: The acceptance criterion text

    F) ADD PRIORITY LABEL
       Tool: "Create Label"
       - card_id: The ID from step B
       - label_name: Use task "priority" field (e.g., "High Priority")
       - color:
         * "Critical" → "red"
         * "High" → "orange"
         * "Medium" → "yellow"
         * "Low" → "green"

    G) ADD CATEGORY LABEL
       Tool: "Create Label"
       - card_id: The ID from step B
       - label_name: Use task "category" field (e.g., "Backend", "Frontend")
       - color:
         * "Backend" → "blue"
         * "Frontend" → "purple"
         * "Database" → "sky"
         * "DevOps" → "lime"
         * "Testing" → "pink"
         * "Documentation" → "black"

    STEP 4: TRACK PROGRESS

    After completing steps A-G for task 1, move to task 2.
    Keep count: "Created 1 of X tasks"

    Repeat steps A-G for task 2, then task 3, etc.

    DO NOT STOP until you've created ALL X tasks.

    STEP 5: FINAL VERIFICATION

    After processing all tasks, count:
    - Total cards created
    - Cards in "To Do" list
    - Cards in "Backlog" list
    - Cards with checklists
    - Cards with labels

    FINAL OUTPUT (must be valid JSON):
    {{
        "total_tasks_in_plan": X,
        "total_cards_created": Y,
        "cards_in_todo": Z,
        "cards_in_backlog": W,
        "all_card_ids": ["id1", "id2", "id3", ...],
        "cards_with_checklists": Y,
        "cards_with_labels": Y,
        "verification": "Created Y of X tasks (100% complete)" or "WARNING: Only created Y of X tasks"
    }}

    CRITICAL REMINDERS:
    - Create a card for EVERY task in the planning output
    - Use EXACT dates from planning (start_date and end_date fields)
    - DO NOT skip tasks
    - DO NOT generate new dates
    - Complete each card fully before moving to next
    - Track your progress: "Task 5 of 20..."
    """,
    agent=trello_task_manager,
    expected_output="""JSON summary with total_tasks_in_plan, total_cards_created, verification status,
    all_card_ids array, and counts for checklists and labels. Must show if all tasks were created.""",
    context=[create_board_structure_task]
)

organize_workflow_task = Task(
    description="""
    Verify the Trello board setup and check completeness.

    Board ID: {board_id}
    Planning Output: {planning_output}
    Execution Results: {{output from previous task}}

    VERIFICATION CHECKLIST:

    1. **Task Completeness Check**:
       - How many tasks were in the planning output?
       - How many cards were created?
       - Percentage complete: (cards created / tasks in plan) × 100%
       - If < 100%, list which tasks are missing

    2. **Lists Summary**:
       - Total lists: 6
       - List names: Backlog, To Do, In Progress, Code Review, Testing, Done

    3. **Cards Summary**:
       - Total cards created
       - Cards in "To Do" list (high priority)
       - Cards in "Backlog" list (other)
       - Cards in other lists (should be 0 initially)

    4. **Quality Metrics**:
       - Cards with checklists: X/Y (should be 100%)
       - Cards with priority labels: X/Y (should be 100%)
       - Cards with category labels: X/Y (should be 100%)
       - Cards with due dates: X/Y (should be 100%)

    5. **Date Verification**:
       - Are cards using dates from planning output?
       - Do dates match the project timeline?
       - Are sprint 1 tasks in "To Do" list?

    6. **Board Readiness Score**: X/10
       Scoring:
       - All tasks created: +4 points
       - All checklists added: +2 points
       - All labels added: +2 points
       - Dates match planning: +2 points

    7. **Issues Found**:
       - List any missing tasks
       - Note any cards without checklists
       - Identify any cards without labels
       - Flag any date mismatches

    8. **Recommendations**:
       - If tasks are missing: "Create remaining tasks manually"
       - Suggest any reorganization needed
       - Next steps for the team

    Provide a clear, readable report (NOT JSON).
    Start with: "BOARD COMPLETENESS: X/Y tasks created (Z%)"
    """,
    agent=trello_workflow_organizer,
    expected_output="""Comprehensive verification report with:
    - Task completeness percentage
    - List of any missing tasks
    - Quality metrics for checklists, labels, dates
    - Board readiness score
    - Issues and recommendations""",
    context=[create_board_structure_task, create_tasks_cards_task]
)


# ================================ Crew ================================

execution_crew = Crew(
    agents=[trello_board_manager, trello_task_manager, trello_workflow_organizer],
    tasks=[create_board_structure_task, create_tasks_cards_task, organize_workflow_task],
    verbose=True,
    memory=False,
    cache=False
)
