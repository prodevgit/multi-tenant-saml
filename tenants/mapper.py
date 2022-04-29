from db_multitenant import mapper

class TenantMapper(mapper.TenantMapper):
    def get_tenant_name(self, request):
        """Takes the first part of the hostname as the tenant"""
        hostname = request.get_host().split(':')[0].lower()
        return hostname.split('.')[0]

    def get_db_name(self, request, tenant_name):
        return 'tenant-%s' % tenant_name

    def get_cache_prefix(self, request, tenant_name, db_name):
        """The arguments db_name and tenant_name are provided by the methods of this TenantMapper"""
        return 'tenant-%s' % tenant_name