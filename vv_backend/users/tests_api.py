from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User
from django.utils import timezone
from .models import EmailVerification
from .models import PasswordReset


class UserRegistrationTestCase(APITestCase):
    data = {
        'email': 'test@example.com',
        'password': 'password123',
        'password2': 'password123',
        'username': 'testuser',
        'has_agreed_to_terms': True,
        'has_agreed_to_privacy_policy': True
    }

    def test_user_registration(self):
        url = reverse('register')

        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_registration_sends_verification_email(self):
        # Create a user

        url = reverse('register')
        self.client.post(url, self.data, format='json')
        email_verification = EmailVerification.objects.filter(
            sent_to=self.data['email']).first()

        # Check if an EmailVerification object has been created
        self.assertIsNotNone(email_verification)

        # Check the details of the verification email
        self.assertEqual(email_verification.sent_to, self.data['email'])
        # self.assertEqual(email_verification.sent_count, 1)
        self.assertTrue(timezone.now() < email_verification.expires_at)

    def test_user_registration_with_invalid_data(self):
        url = reverse('register')
        data = {
            'email': '',
            'password': 'password123', }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VerifyEmailTestCase(APITestCase):
    data = {
        'email': 'test@example.com',
        'password': 'password123',
        'password2': 'password123',
        'username': 'testuser',
        'has_agreed_to_terms': True,
        'has_agreed_to_privacy_policy': True
    }

    def test_verify_email(self):
        # Create a user
        url = reverse('register')
        self.client.post(url, self.data, format='json')

        # Get the verification token
        email_verification = EmailVerification.objects.filter(
            sent_to=self.data['email']).first()
        token = email_verification.token

        # Verify the email
        url = reverse('verify_email')
        url_with_token = f'{url}?token={token}'
        response = self.client.get(url_with_token, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pass


class BaseTestCase(APITestCase):
    def setUp(self) -> None:
        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123',
            'username': 'testuser',
            'has_agreed_to_terms': True,
            'has_agreed_to_privacy_policy': True
        }
        url = reverse('register')
        self.client.post(url, self.user_data, format='json')
        url = reverse('verify_email')
        email_verification = EmailVerification.objects.filter(
            sent_to=self.user_data['email']).first()
        token = email_verification.token
        url_with_token = f'{url}?token={token}'
        self.client.get(url_with_token, format='json')

    def get_token(self):
        url = reverse('login')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        return response.data['token']


class UserLoginTestCase(BaseTestCase):
    def test_user_login(self):
        url = reverse('login')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)


class UserLogoutTestCase(BaseTestCase):
    def test_user_logout(self):
        url = reverse('logout')
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ProfileTestCase(BaseTestCase):
    def test_profile(self):
        url = reverse('profile')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_with_token(self):
        url = reverse('profile')
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])

    def update_profile(self):
        url = reverse('update')
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        data = {
            'email': 'test@example.com',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(User.objects.get().email, data['email'])


class DisableTestCase(BaseTestCase):
    def test_disable(self):
        url = reverse('disable')
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.get().is_active, False)
        self.assertEqual(User.objects.get().email, self.user_data['email'])


class PasswordResetRequestTestCase(BaseTestCase):
    def test_password_reset_request(self):
        url = reverse('reset_password_request')
        data = {
            'email': self.user_data['email']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordResetTestCase(BaseTestCase):
    def get_password_reset_token(self):
        url = reverse('reset_password_request')
        data = {
            'email': self.user_data['email']
        }
        self.client.post(url, data, format='json')
        user = User.objects.get(email=self.user_data['email'])
        password_reset = PasswordReset.objects.filter(user=user).first()
        return password_reset.token

    def test_password_reset(self):
        url = reverse('reset_password')
        token = self.get_password_reset_token()

        data = {
            'token': token,
            'password': 'newpassword',
            'password2': 'newpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check login with new password
        url = reverse('login')
        data = {
            'email': self.user_data['email'],
            'password': 'newpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
