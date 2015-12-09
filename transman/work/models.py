from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Mine(models.Model):
    name=models.CharField(max_length=50)
    balance=models.DecimalField(max_digits=10,decimal_places=2)

class CoalType(models.Model):
    name=models.CharField(max_length=10)
    unit=models.DecimalField(max_digits=10,decimal_places=2)

class TransRec(models.Model):
    car_no=models.CharField(max_length=10)
    driver_name=models.CharField(max_length=10)
    contact_info=models.CharField(max_length=20)
    mine=models.ForeignKey(Mine)
    coal_type=models.ForeignKey(CoalType)
    setoff_amount=models.FloatField(null=True)
    arrive_amount=models.FloatField(null=True)
    setoff_time=models.DateTimeField(auto_now=True)
    arrive_time=models.DateTimeField(null=True)
    qrcode=models.CharField(max_length=10,null=True,unique=True)

class UserMine(models.Model):
    user=models.ForeignKey(User)
    mine=models.ForeignKey(Mine)
