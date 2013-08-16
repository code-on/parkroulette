from decimal import Decimal
import simplejson
from django.conf import settings
from django import forms
from django.contrib.gis.geos import fromstr
from django.utils.functional import cached_property
from content import HOURS_DICT, WEEK_DAYS
from content.data import Data, get_place_data
from precalculated.models import CachedData


class TicketSearchForm(forms.Form):
    DISTANCE_CHOICES = (
        #('0.00015', '50ft (15m)'),
        ('0.0003', '100ft (30m)'),
        ('0.0006', '200ft (60m)'),
        ('0.0009', '300ft (90m)'),
    )
    address = forms.CharField(
        label='Parking address',
        widget=forms.TextInput(
            attrs={'type': 'text', 'class': 'input-block-level input-medium', 'placeholder': 'e.g. 1234 Market St'})
    )
    distance = forms.ChoiceField(
        initial=DISTANCE_CHOICES[0][0],
        choices=DISTANCE_CHOICES,
        label='Within distance',
        widget=forms.Select(attrs={'class': 'small-widget'}),
    )

    def clean(self):
        return self.cleaned_data

    def get_data_object(self, start_hour=None, end_hour=None, week_day=None):
        if settings.ENABLE_PRECALCULATED and not (start_hour or end_hour or week_day):
            address = self.cleaned_data['address']
            distance = round(100000 * float(self.cleaned_data['distance']))

            place, (lng, lat) = get_place_data(address)
            geopoint = fromstr('POINT({lng} {lat})'.format(lat=lat, lng=lng), srid=4269) if lat and address else None

            cache = None
            if geopoint:
                cache = CachedData.objects.exclude(json='').filter(location__distance_lt=(geopoint, distance))
            if cache:
                result = simplejson.loads(cache[0].json)
                result['place'] = '%s (precached)' % place
                result['address'] = address
                new_heatmap = []
                for sublist in result['tickets_heatmap']:
                    new_sublist = []
                    for item in sublist:
                        item = item.replace('Precached', address)
                        new_sublist.append(item)
                    new_heatmap.append(new_sublist)
                result['tickets_heatmap'] = new_heatmap
                return result

        return Data(
            address=self.cleaned_data['address'],
            distance=self.cleaned_data['distance'],
            start_hour=self.hours(start_hour),
            end_hour=self.hours(end_hour),
            week_day=week_day
        )

    def hours(self, hour):
        if hour is None:
            return None
        return int(hour)

    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[self.add_prefix(key)] = self.error_class(value).as_text()
        return output