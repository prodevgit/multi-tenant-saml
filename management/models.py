from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Module(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("Module Name", max_length=50, default=False, unique=True)
    slug = models.SlugField(unique=True)
    display_name = models.CharField("Display Name", max_length=50, default=False)
    content_type = models.ForeignKey(
        ContentType, blank=True, null=True, on_delete=models.CASCADE
    )
    parent_module_id = models.ForeignKey(
        "Module", blank=True, null=True, on_delete=models.CASCADE
    )
    order = models.IntegerField("Order", default=0, blank=True, null=True)
    chained_module = models.BooleanField(default=False)

    class Meta:
        db_table = 'modules'

    def __str__(self):
        return "{0}".format(self.display_name)