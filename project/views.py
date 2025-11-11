from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import CreateProjectSerializer, updateProjectSerializer
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
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
