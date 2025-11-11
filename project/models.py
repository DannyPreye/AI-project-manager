from django.db import models
from uuid import uuid4

from organization.models import Organization
# Create your models here.

class Project(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    trello_board_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.organization.name}"
    def get_trello_board_id(self):
        return self.trello_board_id
    def set_trello_board_id(self, trello_board_id):
        self.trello_board_id = trello_board_id
        self.save()

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    role = models.CharField(max_length=255)
    skills = models.JSONField(default=list)
    trello_member_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.project.name}"
    def get_trello_member_id(self):
        return self.trello_member_id
    def set_trello_member_id(self, trello_member_id):
        self.trello_member_id = trello_member_id
        self.save()

class ProjectTList(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    trello_list_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.project.name}"
    def get_trello_list_id(self):
        return self.trello_list_id
    def set_trello_list_id(self, trello_list_id):
        self.trello_list_id = trello_list_id
        self.save()

class ProjectCard(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    trello_card_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.project.name}"
    def get_trello_card_id(self):
        return self.trello_card_id
