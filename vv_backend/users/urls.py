from django.urls import path

from users.views import RegistrationAPI
from users.views import LoginAPI, LogoutAPI, LogoutAllAPI
from users.views import ProfileAPI, UpdateAPI, DisableAPI
from users.views import VerifyEmailAPI, ResendVerificationEmailAPI
from users.views import PasswordResetRequestAPI, PasswordResetAPI
# from users.views import GoogleLoginAPI, GoogleCallbackAPI

urlpatterns = [
    path('register/', RegistrationAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),

    path('logout/', LogoutAPI.as_view(), name='logout'),
    path('logout-all/', LogoutAllAPI.as_view(), name='logoutall'),
    
    path('profile/', ProfileAPI.as_view(), name='profile'),
    path('update/', UpdateAPI.as_view(), name='update'),
    path('disable/', DisableAPI.as_view(), name='disable'),
    
    path('verify-email/', VerifyEmailAPI.as_view(), name='verify_email'),
    path('resend-verification-email/', ResendVerificationEmailAPI.as_view(), name='resend_email_verification'),

    path('reset-password-request/', PasswordResetRequestAPI.as_view(), name='reset_password_request'),
    path('reset-password/', PasswordResetAPI.as_view(), name='reset_password'),

    # # social login
    # path('login-google/', GoogleLoginAPI.as_view(), name='login-google'),
    # path('login-google/callback/', GoogleCallbackAPI.as_view(), name='login-google-callback'),
]