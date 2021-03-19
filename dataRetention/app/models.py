from django.db import models
import uuid

class User(models.Model):
    email = models.EmailField(unique = True, null=False, primary_key=True)

class Stay_Data(models.Model):
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    datein = models.DateField()
    dateout = models.DateField()

class Receipt_Data(models.Model):
    id_receipt = models.CharField(unique=True, max_length = 100)
    receipt_timestamp = models.CharField(max_length = 100)
    stay_id = models.OneToOneField(Stay_Data, on_delete=models.CASCADE, primary_key=True)
  