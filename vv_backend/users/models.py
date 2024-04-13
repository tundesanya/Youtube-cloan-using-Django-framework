import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

from django_countries.fields import CountryField


class User(AbstractUser):
    """Our own user model, overridding django's default user model for extra fields."""

    # Use email to login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # for creating a superuser through manage.py, has no effect on normal user creation
    # # For Soft Delete
    # objects = IsActiveUserManager()
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    
    class SocialLogin(models.TextChoices):
        EMAIL = "Email", 'email'
        GOOGLE = "Google", 'google'
        FACEBOOK = "Facebook", 'facebook'
    social_login = models.CharField(
        choices=SocialLogin.choices,
        default=SocialLogin.EMAIL
    )

    # Personal Profile fields
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    dob = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = CountryField(blank=True)
    bio = models.TextField(blank=True)
    # TODO: Nishil: Move profile pictures to S3
    profile_picture = models.ImageField(null=True, blank=True, upload_to='assets/profile_pictures/')

    # TODO: Should this be moved to a separate file, eg: common/...? will it take effect if we update the file and models are already migrated after?
    # Also take a look at this: https://github.com/jacksonllee/iso639
    # ISO 639-1 language codes
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('zh', 'Chinese'),
        ('ru', 'Russian'),
        ('ar', 'Arabic'),
        ('hi', 'Hindi'),
        ('bn', 'Bengali'),
        ('pt', 'Portuguese'),
        ('kn', 'Kannada'),
        ('ml', 'Malayalam'),
        ('th', 'Thai'),
        ('vi', 'Vietnamese'),
        ('tl', 'Filipino'),
        ('id', 'Indonesian')
        # Frank: Add more languages as needed
    ]
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en', blank=True)

    # Flags
    is_verified = models.BooleanField(default=False)
    has_agreed_to_terms = models.BooleanField(default=False)
    has_agreed_to_privacy_policy = models.BooleanField(default=False)
    has_finished_onboarding = models.BooleanField(default=False)


class EmailVerification(models.Model):
    """Email verification model to store email verification requests"""

    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verifications")
    # TODO: unique = True has performance issues imo, can we rely on math being math?
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    sent_to = models.EmailField()
    sent_count = models.IntegerField(default=0)
    # is_sent = models.BooleanField(default=False)
    cooldown = models.DurationField(default="0:30:00", blank=True, null=True)   # 30 minutes
    # is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"User Email Verification: {self.user.email}"


class PasswordReset(models.Model):
    """Reset password model to store reset password requests"""

    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_resets")
    # TODO: again the unique = True thing
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    # sent_to = models.EmailField()
    sent_count = models.IntegerField(default=0)
    # is_sent = models.BooleanField(default=False)
    cooldown = models.DurationField(default="0:30:00", blank=True, null=True)   # 30 minutes
    # is_active = models.BooleanField(default=True)


# TODO: Nishil: Add UserSettings Functionality
# class UserSettings(models.Model):
# class UserDevice(models.Model):?


class Friendship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requested_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requested_friendships")
    sent_to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receieved_friendships")

    # Friendship status, default = PENDING
    class Status(models.IntegerChoices):
        PENDING = 0, "PENDING",
        ACCEPTED = 1, "ACCEPTED",
        REJECTED = 2, "REJECTED",
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.PENDING
    )

    message = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # not a field updated from request payload, but internal update when a friendship is accepted
    # TODO write corresponding auto update function by creating functions like "Friendship.accept()"
    friend_since = models.DateTimeField(blank=True, null=True)
