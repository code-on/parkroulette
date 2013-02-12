import json
from content.forms import TicketSearchForm
from django.db import DatabaseError
from django.db import connection
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt


def get_pt_frequency(lat, lng, start_time=None, end_time=None, week_day=None):
    cursor = connection.cursor()
    filters = []
    filters_text = ''
    selects = ''

    if week_day:
        filters.append('EXTRACT(ISODOW FROM day) = {0}'.format(week_day))

    if start_time is not None:
        pass
        #selects = ''', EXTRACT(hour FROM start_datetime) AS start_hour,
        #               EXTRACT(minute FROM start_datetime) AS start_minute,
        #               EXTRACT(hour FROM end_datetime) AS end_hour,
        #               EXTRACT(minute FROM end_datetime) AS end_minute
        #'''
        filters.extend([
        #    'start_hour <= {0}'.format(start_time.hour),
        #    'start_minute <= {0}'.format(start_time.minute),
        #    'end_hour >= {0}'.format(end_time.hour),
        #    'end_minute >= {0}'.format(end_time.minute),
        ])

    for filter in filters:
        filters_text += ' AND {0}'.format(filter)

    sql = """
        SELECT COUNT(1) AS cnt, EXTRACT(epoch FROM (MAX(end_datetime) - MIN(start_datetime))) / 3600 AS hours{selects}
        FROM paths
        WHERE ST_DWithin(path,
            ST_GeomFromText('POINT(%s %s)', 4269),
            -- 10 meters
            0.0001){filters};
        """.format(selects=selects, filters=filters_text)
    cursor.execute(sql, (lng, lat))
    row = cursor.fetchone()

    count = row[0]

    if week_day:
        count *= 7

    #if start_time is not None:
    #    minutes = (end_time.hour - start_time.hour) * 60 + end_time.minute - start_time.minute
    #    count *= 24.0 * 60 / minutes

    hours = row[1]
    frequency = count / hours
    return frequency


def get_pt_citations(lat, lng, start_time=None, end_time=None, week_day=None):
    cursor = connection.cursor()
    filters = []
    filters_text = ''
    selects = ''

    if week_day:
        filters.append('EXTRACT(ISODOW FROM issue_datetime) = {0}'.format(week_day))

    if start_time is not None:
        #selects = ''', EXTRACT(hour FROM start_datetime) AS start_hour,
        #               EXTRACT(minute FROM start_datetime) AS start_minute,
        #               EXTRACT(hour FROM end_datetime) AS end_hour,
        #               EXTRACT(minute FROM end_datetime) AS end_minute
        #'''
        filters.extend([
            #'start_hour <= {0}'.format(start_time.hour),
            #'start_minute <= {0}'.format(start_time.minute),
            #'end_hour >= {0}'.format(end_time.hour),
            #'end_minute >= {0}'.format(end_time.minute),
        ])

    for filter in filters:
        filters_text += ' AND {0}'.format(filter)

    try:
        cursor.execute("""
            SELECT
            COUNT(*) AS cnt,
            violation,
            violation_description AS description,
            fine_amt,
            split_part(location, ' ', 2) AS street,{selects}
            ROUND(MAX(ST_Distance_Sphere(
                geopoint,
                -- libery
                ST_SetSRID(ST_Point(%s, %s), 4269)))) AS meters
            FROM tickets
            WHERE ST_DWithin(
                geopoint,
                ST_SetSRID(ST_Point(%s, %s), 4269),
                0.0002){filters}
            GROUP BY
                violation, violation_description, fine_amt, street
            ORDER BY cnt DESC;
            """.format(selects=selects, filters=filters_text), (lng, lat, lng, lat))
    except DatabaseError:
        return []
    rows = cursor.fetchall()
    return rows


def home(request, template='home.html'):
    context = {
        'form': TicketSearchForm(),
    }
    return TemplateResponse(request, template, context)


@csrf_exempt
def get_chance(request):
    response = {
        'chance': None,
        'lat': None,
        'lng': None,
        'place': None,
    }
    form = TicketSearchForm(request.REQUEST)
    if form.is_valid():
        times = form.get_time()
        week_day = form.cleaned_data['week_day']
        chance = get_pt_frequency(form.geo_data['lat'], form.geo_data['lng'], times[0], times[1], week_day)
        if chance:
            chance *= 100
        response['place'] = form.geo_data['place']
        response['lat'] = form.geo_data['lat']
        response['lng'] = form.geo_data['lng']
        response['chance'] = chance
    return HttpResponse(json.dumps(response), mimetype="application/json")

WEEK_DAYS = dict((
    ('7', 'Sunday'),
    ('1', 'Monday'),
    ('2', 'Tuesday'),
    ('3', 'Wednesday'),
    ('4', 'Thursday'),
    ('5', 'Friday'),
    ('6', 'Saturday'),
))

@csrf_exempt
def get_laws(request):
    response = {
        'laws': None,
        'lat': None,
        'lng': None,
        'place': None,
    }
    form = TicketSearchForm(request.POST)
    if form.is_valid():
        times = form.get_time()
        week_day = form.cleaned_data['week_day']
        citations = get_pt_citations(form.geo_data['lat'], form.geo_data['lng'], times[0], times[1], week_day)
        if citations:
            html_laws = render_to_string('_laws.html', {
                'citations': citations,
                'place': form.geo_data['place'],
                'start_time': times[0],
                'end_time': times[1],
                'week_day': WEEK_DAYS.get(week_day),
            })
            response['laws'] = html_laws
        response['place'] = form.geo_data['place']
        response['lat'] = form.geo_data['lat']
        response['lng'] = form.geo_data['lng']

    return HttpResponse(json.dumps(response), mimetype="application/json")