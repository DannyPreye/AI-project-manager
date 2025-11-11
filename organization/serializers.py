from time import timezone
import uuid
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Organization, OrganizationMember, UserToken, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import EmailMessage


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_verified': self.user.is_verified,
            'organization': self.user.organization.id if self.user.organization else None,
        }

        return data

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    organization_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', "first_name", "last_name", "organization_name", 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        organization = Organization.objects.create(name=validated_data['organization_name'])
        organization.admin = user
        organization.save()
        user.organization = organization
        user.save()
        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    def validate_code(self, value):
        if UserToken.objects.filter(email=self.context['email'], token=value).exists():
            user_token = UserToken.objects.get(email=self.context['email'], token=value)
            if user_token.expires_at < timezone.now():
                raise serializers.ValidationError("Code has expired")
            if user_token.is_validated:
                raise serializers.ValidationError("Code has already been used")
            return value
        else:
            raise serializers.ValidationError("Invalid code")


    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        user.is_verified = True
        user.save()
        # delete the user token
        UserToken.objects.filter(email=validated_data['email'], token=validated_data['code']).delete()
        return user


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email does not exist")
        return value
    def validate_user(self, value):
        if value.is_verified:
            raise serializers.ValidationError("Email is already verified")
        return value

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        if user.is_verified:
            raise serializers.ValidationError("Email is already verified")
        new_token = UserToken.objects.create(user=user, token=uuid.uuid4())
        verification_url = f"http://localhost:3000/verify-email/{new_token.token}"

        # send the verification email to the user
        self.send_verification_email(user, verification_url)

    def send_verification_email(self, user, verification_url):
        # send a verification email to the user using the email backend
        email = EmailMessage(
            'Verify your email',
            'Click here to verify your email: ' + verification_url,
            'noreply@example.com',
            [user.email],
        )
        email.send()
        return user

class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email does not exist")
        return value
    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        new_token = UserToken.objects.create(user=user, token=uuid.uuid4())
        verification_url = f"http://localhost:3000/reset-password/{new_token.token}"
        # send the verification email to the user
        self.send_verification_email(user, verification_url)
        return user
    def send_verification_email(self, user, verification_url):
        # send a verification email to the user using the email backend
        email = EmailMessage(
            'Reset your password',
            'Click here to reset your password: ' + verification_url,
            'noreply@example.com',
            [user.email],
        )
        email.send()
        return user

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate_token(self, value):
        if not UserToken.objects.filter(token=value).exists():
            raise serializers.ValidationError("Invalid token.")
        return value
    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs

    def create(self, validated_data):
        token = validated_data["token"]
        user_token = UserToken.objects.get(token=token)
        if user_token.is_validated:
            raise serializers.ValidationError("Token already used.")
        user_token.is_validated = True
        user = user_token.user
        user.password = validated_data["password"]
        user.is_active = True
        user.is_verified = True
        user.save()
        return {"message": "Password reset successfully."}


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'organization']


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', "organization_name"]
    def create(self, validated_data):
        user = self.context['request'].user
        if validated_data['first_name']:
            user.first_name = validated_data['first_name']
        if validated_data['last_name']:
            user.last_name = validated_data['last_name']
        if validated_data['organization_name']:
            organization = Organization.objects.create(name=validated_data['organization_name'])
            organization.admin = user
            organization.save()
            user.organization = organization
        user.save()
        return user
