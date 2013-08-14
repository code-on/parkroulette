from decimal import Decimal
from content.models import Ticket, Path


def _get_paths_cache_name(geopoint, distance):
    return 'paths:%s,%s,%s' % (geopoint._cs[0][0], geopoint._cs[0][1], distance)


def _get_tickets_cache_name(geopoint, distance, week_day=None):
    if week_day:
        return '%s,%s,%s,%s' % (week_day, geopoint._cs[0][0], geopoint._cs[0][1], distance)
    return 'tickets:%s,%s,%s' % (geopoint._cs[0][0], geopoint._cs[0][1], distance)


def _get_path_qs(geopoint, distance):
    return Path.objects.filter(valid=True, path__dwithin=(geopoint, Decimal(distance))).only('start_datetime', 'day')


def _get_ticket_qs(geopoint, distance, start_hour=None, end_hour=None, week_day=None):
    if week_day:
        tc_qs = Ticket.objects.filter(geopoint__dwithin=(geopoint, Decimal(distance)), issue_datetime__week_day=week_day).only('fine_amt')
        # for now django can't filter by __hour__lt (only by __hour in dev version) //28.02.2013
    else:
        tc_qs = Ticket.objects.filter(geopoint__dwithin=(geopoint, Decimal(distance))).only('fine_amt', 'issue_datetime')
    if start_hour is not None:
        tc_qs = tc_qs.extra(
            where=[
                'EXTRACT(hour FROM issue_datetime) < %s',
                'EXTRACT(hour FROM issue_datetime) >= %s',
            ],
            params=[end_hour, start_hour]
        )
    return tc_qs


def _get_tickets_fine(geopoint, distance):
    return Ticket.objects.filter(geopoint__dwithin=(geopoint, Decimal(distance)), fine_amt__isnull=False).values_list('fine_amt', flat=True)
