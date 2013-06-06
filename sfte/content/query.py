from decimal import Decimal
from content.models import Ticket, Path


def _get_path_qs(geopoint, distance, start_hour=None, end_hour=None, week_day=None):
    ph_qs = Path.objects.filter(valid=True).filter(path__dwithin=(geopoint, Decimal(distance)))

    if week_day:
        ph_qs = ph_qs.filter(day__week_day=week_day)

    if start_hour is not None:
        ph_qs = ph_qs.extra(
            where=[
                'EXTRACT(hour FROM start_datetime) < %s',
                'EXTRACT(hour FROM end_datetime) >= %s',
            ],
            params=[end_hour, start_hour]
        )
    return ph_qs


def _get_ticket_qs(geopoint, distance, start_hour=None, end_hour=None, week_day=None):
    tc_qs = Ticket.objects.filter(geopoint__dwithin=(geopoint, Decimal(distance)))

    if week_day:
        tc_qs = tc_qs.filter(issue_datetime__week_day=week_day)

    # for now django can't filter by __hour__lt (only by __hour in dev version) //28.02.2013
    if start_hour is not None:
        tc_qs = tc_qs.extra(
            where=[
                'EXTRACT(hour FROM issue_datetime) < %s',
                'EXTRACT(hour FROM issue_datetime) >= %s',
            ],
            params=[end_hour, start_hour]
        )
    return tc_qs
