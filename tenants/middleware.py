from django.db import connection
from utils.functions import tenant_db_from_request
from tenants.mapper import TenantMapper
from db_multitenant.middleware import MultiTenantMiddleware


class TenantMiddleware(MultiTenantMiddleware):
    
    def process_request(self, request):
        mapper = TenantMapper()
        threadlocal = connection.get_threadlocal()
        tenant_name = mapper.get_tenant_name(request)
        threadlocal.set_tenant_name(tenant_name)
        db_name = tenant_db_from_request(request)
        threadlocal.set_db_name(db_name)
        threadlocal.set_cache_prefix(mapper.get_cache_prefix(request, tenant_name, db_name))


