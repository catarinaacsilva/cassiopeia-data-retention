import uuid
from enum import Enum
from django.db import models
from jsonfield import JSONField


class User(models.Model):
    email = models.EmailField(unique = True, null=False, primary_key=True)


class State(Enum):
    av = 'Available'
    re = 'Requested'
    de = 'Deleted'

    def __str__(self):
        return self.value

class Stay(models.Model):
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    datein = models.DateField()
    dateout = models.DateField()
    choices = [(tag, tag.value) for tag in State]
    state = models.CharField(max_length=16, choices=[(tag, tag.value) for tag in State], default=State.av)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['email', 'datein', 'dateout'], name='unique_stay')]


class Stay_Receipt(models.Model):
    stayid = models.ForeignKey(Stay, on_delete=models.CASCADE)
    receiptid = models.UUIDField()

    class Meta:
        unique_together = (('stayid', 'receiptid'),)


class Stay_Data_Con(models.Model):
    stayid = models.OneToOneField(Stay, on_delete=models.CASCADE, primary_key=True)
    conn = JSONField()