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
            email = 'admin@prolancehub.in'
            username = 'admin.prolance'
            first_name = 'Admin'
            last_name = 'Dev'
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
                password="6282475522",
                is_superuser=True
                )
            saml_configuration = SAMLConfiguration.objects.create
            tenant = Tenant.objects.create(
                name="Prolance Hub",
                subdomain_prefix="master",
                is_master=True,
                db_name=settings.DATABASES['default']['NAME']
                )
        except Exception as exception:
            logger.exception(exception)
            