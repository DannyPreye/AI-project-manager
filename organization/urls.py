from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView


auth_urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path("login/", TokenObtainPairView.as_view(), name='login'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('request-reset-password/', views.RequestResetPasswordView.as_view(), name='request-reset-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('resend-verification-email/', views.ResendVerificationEmailView.as_view(), name='resend-verification-email'),
]

urlpatterns = [
    path('auth/', include(auth_urlpatterns)),
]
