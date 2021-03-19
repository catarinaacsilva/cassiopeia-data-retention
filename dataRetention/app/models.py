from django.db import models
import uuid

class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

class Stay_Data(models.Model):
    email = models.EmailField(unique = True, null=False, primary_key=True)
    datein = models.DateField()
    dateout = models.DateField()

class Receipt_Data(models.Model):
    id_receipt = models.CharField(unique=True, max_length = 100)
    receipt_timestamp = models.CharField(max_length = 100)
    email = models.OneToOneField(Stay_Data, on_delete=models.CASCADE, primary_key=True)
  