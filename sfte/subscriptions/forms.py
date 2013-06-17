import re

from django import forms
from django.forms.util import ErrorList
from django.core.exceptions import ValidationError
from .models import CitySubscription


class CitySubscriptionForm(forms.ModelForm):
    class Meta:
        model = CitySubscription
        widgets = {'email': forms.TextInput(attrs={'class': 'input-block-level'}),
                   'city': forms.TextInput(attrs={'class': 'input-block-level'})
        }

    def not_exists(self):
        if 'email' and 'city' in self.cleaned_data:
            email = self.cleaned_data['email']
            city = self.cleaned_data['city']
            if CitySubscription.objects.filter(email=email).exists() and CitySubscription.objects.filter(
                    city=city).exists():
                msg = u"Already in database"
                self._errors["city"] = ErrorList([msg])
                return ''
        return True