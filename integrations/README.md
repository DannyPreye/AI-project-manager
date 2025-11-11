# Project Management Integrations

This package provides integrations with project management tools like Trello, with support for ClickUp and Jira coming soon.

Built with the [trello-py package](https://github.com/tghw/trello-py) for reliable Trello API interaction.

## Setup

### Trello Setup

1. **Get your Trello API credentials:**
   - Go to https://trello.com/app-key
   - Copy your API Key
   - Click "Token" link or use `TrelloIntegration.get_token_url()` to generate authorization URL
   - Generate a Token

2. **Set environment variables:**
   ```bash
   export TRELLO_API_KEY="your_api_key_here"
   export TRELLO_API_TOKEN="your_api_token_here"
   export TRELLO_WORKSPACE_ID="optional_workspace_id"  # Optional
   ```

   Or create a `.env` file:
   ```
   TRELLO_API_KEY=your_api_key_here
   TRELLO_API_TOKEN=your_api_token_here
   TRELLO_WORKSPACE_ID=optional_workspace_id
   ```

## Usage

### Basic Usage (Direct API)

```python
from integrations import TrelloIntegration, TeamMember

# Initialize Trello
trello = TrelloIntegration(
    api_key="your_api_key",
    api_token="your_api_token"
)

# Create a project board
team_members = [
    TeamMember(
        name="John Doe",
        email="john@example.com",
        role="Developer",
        skills=["Python", "JavaScript"]
    )
]

board_id = trello.create_project(
    project_name="My Awesome Project",
    project_description="Building something great!",
    project_timeline="2025-11-10 to 2026-01-01",
    team_members=team_members
)

# Create lists
todo_list_id = trello.create_list(board_id, "To Do")
in_progress_id = trello.create_list(board_id, "In Progress")
done_list_id = trello.create_list(board_id, "Done")

# Create cards
assignee = TeamMember(
    name="John Doe",
    email="john@example.com",
    role="Developer",
    skills=["Python"]
)

card_id = trello.create_card(
    list_id=todo_list_id,
    card_name="Implement user authentication",
    card_description="Add JWT-based authentication system",
    card_due_date="2025-12-01",
    card_assignee=assignee
)
```

### Usage with CrewAI Agents

#### Option 1: Use All Tools

```python
from crewai import Agent, Task, Crew
from integrations import get_all_trello_tools

# Create an agent with all Trello tools
project_manager = Agent(
    role="Project Manager",
    goal="Set up project boards and organize tasks in Trello",
    backstory="Expert at project organization and task management",
    tools=get_all_trello_tools(),  # Includes all 17 tools
    verbose=True
)

# Create a task
setup_task = Task(
    description="""
    Create a Trello board for the project 'E-commerce Platform'.
    Create lists: 'To Do', 'In Progress', 'Review', 'Done'.
    Add cards with checklists and labels for priority.
    """,
    agent=project_manager,
    expected_output="Trello board structure with all IDs"
)

# Run the crew
crew = Crew(
    agents=[project_manager],
    tasks=[setup_task]
)

result = crew.kickoff()
print(result)
```

#### Option 2: Use Essential Tools Only

```python
from integrations import get_essential_trello_tools

# Create an agent with only essential tools (6 basic tools)
simple_manager = Agent(
    role="Project Setup Manager",
    goal="Create basic Trello board structure",
    backstory="Focused on core project setup tasks",
    tools=get_essential_trello_tools(),  # Only board, list, card, move, checklist tools
    verbose=True
)
```

#### Option 3: Use Specific Tools

```python
from integrations import (
    TrelloCreateBoardTool,
    TrelloCreateListTool,
    TrelloCreateCardTool,
    TrelloMoveCardTool
)

# Create an agent with specific tools
task_manager = Agent(
    role="Task Manager",
    goal="Manage task cards only",
    backstory="Specialized in task management",
    tools=[
        TrelloCreateCardTool(),
        TrelloMoveCardTool(),
    ],
    verbose=True
)
```

### Integration in Your Flow

```python
from crewai.flow import Flow, start, listen
from integrations import create_trello_tools

class ProjectFlow(Flow):
    def __init__(self):
        super().__init__()
        # Initialize Trello tools
        self.create_board, self.create_list, self.create_card = create_trello_tools()

    @start()
    def setup_project(self):
        # Your project setup logic
        pass

    @listen(setup_project)
    def create_trello_board(self, project_data):
        # Agent with Trello tools can create board and tasks
        pass
```

## Available Tools

### All 17 Trello Tools

**Board Management:**
- `TrelloCreateBoardTool` - Create a new board with team members

**List Management:**
- `TrelloCreateListTool` - Create a new list on a board
- `TrelloUpdateListTool` - Update list name
- `TrelloDeleteListTool` - Delete a list

**Card Management:**
- `TrelloCreateCardTool` - Create a new card with description, assignees, and due date
- `TrelloUpdateCardTool` - Update card details
- `TrelloDeleteCardTool` - Delete a card
- `TrelloMoveCardTool` - Move card between lists

**Checklist Management:**
- `TrelloCreateChecklistTool` - Create a checklist on a card
- `TrelloUpdateChecklistTool` - Update checklist name
- `TrelloDeleteChecklistTool` - Delete a checklist
- `TrelloAddChecklistItemTool` - Add item to checklist

**Label Management:**
- `TrelloCreateLabelTool` - Create a label with color
- `TrelloUpdateLabelTool` - Update label name/color
- `TrelloDeleteLabelTool` - Delete a label
- `TrelloAddLabelToCardTool` - Add label to card
- `TrelloRemoveLabelFromCardTool` - Remove label from card

### Convenience Functions

- `get_all_trello_tools()` - Returns all 17 tools
- `get_essential_trello_tools()` - Returns 6 essential tools (board, list, card, move, checklist basic operations)

## API Reference

### TrelloIntegration

#### Methods

- **`create_project(project_name, project_description, project_timeline, team_members)`**
  - Creates a new Trello board
  - Returns: `board_id` (str)

- **`create_list(project_id, list_name)`**
  - Creates a new list on a board
  - Returns: `list_id` (str)

- **`create_card(list_id, card_name, card_description, card_due_date, card_assignee)`**
  - Creates a new card on a list
  - Returns: `card_id` (str)

- **`get_project(project_id)`**
  - Gets board details
  - Returns: `Project` object

- **`get_list(list_id)`**
  - Gets list details with cards
  - Returns: `List` object

- **`get_card(card_id)`**
  - Gets card details
  - Returns: `Card` object

- **`add_member_to_board(board_id, member_email)`**
  - Adds a member to the board
  - Returns: `bool`

- **`add_label_to_card(card_id, label_name, color)`**
  - Adds a label to a card
  - Returns: `label_id` (str)

## Future Integrations

- **ClickUp** - Coming soon
- **Jira** - Coming soon

To add a new integration, extend the `Integration` abstract class in `integrations/index.py` and implement all abstract methods.

## Requirements

```bash
pip install requests pydantic crewai crewai-tools
```

