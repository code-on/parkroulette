# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Data'
        db.create_table(u'precalculated_data', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=4269)),
            ('json', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'precalculated', ['Data'])


    def backwards(self, orm):
        # Deleting model 'Data'
        db.delete_table(u'precalculated_data')


    models = {
        u'precalculated.data': {
            'Meta': {'object_name': 'Data'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '4269'})
        }
    }

    complete_apps = ['precalculated']