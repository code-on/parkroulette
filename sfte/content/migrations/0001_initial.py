# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Log'
        db.create_table(u'content_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('week_day', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('from_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('to_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal(u'content', ['Log'])

        # Adding model 'Path'
        db.create_table(u'paths', (
            ('path_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('path', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=4269, null=True, blank=True)),
            ('badge', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('day', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('chunk', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('start_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('end_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('start_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('waypoints', self.gf('django.contrib.gis.db.models.fields.MultiPointField')(srid=4269, null=True, blank=True)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'content', ['Path'])

        # Adding model 'Ticket'
        db.create_table(u'tickets', (
            ('ticket_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('ag', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('citation', self.gf('django.db.models.fields.TextField')(unique=True, blank=True)),
            ('issue_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('plate', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('vin', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('make', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cl', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('location', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('badge', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('violation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('violation_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('meter', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('fine_amt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('penalty_1', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('penalty_2', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('penalty_4', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('penalty_5', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pay_amt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('outstanding', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('s', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('geopoint', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=4269, null=True, blank=True)),
        ))
        db.send_create_signal(u'content', ['Ticket'])


    def backwards(self, orm):
        # Deleting model 'Log'
        db.delete_table(u'content_log')

        # Deleting model 'Path'
        db.delete_table(u'paths')

        # Deleting model 'Ticket'
        db.delete_table(u'tickets')


    models = {
        u'content.log': {
            'Meta': {'object_name': 'Log'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'from_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'week_day': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        u'content.path': {
            'Meta': {'object_name': 'Path', 'db_table': "u'paths'"},
            'badge': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'chunk': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'day': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'path': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '4269', 'null': 'True', 'blank': 'True'}),
            'path_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'start_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'waypoints': ('django.contrib.gis.db.models.fields.MultiPointField', [], {'srid': '4269', 'null': 'True', 'blank': 'True'})
        },
        u'content.ticket': {
            'Meta': {'object_name': 'Ticket', 'db_table': "u'tickets'"},
            'ag': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'badge': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'citation': ('django.db.models.fields.TextField', [], {'unique': 'True', 'blank': 'True'}),
            'cl': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'fine_amt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geopoint': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '4269', 'null': 'True', 'blank': 'True'}),
            'issue_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'make': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meter': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'outstanding': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pay_amt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'penalty_1': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'penalty_2': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'penalty_4': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'penalty_5': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'plate': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            's': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ticket_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'vin': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'violation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'violation_description': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['content']