from models import Subscriber
from django.contrib.gis import admin


class LogSubscriber(admin.ModelAdmin):
    list_display = ('email', 'timestamp')

admin.site.register(Subscriber, LogSubscriber)