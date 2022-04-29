from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain_prefix = models.CharField(max_length=100, unique=True)
    is_master = models.BooleanField(default=False)
    db_name = models.CharField(max_length=100)
    saml_configuration = models.ForeignKey('saml.SAMLConfiguration', on_delete=models.CASCADE)