from content import HOURS_DICT
from decimal import Decimal
import json
from content.forms import TicketSearchForm
from content.models import Log, Ticket, Path
from django.core.cache import get_cache
from django.db.models import Max, Min
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from collections import Counter
from django.views.generic import TemplateView

cache = get_cache('default')


def _get_all_hours_count():
    if 'hours_count' not in cache:
        paths_data = Path.objects.aggregate(max=Max('day'), min=Min('day'))
        cache.set('hours_count', (paths_data['max'] - paths_data['min']).days * 24)
    return cache.get('hours_count')


def _get_path_qs(geopoint, distance, start_time=None, end_time=None, week_day=None):
    ph_qs = Path.objects.filter(path__dwithin=(geopoint, Decimal(distance)))

    if week_day:
        ph_qs = ph_qs.filter(day__week_day=week_day)

    if start_time is not None:
        ph_qs = ph_qs.extra(
            where=[
                'EXTRACT(hour FROM start_datetime) < %s',
                'EXTRACT(hour FROM end_datetime) >= %s',
                ],
            params=[end_time.hour, start_time.hour]
        )
    return ph_qs


def _get_ticket_qs(geopoint, distance, start_time=None, end_time=None, week_day=None):
    tc_qs = Ticket.objects.filter(geopoint__dwithin=(geopoint, Decimal(distance)))

    if week_day:
        tc_qs = tc_qs.filter(issue_datetime__week_day=week_day)

    # for now django can't filter by __hour__lt (only by __hour in dev version) //28.02.2013
    if start_time is not None:
        tc_qs = tc_qs.extra(
            where=[
                'EXTRACT(hour FROM issue_datetime) < %s',
                'EXTRACT(hour FROM issue_datetime) >= %s',
            ],
            params=[end_time.hour, start_time.hour]
        )
    return tc_qs


def get_pt_frequency(geopoint, distance, start_time=None, end_time=None, week_day=None):
    ph_qs = _get_path_qs(geopoint, distance, start_time, end_time, week_day)

    datetimes = ph_qs.values_list('start_datetime', flat=True)
    hours = map(lambda x: (x.year, x.month, x.day, x.hour), datetimes)

    pcount = count = len(set(hours))
    hours_count = _get_all_hours_count()

    if count == 0:
        return {'frequency': None, 'count': count}

    if week_day:
        pcount *= 7

    if start_time is not None:
        pcount *= (end_time.hour - start_time.hour)

    frequency = 1.0 * pcount / hours_count
    return {'frequency': frequency, 'count': count}


def get_tickets_count(geopoint, distance, start_time=None, end_time=None, week_day=None):
    tc_qs = _get_ticket_qs(geopoint, distance, start_time, end_time, week_day)
    return tc_qs.count()


def get_pt_citations(geopoint, distance, start_time=None, end_time=None, week_day=None):
    tc_qs = _get_ticket_qs(geopoint, distance, start_time, end_time, week_day)

    tc_qs = tc_qs.extra(select={
        'street': 'split_part(location, \' \', 2)'
    }).order_by('street', 'violation', 'violation_description', 'fine_amt')

    grouped_tickets = Counter(tc_qs.values_list('street', 'violation', 'violation_description', 'fine_amt'))

    table = map(lambda x: [x[1]] + list(x[0][1:]), grouped_tickets.items())
    table.sort(key=lambda x: x[0], reverse=True)
    return table


def home(request, template='home.html'):
    context = {
        'form': TicketSearchForm(),
    }
    return TemplateResponse(request, template, context)


def get_chance(request):
    form = TicketSearchForm(request.GET or None)
    context = {'form': form}
    if form.is_valid():
        times = form.times
        Log.objects.create(
            address=form.cleaned_data['text'],
            from_time=times[0], to_time=times[1], week_day=form.get_week_day_display(),
            type=Log.CHANCE,
        )
        if form.geo_data['lat']:
            distance = form.cleaned_data['distance']
            week_day = form.cleaned_data['week_day']
            fr_data = get_pt_frequency(form.geo_data['geopoint'], distance, times[0], times[1], week_day)
            chance = fr_data['frequency']
            if chance:
                chance *= 100
                tickets_count = get_tickets_count(form.geo_data['geopoint'], distance, times[0], times[1], week_day)
            else:
                tickets_count = None
            context.update({
                'distance': form.get_distance_display(),
                'chance': chance,
                'count': tickets_count,
                'patrol_count': fr_data['count'],
                'place': form.get_place(),
                'start_time': times[0],
                'end_time': times[1],
                'week_day': form.get_week_day_display(),
                'lng': form.geo_data['lng'],
                'lat': form.geo_data['lat'],
            })
    return TemplateResponse(request, 'chance.html', context)


def get_laws(request):
    form = TicketSearchForm(request.GET)
    context = {'form': form}
    if form.is_valid():
        times = form.times
        Log.objects.create(
            address=form.cleaned_data['text'],
            from_time=times[0], to_time=times[1], week_day=form.get_week_day_display(),
            type=Log.LAWS,
        )
        if form.geo_data['lat']:
            distance = form.cleaned_data['distance']
            week_day = form.cleaned_data['week_day']
            citations = get_pt_citations(form.geo_data['geopoint'], distance, times[0], times[1], week_day)
            context.update({
                'distance': form.get_distance_display(),
                'citations': citations,
                'place': form.get_place(),
                'start_time': times[0],
                'end_time': times[1],
                'week_day': form.get_week_day_display(),
                'lat': form.geo_data['lat'],
                'lng': form.geo_data['lng'],
            })
    return TemplateResponse(request, 'laws.html', context)


def _get_heatmap(datetimes):
    day_hours = map(lambda x: (x.weekday() % 7, x.hour), datetimes)
    grouped_tickets = Counter(day_hours)

    data = [['', 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'Total']]
    day_total = [0, 0, 0, 0, 0, 0, 0]
    for hour in range(24):
        hour_data = [HOURS_DICT[hour]]
        hour_total = 0
        for day in range(7):
            count = grouped_tickets.get((day, hour), 0)
            hour_data.append(count)
            day_total[day] += count
            hour_total += count
            #grouped_tickets.setdefault((day, hour), 0)
        hour_data.append(hour_total)
        data.append(hour_data)
    all_count = sum(day_total)
    data.append(['Total'] + day_total + [''])
    return data, all_count


def get_heatmap_tickets(geopoint, distance):
    tc_qs = _get_ticket_qs(geopoint, distance)
    datetimes = tc_qs.values_list('issue_datetime', flat=True)
    return _get_heatmap(datetimes)


def get_heatmap_paths(geopoint, distance):
    ph_qs = _get_path_qs(geopoint, distance)
    datetimes = ph_qs.values_list('start_datetime', flat=True)
    return _get_heatmap(datetimes)


def get_heatmap(request):
    form = TicketSearchForm(request.GET)
    context = {'form': form}
    if form.is_valid():
        Log.objects.create(
            address=form.cleaned_data['text'],
            type=Log.HEATMAP,
        )
        if form.geo_data['lat']:
            distance = form.cleaned_data['distance']
            tickets_heatmap, tickets_count = get_heatmap_tickets(form.geo_data['geopoint'], distance)
            paths_heatmap, paths_count = get_heatmap_paths(form.geo_data['geopoint'], distance)
            context.update({
                'distance': form.get_distance_display(),
                'tickets_heatmap': tickets_heatmap,
                'tickets_count': tickets_count,
                'paths_heatmap': paths_heatmap,
                'paths_count': paths_count,
                'place': form.get_place(),
                'lat': form.geo_data['lat'],
                'lng': form.geo_data['lng'],
            })
    return TemplateResponse(request, 'heatmap.html', context)