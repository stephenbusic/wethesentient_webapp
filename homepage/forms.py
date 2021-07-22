from .models import Subscriber
from django import forms

class SubscriberForm(forms.ModelForm):

    class Meta:
        model = Subscriber
        fields = ('email',)