from django.db import models

# Create your models here.
class TransRec(models.Model):
    car_no=models.CharField(max_length=10)
    driver_name=models.CharField(max_length=10)
    contact_info=models.CharField(max_length=20)
    setoff_amount=models.FloatField(null=True)
    arrive_amount=models.FloatField(null=True)
    setoff_time=models.DateTimeField(auto_now=True)
    arrive_time=models.DateTimeField(null=True)

