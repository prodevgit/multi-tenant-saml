import datetime
import json
import logging
import os
import re

from api.v1.views.tenant.serializer import TenantCreateSerializer
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     RetrieveUpdateAPIView)
from rest_framework.response import Response
from tenants.celery_tasks import create_tenant_db
from tenants.models import Tenant
from utils.functions import tenant_from_request

logger = logging.getLogger(__name__)

class TenantCreateView(CreateAPIView):
    serializer_class = TenantCreateSerializer

    def perform_create(self, serializer):
        data = {}
        try:

            tenant = tenant_from_request(self.request)
            
            if not tenant.is_master:
                raise Exception("Only master tenant can create new tenant")
            if serializer.is_valid():
                if self.request.user.role.name == "Admin":
                    tenant = serializer.save()
                    tenant.db_name = self.request.data.get('subdomain_prefix')
                    tenant.save()
                    create_tenant_db.delay(tenant.subdomain_prefix)
                    data["status"] = "success"
                    data["message"] = 'Tenant Created Successfully'
                    data["code"] = status.HTTP_201_CREATED
                else:
                    data["status"] = 'failed'
                    data["message"] = 'Insufficient permissions'
                    data['code'] = status.HTTP_403_FORBIDDEN
            else:
                data["message"] = 'Tenant creation failed'
                data["details"] = serializer.errors
                data["status"] = "failed"
                data['code'] = status.HTTP_400_BAD_REQUEST

        except Exception as exception:
            logger.exception("Something went wrong %s", exception)
            data["status"] = "failed"
            data["message"] = "Something_went_wrong {label}".format(label=exception)
            data["code"] = 500
        return data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        data = self.perform_create(serializer)
        http_code = data.pop("code", None)
        return Response(data=data, status=http_code)
