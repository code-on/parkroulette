import time
from content.views import _get_path_qs
from django.contrib.gis.geos import fromstr
from django.core.management import BaseCommand

addresses = [
    ('3231 Octavia Street', (37.802104, -122.429756)),
    ('2359 Broderick Street', (37.7920764, -122.4429737)),
    ('1106 San Francisco Bicycle Route 10', (37.7960964, -122.4135082)),
    ('491 San Francisco Bicycle Route 11', (37.7948013, -122.40153)),
    ('1549 Pine Street', (37.7894256, -122.4221134)),
    ('3122 Geary Boulevard', (37.7818716, -122.4525988)),
    ('1669 Turk Street', (37.77973, -122.436583)),
    ('1689 San Francisco Bicycle Route 32', (37.7707472, -122.4485734)),
    ('4102 San Francisco Bicycle Route 50', (37.7624209, -122.4365459)),
    ('449 San Francisco Bicycle Route 30', (37.7876188, -122.3941452)),
    ('68 Lech Walesa', (37.7778808, -122.4190177)),
    ('857 San Francisco Bicycle Route 50', (37.7344011, -122.4807539)),
    ('483 Brannan Street', (37.7787605, -122.3959895)),
    ('1084 Bryant Street', (37.7714975, -122.4083169)),
]


class Command(BaseCommand):

    def handle(self, *args, **options):
        handle_func = self.handle_point_path
        if 'tickets' in args:
            handle_func = self.handle_point_ticket

        if 'all' in args:
            for lat in xrange(3771, 3778):
                lat = '%.2f' % (lat/100.)
                for lng in xrange(12238, 12250):
                    lng = '-%.2f' % (lng/100.)
                    handle_funclat, lng)
        else:
            for (address, (lat, lng)) in addresses:
                handle_func(lat, lng)

    def handle_point_path(self, lat, lng):
        geopoint = fromstr('POINT({lng} {lat})'.format(lat=lat, lng=lng), srid=4269)
        start_time = time.time()
        list(_get_path_qs(geopoint, '0.0002').values_list('start_datetime', flat=True))
        print('{time}s: {lat} {lng}'.format(time=time.time()-start_time, lat=lat, lng=lng))

    def handle_point_ticket(self, lat, lng):
        geopoint = fromstr('POINT({lng} {lat})'.format(lat=lat, lng=lng), srid=4269)
        start_time = time.time()
        list(_get_path_qs(geopoint, '0.0002').values_list('ticket_id', flat=True))
        print('{time}s: {lat} {lng}'.format(time=time.time()-start_time, lat=lat, lng=lng))
