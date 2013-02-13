from content.models import Log
from django.contrib import admin


class LogAdmin(admin.ModelAdmin):
    list_display = ('address', 'week_day', 'from_time', 'to_time', 'type')
    list_filter = ('type',)

admin.site.register(Log, LogAdmin)