from datetime import datetime, date

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from bands.models import Musician, Band


# Register your models here.
class DecadeListFilter(admin.SimpleListFilter):
    title = "decade_born"
    parameter_name = "decade"

    def lookups(self, request, model_admin):
        result = []

        this_year = datetime.today().year
        this_decade = (this_year // 10) * 10
        start = this_decade - 10

        for year in range(start, start - 100, -10):
            result.append((str(year), f"{year}-{year+9}"))

        return result

    def queryset(self, request, queryset):
        start = self.value()
        if start is None:
            return queryset

        start = int(start)
        result = queryset.filter(
            birth__gte=date(start, 1, 1),
            birth__lte=date(start + 9, 12, 31),
        )

        return result


@admin.register(Musician)
class MusicianAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "last_name",
        "first_name",
        "birth",
        "show_weekday",
        "show_bands",
    )
    search_fields = ("last_name", "first_name")
    list_filter = (DecadeListFilter,)

    def show_weekday(self, obj):
        return obj.birth.strftime("%A")

    show_weekday.short_description = "Birth weekday"

    def show_bands(self, obj):
        bands = obj.band_set.all()
        if len(bands) == 0:
            return format_html("<i>None</i>")

        plural = ""
        if len(bands) > 1:
            plural = "s"

        param = "?id__in=" + ",".join([str(b.id) for b in bands])
        url = reverse("admin:bands_band_changelist") + param
        return format_html("<a href='{}'>Band{}</a>", url, plural)

    show_bands.short_description = "Bands"


@admin.register(Band)
class BandAdmin(admin.ModelAdmin):
    pass
