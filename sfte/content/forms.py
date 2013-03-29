import datetime
import logging
import time
from content import HOURS_DICT
from django import forms
from django.contrib.gis.geos import fromstr
from django.utils.functional import cached_property
from geopy import geocoders

logger = logging.getLogger()

WEEK_DAYS = (
    ('1', 'Sunday'),
    ('2', 'Monday'),
    ('3', 'Tuesday'),
    ('4', 'Wednesday'),
    ('5', 'Thursday'),
    ('6', 'Friday'),
    ('7', 'Saturday'),
)

WEEK_DAYS_DICT = dict(WEEK_DAYS)

DISTANCE_DICT = dict((
    ('0.0001', '10'), ('0.0002', '20'), ('0.0003', '30'),
    ('0.0004', '40'), ('0.0005', '50'), ('0.001', '100'),
))


class TicketSearchForm(forms.Form):
    WEEK_DAY_CHOICES = (
        ('', '--------'),
    ) + WEEK_DAYS
    HOUR_CHOICES = (('', '--------'),) + tuple(HOURS_DICT.items())
    DISTANCE_CHOICES = (
        ('0.0001', '10m'), ('0.0002', '20m'), ('0.0003', '30m'),
        ('0.0004', '40m'), ('0.0005', '50m'), ('0.001', '100m'),
    )
    text = forms.CharField(
        label='Type your parking address:',
        widget=forms.TextInput(attrs={'placeholder': 'f.e. 1234 Market st'})
    )
    distance = forms.ChoiceField(
        initial=DISTANCE_CHOICES[1][0],
        choices=DISTANCE_CHOICES,
        label='Distance',
        widget=forms.Select(attrs={'class': 'small-widget'}),
    )
    from_time = forms.ChoiceField(
        choices=HOUR_CHOICES,
        label='From time',
        widget=forms.Select(attrs={'class': 'small-widget'}),
        required=False,
    )
    to_time = forms.ChoiceField(
        choices=HOUR_CHOICES,
        label='To time',
        widget=forms.Select(attrs={'class': 'small-widget'}),
        required=False,
    )
    week_day = forms.ChoiceField(
        choices=WEEK_DAY_CHOICES,
        label='Week day',
        widget=forms.Select(attrs={'class': 'small-widget'}),
        required=False,
    )

    def clean(self):
        data = self.cleaned_data
        if self.cleaned_data['from_time'] and self.cleaned_data['to_time']:
            ft, tt = self.hours
            if ft >= tt:
                raise forms.ValidationError('"To time" must be later than "From time"')
        return data

    @cached_property
    def geo_data(self):
        start_time = time.time()
        g = geocoders.GoogleV3(domain='maps.google.com')
        place, (lat, lng) = g.geocode(
            u'{address}, San Francisco, CA, United States'.format(address=self.cleaned_data['text']),
            exactly_one=False
        )[0]
        logger.info('Time for getting coords by address: {}s'.format(time.time()-start_time))
        geopoint = fromstr('POINT({lng} {lat})'.format(lat=lat, lng=lng), srid=4269) if lat else None
        return {'place': place, 'lat': lat, 'lng': lng, 'geopoint': geopoint}

    def get_week_day_display(self):
        return WEEK_DAYS_DICT.get(self.cleaned_data.get('week_day'))

    def get_distance_display(self):
        return DISTANCE_DICT[self.cleaned_data['distance']]

    def get_place(self):
        #return self.geo_data['place']
        return self.cleaned_data['text']

    @cached_property
    def hours(self):
        ft, tt = self.cleaned_data['from_time'], self.cleaned_data['to_time']
        if not ft and not tt:
            return None, None
        if ft and not tt:
            tt = 24
        elif tt and not ft:
            ft = 0
        ft, tt = int(ft), int(tt)
        return ft, tt

    @cached_property
    def times(self):
        start_hour, end_hour = self.hours
        if not start_hour:
            return None, None
        return datetime.time(start_hour % 24), datetime.time(end_hour % 24)

    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[self.add_prefix(key)] = self.error_class(value).as_text()
        return output