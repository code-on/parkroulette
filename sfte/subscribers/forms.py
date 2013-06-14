from django import forms
from .models import Subscriber


class SubscrubierForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        widgets = {'email': forms.TextInput(attrs={'class': 'input-block-level'})}