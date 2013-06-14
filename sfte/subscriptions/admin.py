from models import CitySubscription
from django.contrib.gis import admin


class AdminCitySubscription(admin.ModelAdmin):
    list_display = ('city', 'email', 'timestamp')

admin.site.register(CitySubscription, AdminCitySubscription)