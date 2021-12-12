
from django import forms
from .models import *

class reviewform(forms.ModelForm):
    class Meta:
        model = review
        fields = ['review_title', 'review', 'rating']
        widgets = {
            'item': forms.HiddenInput(),
            'user':forms.HiddenInput(),
            'review_predict':forms.HiddenInput()
        }