from __future__ import unicode_literals
from django.contrib.gis.db import models


class Log(models.Model):
    CHANCE, LAWS, HEATMAP = range(1, 4)
    TYPE_CHOICES = (
        (CHANCE, 'Chance'),
        (LAWS, 'Laws'),
        (HEATMAP, 'Heatmap'),
    )
    address = models.CharField(max_length=255)
    week_day = models.CharField(max_length=10, blank=True, null=True)
    from_time = models.TimeField(null=True, blank=True)
    to_time = models.TimeField(null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)


    def __unicode__(self):
        return self.address


class Path(models.Model):
    path_id = models.IntegerField(primary_key=True)
    path = models.LineStringField(srid=4269, null=True, blank=True)
    badge = models.TextField(blank=True)
    day = models.DateField(null=True, blank=True)
    chunk = models.IntegerField(null=True, blank=True)
    start_address = models.TextField(blank=True)
    end_address = models.TextField(blank=True)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    waypoints = models.MultiPointField(srid=4269, null=True, blank=True)
    valid = models.BooleanField(default=True)

    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'paths'


class Ticket(models.Model):
    ticket_id = models.IntegerField(primary_key=True)
    ag = models.IntegerField(null=True, blank=True)
    citation = models.TextField(unique=True, blank=True)
    issue_datetime = models.DateTimeField(null=True, blank=True)
    plate = models.TextField(blank=True)
    vin = models.TextField(blank=True)
    make = models.TextField(blank=True)
    body = models.TextField(blank=True)
    cl = models.TextField(blank=True)
    location = models.TextField(blank=True)
    badge = models.TextField(blank=True)
    violation = models.TextField(blank=True)
    violation_description = models.TextField(blank=True)
    meter = models.TextField(blank=True)
    fine_amt = models.TextField(blank=True) # This field type is a guess.
    penalty_1 = models.TextField(blank=True) # This field type is a guess.
    penalty_2 = models.TextField(blank=True) # This field type is a guess.
    penalty_4 = models.TextField(blank=True) # This field type is a guess.
    penalty_5 = models.TextField(blank=True) # This field type is a guess.
    pay_amt = models.TextField(blank=True) # This field type is a guess.
    outstanding = models.TextField(blank=True) # This field type is a guess.
    s = models.TextField(blank=True)
    geopoint = models.PointField(srid=4269, null=True, blank=True)

    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'tickets'