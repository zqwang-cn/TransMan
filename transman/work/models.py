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
    user=models.OneToOneField(User,on_delete=models.CASCADE,verbose_name='用户')
    class Meta:
        verbose_name='磅房'
        verbose_name_plural='磅房'
    def __unicode__(self):
        return self.name

#class UserInfo(models.Model):
#    user=models.OneToOneField(User,on_delete=models.CASCADE,verbose_name='用户')
#    mine=models.ForeignKey(Mine,null=True,blank=True,verbose_name='所属煤矿')
#    scale=models.ForeignKey(Scale,null=True,blank=True,verbose_name='所属磅房')
#    class Meta:
#        verbose_name='用户属性'
#        verbose_name_plural='用户属性'
#    def __unicode__(self):
#        return self.user.username

class CoalType(models.Model):
    name=models.CharField('名称',max_length=10)
    class Meta:
        verbose_name='煤类型'
        verbose_name_plural='煤类型'
    def __unicode__(self):
        return self.name

class CardValue(models.Model):
    value=models.PositiveIntegerField('价值')
    class Meta:
        verbose_name='油卡'
        verbose_name_plural='油卡'
    def __unicode__(self):
        return str(self.value)

class TransRec(models.Model):
    car_no=models.CharField(max_length=10)
    driver_name=models.CharField(max_length=10)
    contact_info=models.CharField(max_length=20)
    mine=models.ForeignKey(Mine)
    coal_type=models.ForeignKey(CoalType)
    setoff_time=models.DateTimeField(auto_now_add=True)
    qrcode=models.CharField(max_length=10,null=True,unique=True)

    setoff_amount=models.FloatField(null=True)
    arrive_amount=models.FloatField(null=True)
    scale=models.ForeignKey(Scale,null=True)
    arrive_time=models.DateTimeField(null=True)

    card=models.ForeignKey(CardValue,null=True)
    cash=models.FloatField(null=True)
    class Meta:
        permissions=(
            ('mine','mine'),
            ('scale','scale'),
            ('account','account'),
        )
