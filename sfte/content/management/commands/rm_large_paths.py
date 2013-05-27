from content.models import Path
from django.core.management import BaseCommand



class Command(BaseCommand):

    def handle(self, *args, **options):
        print 'Total', Path.objects.count()
        removed = 0
        for p in Path.objects.all().iterator():
            if len(p.path) > 250:
                removed += 1
                print removed
                p.delete()
