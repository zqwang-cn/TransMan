#coding:utf-8
from django import forms

class ScanForm(forms.Form):
    qrcode=forms.CharField(label=("二维码 "),required=True)
