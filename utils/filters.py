import imp
import logging
import django_filters as filters
from django.contrib.auth import get_user_model
from django.db import models
from accounts.models import Roles

User = get_user_model()
logger = logging.getLogger(__name__)

class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = "__all__"
        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }

class RolesFilter(filters.FilterSet):
    class Meta:
        model = Roles
        fields = "__all__"
        filter_overrides = {
            models.CharField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }


