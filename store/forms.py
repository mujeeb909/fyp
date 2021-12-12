
from django import forms

class ContactForm(forms.Form):
    Name = forms.CharField(
        required=True,
        label='Name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter Your NAME'})
    )
    Email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    Subject = forms.CharField(
        required=True,
        label='Subject',
        widget=forms.TextInput(attrs={'placeholder': 'Subject'})
    )
    Message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Comment'}))