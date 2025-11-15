import asyncio
from celery import shared_task
from .models import Project, ProjectMember
from crews.main import run_flow




@shared_task
def create_project(project_id: str):
    project = Project.objects.get(id=project_id)
    team_members = ProjectMember.objects.filter(project=project)

    # Convert QuerySet to list of dicts for serialization
    team_members_list = [
        {
            "name": member.name,
            "email": member.email,
            "role": member.role,
            "skills": member.skills,
            "trello_member_id": member.trello_member_id
        }
        for member in team_members
    ]

    project_data = {
    "project_name": project.name,
    "industry": project.industry,
    "project_description": project.description,  # Changed from "description"
    "team_members": team_members_list,
    "project_timeline": f"{project.start_date} to {project.end_date}",
    "board_id": project.trello_board_id,
    "project_id": str(project.id)
}

    # Use asyncio.run() to properly execute the async function
    result = asyncio.run(run_flow(project_data))

    # Make sure to return a JSON-serializable result
    return {
        "status": "success",
        "project_id": str(project.id),
        "result": str(result)  # Convert result to string if needed
    }
