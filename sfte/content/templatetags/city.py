from django import template
from django.contrib.gis.geoip import *

register = template.Library()


@register.filter
def sanfrancisco(request):
    if HAS_GEOIP:
        g = GeoIP().city(get_ip(request))
        if g:
            return g['city'] == 'San Francisco' and g['area_code'] == 415
    return


@register.filter
def california(request):
    if HAS_GEOIP:
        g = GeoIP().city(get_ip(request))
        if g:
            return g['region'] == 'CA' and g['country_code'] == 'US'
    return


def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
