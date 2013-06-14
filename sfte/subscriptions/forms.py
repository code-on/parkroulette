import re

from django import forms
from django.core.exceptions import ValidationError
from .models import CitySubscription


class CitySubscriptionForm(forms.ModelForm):
    class Meta:
        model = CitySubscription
        widgets = {'email': forms.TextInput(attrs={'class': 'input-block-level'}),
                   'city': forms.TextInput(attrs={'class': 'input-block-level'})
                   }

    def clean_email(self):
        email = self.cleaned_data['email']
        self.email_match(email)
        city = self.cleaned_data['city']
        if CitySubscription.objects.filter(email=email).exists() and CitySubscription.objects.filter(
                city=city).exists():
            raise ValidationError("Subscribed already")
        return email

    @staticmethod
    def email_match(email):
        #only one @, at least one character before the @, before the period and after it
        match = re.match(r'^[^@]+@[^@]+\.[^@]+$', email)
        if match:
            return
        raise ValidationError("Enter a valid email address.")