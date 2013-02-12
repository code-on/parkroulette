import datetime
from django import forms
from django.utils.functional import cached_property
from geopy import geocoders


class TicketSearchForm(forms.Form):
    WEEK_DAY_CHOICES = (
        ('', '--------'),
        (7, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )
    HOUR_CHOICES = (
        ('', '--------'),
        (0, '12AM'), (1, '1AM'), (2, '2AM'), (3, '3AM'), (4, '4AM'), (5, '5AM'),
        (6, '6AM'), (7, '7AM'), (8, '8AM'), (9, '9AM'), (10, '10AM'), (11, '11AM'),
        (12, '12PM'), (13, '1PM'), (14, '2PM'), (15, '3PM'), (16, '4PM'), (17, '5PM'),
        (18, '6PM'), (19, '7PM'), (20, '8PM'), (21, '9PM'), (22, '10PM'), (23, '11PM'),
    )
    text = forms.CharField(
        label='Type your parking address:',
        widget=forms.TextInput(attrs={'placeholder': 'f.e. 1234 Market st'})
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

    @cached_property
    def geo_data(self):
        g = geocoders.GoogleV3(domain='maps.google.com')
        place, (lat, lng) = g.geocode(
            u'{address}, San Francisco, CA, United States'.format(address=self.cleaned_data['text']),
            exactly_one=False
        )[0]
        return {'place': place, 'lat': lat, 'lng': lng}

    def get_time(self):
        # ToDo: check for empty fields
        if not self.cleaned_data['from_time'] or not self.cleaned_data['to_time']:
            return None, None
        return datetime.time(int(self.cleaned_data['from_time'])), datetime.time(int(self.cleaned_data['to_time']))