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
            for path in Path.objects.all()[i:i+CHUNK_SIZE].iterator():
                old_val = path.valid
                for p in path.path:
                    if not self.is_valid(-122.514578, 37.708202, -122.357232, 37.810937, p[0], p[1]):
                        path.valid, new_val = False, False
                        removed += 1
                        print 'Invalid Path with id: {0}'.format(path.path_id)
                        print 'removed: {0}'.format(removed)
                        break
                    else:
                        path.valid, new_val = True, True
                if old_val != new_val:
                    path.save()

        print '---------------------------------'
        print 'Total valid paths after: {0}'.format(Path.objects.filter(valid=True).count())
        print 'Total invalid paths after: {0}'.format(Path.objects.filter(valid=False).count())
        print '---------------------------------'
        print '{0} entries were removed'.format(removed)

    def is_valid(self, x1, y1, x2, y2, x, y):
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
        return False


