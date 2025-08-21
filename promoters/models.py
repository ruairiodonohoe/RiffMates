from django.db import models


# Create your models here.
class Promoter(models.Model):
    common_name = models.CharField(max_length=25)
    full_name = models.CharField(max_length=50)
    famous_for = models.CharField(max_length=50)
    birth = models.DateField(blank=True, null=True)
    death = models.DateField(blank=True, null=True)
    # street_address = models.CharField(max_length=50, null=True)
    # city = models.CharField(max_length=50, null=True)
    # province_state = models.CharField(max_length=50, null=True)
    # country = models.CharField(max_length=50, null=True)
    # postal_zip_code = models.CharField(max_length=50, null=True)
    # address = models.CharField(max_length=200, null=True, blank=True)
