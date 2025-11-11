from celery import shared_task
from .models import Project
from crews.main import run_flow




@shared_task
def create_project(project_id:str):
    project = Project.objects.get(id=project_id)
    result = run_flow(project)
    return result
