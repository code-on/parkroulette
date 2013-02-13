from django.db import models


class Log(models.Model):
    CHANCE, LAWS = range(1, 3)
    TYPE_CHOICES = (
        (CHANCE, 'Chance'),
        (LAWS, 'Laws'),
    )
    address = models.CharField(max_length=255)
    week_day = models.CharField(max_length=10, blank=True, null=True)
    from_time = models.TimeField(null=True, blank=True)
    to_time = models.TimeField(null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)


    def __unicode__(self):
        return self.address