#!/usr/bin/env python
import os
import sys

# Developed and tested on django 1.5
import django
assert django.VERSION[0:2] == (1, 5)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
