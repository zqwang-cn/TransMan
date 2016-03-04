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
    car_no=models.CharField('车牌号',max_length=10)
    driver_name=models.CharField('驾驶员姓名',max_length=10)
    contact_info=models.CharField('联系方式',max_length=20)
    mine=models.ForeignKey(Mine,verbose_name='出发煤矿')
    coal_type=models.ForeignKey(CoalType,verbose_name='煤类型')
    scale=models.ForeignKey(Scale,verbose_name='到达磅房')
    setoff_time=models.DateTimeField('出发时间',auto_now_add=True)
    qrcode=models.CharField('二维码',max_length=10,unique=True)

    setoff_amount=models.FloatField('矿发量',null=True)
    arrive_amount=models.FloatField('实收量',null=True)
    unit=models.FloatField('单价',null=True)
    opscale=models.ForeignKey(User,null=True,related_name='opscale',verbose_name='磅房操作员')
    arrive_time=models.DateTimeField('到达时间',null=True)

    card=models.ForeignKey(Card,null=True,verbose_name='油卡')
    cash=models.FloatField(null=True,verbose_name='现金')
    card_payed=models.BooleanField(default=False,verbose_name='油卡已付')
    cash_payed=models.BooleanField(default=False,verbose_name='现金已付')
    opaccount=models.ForeignKey(User,null=True,related_name='opaccount',verbose_name='账务操作员')
    def __unicode__(self):
        return self.car_no+' '+self.setoff_time.strftime('%Y-%m-%d %H:%M:%S')
    class Meta:
        verbose_name='进货记录'
        verbose_name_plural='进货记录'
        permissions=(
            ('mine','mine'),
            ('scale','scale'),
            ('account','account'),
        )

class OutRec(models.Model):
    car_no=models.CharField('车牌号',max_length=10,blank=True)
    driver_name=models.CharField('驾驶员姓名',max_length=10,blank=True)
    contact_info=models.CharField('联系方式',max_length=20,blank=True)
    scale=models.ForeignKey(Scale,verbose_name='出发磅房')
    unit=models.FloatField('单价')
    amount=models.FloatField('数量')
    setoff_time=models.DateTimeField('出发时间',auto_now_add=True)
    qrcode=models.CharField('二维码',max_length=10,blank=True)
    payed=models.BooleanField('已付款',default=False)
    def __unicode__(self):
        return self.car_no+' '+self.setoff_time.strftime('%Y-%m-%d %H:%M:%S')
    class Meta:
        verbose_name='出货记录'
        verbose_name_plural='出货记录'
