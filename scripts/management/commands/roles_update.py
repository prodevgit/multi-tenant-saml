import logging
from django.core.management.base import BaseCommand

from accounts.models import Roles

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Add Roles"
     
    def handle(self, *args, **options):
        try:
            roles_list = [
                'Admin',
                'User',
            ]
            for role in roles_list:
                Roles.objects.create(name=role)
            print('Created roles')
        except Exception as exception:
            logger.exception(exception)
            