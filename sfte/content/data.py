from collections import Counter
from decimal import Decimal
import json
import logging
import time
import datetime

from django.contrib.gis.geos import fromstr
from django.core.cache import get_cache
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from django.utils.http import urlquote
from django.utils.text import slugify
from django.conf import settings

from pygeocoder.pygeocoder import Geocoder
from googlemaps.googlemaps import GoogleMaps

from content import HOURS_DICT, WEEK_DAYS_DICT, DISTANCE_DICT
from content.models import Log
from content.query import _get_path_qs, _get_ticket_qs, _get_tickets_fine
from utils import binggeocode


logger = logging.getLogger()
cache = get_cache('default')
address_cache = get_cache('addresses')


def create_log(address, type):
    Log.objects.create(
        address=address,
        type=type,
    )


def get_place_data(address):
    sl_address = slugify(address)
    data = address_cache.get(sl_address)
    if data is None:

        if settings.GEOCODING_PROVIDER == 'google':
            result = Geocoder.geocode('{address}, San Francisco, CA, United States'.format(address=address))
            if result.route is None:
                return None, (None, None)
            if result.street_number is None:
                result.street_number = ''
            data = ('{0} {1}'.format(result.street_number, result.route), get_coordinates(result))
            address_cache.set(sl_address, data)
        elif settings.GEOCODING_PROVIDER == 'bing':
            try:
                data = binggeocode.query(address)
            except binggeocode.GeocodeError:
                return None, (None, None)
            address_cache.set(sl_address, data)
        else:
            raise NotImplementedError

    return data


def get_coordinates(result):
    origin = ', '.join([i['long_name'] for i in result.current_data['address_components'][1:]]).encode('ascii',
                                                                                                       'ignore')
    dest = ', '.join([i['long_name'] for i in result.current_data['address_components']]).encode('ascii', 'ignore')
    addr = GoogleMaps(settings.GOOGLE_API_KEY)
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
    counts = []
    for hour in range(24):
        hour_data = [hour_func(HOURS_DICT[hour], hour)]
        hour_total = 0
        for day in range(7):
            count = grouped_tickets.get((day, hour), 0)
            counts.append(count)
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
        'legend': calculate_legend(counts, 5)
    }


def _get_heatmap_paths_data(datetimes, cell_func=lambda x: x, hour_func=lambda x: x, day_func=lambda x: x,
                            count_func=lambda x: x):
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
            counts.append(count_func(count))
            hour_data.append(cell_func(count))
            day_total[day] += count
            hour_total += count
        hour_data.append(hour_func(hour_total))
        data.append(hour_data)
    all_count = sum(day_total)
    for i in range(7):
        day_total[i] = day_func(day_total[i])

    data.append(['Total'] + day_total + [''])
    return {
        'heatmap': data,
        'count': all_count,
        'legend': calculate_legend(counts, 5),
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

    def __init__(self, address, distance, week_day=None, end_hour=None, start_hour=None, init_lat=None, init_lng=None):
        self.address = address
        self.distance = distance
        self.week_day = week_day
        self.end_hour = end_hour
        self.start_hour = start_hour
        self.init_lat = init_lat
        self.init_lng = init_lng
        self.path_qs = list(self.get_path_qs()) if self.get_path_qs() else None

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
        return fromstr('POINT({lng} {lat})'.format(lat=self.lat, lng=self.lng),
                       srid=4269) if self.lat and self.address else None

    @cached_property
    def lat(self):
        return self.init_lat or self.geo_data['lat']

    @cached_property
    def lng(self):
        return self.init_lng or self.geo_data['lng']

    def get_path_qs(self):
        return _get_path_qs(self.geopoint, self.distance) if self.geopoint else None

    def get_ticket_qs(self, ignore_daytime=False):
        if not ignore_daytime:
            extra_args = [self.start_hour, self.end_hour, self.week_day]
        else:
            extra_args = []
        return _get_ticket_qs(self.geopoint, self.distance, *extra_args)

    def get_tickets_fine(self):
        return _get_tickets_fine(self.geopoint, self.distance)

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
    def years_count(self):
        return float(self.hours_count) / (24 * 365)

    @cached_property
    def tickets_count(self):
        return self.get_ticket_qs().count()

    @cached_property
    def tickets_avg_cost(self):
        # don't worked, need store "fine_amt" in decimal field, not monetary field
        #return self.get_ticket_qs().aggregate(average=Avg('fine_amt'), count=Count())['average']

        values = [x.fine_amt for x in self.get_ticket_qs() if x.fine_amt]
        values = map(lambda x: Decimal(x[1:].replace(',', '')), values)
        #temporary workaround
        try:
            return sum(values) / len(values)
        except ZeroDivisionError:
            return 0


    @cached_property
    def tickets_exp_cost(self):
        return self.tickets_avg_cost * Decimal(unicode(self.patrol_frequency))

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
        datetimes = [x.issue_datetime for x in tc_qs]
        return _get_heatmap_tickets_data(datetimes, url)

    def tickets_heatmap(self):
        return self.tickets_heatmap_data['heatmap']

    def tickets_heatmap_count(self):
        return self.tickets_heatmap_data['count']

    def tickets_heatmap_legend(self):
        return self.tickets_heatmap_data['legend']

    @cached_property
    def paths_heatmap_data(self):
        datetimes = [p.start_datetime for p in self.path_qs]
        return _get_heatmap_paths_data(datetimes)

    @cached_property
    def paths_heatmap(self):
        return self.paths_heatmap_data['heatmap']

    def paths_heatmap_count(self):
        return self.paths_heatmap_data['count']

    def paths_heatmap_legend(self):
        return self.paths_heatmap_data['legend']

    @cached_property
    def costs_heatmap_data(self):
        datetimes = [p.start_datetime for p in self.path_qs]

        def cost_function_factory(divisor):
            # $ symbol is stripped out before value is passed to colorizer
            return lambda c: '${0:.2f}'.format(
                (self.tickets_avg_cost * c) / divisor
            )

        cell_func = cost_function_factory(self.hours_count / (24 * 7))
        hour_func = cost_function_factory(self.hours_count / 24)
        day_func = cost_function_factory(self.hours_count / 7)
        # TODO: get $ symbol in legend
        count_func = lambda c: int((self.tickets_avg_cost * c) / (24 * 7))

        return _get_heatmap_paths_data(datetimes, cell_func, hour_func, day_func, count_func)

    @cached_property
    def costs_heatmap(self):
        return self.costs_heatmap_data['heatmap']

    def costs_heatmap_count(self):
        return self.costs_heatmap_data['count']

    def costs_heatmap_legend(self):
        return self.costs_heatmap_data['legend']

    @cached_property
    def now_chance(self):
        # assumes settings.TIME_ZONE is PDT
        now = datetime.datetime.now()
        # assumes heatmap has a header row and column
        hour_row = self.paths_heatmap[now.hour + 1]
        # Weekday as a decimal number, where 0 is Sunday and 6 is Saturday
        weekday = int(now.strftime('%w'))
        now_paths = hour_row[weekday + 1]
        return 100 * Decimal(now_paths) / (self.hours_count / (24 * 7))

    @cached_property
    def now_tickets_exp_cost(self):
        # assumes settings.TIME_ZONE is PDT
        now = datetime.datetime.now()
        # assumes heatmap has a header row and column
        hour_row = self.costs_heatmap[now.hour + 1]
        # Weekday as a decimal number, where 0 is Sunday and 6 is Saturday
        weekday = int(now.strftime('%w'))
        # Returns a formatted amount such as $1.76
        return hour_row[weekday + 1]

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


class PrecalculatedData(Data):
    """
    Subclass of the poorly named "Data" class that intercepts calls to
    selected methods for which we have precalculated results. Methods that
    query the database are intentionally not implemented.
    """

    def __init__(self, address, distance, precalculated_data, init_lat=None, init_lng=None):
        self.address = address
        self.distance = distance
        self.precalculated_data = precalculated_data
        self.init_lat = init_lat
        self.init_lng = init_lng

    def get_ticket_qs(self, ignore_daytime=False):
        raise NotImplementedError

    def get_path_qs(self):
        raise NotImplementedError

    @cached_property
    def hours_count(self):
        return self.precalculated_data['hours_count']

    @cached_property
    def costs_heatmap(self):
        return self.precalculated_data['costs_heatmap']

    @cached_property
    def costs_heatmap_count(self):
        return self.precalculated_data['costs_heatmap_count']

    @cached_property
    def costs_heatmap_legend(self):
        return self.precalculated_data['costs_heatmap_legend']

    @cached_property
    def tickets_heatmap(self):
        return self.precalculated_data['tickets_heatmap']

    @cached_property
    def tickets_heatmap_count(self):
        return self.precalculated_data['tickets_heatmap_count']

    @cached_property
    def tickets_heatmap_legend(self):
        return self.precalculated_data['tickets_heatmap_legend']

    @cached_property
    def paths_heatmap(self):
        return self.precalculated_data['paths_heatmap']

    @cached_property
    def paths_heatmap_count(self):
        return self.precalculated_data['paths_heatmap_count']

    @cached_property
    def paths_heatmap_legend(self):
        return self.precalculated_data['paths_heatmap_legend']

    @cached_property
    def tickets_count(self):
        return self.precalculated_data['tickets_count']

    @cached_property
    def tickets_avg_cost(self):
        return self.precalculated_data['tickets_avg_cost']

    @cached_property
    def tickets_exp_cost(self):
        return self.precalculated_data['tickets_exp_cost']

    @cached_property
    def chance(self):
        return self.precalculated_data['chance']

    @cached_property
    def patrols_count(self):
        return self.precalculated_data['patrols_count']

