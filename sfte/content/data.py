from collections import Counter
from decimal import Decimal
import json
import logging
import time
import datetime
from content import HOURS_DICT, WEEK_DAYS_DICT, DISTANCE_DICT
from content.models import Path, Log
from content.query import _get_path_qs, _get_ticket_qs
from django.contrib.gis.geos import fromstr
from django.core.cache import get_cache
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from django.utils.http import urlquote
from django.utils.text import slugify
from pygeocoder.pygeocoder import Geocoder
from googlemaps.googlemaps import GoogleMaps

logger = logging.getLogger()
cache = get_cache('default')
address_cache = get_cache('addresses')


def get_place_data(address):
    sl_address = slugify(address)
    data = address_cache.get(sl_address)
    if not data:
        result = Geocoder.geocode(u'{address}, San Francisco, CA, United States'.format(address=address))
        if not result.route:
            result = Geocoder.geocode(address)
        if not result.street_number:
            result.street_number = u''
        data = (result.street_number + ' ' + result.route, get_coordinates(result))
        address_cache.set(sl_address, data)
    return data


def get_coordinates(result):
    origin = ', '.join([i['long_name'] for i in result.current_data['address_components'][1:]]).encode('ascii', 'ignore')
    dest = ', '.join([i['long_name'] for i in result.current_data['address_components']]).encode('ascii', 'ignore')
    #my own api key, temporary hack
    addr = GoogleMaps('AIzaSyAe9JodBrnCM2Pc-2NdzieA27VCLYaERRE')
    coordinates = addr.directions(origin, dest)
    return tuple(coordinates['Directions']['Routes'][0]['End']['coordinates'][0:2])


def _get_all_hours_count(qs):
    if 'hours_count' not in cache:
        paths_data = [p.day for p in qs]
        cache.set('hours_count', (max(paths_data) - min(paths_data)).days * 24)
    return cache.get('hours_count')


def _get_heatmap_tickets_data(datetimes, url):
    day_param_func = lambda d: '&week_day={0}'.format(d + 1)
    day_func = lambda c, d: '<a href="{0}{1}">{2}</a>'.format(url, day_param_func(d), c)

    hour_param_func = lambda h: '&from_time={0}&to_time={1}'.format(h, h + 1)
    hour_func = lambda c, h: '<a href="{0}{1}">{2}</a>'.format(url, hour_param_func(h), c)

    cell_func = lambda c, d, h: '<a href="{0}{1}{2}">{3}</a>'.format(
        url, hour_param_func(h), day_param_func(d), c
    )

    day_hours = map(lambda x: (x.isoweekday() % 7, x.hour), datetimes)
    grouped_tickets = Counter(day_hours)

    data = [['', 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'Total']]
    for i in range(1, 8):
        data[0][i] = day_func(data[0][i], i - 1)

    day_total = [0, 0, 0, 0, 0, 0, 0]
    for hour in range(24):
        hour_data = [hour_func(HOURS_DICT[hour], hour)]
        hour_total = 0
        for day in range(7):
            count = grouped_tickets.get((day, hour), 0)
            hour_data.append(cell_func(count, day, hour))
            day_total[day] += count
            hour_total += count
        hour_data.append(hour_func(hour_total, hour))
        data.append(hour_data)
    all_count = sum(day_total)
    for i in range(7):
        day_total[i] = day_func(day_total[i], i)
    data.append(['Total'] + day_total + [''])
    return {
        'heatmap': data,
        'count': all_count,
    }


def _get_heatmap_paths_data(datetimes):
    day_hours = map(lambda x: (x.isoweekday() % 7, x.hour), datetimes)
    grouped_tickets = Counter(day_hours)
    data = [['', 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'Total']]
    day_total = [0, 0, 0, 0, 0, 0, 0]
    counts = []
    for hour in range(24):
        hour_data = [HOURS_DICT[hour]]
        hour_total = 0
        for day in range(7):
            count = grouped_tickets.get((day, hour), 0)
            counts.append(count)
            hour_data.append(count)
            day_total[day] += count
            hour_total += count
        hour_data.append(hour_total)
        data.append(hour_data)
    all_count = sum(day_total)
    data.append(['Total'] + day_total + [''])
    return {
        'heatmap': data,
        'count': all_count,
        'legend': calculate_legend(counts, 5)
    }


def calculate_legend(counts, steps):
    if len(counts) > 0:
        legend = [0]
        count = 0
        max_count = max(counts)
        delta = max_count / float(steps - 1)
        for i in range(steps - 2):
            count += delta
            legend.append(int(count))
        legend.append(max_count)
        return legend


class Data(object):
    year = 2012

    def __init__(self, address, distance, week_day=None, end_hour=None, start_hour=None):
        self.address = address
        self.distance = distance
        self.week_day = week_day
        self.end_hour = end_hour
        self.start_hour = start_hour
        self.path_qs = list(self.get_path_qs())

    def create_log(self, type):
        Log.objects.create(
            address=self.address,
            type=type,
        )

    @property
    def place(self):
        return self.address

    def times(self):
        if not self.start_hour:
            return None, None
        return datetime.time(self.start_hour % 24), datetime.time(self.end_hour % 24)


    def start_time(self):
        return self.times()[0]

    def end_time(self):
        return self.times()[1]

    def get_distance_display(self):
        return DISTANCE_DICT[self.distance]

    def get_week_day_display(self):
        return WEEK_DAYS_DICT.get(self.week_day)

    @cached_property
    def geo_data(self):
        start_time = time.time()
        place, (lng, lat) = get_place_data(self.address)
        self.address = place
        logger.info('Time for getting coords by address: {}s'.format(time.time() - start_time))
        return {'place': place, 'lat': lat, 'lng': lng}

    @cached_property
    def geopoint(self):
        return fromstr('POINT({lng} {lat})'.format(lat=self.lat, lng=self.lng), srid=4269) if self.lat else None

    @cached_property
    def lat(self):
        return self.geo_data['lat']

    @cached_property
    def lng(self):
        return self.geo_data['lng']

    @cached_property
    def get_all_hours_count(self):
        if 'hours_count' not in cache:
            paths_data = [p.day for p in self.path_qs]
            cache.set('hours_count', (max(paths_data) - min(paths_data)).days * 24)
        return cache.get('hours_count')

    def get_path_qs(self):
        return _get_path_qs(self.geopoint, self.distance)

    def get_ticket_qs(self, ignore_daytime=False):
        if not ignore_daytime:
            extra_args = [self.start_hour, self.end_hour, self.week_day]
        else:
            extra_args = []
        return _get_ticket_qs(self.geopoint, self.distance, *extra_args)

    def laws_list(self):
        tc_qs = self.get_ticket_qs()

        tc_qs = tc_qs.extra(select={
            'street': 'split_part(location, \' \', 2)'
        }).order_by('street', 'violation', 'violation_description', 'fine_amt')

        grouped_tickets = Counter(tc_qs.values_list('street', 'violation', 'violation_description', 'fine_amt'))

        table = map(lambda x: [x[1]] + list(x[0]), grouped_tickets.items())
        table.sort(key=lambda x: x[0], reverse=True)
        return table

    @cached_property
    def hours_count(self):
        return _get_all_hours_count(self.path_qs)

    @cached_property
    def tickets_count(self):
        return self.get_ticket_qs().count()

    @cached_property
    def tickets_avg_cost(self):
        # don't worked, need store "fine_amt" in decimal field, not monetary field
        #return self.get_ticket_qs().aggregate(average=Avg('fine_amt'), count=Count())['average']

        values = list(self.get_ticket_qs().filter(fine_amt__isnull=False).values_list('fine_amt', flat=True))
        values = map(lambda x: Decimal(x[1:]), values)
        #temporary workaround
        try:
            return sum(values) / len(values)
        except ZeroDivisionError:
            return 0


    @cached_property
    def tickets_exp_cost(self):
        return self.tickets_avg_cost * Decimal(self.patrol_frequency)

    @cached_property
    def patrol_data(self):
        datetimes = [p.start_datetime for p in self.path_qs]
        hours = map(lambda x: (x.year, x.month, x.day, x.hour), datetimes)
        pcount = count = len(set(hours))

        if count == 0:
            return {'frequency': None, 'count': count, 'hours_count': 0}

        frequency = 1.0 * pcount / self.hours_count
        return {'frequency': frequency, 'count': count}

    @property
    def chance(self):
        if self.patrol_frequency:
            return self.patrol_frequency * 100
        return None

    @cached_property
    def patrol_frequency(self):
        return self.patrol_data['frequency']

    @property
    def patrols_count(self):
        return self.patrol_data['count']

    @cached_property
    def tickets_heatmap_data(self):
        url = '{0}?address={1}&distance={2}'.format(reverse('get-laws'), urlquote(self.address), self.distance)
        tc_qs = self.get_ticket_qs(ignore_daytime=True)
        datetimes = tc_qs.values_list('issue_datetime', flat=True)
        return _get_heatmap_tickets_data(datetimes, url)

    def tickets_heatmap(self):
        return self.tickets_heatmap_data['heatmap']

    def tickets_heatmap_count(self):
        return self.tickets_heatmap_data['count']

    @cached_property
    def paths_heatmap_data(self):
        datetimes = [p.start_datetime for p in self.path_qs]
        return _get_heatmap_paths_data(datetimes)

    def paths_heatmap(self):
        return self.paths_heatmap_data['heatmap']

    def paths_heatmap_count(self):
        return self.paths_heatmap_data['count']

    def paths_heatmap_legend(self):
        return self.paths_heatmap_data['legend']

    @cached_property
    def paths_for_debug(self):
        if self.lat:
            paths = [p.path for p in self.path_qs]
            return [way.tuple for way in paths]
        return []

    def get_json_paths_for_debug(self):
        return json.dumps(self.paths_for_debug)

    def get_paths_count_for_debug(self):  # Not uses
        return len(self.paths_for_debug)






