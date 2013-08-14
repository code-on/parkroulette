from django.contrib.gis.db import models


class CachedData(models.Model):
    location = models.PointField(srid=4269)
    json = models.TextField(blank=True)

    objects = models.GeoManager()

    class Meta:
        verbose_name = u'Cached data'
        verbose_name_plural = u'Cached data'
