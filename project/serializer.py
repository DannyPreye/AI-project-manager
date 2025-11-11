from rest_framework import serializers

from integrations.trello import TrelloIntegration
from .models import Project, ProjectMember, ProjectTList, ProjectCard

trello_integration = TrelloIntegration()

class CreateProjectSerializer(serializers.ModelSerializer):
    team_members = serializers.ListField(child=serializers.DictField())
    def validate_team_members(self, value):
        for member in value:
            if 'name' not in member:
                raise serializers.ValidationError("Name is required")
            if 'email' not in member:
                raise serializers.ValidationError("Email is required")
            if 'role' not in member:
                raise serializers.ValidationError("Role is required")
    class Meta:
        model = Project
        fields = '__all__'
    def create(self, validated_data):

        board = trello_integration.create_board(validated_data['name'], validated_data['description'], validated_data['team_members'])
        invite_team_members = trello_integration.invite_team_members(board.id, validated_data['team_members'])
        project = Project.objects.create(
            name=validated_data['name'],
            description=validated_data['description'],
            organization=validated_data['organization'],
            trello_board_id=board.id
        )
        return project


# class updateProjectSerializer(serializers.ModelSerializer):
