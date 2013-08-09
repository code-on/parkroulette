import simplejson
from optparse import make_option
from django.core.management import BaseCommand
from content.models import Path
from precalculated.models import CachedData
from content.data import Data


CHUNK_SIZE = 1000
# distance between precalculated points in one path
STEP_DISTANCE = 0.0005
# smallest allowed distance between two precalculated points
CLOSE_DISTANCE = 0.0002


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--skip-points',
            action='store_true',
            dest='skip-points',
            default=False,
            help='Skip points calculation (only gather data for existing points)'),
        )

    def handle(self, *args, **options):
        if not options.get('skip-points'):
            print '----------------------------------------'
            print 'Calculating points on paths'
            print '----------------------------------------'
            total = Path.objects.filter(valid=True).count()
            count = 0
            for i in range(0, total, CHUNK_SIZE):
                for path in Path.objects.all()[i:i+CHUNK_SIZE].iterator():
                    length = path.path.length
                    distance = created_number = 0
                    while distance <= length:
                        location = path.path.interpolate(distance)
                        if not CachedData.objects.filter(location__distance_lt=(location, CLOSE_DISTANCE)).exists():
                            CachedData.objects.create(location=location)
                            created_number += 1
                        distance += STEP_DISTANCE
                    count += 1
                    print 'Path "%s" done. Created points %s' % (count, created_number)

        print '----------------------------------------'
        print 'Precalculating data for points with empty data'
        print '----------------------------------------'
        count = 0
        for i, pdata in enumerate(CachedData.objects.filter(json='')):
            init_lng, init_lat = pdata.location.coords
            calc = Data(address=u'Precached', distance='0.0003', init_lat=init_lat, init_lng=init_lng)
            results = {
                'address': calc.place,
                'place': calc.place,
                'lng': calc.lng,
                'lat': calc.lat,
                'chance': calc.chance,
                'get_distance_display': calc.get_distance_display(),
                'hours_count': calc.hours_count,
                'now_chance': calc.now_chance,
                'now_tickets_exp_cost': calc.now_tickets_exp_cost,
                'patrols_count': calc.patrols_count,
                'paths_heatmap': calc.paths_heatmap(),
                'paths_heatmap_legend': calc.paths_heatmap_legend(),
                'paths_heatmap_count': calc.paths_heatmap_count(),
                'tickets_count': calc.tickets_count,
                'tickets_avg_cost': calc.tickets_avg_cost,
                'tickets_exp_cost': calc.tickets_exp_cost,
                'tickets_heatmap': calc.tickets_heatmap(),
                'tickets_heatmap_legend': calc.tickets_heatmap_legend(),
                'tickets_heatmap_count': calc.tickets_heatmap_count(),
                'costs_heatmap': calc.costs_heatmap(),
                'costs_heatmap_legend': calc.costs_heatmap_legend(),
                'costs_heatmap_count': calc.costs_heatmap_count(),
            }
            pdata.json = simplejson.dumps(results)
            pdata.save()
            if i % 100 == '0':
                print '%s done...' % i
            count += 1
        print '----------------------------------------'
        print 'Precalculated %s new points, total %s' % (count, CachedData.objects.count())
        print '----------------------------------------'
