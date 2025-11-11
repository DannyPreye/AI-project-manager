from django.shortcuts import render
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from datetime import datetime, timedelta
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from .serializers import (
    RegisterUserSerializer,
    UpdateUserProfileSerializer,
    UserProfileSerializer,
    VerifyEmailSerializer,
    ResendVerificationEmailSerializer,
    RequestResetPasswordSerializer,
    ResetPasswordSerializer,
)

logger = logging.getLogger(__name__)

class RegisterUserView(APIView):
    "User registration view"
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user",
        operation_summary="Register a new user",
        request_body=RegisterUserSerializer,
        responses={
            201: openapi.Response("User registered successfully", RegisterUserSerializer),
            400: openapi.Response("Bad request", openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING),
            })),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Register a new user"""
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    "Verify email view"
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Verify email",
        operation_summary="Verify email",
        request_body=VerifyEmailSerializer,
        responses={
            200: openapi.Response("Email verified successfully", VerifyEmailSerializer),
            400: openapi.Response("Bad request", openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING),
            })),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Verify email"""
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestResetPasswordView(APIView):
    "Request reset password view"
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Request reset password",
        operation_summary="Request reset password",
        request_body=RequestResetPasswordSerializer,
        responses={
            200: openapi.Response("Reset password request sent successfully", RequestResetPasswordSerializer),
            400: openapi.Response("Bad request", openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING),
            })),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Request reset password"""
        serializer = RequestResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    "Reset password view"
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Reset password",
        operation_summary="Reset password",
        request_body=ResetPasswordSerializer,
        responses={
            200: openapi.Response("Password reset successfully", ResetPasswordSerializer),
            400: openapi.Response("Bad request", openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING),
            })),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Reset password"""
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationEmailView(APIView):
    "Resend verification email view"
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Resend verification email",
        operation_summary="Resend verification email",
        request_body=ResendVerificationEmailSerializer,
        responses={
            200: openapi.Response("Verification email resent successfully", ResendVerificationEmailSerializer),
            400: openapi.Response("Bad request", openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING),
            })),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Resend verification email"""
        serializer = ResendVerificationEmailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    "User profile view"
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Get user profile",
        operation_summary="Get user profile",
        responses={
            200: openapi.Response("User profile", UserProfileSerializer),
        },
    )
    def get(self, request):
        """Get user profile"""
        return Response(request.user, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update user profile",
        operation_summary="Update user profile",
        request_body=UpdateUserProfileSerializer,
        responses={
            200: openapi.Response("User profile updated successfully", UpdateUserProfileSerializer),
        },
    )
    def put(self, request):
        """Update user profile"""
        serializer = UpdateUserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
