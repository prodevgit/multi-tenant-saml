import logging
from datetime import date

from rest_framework.serializers import ModelSerializer, SerializerMethodField
from tenants.models import Tenant

logger = logging.getLogger(__name__)

class TenantCreateSerializer(ModelSerializer):
    class Meta:
        model = Tenant
        exclude = ['db_name']