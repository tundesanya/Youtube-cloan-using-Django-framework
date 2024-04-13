from datetime import timedelta

from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.utils import timezone

from rest_framework import generics, permissions, response, status
from rest_framework.views import APIView

from users.models import PasswordReset
from users.serializers import UserSerializer, RegistrationSerializer, LoginSerializer
from users.serializers import PasswordResetRequestSerializer, PasswordResetSerializer
from users.serializers import VerifyEmailSerializer, ResendVerificationEmailSerializer

import knox.views as knox_views


# User.Register API (Create)
class RegistrationAPI(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        # TODO: figure out if only serializer.is_valid(raise_exception=True) is enough so we can remove the if statement
        serializer.is_valid(raise_exception=True)
        # # # if serializer.is_valid():
        user = serializer.save()
        # a verification email should be sent to the user by the post_save signal at this point
        return response.Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "detail": "User registered successfully. Please verify your email to login.",
        }, status=status.HTTP_201_CREATED)
        # # # return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User.Login API
class LoginAPI(knox_views.LoginView):
    permission_classes = (permissions.AllowAny, )
    # To get 'options' request to show proper https actions based on our serializer

    def get_serializer(self, *args, **kwargs):
        return LoginSerializer(*args, **kwargs)

    # Override knox's get_token_ttl to add remember_me functionality
    def get_token_ttl(self):
        request = self.request
        if request.data.get('remember_me'):
            return timedelta(days=30)
        return super().get_token_ttl()

    def post(self, request):
        # serializer = AuthTokenSerializer(data=request.data)
        serializer = LoginSerializer(data=request.data)
        # TODO: figure out if only serializer.is_valid(raise_exception=True) is enough so we can remove the if statement
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        # login() will also set the user in the session.
        login(request, user)
        # set cookie for token
        response = super(LoginAPI, self).post(request, format=None)
        response.data['user'] = UserSerializer(user).data
        token = response.data['token']
        response.set_cookie(key='token', value=token, httponly=True)
        return response


# User.Logout API
class LogoutAPI(knox_views.LogoutView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, format=None):
        response = super(LogoutAPI, self).post(request, format=None)
        # logout() will also flush the user session.
        logout(request)
        response.delete_cookie('token')
        return response


# User.LogoutAll API
class LogoutAllAPI(knox_views.LogoutAllView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, format=None):
        response = super(LogoutAllAPI, self).post(request, format=None)
        # logout() will also flush the user session.
        logout(request)
        response.delete_cookie('token')
        return response


# User.Profile API (Retrieve - Logged-in User)
class ProfileAPI(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# User.Update API (Update - Logged-in User)
class UpdateAPI(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "detail": "User updated successfully."
        }, status=status.HTTP_200_OK)


# TODO: Replace the json response with a template/redirect to a page
# User.EmailVerification API
class VerifyEmailAPI(APIView):
    permission_classes = (permissions.AllowAny, )

    # For 'options' request, kinda cosmetic only no actual effect on api logic
    def get_serializer(self, *args, **kwargs):
        return VerifyEmailSerializer(*args, **kwargs)

    def get(self, request):
        serializer = VerifyEmailSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({
            "detail": "Email verified successfully. You can close this page and login."
        }, status=status.HTTP_200_OK)


class ResendVerificationEmailAPI(APIView):
    """
    This is only for users who have not verified their email yet after registration.
    Does not apply to users who have updated their email and need to verify the new email.
    If the verification email for the new email is expired, the user should update their email again.
    """
    permission_classes = (permissions.AllowAny, )

    def get_serializer(self, *args, **kwargs):
        return ResendVerificationEmailSerializer(*args, **kwargs)

    def post(self, request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({
            "detail": "Verification email sent successfully."
        }, status=status.HTTP_200_OK)

# User.PasswordResetRequest API


class PasswordResetRequestAPI(APIView):
    permission_classes = (permissions.AllowAny, )

    def get_serializer(self, *args, **kwargs):
        return PasswordResetRequestSerializer(*args, **kwargs)

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({
            "detail": "Password reset email sent successfully."
        }, status=status.HTTP_200_OK)


# User.PasswordReset API
class PasswordResetAPI(APIView):
    permission_classes = (permissions.AllowAny, )

    def get_serializer(self, *args, **kwargs):
        return PasswordResetSerializer(*args, **kwargs)

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({
            "detail": "Password reset successfully."
        }, status=status.HTTP_200_OK)


# User.Delete API (Delete - Logged-in User)
class DisableAPI(generics.DestroyAPIView):
    """Set is_active=False for the user"""

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        logout(request)
        return response.Response({
            "detail": "User disabled successfully."
        }, status=status.HTTP_204_NO_CONTENT)


# # Social Logins

# # Google
# class GoogleLoginAPI(generics.GenericAPIView):
#     def get(self, request, format=None):
#         base_url = "https://accounts.google.com/o/oauth2/v2/auth"
#         params = {
#             'response_type': 'code',
#             'client_id': django_settings.GOOGLE_OAUTH['client_id'],
#             'redirect_uri': django_settings.GOOGLE_OAUTH['redirect_uri'],
#             'scope': 'openid email profile',
#             'access_type': 'offline',
#             'prompt': 'consent',
#         }
#         auth_url = f"{base_url}?{urlencode(params)}"
#         print(auth_url)
#         return HttpResponseRedirect(auth_url)

# class GoogleCallbackAPI(generics.GenericAPIView):
#     def get(self, request, format=None):
#         print(request.GET)
#         code = request.GET.get('code')
#         token_url = 'https://oauth2.googleapis.com/token'
#         data = {
#             'code': code,
#             'client_id': django_settings.GOOGLE_OAUTH['client_id'],
#             'client_secret': django_settings.GOOGLE_OAUTH['client_secret'],
#             'redirect_uri': django_settings.GOOGLE_OAUTH['redirect_uri'],
#             'grant_type': 'authorization_code',
#         }
#         token_response = requests.post(token_url, data=data)
#         token_json = token_response.json()
#         access_token = token_json.get('access_token')

#         # Retrieve user information from Google
#         userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
#         userinfo_response = requests.get(userinfo_url, params={'access_token': access_token})
#         user_info = userinfo_response.json()
#         print(user_info)

#         # save user info to the database
#         User = get_user_model()
#         user, created = User.objects.get_or_create(email=user_info['email'])
#         if created:
#             user.username = user_info['email']
#             user.email = user_info['email']
#             user.first_name = user_info['given_name']
#             user.last_name = user_info['family_name']
#             user.picture = user_info['picture']
#             user.save()

#         login(request, user)
#         _, token = AuthToken.objects.create(user)

#         # Redirect to a page in your application or return a response
#         resp = response.Response({
#             "user": UserSerializer(user).data,
#             "token": token
#         }, status=status.HTTP_200_OK)
#         resp.set_cookie(key='token', value=token, httponly=True)
#         return resp
