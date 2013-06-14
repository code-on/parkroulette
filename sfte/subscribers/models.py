from django.contrib.gis.db import models


class Subscriber(models.Model):
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.email


