from django.contrib.gis.db import models


class CachedData(models.Model):
    location = models.PointField(srid=4269)
    json = models.TextField(blank=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.json

    class Meta:
        verbose_name = u'Cached data'
        verbose_name_plural = u'Cached data'
