from crewai import Crew, Agent, Task, LLM
from dotenv import load_dotenv
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
import os

load_dotenv()

llm = LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))


# ================================ Agents ================================
task_generator = Agent(
    role="Task Breakdown Specialist",
    goal="Convert project analysis into highly detailed, actionable tasks with clear specifications",
    backstory="""You are a senior technical project manager with 15 years of experience breaking down
    complex projects into granular, executable tasks. You NEVER create vague tasks - every task you
    create has specific deliverables, clear acceptance criteria, and estimated effort. You think like
    a developer and understand what makes a task truly actionable.""",
    llm=llm,
    verbose=True,
)

timeline_planner = Agent(
    role="Timeline Architect",
    goal="Create realistic, detailed project schedules with specific dates and milestones",
    backstory="""Expert project scheduler who creates detailed timelines with specific start and end dates.
    You understand task dependencies, resource constraints, and critical path analysis. You always provide
    concrete dates and realistic time estimates based on team capacity.""",
    llm=llm,
    verbose=True,
)

task_assigner = Agent(
    role="Assignment Optimizer",
    goal="Match tasks to team members with clear justification and workload balancing",
    backstory="""Resource allocation expert who deeply analyzes team member skills, capacity, and
        workload to make optimal task assignments. You provide detailed reasoning for each assignment
        and ensure no team member is overloaded.""",
    llm=llm,
    verbose=True,
)

planning_synthesizer = Agent(
    role="Project Planning Synthesizer",
    goal="Consolidate all planning outputs into a comprehensive, execution-ready project plan",
    backstory="""You are a master project coordinator who excels at bringing together complex
    planning information into clear, actionable formats. You take outputs from task breakdown,
    timeline planning, and team assignments and synthesize them into a single, comprehensive
    project plan that anyone can follow. Your plans are known for being complete, well-organized,
    and immediately actionable. You ensure nothing is lost in translation and all critical
    information is preserved and easily accessible.""",
    llm=llm,
    verbose=True,
)

# ================================ Tasks ================================
task_generation_task = Task(
    description="""
                Based on the comprehensive research insights: {research_output}

                Break down the ENTIRE project into granular, actionable tasks. For EACH task, you MUST provide:

                1. **Task Title**: Clear, action-oriented (e.g., "Implement JWT Authentication Middleware", not "Authentication")

                2. **Detailed Description**:
                   - What exactly needs to be built/done
                   - Technical specifications and requirements
                   - Any specific technologies, libraries, or frameworks to use
                   - Edge cases to handle

                3. **Acceptance Criteria**:
                   - Minimum 3-5 specific, testable criteria
                   - Each criterion should be measurable (e.g., "API returns 401 for invalid tokens", not "works correctly")

                4. **Effort Estimate**:
                   - Provide in hours or days
                   - Consider complexity, unknowns, testing, and code review time

                5. **Priority**: Critical / High / Medium / Low with justification

                6. **Dependencies**:
                   - List specific tasks that must be completed first
                   - Explain why the dependency exists

                7. **Category/Phase**: (e.g., Backend, Frontend, Database, DevOps, Design, Testing)

                8. **Technical Requirements**:
                   - Specific files/modules to create or modify
                   - APIs to build or integrate
                   - Database schema changes needed

                IMPORTANT RULES:
                - Break large features into multiple small tasks (2-16 hours each)
                - Each task should be completable by ONE person
                - Be EXTREMELY specific - avoid vague language
                - Include setup tasks (environment, tools, dependencies)
                - Include testing tasks for each feature
                - Include documentation tasks
                - Include deployment/DevOps tasks

                Format output as a detailed JSON array with all fields for each task.
                """,
    agent=task_generator,
    expected_output="""Comprehensive JSON array of tasks, where each task contains:
                {title, description, acceptance_criteria[], effort_hours, priority, dependencies[],
                category, technical_requirements, assigned_to (leave empty for now)}.
                Minimum 20-50 detailed tasks covering all project phases.""",
)

timeline_planning_task = Task(
    description="""
                Based on the detailed task list from the previous step and the project timeline,
                create a comprehensive project schedule with specific dates.

                Your timeline MUST include:

                1. **Start and End Dates for EVERY Task**:
                   - Provide actual dates (YYYY-MM-DD format)
                   - Consider task dependencies - dependent tasks must start after prerequisites complete
                   - Account for parallel work where tasks can run concurrently

                2. **Sprint/Phase Breakdown**:
                   - Organize tasks into logical sprints or phases (typically 1-2 weeks each)
                   - Each sprint should have a clear goal/theme
                   - List all tasks in each sprint

                3. **Milestones**:
                   - Identify 5-10 key milestones (major deliverables or checkpoints)
                   - Provide specific dates for each milestone
                   - Describe what "done" looks like for each milestone

                4. **Critical Path Analysis**:
                   - Identify the critical path (longest chain of dependent tasks)
                   - Highlight tasks on the critical path that cannot be delayed
                   - Calculate total project duration

                5. **Resource Allocation Timeline**:
                   - Show how many team members are needed during each phase
                   - Identify potential bottlenecks or periods of high resource demand

                6. **Buffer Time**:
                   - Include buffer time for unknowns (typically 15-20% of task estimates)
                   - Mark buffer periods explicitly in the timeline

                IMPORTANT: Use the project deadline from the research to work backwards.
                Be realistic about how much can be accomplished in the given timeframe.
                """,
    agent=timeline_planner,
    expected_output="""Detailed project timeline in JSON format with:
                {sprints: [{sprint_name, start_date, end_date, tasks[], goal}],
                milestones: [{name, date, deliverables[]}],
                critical_path: [task_ids],
                project_start_date,
                project_end_date,
                total_duration_days}""",
    context=[task_generation_task],
)

task_assignment_task = Task(
    description="""
                Assign every task to the most appropriate team member(s) based on their skills and capacity.

                Team Members Available: {team_members}

                For EACH task, you must:

                1. **Analyze Skill Match**:
                   - Review the task's technical requirements
                   - Match with team member skills
                   - Assign to the team member with the best skill match

                2. **Consider Workload Balance**:
                   - Calculate total hours assigned to each team member
                   - Ensure no one is overloaded (typically max 6 productive hours/day)
                   - Distribute work evenly when possible

                3. **Respect Dependencies**:
                   - If tasks are dependent, consider assigning to same person for continuity
                   - OR ensure clear handoff documentation between team members

                4. **Account for Skill Gaps**:
                   - If a task requires skills no one has, flag it
                   - Suggest either training time or external help

                5. **Provide Assignment Justification**:
                   - Explain WHY you chose this person
                   - What specific skills make them suitable
                   - Any concerns or risks with the assignment

                6. **Calculate Team Member Utilization**:
                   - For each team member, show: total tasks, total hours, utilization %
                   - Flag if anyone is under-utilized or over-utilized

                Output Format: JSON with complete task assignments plus team utilization summary.
                """,
    agent=task_assigner,
    expected_output="""JSON containing:
                {assigned_tasks: [{task_id, task_title, assigned_to, justification, backup_assignee}],
                team_utilization: [{member_name, total_tasks, total_hours, utilization_percentage, workload_status}],
                skill_gaps: [{task_id, missing_skill, recommendation}],
                assignment_risks: [any concerns about assignments]}""",
    context=[task_generation_task, timeline_planning_task],
)

planning_synthesis_task = Task(
    description="""
                Consolidate ALL planning outputs into a single, comprehensive, execution-ready project plan.

                You have outputs from:
                1. Task Generation (detailed task breakdown)
                2. Timeline Planning (schedule and milestones)
                3. Task Assignment (team assignments and utilization)

                Create a COMPLETE consolidated plan that includes:

                ## 1. EXECUTIVE SUMMARY
                - Project overview
                - Total tasks count
                - Total estimated effort (hours/days)
                - Project duration (start to end date)
                - Number of sprints/phases
                - Key milestones
                - Team size and composition
                - Critical success factors

                ## 2. COMPLETE TASK LIST
                For EACH task, consolidate and provide:
                - Task ID (unique identifier)
                - Task Title
                - Full Description
                - Acceptance Criteria (all items)
                - Effort Estimate (hours)
                - Priority Level (Critical/High/Medium/Low)
                - Category/Phase
                - Technical Requirements
                - Dependencies (list of task IDs)
                - Assigned To (team member name and email)
                - Assignment Justification
                - Start Date (YYYY-MM-DD)
                - End Date (YYYY-MM-DD)
                - Sprint/Phase number
                - Status (default: "Not Started")

                ## 3. SPRINT/PHASE BREAKDOWN
                For each sprint/phase:
                - Sprint Number/Name
                - Start Date
                - End Date
                - Sprint Goal/Theme
                - List of Task IDs in this sprint
                - Team members involved
                - Key deliverables

                ## 4. TIMELINE & MILESTONES
                - Project start date
                - Project end date
                - Total duration (days/weeks)
                - All milestones with dates
                - Critical path task IDs
                - Buffer periods

                ## 5. TEAM ASSIGNMENTS & UTILIZATION
                For each team member:
                - Name and role
                - Assigned task IDs
                - Total tasks assigned
                - Total estimated hours
                - Utilization percentage
                - Workload status
                - Key responsibilities

                ## 6. DEPENDENCIES MAP
                - List all task dependencies
                - Identify which tasks block others
                - Highlight critical path items

                ## 7. RISKS & CONSIDERATIONS
                - Assignment risks
                - Skill gaps
                - Timeline risks
                - Dependency risks
                - Mitigation recommendations

                ## 8. EXECUTION INSTRUCTIONS
                Provide clear instructions for the execution crew:
                - How tasks should be organized in Trello lists
                - Which tasks should go in which list initially
                - Label scheme recommendations (priority colors, type labels)
                - Checklist items to add to each card
                - Any special notes or considerations

                IMPORTANT:
                - Include ALL tasks from task generation (don't skip any)
                - Ensure dates are consistent between sections
                - Verify all assignments are included
                - Double-check that dependencies reference valid task IDs
                - Format as well-structured JSON or Markdown
                - This output will be used directly by the execution crew to create Trello cards

                The execution crew will use this EXACT output to:
                1. Create Trello lists
                2. Create cards for each task
                3. Add checklists from acceptance criteria
                4. Assign team members
                5. Set due dates
                6. Create and apply labels
                7. Organize cards into appropriate lists

                Make sure EVERY piece of information needed for execution is included and clearly formatted.
                """,
    agent=planning_synthesizer,
    expected_output="""Complete, consolidated project plan in JSON format with ALL sections:
                {
                    "executive_summary": {summary data},
                    "tasks": [complete array of all tasks with all fields],
                    "sprints": [sprint breakdown with task IDs],
                    "timeline": {dates, milestones, critical_path},
                    "team_assignments": [team member data with assignments],
                    "dependencies": [dependency mapping],
                    "risks": [all identified risks],
                    "execution_instructions": {guidance for execution crew}
                }

                This must be complete, well-formatted, and ready for immediate use by the execution crew.
                Minimum 20-50 tasks with complete details for each.""",
    context=[task_generation_task, timeline_planning_task, task_assignment_task],
)


# ================================ Crew ================================
planning_crew = Crew(
    agents=[task_generator, timeline_planner, task_assigner, planning_synthesizer],
    tasks=[task_generation_task, timeline_planning_task, task_assignment_task, planning_synthesis_task],
    verbose=True,
)
