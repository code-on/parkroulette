from content import HOURS_DICT, WEEK_DAYS
from content.data import Data
from django import forms
from django.utils.functional import cached_property


class TicketSearchForm(forms.Form):
    WEEK_DAY_CHOICES = (
        ('', '--------'),
    ) + WEEK_DAYS
    HOUR_CHOICES = (('', '--------'),) + tuple(HOURS_DICT.items())
    DISTANCE_CHOICES = (
        ('0.0001', '10m'), ('0.0002', '20m'), ('0.0003', '30m'),
        ('0.0004', '40m'), ('0.0005', '50m'), ('0.001', '100m'),
    )
    address = forms.CharField(
        label='Type your parking address:',
        widget=forms.TextInput(
            attrs={'type': 'text', 'class': 'input-block-level input-medium', 'placeholder': 'f.e. 1234 Market st'})
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

    def get_data_object(self):
        return Data(
            address=self.cleaned_data['address'],
            distance=self.cleaned_data['distance'],
            week_day=self.cleaned_data['week_day'],
            start_hour=self.hours[0],
            end_hour=self.hours[1],
        )

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

    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[self.add_prefix(key)] = self.error_class(value).as_text()
        return output