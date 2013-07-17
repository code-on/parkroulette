from decimal import Decimal
from content.models import Ticket, Path


def _get_path_qs(geopoint, distance):
    ph_qs = Path.objects.filter(valid=True).filter(path__dwithin=(geopoint, Decimal(distance)))
    return ph_qs


def _get_ticket_qs(geopoint, distance):
    tc_qs = Ticket.objects.filter(geopoint__dwithin=(geopoint, Decimal(distance)))
    return tc_qs
