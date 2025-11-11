# AI Project Manager Crews - Complete Workflow

This system uses multiple AI crews to research, plan, and execute project management tasks, automatically creating structured Trello boards.

## 🚀 Complete Workflow

### Flow Overview

```
Project Data → Research Crew → Planning Crew → Trello Board Creation → Execution Crew → Complete Trello Board
```

## 📋 Crews

### 1. **Research Crew** (`research_crew.py`)

**Purpose:** Conduct comprehensive research on the project

**Agents:**
- `industry_researcher` - Market research and competitive analysis
- `project_analyzer` - Project scope and technical architecture analysis
- `team_assessor` - Team capability assessment
- `project_research_summarize` - Synthesizes all research into comprehensive report

**Output:** 3000-5000 word comprehensive research report including:
- Industry analysis
- Project scope with 10-30 deliverables
- 15-25 risks with mitigation strategies
- Team assessment
- Resource requirements

---

### 2. **Planning Crew** (`planning_crew.py`)

**Purpose:** Transform research into detailed, actionable project plans

**Agents:**
- `task_generator` - Breaks down project into granular tasks (20-50 tasks)
- `timeline_planner` - Creates detailed schedule with dates and milestones
- `task_assigner` - Assigns tasks to team members based on skills

**Output:** Detailed project plan with:
- 20-50 specific tasks with acceptance criteria
- Timeline with specific dates
- Task assignments with justifications
- Team utilization analysis

---

### 3. **Execution Crew** (`execution_crew.py`) ✨ NEW

**Purpose:** Create and populate Trello boards based on project plan

**Agents:**
- `trello_board_manager` - Creates board structure and lists
- `trello_task_manager` - Creates detailed cards with checklists
- `trello_workflow_organizer` - Organizes cards and optimizes workflow

**Tools Used:** All 17 Trello tools from `integrations/trello_tool.py`

**Output:** Fully populated Trello board with:
- Organized workflow lists (Backlog, To Do, In Progress, Review, Testing, Done)
- Detailed cards for each task
- Checklists with acceptance criteria
- Labels for priority and type
- Team member assignments
- Due dates

---

## 🔄 Main Flow (`main.py`)

### Flow Steps

```python
class ProJectFlow(Flow[ProjectData]):

    @start()
    def get_project_data(self):
        # Extract project data from state

    @listen(get_project_data)
    def run_research_crew(self, project_data):
        # Run comprehensive research

    @listen(run_research_crew)
    async def run_planning_crew(self, research_output):
        # Create detailed project plan

    @listen(run_planning_crew)
    def create_trello_board(self, planning_output):
        # Create empty Trello board and invite team

    @listen(create_trello_board)
    def run_execution_crew(self, board_info):
        # Populate board with lists, cards, checklists, labels
```

---

## 🛠️ Trello Integration

### Setup Required

1. **Environment Variables** (`.env`):
```bash
TRELLO_API_KEY=your_api_key
TRELLO_API_TOKEN=your_api_token
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key
```

2. **Get Trello Credentials**:
   - Go to https://trello.com/app-key
   - Copy your API Key
   - Generate a Token

### What Gets Created

1. **Board Structure:**
   ```
   Board: [Project Name]
   ├── Backlog
   ├── To Do
   ├── In Progress
   ├── Code Review
   ├── Testing
   └── Done
   ```

2. **For Each Task:**
   - **Card** with detailed description
   - **Checklist** with acceptance criteria
   - **Labels** for priority (red/orange/yellow/green) and type (blue/purple/sky)
   - **Assignee** based on skills match
   - **Due date** from timeline
   - **Comments** with technical requirements

---

## 📊 Available Trello Tools

The execution crew has access to **17 Trello tools**:

### Board & List Management
- Create lists
- Update lists
- Delete lists

### Card Management
- Create cards with description, assignees, due dates
- Update cards
- Delete cards
- Move cards between lists

### Checklist Management
- Create checklists on cards
- Update checklist names
- Delete checklists
- Add items to checklists

### Label Management
- Create labels with colors
- Update labels
- Delete labels
- Add labels to cards
- Remove labels from cards

---

## 🎯 Usage

### Run the Complete Flow

```bash
python crews/main.py
```

### What Happens:

1. **Research Phase** (~5-10 minutes)
   - Industry research with web search
   - Project analysis
   - Team assessment
   - Comprehensive report generation

2. **Planning Phase** (~5-10 minutes)
   - Task breakdown (20-50 tasks)
   - Timeline creation
   - Task assignments

3. **Board Creation** (~1 minute)
   - Empty board created
   - Team members invited

4. **Execution Phase** (~10-20 minutes)
   - Lists created (6 standard lists)
   - Cards created for each task (20-50 cards)
   - Checklists added to cards
   - Labels created and applied
   - Cards organized into appropriate lists

**Total Time:** ~20-40 minutes

**Result:** Fully populated Trello board ready for team to start work!

---

## 📝 Example Project Data

```python
project_data = {
    "project_name": "AI Agentic Project Management System",
    "project_description": "A web application that uses AI agents to manage projects",
    "project_timeline": "2025-01-01 to 2025-12-31",
    "industry": "AI",
    "team_members": [
        {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "Project Manager",
            "skills": ["nextjs", "react", "python", "django"],
            "trello_member_id": "optional"
        },
        # ... more team members
    ]
}
```

---

## 🔧 Customization

### Modify Board Structure

Edit `execution_crew.py` → `create_board_structure_task`:

```python
# Add custom lists
1. Create workflow lists on the board in this exact order:
   - Your Custom List 1
   - Your Custom List 2
   - etc.
```

### Modify Label Scheme

Edit `execution_crew.py` → `create_tasks_cards_task`:

```python
6. **Labels**: Create and add labels for:
   - Your custom label scheme
```

### Add More Task Details

Edit `execution_crew.py` agents' backstories and task descriptions to include additional information you want in cards.

---

## 🎨 Output Example

After running, you'll have a Trello board like:

```
📋 AI Agentic Project Management System

Backlog (15)
├── 📝 Implement advanced AI features [Medium] [Feature]
├── 📝 Add analytics dashboard [Low] [Feature]
└── ...

To Do (10)
├── 🔥 Set up project infrastructure [Critical] [Feature]
│   ├── ☐ Set up GitHub repository
│   ├── ☐ Configure CI/CD pipeline
│   └── ☐ Set up development environment
├── 🔥 Design database schema [High] [Feature]
└── ...

In Progress (0)

Code Review (0)

Testing (0)

Done (0)
```

---

## 🐛 Troubleshooting

### "Trello API Error"
- Check your `TRELLO_API_KEY` and `TRELLO_API_TOKEN` in `.env`
- Verify token hasn't expired

### "Team member not found"
- Ensure email addresses match Trello accounts
- Team members must have Trello accounts to be invited

### "Too many API calls"
- Trello has rate limits (300 requests/10 seconds)
- The crew automatically handles this, but very large projects may need to wait

### "Cards not created"
- Check that board_id is being passed correctly
- Verify planning output contains tasks in expected format
- Check agent logs for specific errors

---

## 📚 Next Steps

1. **Run the flow** with your project data
2. **Access your Trello board** using the board ID printed in output
3. **Review and adjust** cards as needed
4. **Start working!** Your team can now pick up tasks from "To Do"

---

## 🚀 Future Enhancements

- [ ] Add ClickUp integration
- [ ] Add Jira integration
- [ ] Add GitHub Issues integration
- [ ] Support multiple boards per project
- [ ] Add sprint planning automation
- [ ] Add time tracking integration
- [ ] Add progress reporting
- [ ] Add AI-powered task suggestions

---

## 📄 License

[Your License Here]

## 🤝 Contributing

[Your Contributing Guidelines Here]

