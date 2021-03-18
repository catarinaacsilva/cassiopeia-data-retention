from django.db import models
import uuid

class User_Data(models.Model):
    email = models.EmailField(unique = True, null=False, primary_key=True)
    id_receipt = models.CharField(unique=True, max_length = 100)

class Dates_Stay(models.Model):
    datein = models.DateField()
    dataout = models.DateField()
    receipt_timestamp = models.CharField(max_length = 100)
    email = models.ForeignKey(Data_Retention, on_delete=models.CASCADE)