from django import forms
from .models import *


class ReleveForm(forms.ModelForm):
    class Meta:
        model = RELEVE
        fields = ['pdf']

class DateFilterForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

class SmsForm(forms.ModelForm):
    class Meta:
        model = Sms
        fields = '__all__'

class PdfFormUploadForm(forms.ModelForm):
    class Meta:
        model = ExtractedInfo
        fields = ['pdf']  