import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from accounts.models import Roles

from django.contrib.auth import  get_user_model

from tenants.models import Tenant


logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = "Admin user setup"
     
    def handle(self, *args, **options):
        try:
            tenant = options['tenant'][0]
            email = f'admin@{tenant}.{settings.APP_DOMAIN}'
            username = f'admin.{tenant}'
            first_name = 'Admin'
            last_name = tenant.capitalize()
            full_name = f"{first_name} {last_name}"
            role = Roles.objects.get(name='Admin')
            user = User.objects.create_user(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                is_client_admin=False,
                is_active=True,
                role=role,
                password="12345678",
                is_superuser=True
                )
            print(f'Created admin user for tenant {tenant}')
        except Exception as exception:
            logger.exception(exception)
    
    def add_arguments(self, parser):
        parser.add_argument('tenant', nargs='+', type=str)