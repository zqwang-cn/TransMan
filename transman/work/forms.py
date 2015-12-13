#coding:utf-8
from django import forms
from .models import TransRec

class ScanForm(forms.Form):
    qrcode=forms.CharField(label=("二维码 "),required=True)

#class NewForm(forms.Form):
#    def __init__(self,mine_choices,coal_type_choices,*args,**kwargs):
#        super(NewForm,self).__init__(*args,**kwargs)
#        self.fields['mine'].choices=mine_choices
#        self.fields['coal_type'].choices=coal_type_choices
#
#    car_no=forms.CharField(label=("车牌号 "),required=True)
#    driver_name=forms.CharField(label=("驾驶员姓名 "),required=True)
#    contact_info=forms.CharField(label=("联系方式 "),required=True)
#    mine=forms.ChoiceField(label=("出发煤矿"),choices=(),required=True)
#    coal_type=forms.ChoiceField(label=("煤类型"),choices=(),required=True)

class NewForm(forms.ModelForm):
    def __init__(self,mine_queryset,*args,**kwargs):
        super(NewForm,self).__init__(*args,**kwargs)
        self.fields['mine'].queryset=mine_queryset
    class Meta:
        model=TransRec
        fields=[
            'car_no',
            'driver_name',
            'contact_info',
            'mine',
            'coal_type'
        ]
        labels={
            'car_no':'车牌号',
            'driver_name':'驾驶员姓名',
            'contact_info':'联系方式',
            'mine':'出发煤矿',
            'coal_type':'煤类型'
        }

class ArriveForm(forms.ModelForm):
    class Meta:
        model=TransRec
        fields=[
            'setoff_amount',
            'arrive_amount',
        ]
        labels={
            'setoff_amount':'矿发量',
            'arrive_amount':'实收量'
        }
