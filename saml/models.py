from django.db import models

class SAMLConfiguration(models.Model):

    idp_entity_id = models.TextField()
    idp_single_sign_on = models.TextField()
    idp_single_logout = models.TextField()
    saml_certificate = models.TextField()
    sp_entity_id = models.TextField()
    assertion_consumer_service = models.TextField()
    sp_logout = models.TextField()
    
    class Meta:
        verbose_name = 'SAML Configuration'
        verbose_name_plural = 'SAML Configurations'

