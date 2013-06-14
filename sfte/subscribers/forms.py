import re

from django import forms
from django.core.exceptions import ValidationError
from .models import Subscriber


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        widgets = {'email': forms.TextInput(attrs={'class': 'input-block-level'})}

    def clean_email(self):
        email = self.cleaned_data['email']
        self.email_match(email)
        if Subscriber.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    @staticmethod
    def email_match(email):
        #only one @, at least one character before the @, before the period and after it
        match = re.match(r'^[^@]+@[^@]+\.[^@]+$', email)
        if match:
            return
        raise ValidationError("Enter a valid email address.")