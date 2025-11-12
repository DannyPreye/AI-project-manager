from crewai import Crew, Agent, Task, LLM
from dotenv import load_dotenv
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
import os

load_dotenv()

llm = LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))


# ================================ Agents ================================
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
task_generation_task = Task(
    description="""
    Break down the project into detailed, actionable tasks based on the research.

    Research Output: {research_output}

    Create 15-25 tasks that cover the entire project. For EACH task, provide:

    1. **title**: Clear, action-oriented (e.g., "Implement User Authentication API")
    2. **description**: What needs to be built, technical specs, edge cases (2-3 sentences)
    3. **acceptance_criteria**: List of 3-5 specific, testable criteria
    4. **effort_hours**: Realistic estimate (4-40 hours per task)
    5. **priority**: "Critical", "High", "Medium", or "Low"
    6. **category**: "Backend", "Frontend", "Database", "DevOps", "Design", "Testing", or "Documentation"
    7. **dependencies**: List of task titles that must be completed first (can be empty list)
    8. **technical_requirements**: Specific files, APIs, or technologies needed

    TASK CREATION RULES:
    - Break large features into multiple small tasks (4-16 hours each)
    - Each task should be completable by ONE person
    - Be specific - avoid vague language
    - Include setup, development, testing, and documentation tasks
    - Ensure tasks can be worked on in parallel when possible

    OUTPUT FORMAT - MUST be valid JSON only, no additional text:
    {{
        "tasks": [
            {{
                "title": "Setup Development Environment",
                "description": "Configure local environment with Node.js, React, PostgreSQL. Set up linting and Git hooks.",
                "acceptance_criteria": [
                    "All team members can run app locally",
                    "ESLint and Prettier configured",
                    "Git pre-commit hooks working"
                ],
                "effort_hours": 8,
                "priority": "Critical",
                "category": "DevOps",
                "dependencies": [],
                "technical_requirements": "Node.js 18+, PostgreSQL 14+, VS Code"
            }},
            {{
                "title": "Design Database Schema",
                "description": "Create PostgreSQL schema for users, projects, tasks. Include migrations and indexes.",
                "acceptance_criteria": [
                    "ER diagram created and reviewed",
                    "All tables created with proper indexes",
                    "Migration scripts tested"
                ],
                "effort_hours": 16,
                "priority": "Critical",
                "category": "Database",
                "dependencies": ["Setup Development Environment"],
                "technical_requirements": "PostgreSQL, Sequelize/Prisma ORM"
            }}
        ]
    }}

    CRITICAL: Return ONLY the JSON object. NO explanatory text before or after.
    Create 15-25 tasks minimum.
    """,
    agent=task_generator,
    expected_output="Valid JSON object with 'tasks' array containing 15-25 task objects, each with all 8 required fields. NO additional text."
)

timeline_planning_task = Task(
    description="""
    Create a project timeline with specific dates for all tasks.

    Task List: {{output from previous task}}

    Analyze the tasks and create a timeline that includes:

    1. **Start and End Dates**: Assign specific dates (YYYY-MM-DD) to each task
    2. **Sprint Organization**: Group tasks into 1-2 week sprints
    3. **Milestones**: Identify 5-8 key project milestones with dates
    4. **Critical Path**: List tasks that cannot be delayed

    SCHEDULING RULES:
    - Respect task dependencies (dependent tasks start after prerequisites)
    - Allow parallel work where tasks have no dependencies
    - Assume 6 productive hours per day per person
    - Add 15% buffer time for unknowns
    - project timeline: {project_timeline}


    OUTPUT FORMAT - Valid JSON only:
    {{
        "project_start_date": "2025-11-15",
        "project_end_date": "2026-01-31",
        "total_duration_days": 77,
        "sprints": [
            {{
                "sprint_number": 1,
                "sprint_name": "Foundation & Setup",
                "start_date": "2025-11-15",
                "end_date": "2025-11-29",
                "goal": "Complete environment setup and database design",
                "task_titles": ["Setup Development Environment", "Design Database Schema"]
            }}
        ],
        "milestones": [
            {{
                "name": "Development Environment Ready",
                "date": "2025-11-16",
                "deliverables": ["Local dev environment", "CI/CD pipeline"]
            }}
        ],
        "critical_path": ["Setup Development Environment", "Design Database Schema", "Implement Authentication"],
        "task_schedule": [
            {{
                "title": "Setup Development Environment",
                "start_date": "2025-11-15",
                "end_date": "2025-11-16",
                "assigned_sprint": 1
            }}
        ]
    }}

    CRITICAL: Return ONLY the JSON object. NO explanatory text.
    """,
    agent=timeline_planner,
    expected_output="Valid JSON object with project dates, sprints array, milestones array, critical_path array, and task_schedule array. NO additional text.",
    context=[task_generation_task]
)

task_assignment_task = Task(
    description="""
    Assign tasks to team members based on their skills and balance workload.

    Team Members: {team_members}
    Tasks: {{output from task_generation_task}}

    For each task, assign to the best team member considering:
    - Skill match (does their expertise align with task requirements?)
    - Workload balance (distribute hours evenly)
    - Dependencies (same person for related tasks = better continuity)

    Calculate team utilization:
    - Total hours per person
    - Utilization percentage (assume 6 productive hours/day)
    - Identify if anyone is over/under-utilized

    OUTPUT FORMAT - Valid JSON only:
    {{
        "assignments": [
            {{
                "task_title": "Setup Development Environment",
                "assigned_to": "Alice Johnson",
                "justification": "Full-stack developer with DevOps experience, familiar with Node.js and React setup",
                "backup_assignee": "Carol Chen"
            }}
        ],
        "team_utilization": [
            {{
                "member_name": "Alice Johnson",
                "role": "Full Stack Developer",
                "total_tasks": 8,
                "total_hours": 96,
                "utilization_percentage": 80,
                "workload_status": "Well Balanced"
            }}
        ],
        "skill_gaps": [
            {{
                "task_title": "Setup AWS Infrastructure",
                "missing_skill": "AWS DevOps",
                "recommendation": "Provide AWS training to Carol Chen or hire DevOps consultant"
            }}
        ]
    }}

    CRITICAL: Return ONLY the JSON object. NO explanatory text.
    Ensure EVERY task is assigned to someone.
    """,
    agent=task_assigner,
    expected_output="Valid JSON object with assignments array (one per task), team_utilization array, and skill_gaps array. NO additional text.",
    context=[task_generation_task, timeline_planning_task]
)

planning_synthesis_task = Task(
    description="""
    Consolidate ALL planning outputs into one comprehensive project plan.

    You have:
    1. Tasks with details (from task_generation_task)
    2. Timeline and sprints (from timeline_planning_task)
    3. Team assignments (from task_assignment_task)

    Create a COMPLETE consolidated plan that merges all information.

    OUTPUT FORMAT - Valid JSON only:
    {{
        "executive_summary": {{
            "project_name": "Extract from research",
            "total_tasks": 20,
            "total_estimated_hours": 320,
            "project_duration_days": 77,
            "project_start_date": "2025-11-15",
            "project_end_date": "2026-01-31",
            "number_of_sprints": 5,
            "team_size": 3,
            "key_milestones": 6
        }},
        "tasks": [
            {{
                "task_id": "T001",
                "title": "Setup Development Environment",
                "description": "Configure local dev environment...",
                "acceptance_criteria": ["Criterion 1", "Criterion 2"],
                "effort_hours": 8,
                "priority": "Critical",
                "category": "DevOps",
                "dependencies": [],
                "technical_requirements": "Node.js 18+, PostgreSQL",
                "assigned_to": "Alice Johnson",
                "assignment_justification": "Full-stack dev with DevOps experience",
                "start_date": "2025-11-15",
                "end_date": "2025-11-16",
                "sprint_number": 1,
                "status": "Not Started"
            }}
        ],
        "sprints": [
            {{
                "sprint_number": 1,
                "sprint_name": "Foundation & Setup",
                "start_date": "2025-11-15",
                "end_date": "2025-11-29",
                "goal": "Complete environment and database setup",
                "task_ids": ["T001", "T002"],
                "team_members": ["Alice Johnson", "Carol Chen"]
            }}
        ],
        "timeline": {{
            "project_start_date": "2025-11-15",
            "project_end_date": "2026-01-31",
            "total_duration_days": 77,
            "milestones": [
                {{
                    "name": "Development Environment Ready",
                    "date": "2025-11-16",
                    "deliverables": ["Local dev environment", "CI/CD pipeline"]
                }}
            ],
            "critical_path": ["T001", "T002", "T003"]
        }},
        "team_assignments": [
            {{
                "member_name": "Alice Johnson",
                "role": "Full Stack Developer",
                "assigned_task_ids": ["T001", "T003"],
                "total_tasks": 8,
                "total_hours": 96,
                "utilization_percentage": 80,
                "workload_status": "Well Balanced"
            }}
        ],
        "dependencies": [
            {{
                "task_id": "T002",
                "depends_on": ["T001"],
                "reason": "Database setup requires dev environment"
            }}
        ],
        "risks": [
            {{
                "category": "Skill Gap",
                "description": "No AWS expertise on team",
                "mitigation": "Provide AWS training or hire consultant",
                "priority": "Medium"
            }}
        ],
        "execution_instructions": {{
            "list_organization": "High priority tasks in 'To Do', others in 'Backlog'",
            "label_scheme": {{
                "priority_colors": {{
                    "Critical": "red",
                    "High": "orange",
                    "Medium": "yellow",
                    "Low": "green"
                }},
                "category_colors": {{
                    "Backend": "blue",
                    "Frontend": "purple",
                    "Database": "sky",
                    "DevOps": "lime",
                    "Testing": "pink",
                    "Documentation": "black"
                }}
            }},
            "checklist_creation": "Use acceptance_criteria array for checklist items",
            "special_notes": "Start with sprint 1 tasks in 'To Do', rest in 'Backlog'"
        }}
    }}

    CRITICAL REQUIREMENTS:
    1. Output ONLY valid JSON - NO explanatory text before or after
    2. Include ALL tasks from task_generation (don't skip any)
    3. Merge dates from timeline_planning into each task
    4. Merge assignments from task_assignment into each task
    5. Generate task IDs (T001, T002, etc.) for easy reference
    6. Ensure dates are consistent across all sections
    7. Every task must have start_date, end_date, and assigned_to

    This output will be used directly by the execution crew to create Trello cards.
    Make sure it's complete and properly formatted.
    """,
    agent=planning_synthesizer,
    expected_output="""Complete consolidated project plan in valid JSON format with:
    - executive_summary object
    - tasks array (15-25 tasks with ALL fields merged)
    - sprints array
    - timeline object
    - team_assignments array
    - dependencies array
    - risks array
    - execution_instructions object

    NO additional text outside the JSON object.""",
    context=[task_generation_task, timeline_planning_task, task_assignment_task]
)


# ================================ Crew ================================
planning_crew = Crew(
    agents=[task_generator, timeline_planner, task_assigner, planning_synthesizer],
    tasks=[task_generation_task, timeline_planning_task, task_assignment_task, planning_synthesis_task],
    verbose=True,
    memory=False,  # Disable memory for consistent behavior
    cache=False    # Disable cache for fresh execution
)
