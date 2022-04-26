import logging
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from accounts.managers import UserManager

logger = logging.getLogger(__name__)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    full_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    is_client_admin = models.BooleanField(default=False)
    token = models.CharField(max_length=255, null=True, blank=True)
    is_send_activate_mail = models.BooleanField(default=False)
    is_instance_activated = models.BooleanField(default=False)
    username = models.CharField(max_length=30, null=True, blank=True)
    role = models.ForeignKey(
        'accounts.Roles', blank=True, null=True, on_delete=models.SET_NULL
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['is_active', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        '''
        Returns the full name for the user.
        '''
        return self.full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name.strip()

    def natural_key(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_active': self.is_active,
            'is_superuser': self.is_superuser,
        }

    def get_display_name(self):
        name = self.get_full_name()
        display_name = name.replace(" ", "")
        return f"@{display_name}"

    @property
    def return_type(self):
        return "user"

    def __repr__(self):
        return "{0} - {1}".format(self.get_full_name(), self.email)

    def __str__(self):
        return "{0}".format(self.get_full_name())


class Roles(models.Model):
    object_id = models.UUIDField(
        unique=True,
        editable=False,
        default=uuid.uuid4,
        verbose_name='Public identifier',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name
