import logging

from accounts.models import Roles
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import exceptions, serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ModelSerializer, SerializerMethodField

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            message = _('Must include "email" and "password".')
            raise exceptions.ValidationError(message)

        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            message = _('Must include "username" and "password".')
            raise exceptions.ValidationError(message)

        return user

    def _validate_username_email(self, username, email, password):
        user = None
        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            message = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(message)

        return user

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if (
                app_settings.AUTHENTICATION_METHOD
                == app_settings.AuthenticationMethod.EMAIL
            ):
                user = self._validate_email(email, password)

            # Authentication through username
            elif (
                app_settings.AUTHENTICATION_METHOD
                == app_settings.AuthenticationMethod.USERNAME
            ):
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = User.objects.get(email__iexact=email).email
                except User.DoesNotExist:
                    username=email
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            print('Checking if user is active')
            if not user.is_active:
                message = 'User account is disabled.'
                raise exceptions.ValidationError(message)
        else:
            message = 'Unable to log in with provided credentials.'
            raise exceptions.ValidationError(message)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            if (
                app_settings.EMAIL_VERIFICATION
                == app_settings.EmailVerificationMethod.MANDATORY
            ):
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError('E-mail is not verified.')

        attrs['user'] = user
        return attrs

class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """

    class Meta:
        model = Token
        fields = ('key',)


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)


class UserListSerializer(ModelSerializer):

    role = SerializerMethodField(read_only=True)
    entity = SerializerMethodField(read_only=True)
    full_name = SerializerMethodField(read_only=True)
    phone_number = SerializerMethodField(read_only=True)

    def get_role(self, user):
        try:
            if user.role:
                user_dict = {
                    "id": user.role.id,
                    "value": user.role.name,
                }
                return user_dict
            else:
                return None
        except Exception as exception:
            logger.exception(
                "Getting Exception while Fetching License type as %s", exception
            )
            return None

    def get_entity(self, user):
        try:
            if user.entity:
                user_dict = {
                    "id": user.entity.id,
                    "value": user.entity.name,
                }
                return user_dict
            else:
                return None
        except Exception as exception:
            logger.exception(
                "Getting Exception while Fetching License type as %s", exception
            )
            return None

    def get_full_name(self, user):
        return user.get_full_name()

    

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "username",
            "email",
            "role",
            'entity',
            'phone_number',
        )


class RoleSerializer(ModelSerializer):
    class Meta:
        model = Roles
        fields = [
            "id",
            "name",
        ]
