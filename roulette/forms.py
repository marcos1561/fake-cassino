from django import forms

class MyForm(forms.Form):
    entry_field = forms.CharField(label='Entry Field')