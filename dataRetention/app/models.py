from django.db import models
import uuid

class Data_Retention(models.Model):
    data_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = 
    event_id = 
    state_id = 
    id_receipt =

class Dates(models.Model):
    datein =
    dataout =
    event_created =
    state_last_changed =
    state_last_updated =
    state_created =
    receipt_timestamp = 

