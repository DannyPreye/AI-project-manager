# Trello Integration Setup Guide

This integration uses the [trello-py package](https://github.com/tghw/trello-py) to interact with the Trello API.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `trello==0.9.7.3` (already in requirements.txt).

### 2. Get Trello API Credentials

1. Go to [https://trello.com/app-key](https://trello.com/app-key)
2. Copy your **API Key** (shown immediately on the page)
3. Click the "Token" link (or manually generate one using the `get_token_url` method)
4. Authorize the application and copy the generated **Token**

**Alternative - Generate Token URL Programmatically:**

```python
from integrations import TrelloIntegration

# Generate authorization URL
url = TrelloIntegration.get_token_url('My App', expires='30days', write_access=True)
print(url)
# Send your user to this URL to authorize and get their token
```

### 3. Set Environment Variables

Add these to your `.env` file:

```bash
# Existing vars
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# Add these for Trello
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_API_TOKEN=your_trello_api_token_here
TRELLO_WORKSPACE_ID=optional_workspace_id  # Optional
```

### 4. Test the Integration

Run the example:

```bash
python integrations/example_usage.py
```

## Adding Trello to Your Existing Crew

### Option 1: Add to Execution Crew

Create a new crew that handles Trello operations after planning:

```python
from integrations import create_trello_tools

# In your main.py or new execution_crew.py
create_board_tool, create_list_tool, create_card_tool = create_trello_tools()

trello_executor = Agent(
    role="Trello Execution Manager",
    goal="Create Trello boards and populate them with project tasks",
    backstory="Expert at translating project plans into actionable Trello boards",
    tools=[create_board_tool, create_list_tool, create_card_tool],
    llm=llm,
    verbose=True
)

trello_setup_task = Task(
    description="""
    Based on the project plan: {project_plan}
    And team members: {team_members}

    Create a Trello board with:
    1. Appropriate lists for project phases
    2. Cards for each deliverable and task
    3. Proper assignments to team members
    4. Due dates based on timeline
    """,
    agent=trello_executor,
    expected_output="Summary of created Trello board with all IDs"
)

execution_crew = Crew(
    agents=[trello_executor],
    tasks=[trello_setup_task],
    verbose=True
)
```

### Option 2: Integrate into Your Flow

Update your `main.py` flow:

```python
from integrations import create_trello_tools
from crews.research_crew import research_crew
from crews.planning_crew import planning_crew

class ProjectFlow(Flow):
    def __init__(self):
        super().__init__()
        # Initialize Trello tools
        self.create_board, self.create_list, self.create_card = create_trello_tools()

    @start()
    def get_project_data(self):
        # ... your existing code
        pass

    @listen(get_project_data)
    def run_research_crew(self, project_data):
        return research_crew.kickoff(project_data)

    @listen(run_research_crew)
    async def run_planning_crew(self, research_output):
        return await planning_crew.kickoff_async(
            inputs={
                "research_output": research_output.raw,
                "team_members": self.project_data["team_members"]
            }
        )

    @listen(run_planning_crew)
    def run_trello_setup(self, planning_output):
        """New step: Create Trello board from planning output"""
        from crewai import Agent, Task, Crew

        trello_executor = Agent(
            role="Trello Execution Manager",
            goal="Create Trello boards from project plans",
            backstory="Expert at setting up project management boards",
            tools=[self.create_board, self.create_list, self.create_card],
            llm=LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
            verbose=True
        )

        task = Task(
            description=f"""
            Create a Trello board based on this planning output:
            {planning_output.raw}

            Team: {self.project_data["team_members"]}
            Project: {self.project_data["project_name"]}
            Timeline: {self.project_data["project_timeline"]}
            """,
            agent=trello_executor,
            expected_output="Trello board summary with IDs"
        )

        crew = Crew(agents=[trello_executor], tasks=[task], verbose=True)
        return crew.kickoff()
```

## Troubleshooting

### Issue: "Authentication failed"
- Verify your TRELLO_API_KEY and TRELLO_API_TOKEN are correct
- Make sure the token hasn't expired (tokens don't expire by default, but can be revoked)
- Check that you've authorized the token with the necessary scopes

### Issue: "Board not found"
- Ensure the board_id is correct
- Check that your API token has access to the board
- Verify the board hasn't been deleted

### Issue: "Cannot add member"
- The email must be associated with an existing Trello account
- The member must not already be on the board
- You need proper permissions to add members

## API Rate Limits

Trello has rate limits:
- 300 requests per 10 seconds per API key
- 100 requests per 10 seconds per token

The integration includes error handling for rate limits.

## Next Steps

1. **Customize the tools** - Modify `trello_tool.py` to add more fields or functionality
2. **Add ClickUp** - Implement `clickup.py` following the same pattern as `trello.py`
3. **Add Jira** - Implement `jira.py` for Jira integration
4. **Enhance parsing** - Improve the parsing of team member assignments in get methods

## Support

For issues or questions:
- Trello API Documentation: https://developer.atlassian.com/cloud/trello/rest/
- CrewAI Documentation: https://docs.crewai.com/

