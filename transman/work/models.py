#coding:utf-8
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Mine(models.Model):
    name=models.CharField('名称',max_length=50)
    user=models.ForeignKey(User,verbose_name='用户')
    class Meta:
        verbose_name='煤矿'
        verbose_name_plural='煤矿'
    def __unicode__(self):
        return self.name

class Scale(models.Model):
    name=models.CharField('名称',max_length=50)
    #user=models.OneToOneField(User,on_delete=models.CASCADE,verbose_name='用户')
    class Meta:
        verbose_name='磅房'
        verbose_name_plural='磅房'
    def __unicode__(self):
        return self.name

class UserScaleInfo(models.Model):
    user=models.OneToOneField(User,verbose_name='用户')
    scale=models.ForeignKey(Scale,null=True,verbose_name='磅房')
    class Meta:
        verbose_name='用户所属磅房'
        verbose_name_plural='用户所属磅房'
    def __unicode__(self):
        return str(self.user)+'_'+self.scale.name

class CoalType(models.Model):
    name=models.CharField('名称',max_length=10)
    class Meta:
        verbose_name='煤类型'
        verbose_name_plural='煤类型'
    def __unicode__(self):
        return self.name

class Card(models.Model):
    value=models.PositiveIntegerField('价值')
    balance=models.PositiveIntegerField('余量',default=0)
    class Meta:
        verbose_name='油卡'
        verbose_name_plural='油卡'
    def __unicode__(self):
        return str(self.value)

class Balance(models.Model):
    balance=models.FloatField(default=0)
    class Meta:
        verbose_name='余额'
        verbose_name_plural='余额'
    def __unicode__(self):
        return str(self.balance)

class TransRec(models.Model):
    car_no=models.CharField(max_length=10)
    driver_name=models.CharField(max_length=10)
    contact_info=models.CharField(max_length=20)
    mine=models.ForeignKey(Mine)
    coal_type=models.ForeignKey(CoalType)
    scale=models.ForeignKey(Scale)
    setoff_time=models.DateTimeField(auto_now_add=True)
    qrcode=models.CharField(max_length=10,unique=True)

    setoff_amount=models.FloatField(null=True)
    arrive_amount=models.FloatField(null=True)
    unit=models.FloatField(null=True)
    opscale=models.ForeignKey(User,null=True,related_name='opscale')
    arrive_time=models.DateTimeField(null=True)

    card=models.ForeignKey(Card,null=True)
    cash=models.FloatField(null=True)
    card_payed=models.BooleanField(default=False)
    cash_payed=models.BooleanField(default=False)
    opaccount=models.ForeignKey(User,null=True,related_name='opaccount')
    class Meta:
        permissions=(
            ('mine','mine'),
            ('scale','scale'),
            ('account','account'),
        )

class OutRec(models.Model):
    car_no=models.CharField(max_length=10,blank=True)
    driver_name=models.CharField(max_length=10,blank=True)
    contact_info=models.CharField(max_length=20,blank=True)
    scale=models.ForeignKey(Scale)
    unit=models.FloatField()
    amount=models.FloatField()
    setoff_time=models.DateTimeField(auto_now_add=True)
    qrcode=models.CharField(max_length=10,blank=True)
    payed=models.BooleanField(default=False)
