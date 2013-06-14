from django import forms
from .models import CitySubscription


class CitySubscriptionForm(forms.ModelForm):
    class Meta:
        model = CitySubscription
        widgets = {'email': forms.TextInput(attrs={'class': 'input-block-level'}),
                   'city': forms.TextInput(attrs={'class': 'input-block-level'})
                   }