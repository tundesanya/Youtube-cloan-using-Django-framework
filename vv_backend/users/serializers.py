from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import serializers
# from rest_framework.validators import UniqueValidator

from django_countries.serializer_fields import CountryField

from users.models import EmailVerification, PasswordReset
from users.exceptions import UserUpdateValidationMessage


# NOTE: All Data transform + validation logic should be here and just the presentation logic should be in views.


class UserSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True, required=False)

    class Meta:
        model = get_user_model()
        fields = (
            'email', 'username',
            'first_name', 'last_name', 'gender', 'dob',
            'bio', 'profile_picture',
            'city', 'state', 'country',
            'preferred_language',
            'has_finished_onboarding'
        )
    
    def update(self, instance, validated_data):
        email_updated = False

        if 'email' in validated_data and instance.email != validated_data['email']:
            instance.is_verified = False
            new_email = validated_data.pop('email')
            email_updated = True

        if not any(getattr(instance, attr) != value for attr, value in validated_data.items()) and not email_updated:
            raise UserUpdateValidationMessage({"detail": "No changes were made."}, code="no_changes", status_code=204)
        
        if email_updated:
            # Create a EmailVerification instance for the user
            _ = EmailVerification.objects.create(
                user=instance,
                sent_to=new_email,
                expires_at=timezone.now() + timedelta(minutes=30)
            )
            # a verification email should be sent to the user by the post_save signal at this point
            # raise serializers.ValidationError({"message": "Email updated. Please verify your new email to login with it."})
            raise UserUpdateValidationMessage({"detail": "Email updated. Please verify your new email to login with it."}, code="email_updated", status_code=202)
        
        instance = super().update(instance, validated_data)
        return instance


class RegistrationSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=get_user_model().objects.all())])
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    # TODO: should these be required = True?
    has_agreed_to_terms = serializers.BooleanField(required=True)
    has_agreed_to_privacy_policy = serializers.BooleanField(required=True)

    class Meta:
        model = get_user_model()
        fields = (
            'email', 'password', 'password2', 'username',
            'first_name', 'last_name', 'gender', 'dob', 
            'bio', 'profile_picture',
            'city', 'state', 'country',
            'preferred_language',
            'has_agreed_to_terms', 'has_agreed_to_privacy_policy'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        if not data['has_agreed_to_terms']:
            raise serializers.ValidationError({'has_agreed_to_terms': 'You must agree to the terms.'})
        if not data['has_agreed_to_privacy_policy']:
            raise serializers.ValidationError({'has_agreed_to_privacy_policy': 'You must agree to the privacy policy.'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = get_user_model().objects.create_user(**validated_data)
        
        # Create a EmailVerification instance for the new user
        _ = EmailVerification.objects.create(
            user=user,
            sent_to=user.email,
            expires_at=timezone.now() + timedelta(minutes=30)
        )
        # a verification email should be sent to the user by the post_save signal at this point
        
        # TODO: Remove this. Default is set to False in model itself
        # if settings.DEBUG:
        #     user.is_verified = True
        #     user.save()
        
        return user


class LoginSerializer(serializers.ModelSerializer):
    """
    Serializer for user login (authentication).
    Based on rest_framework.authtoken.serializers.AuthTokenSerializer.
    """

    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True, required=True
    )
    remember_me = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'remember_me')
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            # The authenticate call simply returns None for is_active=False users.
            # (Assuming the default ModelBackend authentication backend.)
            if not user:
                raise serializers.ValidationError('Invalid credentials.', code='authorization')
            if not user.is_verified:
                raise serializers.ValidationError('Email is not verified.', code='authorization')
        else:
            raise serializers.ValidationError('Must include "email" and "password".', code='authorization')
        
        data['user'] = user
        return data


class VerifyEmailSerializer(serializers.ModelSerializer):
    # sent_to = serializers.EmailField(required=True, write_only=True)
    token = serializers.UUIDField(required=True)

    class Meta:
        model = EmailVerification
        # fields = ('sent_to', 'token', )
        fields = ('token', )

    def validate_token(self, value):
        if not EmailVerification.objects.filter(token=value, expires_at__gt=timezone.now()).exists():
            raise serializers.ValidationError("Invalid or expired token.")
        return value
    
    def create(self, validated_data):
        # TODO: Nishil - Check: We should not have to check if email_verification.expires_at > timezone.now()
        # here if we're already doing that in the validate_token method
        email_verification = EmailVerification.objects.get(token=validated_data['token'], expires_at__gt=timezone.now())
        user = email_verification.user
        user.email = email_verification.sent_to
        user.is_verified = True
        user.save()
        email_verification.delete()
        return user


class ResendVerificationEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, write_only=True)

    class Meta:
        model = EmailVerification
        fields = ('email', )

    def validate_email(self, value):
        user = get_user_model().objects.filter(email=value)
        # NOTE: Nishil - we should not have to check if user is_active if we are 
        # implementing and overriding either the user model's default manager or something else (auth backend?)
        if not user.exists() or not user.get().is_active:
            raise serializers.ValidationError("No user found with this email.")
        if user.get().is_verified:
            raise serializers.ValidationError("User is already verified.")
        return value
    
    def create(self, validated_data):
        user = get_user_model().objects.get(email=validated_data['email'])

        # Delete any previous EmailVerification instances for the user
        EmailVerification.objects.filter(user=user).delete()

        # Create a new EmailVerification instance for the user
        _ = EmailVerification.objects.create(
            user=user,
            sent_to=user.email,
            expires_at=timezone.now() + timedelta(minutes=30)
        )
        # a verification email should be sent to the user by the post_save signal at this point
        return user


class PasswordResetRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('email', )
    
    def validate_email(self, value):
        user = get_user_model().objects.filter(email=value)
        # NOTE: Nishil - we should not have to check if user is_active if we are
        # implementing and overriding either the user model's default manager or something else (auth backend?)
        if not user.exists() or not user.get().is_active:
            raise serializers.ValidationError("No user found with this email.")
        return value
    
    def create(self, validated_data):
        user = get_user_model().objects.get(email=validated_data['email'])

        # Delete any previous PasswordReset instances for the user
        PasswordReset.objects.filter(user=user).delete()

        # Create a new PasswordReset instance for the user
        _ = PasswordReset.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        # a password reset email should be sent to the user by the post_save signal at this point
        return user


class PasswordResetSerializer(serializers.ModelSerializer):
    token = serializers.UUIDField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = PasswordReset
        fields = ('token', 'password', 'password2')
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        return data
    
    def validate_token(self, value):
        if not PasswordReset.objects.filter(token=value, expires_at__gt=timezone.now()).exists():
            raise serializers.ValidationError("Invalid or expired token")
        return value
    
    def create(self, validated_data):
        password_reset = PasswordReset.objects.get(token=validated_data['token'], expires_at__gt=timezone.now())
        user = password_reset.user
        user.set_password(validated_data['password'])
        user.save()
        password_reset.delete()
        return user
