from precalculated.models import CachedData
from django.contrib.gis import admin


class CachedDataAdmin(admin.ModelAdmin):
    list_display = ('location',)

admin.site.register(CachedData, CachedDataAdmin)
