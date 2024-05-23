from django.db import models

# Create your models here.
class Date(models.Model):
    date = models.DateField(unique=True)

    def __str__(self):
        return str(self.date)

class RELEVE(models.Model):
    pdf = models.FileField(upload_to='pdf_forms/%Y/%m/%d/')
    date = models.ForeignKey(Date, on_delete=models.CASCADE, related_name='releves' , null=True)
    Date_operation = models.DateField(null=True)
    Date_valeur = models.DateField(null=True)
    Reference = models.CharField(max_length=250, null=True)
    Nature_operation = models.CharField(max_length=250, null=True)
    Montant_debit = models.CharField(max_length=250, null=True)
    Montant_credit = models.CharField(max_length=250, null=True)

    def __str__(self):
        return f"{self.Nature_operation}"
    

class Sms(models.Model):
    service = models.CharField(max_length=250, null=True)
    date = models.TextField(null=True)
    amount = models.CharField(max_length=250, null=True)
    date_f = models.ForeignKey(Date, on_delete=models.CASCADE, related_name='sms', null=True)

    def __str__(self):
        return f"{self.service} - {self.date} - {self.amount}"
    

class ExtractedInfo(models.Model):
    pdf = models.FileField(upload_to='pdf_forms/%Y/%m/%d/') 
    service = models.CharField(max_length=250)
    date = models.CharField(max_length=250 ,null=True)
    amount = models.CharField(max_length=250)
    date_f = models.ForeignKey(Date, on_delete=models.CASCADE, related_name='extracted_infos', null=True)    

    def __str__(self):
        return f"{self.service} - {self.date} - {self.amount}"

class Client(models.Model):
    name = models.CharField(max_length=100)

class Match(models.Model):
    #client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='matches', null=True, blank=True)  # Assuming you have a Client model
    releve = models.ForeignKey(RELEVE, on_delete=models.CASCADE, related_name='matches')
    sms = models.ForeignKey(Sms, on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    facture = models.ForeignKey(ExtractedInfo, on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    date = models.ForeignKey(Date, on_delete=models.CASCADE, related_name='matches', null=True)
    status = models.CharField(max_length=255, default='Pending') 

    def __str__(self):
        return f"Match for RELEVE {self.releve.id}"