from django.core.management import BaseCommand

from content.models import Path

class Command(BaseCommand):
    def handle(self, *args, **options):
        handle_func = self.find_invalid
        all = Path.objects.filter(valid=True)
        for path in all:
            for point in path.path:
                if not handle_func(-122.515335, 37.818328, -122.359646, 37.700121, point[0], point[1]):
                    print 'Invalid path with id: {0}'.format(path.path_id)
                    path.valid = False
                    path.save()
                    break

    def find_invalid(self, x1, y1, x2, y2, x, y):
        if x1 <= x <= x2 and y1 >= y > y2:
            return True
        else:
            return False


