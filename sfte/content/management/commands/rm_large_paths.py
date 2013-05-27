from content.models import Path
from django.core.management import BaseCommand


CHUNK_SIZE = 1000


class Command(BaseCommand):

    def handle(self, *args, **options):
        total = Path.objects.count()
        print 'Total', total
        removed = 0

        for i in range(0, total, CHUNK_SIZE):
            print '---- %d' % i
            for p in Path.objects.all()[i:i+CHUNK_SIZE].iterator():
                if len(p.path) > 250:
                    removed += 1
                    p.delete()
                print '%d (%d)' % (p.path_id, removed)