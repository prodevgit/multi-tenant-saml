import logging

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import ModelSerializer, SerializerMethodField

User = get_user_model()
logger = logging.getLogger(__name__)


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

    def get_phone_number(self, user):
        try:
            user_profile = UserProfile.objects.filter(user=user).first()
            if user_profile:
                return user_profile.contact_number
            else:
                return None
        except Exception as exception:
            logger.exception(
                "Getting Exception while Fetching License type as %s", exception
            )
            return None

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
