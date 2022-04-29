import subprocess
from django.db import connection
from MultiTenantSAML import celery_app
from tenants.models import Tenant
from django.conf import settings

@celery_app.task(name="setup_tenant_db")
def create_tenant_db(tenant):
    try:
        threadlocal = connection.get_threadlocal()
        threadlocal.set_tenant_name('master')
        threadlocal.set_db_name(settings.DATABASES['default']['NAME'])
        tenant = Tenant.objects.get(subdomain_prefix=tenant)
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {tenant.db_name}")
            process = subprocess.Popen(
                f"TENANT_DATABASE_NAME={tenant.db_name} python manage.py migrate",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                executable="/bin/bash",
            )
            out, err = process.communicate()
            errcode = process.returncode
            print("{0}: {1}".format(out, err))
            process = subprocess.Popen(
                f"TENANT_DATABASE_NAME={tenant.db_name} python manage.py roles_update",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                executable="/bin/bash",
            )
            out, err = process.communicate()
            errcode = process.returncode
            print("{0}: {1}".format(out, err))
            process = subprocess.Popen(
                f"TENANT_DATABASE_NAME={tenant.db_name} python manage.py create_user_tenant {tenant.db_name}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                executable="/bin/bash",
            )
            out, err = process.communicate()
            errcode = process.returncode
            print("{0}: {1}".format(out, err))
    except Exception as e:
        print(e)
        
