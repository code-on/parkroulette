from django.db import DatabaseError
from django.template.response import TemplateResponse
from geopy import geocoders


def get_coordinates(address):
    g = geocoders.Google(domain='maps.google.com')
    place, (lat, lng) = g.geocode('{address}, San Francisco, CA, United States'.format(address=address))
    return lng, lat


def get_pt_frequency(coordinates):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
        SELECT cnt, hours, cnt / hours AS tickets_per_hour, start_datetime, end_datetime FROM (
            SELECT COUNT(1) AS cnt, MIN(start_datetime) AS start_datetime, MAX(end_datetime) AS end_datetime,
                EXTRACT(epoch FROM (MAX(end_datetime) - MIN(start_datetime))) / 3600 AS hours
            FROM paths
            WHERE ST_DWithin(path,
                ST_GeomFromText('POINT(%s %s)', 4269),
                -- 10 meters
                0.0001)
        ) a;""", coordinates)
    row = cursor.fetchone()
    frequency = row[2]
    return frequency


def get_pt_citations(coordinates):
    from django.db import connection
    cursor = connection.cursor()
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
                0.0002)
            GROUP BY
                violation, violation_description, fine_amt, street
            ORDER BY cnt DESC;
            """, coordinates * 2)
    except DatabaseError:
        return []
    rows = cursor.fetchall()
    return rows


def home(request, template='home.html'):
    address = request.REQUEST.get('address')
    if address:
        coordinates = get_coordinates(address)
        frequency = get_pt_frequency(coordinates)
        if frequency:
            frequency *= 100
        citations = get_pt_citations(coordinates)
    else:
        coordinates = frequency = None
        citations = []

    context = {
        'address': address,
        'coordinates': coordinates,
        'frequency': frequency,
        'citations': citations,
    }
    return TemplateResponse(request, template, context)