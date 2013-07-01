from django import template
from django.contrib.gis.geoip import GeoIP
from django.conf import settings

register = template.Library()


@register.filter
def city(request):
    g = GeoIP().city(get_ip(request))
    if settings.GEOIP_DEBUG:
        return True
    if g:
        return g['city'] == 'San Francisco' and g['area_code'] == 415
    return


def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip