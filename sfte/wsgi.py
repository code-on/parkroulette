#!/usr/bin/env python
import os, sys

def rel(*x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

sys.path.insert(0, rel('..', 'lib'))
sys.path.insert(0, rel('..', 'sfte'))

# Developed and tested on django 1.5
import django
assert django.VERSION[0:2] == (1, 5)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()