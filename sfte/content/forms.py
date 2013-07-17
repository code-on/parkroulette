from content import HOURS_DICT, WEEK_DAYS
from content.data import Data
from django import forms
from django.utils.functional import cached_property


class TicketSearchForm(forms.Form):
    DISTANCE_CHOICES = (
        ('0.00015', '50ft (15m)'),
        ('0.0003', '100ft (30m)'),
        ('0.0006', '200ft (60m)'),
    )
    address = forms.CharField(
        label='Type your parking address:',
        widget=forms.TextInput(
            attrs={'type': 'text', 'class': 'input-block-level input-medium', 'placeholder': 'f.e. 1234 Market st'})
    )
    distance = forms.ChoiceField(
        initial=DISTANCE_CHOICES[0][0],
        choices=DISTANCE_CHOICES,
        label='Distance',
        widget=forms.Select(attrs={'class': 'small-widget'}),
    )

    def clean(self):
        return self.cleaned_data

    def get_data_object(self, start_hour=None, end_hour=None, week_day=None):
        return Data(
            address=self.cleaned_data['address'],
            distance=self.cleaned_data['distance'],
            start_hour=start_hour,
            end_hour=end_hour,
            week_day=week_day
        )

    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[self.add_prefix(key)] = self.error_class(value).as_text()
        return output