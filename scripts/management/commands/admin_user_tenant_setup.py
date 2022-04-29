import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from accounts.models import Roles

from django.contrib.auth import  get_user_model
from saml.models import SAMLConfiguration

from tenants.models import Tenant


logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = "Admin user setup"
     
    def handle(self, *args, **options):
        try:
            # email = 'admin@prolancehub.in'
            # username = 'admin.prolance'
            # first_name = 'Admin'
            # last_name = 'Dev'
            # full_name = f"{first_name} {last_name}"
            # role = Roles.objects.get(name='Admin')
            # user = User.objects.create_user(
            #     email=email,
            #     username=username,
            #     first_name=first_name,
            #     last_name=last_name,
            #     full_name=full_name,
            #     is_client_admin=False,
            #     is_active=True,
            #     role=role,
            #     password="6282475522",
            #     is_superuser=True
            #     )
            saml_configuration = SAMLConfiguration.objects.create(
                idp_entity_id='https://sts.windows.net/09ce23a3-113b-4a0f-8b29-7d2dd10962e4/',
                idp_single_sign_on='https://login.microsoftonline.com/09ce23a3-113b-4a0f-8b29-7d2dd10962e4/saml2',
                idp_single_logout='https://login.microsoftonline.com/09ce23a3-113b-4a0f-8b29-7d2dd10962e4/saml2',
                saml_certificate='MIIC8DCCAdigAwIBAgIQbRjuTNj7Dp9KOq5M5LQ3azANBgkqhkiG9w0BAQsFADA0MTIwMAYDVQQDEylNaWNyb3NvZnQgQXp1cmUgRmVkZXJhdGVkIFNTTyBDZXJ0aWZpY2F0ZTAeFw0yMjA0MjcxNjQzMDJaFw0yNTA0MjcxNjQzMDJaMDQxMjAwBgNVBAMTKU1pY3Jvc29mdCBBenVyZSBGZWRlcmF0ZWQgU1NPIENlcnRpZmljYXRlMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1XH64VK8tDmJ77DDvip5DJG7azQkc1GgwVnY2vtQvJ8oo2z2TeAxe1QCnEAkHdj1u67TXWlw1IjOOofp0hF24sZ+ZOWvR4HFmKd688hPXurgciUwg25Q2GOjOuRLbMWdKAL0PSbJcOCtVWOeMeyi/ZLn9CX/11JuCFdMs1i8z3tafUGIeA4a/80cu+qG3WDNEpvMr8vYhnVOZokHgNOe3yj7lkRuyuPdcOghViRJvIMnNmGav9s9bIYBjnG5xfV7cD9EXyaSpoRsiifMYorR6YzhnWmnmDlHnV6Uz4U2Fp7sli2oG4wk17pDGOzTWg7z2cs0FGcctsIy5CfVtXjEGQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQA7g7ZOhQToDccQGrZK5H4yEx5aTcqcq8t+MKh1T2PrwSIMdTOLhAO3tf7RfMw1HfR4oQGh0seF0lpTiU7n6v5F35+22phnkYTYU7r6AxfghbmtCu/Ax0wcfOv/EVDcWmeEbueIj6D8Cxl5lnUNTRo/9/4IS8QLhTPgpq4A9KAMXxCfwwHndHuTtXANwd6s6jfrVM3ZFbFTKjNg7onQluELPnnMKg0I+hloX/POS5RF3gecjOJlr66RqoXPbQ/zhLq71stWQ4oIdA2QdVM1gUbEW/UZ+iwIWA+5yhTkZrG8VxQXdBic0eC+Sk4AU1VpuCWj/mpPv+yudcNTUHGtF+T1',
                sp_entity_id='https://student.prolancehub.in',
                assertion_consumer_service='https://student.prolancehub.in/api/v1/auth/set-token',
                sp_logout='https://student.prolancehub.in/api/v1/auth/process-logout'
            )
            tenant = Tenant.objects.create(
                name="Prolance Hub",
                subdomain_prefix="master",
                is_master=True,
                db_name=settings.DATABASES['default']['NAME'],
                saml_configuration=saml_configuration
                )
        except Exception as exception:
            logger.exception(exception)
            