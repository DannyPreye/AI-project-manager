from crewai import Crew, Agent, Task, LLM
from dotenv import load_dotenv
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from integrations.trello_tool import get_all_trello_tools
from pydantic import BaseModel
import os

load_dotenv()

trello_tools = get_all_trello_tools()

llm = LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
class Label(BaseModel):
   name: str
   color: str

class CardSpecification(BaseModel):
   list_id: str
   card_name: str
   description: str
   start_date: str
   end_date: str
   labels: list[Label]
   checklist_items: list[str]


class CardSpecifications(BaseModel):
   card_specifications: list[CardSpecification]

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

task_generator = Agent(
    role="Task Breakdown Specialist",
    goal="Convert project analysis into detailed, actionable tasks with clear specifications",
    backstory="""You are a senior technical project manager who breaks down projects into
    specific, actionable tasks. Each task you create is clear, measurable, and completable
    by a single person in 2-16 hours.

    You ALWAYS include:
    - Specific task titles (action-oriented)
    - Detailed descriptions with technical requirements
    - 3-5 measurable acceptance criteria
    - Realistic effort estimates
    - Clear priority levels
    - Dependencies between tasks

    You NEVER create vague tasks. Every task must be immediately actionable.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)

timeline_planner = Agent(
    role="Timeline Architect",
    goal="Create realistic project schedules with specific dates and milestones",
    backstory="""You are an expert project scheduler who creates detailed timelines with
    specific dates. You understand task dependencies and create realistic schedules that
    account for:
    - Task dependencies (what must be done first)
    - Parallel work opportunities
    - Team capacity and realistic work hours
    - Buffer time for unknowns (15-20%)

    You always provide concrete dates in YYYY-MM-DD format and organize work into
    logical sprints or phases.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)

task_assigner = Agent(
    role="Assignment Optimizer",
    goal="Match tasks to team members based on skills and balance workload",
    backstory="""You are a resource allocation expert who assigns tasks to team members
    based on their skills and availability. You:
    - Match tasks to team members with the best skills
    - Balance workload across the team
    - Identify when team members need training or support
    - Flag when external help may be needed

    You ensure no one is overloaded and everyone's skills are used effectively.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)

planning_synthesizer = Agent(
    role="Project Planning Synthesizer",
    goal="Consolidate all planning outputs into a comprehensive, execution-ready project plan",
    backstory="""You are a master project coordinator who creates comprehensive project
    plans. You take outputs from task breakdown, timeline planning, and team assignments
    and combine them into a single, well-organized plan.

    Your plans include EVERYTHING needed for execution:
    - Complete task list with all details
    - Sprint/phase breakdown
    - Timeline with milestones
    - Team assignments
    - Dependencies
    - Risks and recommendations

    You ensure nothing is lost and all information is clearly organized in valid JSON format.""",
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


task_generation_task = Task(
    description="""
    Break down the project into MODERATE-SIZED, manageable tasks.

    Project Description: {project_description}
    research_output: {research_output}

    TASK GRANULARITY RULES (BALANCED):
    ❌ TOO BROAD: "Develop Core Backend API"
    ❌ TOO GRANULAR: "Create user registration endpoint", "Create user login endpoint" (separate tasks)
    ✅ JUST RIGHT: "Implement User Authentication System" (covers registration, login, JWT, password reset)

    EXAMPLES OF GOOD TASK SIZING:

    1. BACKEND (typically 8-12 tasks):
       - "Setup Backend Project Structure & Dependencies"
       - "Implement User Authentication System" (registration, login, JWT, password management)
       - "Build User Profile Management" (CRUD, updates, preferences)
       - "Create Product/Item Management API" (CRUD endpoints for main entities)
       - "Implement Search & Filtering System"
       - "Setup File Upload & Storage"
       - "Build Notification System"
       - "Implement Payment Integration" (if applicable)

    2. FRONTEND (typically 8-12 tasks):
       - "Setup Frontend Project & Routing"
       - "Create Authentication UI" (login, register, forgot password pages)
       - "Build Dashboard & Navigation"
       - "Implement User Profile Pages"
       - "Create Main Feature UI" (list, detail, create/edit forms)
       - "Build Search & Filter Interface"
       - "Implement Settings & Preferences UI"
       - "Add Responsive Design & Mobile Optimization"

    3. DATABASE (typically 3-5 tasks):
       - "Design & Implement Core Database Schema"
       - "Create Database Migrations & Indexes"
       - "Setup Database Relationships & Constraints"
       - "Create Seed Data & Test Fixtures"

    4. DEVOPS (typically 3-5 tasks):
       - "Setup Development Environment & Docker"
       - "Configure CI/CD Pipeline"
       - "Setup Production Deployment & Monitoring"
       - "Implement Logging & Error Tracking"

    5. TESTING (typically 3-4 tasks):
       - "Write Backend Unit & Integration Tests"
       - "Write Frontend Component Tests"
       - "Create E2E Test Suite for Critical Flows"

    6. DOCUMENTATION (typically 2-3 tasks):
       - "Create API Documentation & Postman Collection"
       - "Write Setup & Deployment Guide"
       - "Create User Documentation"

    EACH TASK SHOULD:
    - Take 3-7 days for one developer
    - Cover a complete functional area (not a single endpoint/component)
    - Have 4-6 clear acceptance criteria
    - Be meaningful enough to show progress

    GENERATE 20-30 TASKS for a complete project.

    Output as JSON array of tasks with:
    - task_id
    - title (clear functional area, not too specific)
    - description (what's included in this task)
    - category (Backend/Frontend/Database/DevOps/Testing/Documentation)
    - priority (Critical/High/Medium/Low)
    - estimated_days (3-7 days realistic)
    - acceptance_criteria (array of 4-6 criteria)
    - dependencies (array of task_ids)
    """,
    agent=planning_synthesizer,
    expected_output="JSON array of 20-30 moderate-sized tasks covering complete functional areas",

)


# ================================ Crew ================================
card_specifications_task = Task(
    description="""
    Convert ALL tasks into Trello card specifications with complete details.

    Task List from previous task: {output from task_generation_task}
    List IDs from board structure: {output from create_board_structure_task}

    STEP 1: EXTRACT LIST IDs FROM create_board_structure_task OUTPUT
    Parse the JSON to get:
    - todo_list_id (for Critical/High priority tasks)
    - backlog_list_id (for Medium/Low priority tasks)

    STEP 2: ANALYZE ALL TASKS
    Go through EVERY task in the task list and count them.

    STEP 3: CREATE CARD SPECIFICATION FOR EACH TASK
    For EACH task, create a card specification with this EXACT format:
    {{
        "list_id": "[list_id from create_board_structure_task output]",
        "card_name": "[task title]",
        "description": "[task description with acceptance criteria]",
        "start_date": "[YYYY-MM-DD - calculate from project timeline {project_timeline}]",
        "end_date": "[YYYY-MM-DD - calculate from project timeline {project_timeline}]",
        "labels": [
            {{"name": "[priority level] Priority", "color": "[priority color]"}},
            {{"name": "[category]", "color": "[category color]"}}
        ],
        "checklist_items": ["[acceptance criterion 1]", "[acceptance criterion 2]", ...]
    }}

    Label colors:
    - Priority: Critical→red, High→orange, Medium→yellow, Low→green
    - Category: Backend→blue, Frontend→purple, Database→sky, DevOps→lime, Testing→pink, Documentation→black

    YOUR FINAL OUTPUT MUST BE A JSON OBJECT with a "card_specifications" field containing an array:
    {{
        "card_specifications": [
            {{
                "list_id": "6731abc123",
                "card_name": "Setup Development Environment",
                "description": "Configure local environment with Node.js, React, PostgreSQL. Set up linting and Git hooks.",
                "start_date": "2025-11-15",
                "end_date": "2025-11-16",
                "labels": [
                    {{"name": "Critical Priority", "color": "red"}},
                    {{"name": "DevOps", "color": "lime"}}
                ],
                "checklist_items": [
                    "All team members can run app locally",
                    "ESLint and Prettier configured",
                    "Git pre-commit hooks working"
                ]
            }},
            {{
                "list_id": "6731def456",
                "card_name": "Design Database Schema",
                "description": "Create PostgreSQL schema for users, projects, tasks. Include migrations and indexes.",
                "start_date": "2025-11-17",
                "end_date": "2025-11-19",
                "labels": [
                    {{"name": "High Priority", "color": "orange"}},
                    {{"name": "Database", "color": "sky"}}
                ],
                "checklist_items": [
                    "ER diagram created and reviewed",
                    "All tables created with proper indexes",
                    "Migration scripts tested"
                ]
            }}
        ]
    }}

    CRITICAL REQUIREMENTS:
    - Create specification for EVERY task in the task list
    - Use ACTUAL list IDs from create_board_structure_task output
    - Calculate realistic dates based on project timeline
    - Each card must have at least 2 labels (priority + category)
    - Each card must have 3-5 checklist items from acceptance criteria
    - Output MUST be a JSON object with "card_specifications" field containing the array
    - Output ONLY the JSON object, NO additional text
    - Minimum 10 card specifications
    """,
    agent=planning_synthesizer,
    expected_output="Valid JSON object with 'card_specifications' field containing an array of card specifications in the exact format specified, one for each task. Minimum 10 cards. NO additional text.",
    context=[create_board_structure_task, task_generation_task],
    output_json=CardSpecifications
)

planning_crew = Crew(
    agents=[trello_board_manager, task_generator, timeline_planner, task_assigner, planning_synthesizer],
    tasks=[create_board_structure_task, task_generation_task, card_specifications_task],
    verbose=True,
    memory=False,  # Disable memory for consistent behavior
    cache=False    # Disable cache for fresh execution
)
