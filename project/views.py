from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from project.tasks import create_project
from .serializer import CreateProjectSerializer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.
class CreateProjectView(APIView):
    permission_classes = [IsAuthenticated]


    @swagger_auto_schema(
        operation_description="Create a new project",
        operation_summary="Create a new project",
        request_body=CreateProjectSerializer,
        responses={
            201: openapi.Response("Project created successfully", CreateProjectSerializer),
            400: openapi.Response("Bad request", openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING),
            })),
        },
        tags=["Project"],
    )
    def post(self, request):
        serializer = CreateProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()

            # Prepare project data for task (use request.data for write_only fields)
            timeline = request.data.get('timeline', {})
            project_data = {
                "project_name": project.name,
                "industry": project.industry,
                "description": project.description,
                "organization": str(project.organization.id),
                "team_members": request.data.get('team_members', []),
                "timeline": f"{timeline.get('start_date')} to {timeline.get('end_date')}"
            }

            try:
                # TODO: Run Celery task here if needed
                create_project.delay(str(project.id))
            except Exception as e:
                print(e)
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
