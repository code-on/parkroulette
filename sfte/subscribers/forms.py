from django import forms
from django.core.exceptions import ValidationError
from .models import Subscriber


class SubscrubierForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        widgets = {'email': forms.TextInput(attrs={'class': 'input-block-level'})}

    def clean_email(self):
        email = self.cleaned_data['email']
        if Subscriber.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email