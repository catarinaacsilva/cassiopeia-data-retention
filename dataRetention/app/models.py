from django.db import models
import uuid

class User(models.Model):
    email = models.EmailField(unique = True, null=False, primary_key=True)

class Stay(models.Model):
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    datein = models.DateField()
    dateout = models.DateField()
    deleted = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['email', 'datein', 'dateout'], name='unique_stay')]

class Stay_Receipt(models.Model):
    stayid = models.ForeignKey(Stay, on_delete=models.CASCADE)
    receiptid = models.UUIDField()

    class Meta:
        unique_together = (('stayid', 'receiptid'),)