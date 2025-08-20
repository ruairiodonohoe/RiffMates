from django.contrib import admin

# Register your models here.
from promoters.models import Promoter


@admin.register(Promoter)
class PromotorAdmin(admin.ModelAdmin):
    list_display = ("id", "common_name", "full_name", "famous_for")
