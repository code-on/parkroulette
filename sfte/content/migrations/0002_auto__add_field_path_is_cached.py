# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Path.is_cached'
        db.add_column(u'paths', 'is_cached',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Path.is_cached'
        db.delete_column(u'paths', 'is_cached')


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
            'is_cached': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'path': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '4269', 'null': 'True', 'blank': 'True'}),
            'path_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'start_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'waypoints': ('django.contrib.gis.db.models.fields.MultiPointField', [], {'srid': '4269', 'null': 'True', 'blank': 'True'})
        },
        u'content.ticket': {
            'Meta': {'object_name': 'Ticket', 'db_table': "u'tickets'", 'managed': 'False'},
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