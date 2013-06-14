from django.db import models


class CitySubscription(models.Model):
    city = models.CharField(max_length=255)
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.city


