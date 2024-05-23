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

## Update
class ReleveFormUpdate(forms.ModelForm):
    class Meta:
        model = RELEVE
        fields = ['Date_operation','Date_valeur','Reference','Nature_operation','Montant_debit','Montant_credit']

class SmsFormUpdate(forms.ModelForm):
    class Meta:
        model = Sms
        fields = ['service','date','amount']

class InvoiceFormUpdate(forms.ModelForm):
    class Meta:
        model = ExtractedInfo
        fields =  ['service','date','amount']

