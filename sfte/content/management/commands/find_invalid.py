from django.core.management import BaseCommand

from content.models import Path


CHUNK_SIZE = 1000


class Command(BaseCommand):
    def handle(self, *args, **options):
        total = Path.objects.filter(valid=True).count()
        total_invalid = Path.objects.filter(valid=False).count()
        removed = 0
        print 'Total valid paths before: {0}'.format(total)
        print 'Total invalid paths before: {0}'.format(total_invalid)

        for i in range(0, total, CHUNK_SIZE):
            print '----{0}----'.format(i)
            for path in Path.objects.filter(valid=True)[i:i+CHUNK_SIZE].iterator():
                    for p in path.path:
                        if self.is_valid(-122.515335, 37.818328, -122.359646, 37.700121, p[0], p[1]):
                            path.valid = False
                            path.save()
                            removed += 1
                            print 'Invalid Path with id: {0}'.format(path.path_id)
                            print 'removed: {0}'.format(removed)
                            break

        print '---------------------------------'
        print 'Total valid paths after: {0}'.format(Path.objects.filter(valid=True).count())
        print 'Total invalid paths after: {0}'.format(Path.objects.filter(valid=False).count())
        print '---------------------------------'
        print '{0} entries were removed'.format(removed)

    def is_valid(self, x1, y1, x2, y2, x, y):
        if x1 <= x <= x2 and y1 >= y > y2:
            return True
        return False


