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
from django.db.models import Max, Min
from django.utils.functional import cached_property
from django.utils.http import urlquote
from django.utils.text import slugify
from geopy import geocoders

logger = logging.getLogger()
cache = get_cache('default')
address_cache = get_cache('addresses')


def get_place_data(address):
    sl_address = slugify(address)
    data = address_cache.get(sl_address)
    if not data:
        g = geocoders.GoogleV3(domain='maps.google.com')
        data = g.geocode(
            u'{address}, San Francisco, CA, United States'.format(address=address),
            exactly_one=False
        )[0]
        address_cache.set(sl_address, data)
    return data


def _get_all_hours_count():
    if 'hours_count' not in cache:
        paths_data = Path.objects.aggregate(max=Max('day'), min=Min('day'))
        cache.set('hours_count', (paths_data['max'] - paths_data['min']).days * 24)
    return cache.get('hours_count')


def _get_heatmap_data(datetimes, url):
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
        data[0][i] = day_func(data[0][i], i-1)

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


class Data(object):
    year = 2012

    def __init__(self, address, distance, week_day=None, start_hour=None, end_hour=None):
        self.address = address
        self.distance = distance
        self.week_day = week_day
        self.start_hour = start_hour
        self.end_hour = end_hour

    def create_log(self, type):
        Log.objects.create(
            address=self.address,
            from_time=self.times[0], to_time=self.times[1], week_day=self.get_week_day_display(),
            type=type,
        )

    @property
    def place(self):
        return self.address

    def get_week_day_display(self):
        return WEEK_DAYS_DICT.get(self.week_day)

    def get_distance_display(self):
        return DISTANCE_DICT[self.distance]

    @cached_property
    def times(self):
        if not self.start_hour:
            return None, None
        return datetime.time(self.start_hour % 24), datetime.time(self.end_hour % 24)

    @property
    def start_time(self):
        return self.times[0]

    @property
    def end_time(self):
        return self.times[1]

    @cached_property
    def geo_data(self):
        start_time = time.time()
        place, (lat, lng) = get_place_data(self.address)
        logger.info('Time for getting coords by address: {}s'.format(time.time()-start_time))
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
            paths_data = Path.objects.aggregate(max=Max('day'), min=Min('day'))
            cache.set('hours_count', (paths_data['max'] - paths_data['min']).days * 24)
        return cache.get('hours_count')

    def get_path_qs(self, ignore_daytime=False):
        if not ignore_daytime:
            extra_args = [self.start_hour, self.end_hour, self.week_day]
        else:
            extra_args = []
        return _get_path_qs(self.geopoint, self.distance, *extra_args)

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
        return _get_all_hours_count()

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
            return sum(values)/len(values)
        except ZeroDivisionError:
            return


    @cached_property
    def tickets_exp_cost(self):
        return self.tickets_avg_cost * Decimal(self.patrol_frequency)

    @cached_property
    def patrol_data(self):
        ph_qs = self.get_path_qs()

        datetimes = ph_qs.values_list('start_datetime', flat=True)
        hours = map(lambda x: (x.year, x.month, x.day, x.hour), datetimes)

        pcount = count = len(set(hours))

        if count == 0:
            return {'frequency': None, 'count': count, 'hours_count': 0}

        if self.week_day:
            pcount *= 7

        if self.start_hour is not None:
            pcount *= (self.end_hour - self.start_hour)

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
        url = '{0}?text={1}&distance={2}'.format(reverse('get-laws'), urlquote(self.address), self.distance)
        tc_qs = self.get_ticket_qs(ignore_daytime=True)
        datetimes = tc_qs.values_list('issue_datetime', flat=True)
        return _get_heatmap_data(datetimes, url)

    def tickets_heatmap(self):
        return self.tickets_heatmap_data['heatmap']

    def tickets_heatmap_count(self):
        return self.tickets_heatmap_data['count']

    @cached_property
    def paths_heatmap_data(self):
        url = '{0}?text={1}&distance={2}'.format(reverse('get-laws'), urlquote(self.address), self.distance)
        ph_qs = self.get_path_qs(ignore_daytime=True)
        datetimes = ph_qs.values_list('start_datetime', flat=True)
        return _get_heatmap_data(datetimes, url)

    def paths_heatmap(self):
        return self.paths_heatmap_data['heatmap']

    def paths_heatmap_count(self):
        return self.paths_heatmap_data['count']

    @cached_property
    def paths_for_debug(self):
        if self.lat:
            return [way.tuple for way in self.get_path_qs(ignore_daytime=True).values_list('path', flat=True)]
        return []

    def get_json_paths_for_debug(self):
        return json.dumps(self.paths_for_debug)

    def get_paths_count_for_debug(self):  # Not uses
        return len(self.paths_for_debug)






