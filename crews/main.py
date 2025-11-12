import asyncio
from crewai.flow import Flow, start, listen
from pydantic import BaseModel
from typing import Optional

from .research_crew import research_crew
from .planning_crew import planning_crew
from .execution_crew import execution_crew

# Import Trello integration for board creation
from integrations.trello import TrelloIntegration, TeamMember

class ProjectData(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    project_timeline: Optional[str] = None
    industry: Optional[str] = None
    team_members: Optional[list[dict]] = None
    board_id: Optional[str] = None
class ProJectFlow(Flow[ProjectData]):

    @start()
    def get_project_data(self):

        project_data = {
            "project_name": self.state.project_name,
            "project_description": self.state.project_description,
            "project_timeline": self.state.project_timeline,
            "industry": self.state.industry,
            "team_members": self.state.team_members
        }

        # TODO: Get project from database later on
        self.project_data = project_data
        return self.project_data

    @listen(get_project_data)
    def run_research_crew(self, project_data):
        print("Running research crew", project_data)
        return research_crew.kickoff(project_data)

    @listen(run_research_crew)
    async def run_planning_crew(self, research_output):
        print("Running planning crew")
        planning_result = await planning_crew.kickoff_async(
            inputs={
                "research_output": research_output.raw,
                "team_members": self.project_data["team_members"],
                "project_timeline": self.project_data["project_timeline"],
            }
        )
        self.planning_output = planning_result.raw
        return planning_result

    @listen(run_planning_crew)
    def create_trello_board(self, planning_output):
        """Create the Trello board before agents start adding cards"""
        print("Creating Trello board...")

        # Initialize Trello integration
        trello = TrelloIntegration()

        # Convert team members to TeamMember objects
        team_members = [
            TeamMember(
                name=member["name"],
                email=member["email"],
                role=member["role"],
                skills=member["skills"]
            )
            for member in self.project_data["team_members"]
        ]

        # Create the board
        board = trello.create_board(
            board_name=self.project_data["project_name"],
            description=self.project_data["project_description"],
            team_members=team_members
        )

        board_id = board["id"]
        print(f"✅ Trello board created with ID: {board_id}")

        # Store board_id for use in execution crew
        self.board_id = board_id

        return {
            "board_id": board_id,
            "board_name": self.project_data["project_name"]
        }

    @listen(create_trello_board)
    def run_execution_crew(self, board_info):
        """Run the execution crew to populate the Trello board"""
        print("Running execution crew to set up Trello board...")

        execution_result = execution_crew.kickoff(
            inputs={
                "project_name": self.project_data["project_name"],
                "board_id": board_info["board_id"],
                "planning_output": self.planning_output,
                "team_members": self.project_data["team_members"],
                "list_ids": {}  # Will be populated by the first task
            }
        )

        return execution_result


async def run_flow(project_data:dict):
    # print("Running flow", project_data)
    flow = ProJectFlow()
    result = await flow.kickoff_async(inputs={
        "project_name": project_data["project_name"],
        "project_description": project_data["project_description"],
        "project_timeline": project_data["project_timeline"],
        "industry": project_data["industry"],
        "team_members": project_data["team_members"]
    })
    print(result)


if __name__ == "__main__":
    project_data = {
        "project_name": "AI Agentic Project Management System",
        "project_description": "A web application that uses AI agents to manage projects",
        "project_timeline": "2025-01-01 to 2025-12-31",  #,
        "industry": "AI",
        "team_members": [
            {"name": "John Doe", "email": "john.doe@example.com",
            "role": "Project Manager",
            "skills": ["nextjs", "react", "tailwind", "typescript", "python", "django", "postgres", "redis", "rabbitmq", "docker", "kubernetes"],
            "trello_member_id": "1234567890"
            },
            {"name": "Jane Doe", "email": "jane.doe@example.com",
            "role": "Frontend Developer",
            "skills": ["nextjs", "react", "tailwind", "typescript"],
            "trello_member_id": "1234567890"
            },
            {"name": "Jim Doe", "email": "jim.doe@example.com",
            "role": "Backend Developer",
            "skills": [ "python", "django", "postgres", "redis", "rabbitmq", "docker", "kubernetes", "langchain", "openai", "anthropic", "google", "azure", "aws"],
            "trello_member_id": "1234567890"
            },
            {"name": "Jill Doe", "email": "jill.doe@example.com",
            "role":"Quality Assurance Engineer",
            "skills":["pytest", "pytest-django", "pytest-asyncio", "pytest-mock", "pytest-cov", "pytest-sugar", "pytest-xdist", "pytest-timeout", "pytest-mock", "pytest-asyncio", "pytest-cov", "pytest-sugar", "pytest-xdist", "pytest-timeout"],
            "trello_member_id": "1234567890"
            },
            {"name": "Jack Doe", "email": "jack.doe@example.com",
            "role":"DevOps Engineer",
            "skills":["docker", "kubernetes", "langchain", "openai", "anthropic", "google", "azure", "aws"],
            "trello_member_id": "1234567890"
            },

        ]
    }
    asyncio.run(run_flow(project_data=project_data))
