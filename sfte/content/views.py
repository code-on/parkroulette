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
    if week_day:
        filters.append('EXTRACT(ISODOW FROM day) = {0}'.format(week_day))

    if start_time is not None:
        filters.extend([
            'EXTRACT(hour FROM start_datetime) < {0}'.format(end_time.hour),
            'EXTRACT(hour FROM end_datetime) >= {0}'.format(start_time.hour),
        ])

    for f in filters:
        filters_text += ' AND {0}'.format(f)

    sql = """
        SELECT COUNT(1) AS cnt, EXTRACT(epoch FROM (MAX(end_datetime) - MIN(start_datetime))) / 3600 AS hours
        FROM paths
        WHERE ST_DWithin(path,
            ST_GeomFromText('POINT(%s %s)', 4269),
            -- 10 meters
            0.0001){filters};
        """.format(filters=filters_text)
    cursor.execute(sql, (lng, lat))
    row = cursor.fetchone()

    count = row[0]

    if week_day:
        count *= 7

    if start_time is not None:
        hours = end_time.hour - start_time.hour
        count *= 24.0 / hours

    hours = row[1]
    frequency = count / hours
    return {'frequency': frequency, 'count': count}


def get_tickest_count(lat, lng, start_time=None, end_time=None, week_day=None):
    cursor = connection.cursor()
    filters = []
    filters_text = ''

    if week_day:
        filters.append('EXTRACT(ISODOW FROM issue_datetime) = {0}'.format(week_day))

    if start_time is not None:
        filters.extend([
            'EXTRACT(hour FROM issue_datetime) < {0}'.format(end_time.hour),
            'EXTRACT(hour FROM issue_datetime) >= {0}'.format(start_time.hour),
        ])

    for f in filters:
        filters_text += ' AND {0}'.format(f)

    cursor.execute("""
            SELECT
            COUNT(*)
            FROM tickets
            WHERE ST_DWithin(
                geopoint,
                ST_SetSRID(ST_Point(%s, %s), 4269),
                0.0002){filters}
            """.format(filters=filters_text), (lng, lat))
    row = cursor.fetchone()
    return row[0]

def get_pt_citations(lat, lng, start_time=None, end_time=None, week_day=None):
    cursor = connection.cursor()
    filters = []
    filters_text = ''

    if week_day:
        filters.append('EXTRACT(ISODOW FROM issue_datetime) = {0}'.format(week_day))

    if start_time is not None:
        filters.extend([
            'EXTRACT(hour FROM issue_datetime) < {0}'.format(end_time.hour),
            'EXTRACT(hour FROM issue_datetime) >= {0}'.format(start_time.hour),
        ])

    for f in filters:
        filters_text += ' AND {0}'.format(f)

    try:
        cursor.execute("""
            SELECT
            COUNT(*) AS cnt,
            violation,
            violation_description AS description,
            fine_amt,
            split_part(location, ' ', 2) AS street,
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
            """.format(filters=filters_text), (lng, lat, lng, lat))
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
        'html': None,
    }
    form = TicketSearchForm(request.REQUEST)
    if form.is_valid() and form.geo_data['lat']:
        times = form.get_time()
        week_day = form.cleaned_data['week_day']
        fr_data = get_pt_frequency(form.geo_data['lat'], form.geo_data['lng'], times[0], times[1], week_day)
        chance = fr_data['frequency']
        if chance:
            chance *= 100
        response['html'] = render_to_string('_chance.html', {
            'chance': chance,
            'count': get_tickest_count(form.geo_data['lat'], form.geo_data['lng'], times[0], times[1], week_day),
            'patrol_count': fr_data['count'],
            'place': form.get_place(),
            'start_time': times[0],
            'end_time': times[1],
            'week_day': form.get_week_day(),
            'lat': form.geo_data['lat'],
            'lng': form.geo_data['lng'],
        })
    else:
        response['html'] = 'Sorry, we cannot find coordinates of this address.'
    return HttpResponse(json.dumps(response), mimetype="application/json")


@csrf_exempt
def get_laws(request):
    response = {
        'html': None,
    }
    form = TicketSearchForm(request.POST)
    if form.is_valid() and form.geo_data['lat']:
        times = form.get_time()
        week_day = form.cleaned_data['week_day']
        citations = get_pt_citations(form.geo_data['lat'], form.geo_data['lng'], times[0], times[1], week_day)
        response['html'] = render_to_string('_laws.html', {
            'citations': citations,
            'place': form.get_place(),
            'start_time': times[0],
            'end_time': times[1],
            'week_day': form.get_week_day(),
            'lat': form.geo_data['lat'],
            'lng': form.geo_data['lng'],
        })
    else:
        response['html'] = 'Sorry, we cannot find coordinates of this address.'
    return HttpResponse(json.dumps(response), mimetype="application/json")