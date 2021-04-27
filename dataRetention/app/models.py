from django.db import models
import uuid

class User(models.Model):
    email = models.EmailField(unique = True, null=False, primary_key=True)

class Stay_Data(models.Model):
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    datein = models.DateField()
    dateout = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email', 'datein', 'dateout'], name='unique_stay')
        ]

class Receipt_Data(models.Model):
    id_receipt = models.UUIDField(default=uuid.uuid4, unique=True)
    stay_id = models.OneToOneField(Stay_Data, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id_receipt', 'stay_id'], name='unique_receipt')
        ]

class Policy_Consent(models.Model):
    #email = models.ForeignKey(User, on_delete=models.CASCADE)
    stay_id = models.OneToOneField(Stay_Data, on_delete=models.CASCADE)
    consent = models.BooleanField()
    policy_id = models.CharField(unique=False, max_length = 100)
    timestamp = models.DateField()
