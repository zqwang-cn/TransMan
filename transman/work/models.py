from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Mine(models.Model):
    name=models.CharField(max_length=50)
    balance=models.DecimalField(max_digits=10,decimal_places=2)

class Scale(models.Model):
    name=models.CharField(max_length=50)

class UserInfo(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    mine=models.ForeignKey(Mine,null=True,blank=True)
    scale=models.ForeignKey(Scale,null=True,blank=True)

class CoalType(models.Model):
    name=models.CharField(max_length=10)
    unit=models.DecimalField(max_digits=10,decimal_places=2)

class TransRec(models.Model):
    car_no=models.CharField(max_length=10)
    driver_name=models.CharField(max_length=10)
    contact_info=models.CharField(max_length=20)
    mine=models.ForeignKey(Mine)
    coal_type=models.ForeignKey(CoalType)
    setoff_time=models.DateTimeField(auto_now=True)
    qrcode=models.CharField(max_length=10,null=True,unique=True)

    setoff_amount=models.FloatField(null=True)
    arrive_amount=models.FloatField(null=True)
    scale=models.ForeignKey(Scale,null=True)
    arrive_time=models.DateTimeField(null=True)

    payed=models.BooleanField(default=False)
    class Meta:
        permissions=(
            ('mine','mine permission'),
            ('scale','scale permission'),
            ('account','account permission'),
        )
