from rest_framework import serializers

from integrations.trello import TrelloIntegration
from organization.models import Organization
from .models import Project, ProjectMember, ProjectTList, ProjectCard
from pydantic import BaseModel
from django.utils import timezone

trello_integration = TrelloIntegration()

class TeamMemberSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    role = serializers.CharField(required=True)
    skills = serializers.ListField(child=serializers.CharField(), required=True)

class TimelineSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    def validate_start_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Start date cannot be in the past")
        return value
    def validate_end_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("End date cannot be in the past")
        return value

class CreateProjectSerializer(serializers.ModelSerializer):
    team_members = serializers.ListField(child=TeamMemberSerializer(), write_only=True)
    organization_id = serializers.CharField(required=True)
    timeline = TimelineSerializer(required=True, write_only=True)
    def validate_team_members(self, value):
        for member in value:
            if 'name' not in member:
                raise serializers.ValidationError("Name is required")
            if 'email' not in member:
                raise serializers.ValidationError("Email is required")
            if 'role' not in member:
                raise serializers.ValidationError("Role is required")
            if 'skills' not in member:
                raise serializers.ValidationError("Skills are required")
        return value
    def validate_organization_id(self, value):
        if not Organization.objects.filter(id=value).exists():
            raise serializers.ValidationError("Organization not found")
        return value
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'industry', 'team_members', 'timeline', "trello_board_id", "organization_id"]
    def create(self, validated_data):
        # Extract non-model fields
        team_members_data = validated_data.pop('team_members', [])
        timeline_data = validated_data.pop('timeline')
        organization_id = validated_data.pop('organization_id')

        print("validated data: ______", validated_data)
        print("team members: ______", team_members_data)
        print("timeline: ______", timeline_data)

        # Create Trello board
        board = trello_integration.create_board(
            validated_data['name'],
            validated_data['description'],
            team_members_data
        )

        # Invite team members to board
        invite_team_members = trello_integration.invite_team_members(board['id'], team_members_data)

        # Get organization
        organization = Organization.objects.get(id=organization_id)

        # Create project
        project = Project.objects.create(
            name=validated_data['name'],
            description=validated_data['description'],
            organization=organization,
            industry=validated_data.get('industry'),
            start_date=timeline_data['start_date'],
            end_date=timeline_data['end_date'],
            trello_board_id=board['id']
        )

        # Optionally: Save team members to ProjectMember model
        for member_data in team_members_data:
            ProjectMember.objects.create(
                project=project,
                name=member_data['name'],
                email=member_data['email'],
                role=member_data['role'],
                skills=member_data['skills']
            )

        return project


# class updateProjectSerializer(serializers.ModelSerializer):
