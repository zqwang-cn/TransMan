from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import TransRec,CoalType,Mine,Scale,Shipment,Balance
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import random,string,datetime
from django.contrib.auth.decorators import permission_required,login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from .forms import ScanForm,NewForm,ArriveForm,PayForm

# Create your views here.
@login_required
def list(request):
    user=request.user
    if user.has_perm('work.account'):
        all_recs=TransRec.objects.order_by('-id').all()
    elif user.has_perm('work.mine'):
        all_recs=TransRec.objects.filter(mine__user=user).order_by('-id')
    elif user.has_perm('work.scale'):
        all_recs=TransRec.objects.filter(scale__user=user).order_by('-id')
    paginator=Paginator(all_recs,5)
    page=request.GET.get('page')
    try:
        recs=paginator.page(page)
    except PageNotAnInteger:
        recs=paginator.page(1)
    except EmptyPage:
        recs=paginator.page(paginator.num_pages)
    return render(request,'work/list.html',{'recs':recs})
    print len(recs)

@permission_required('work.mine',raise_exception=True)
def new(request):
    user=request.user
    if request.method=='POST':
        form=NewForm(Mine.objects.filter(user=user),request.POST)
        if form.is_valid():
            qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
            while TransRec.objects.filter(qrcode=qrcode).exists():
                qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
            rec=TransRec()
            rec.car_no=form.cleaned_data['car_no']
            rec.driver_name=form.cleaned_data['driver_name']
            rec.contact_info=form.cleaned_data['contact_info']
            rec.mine=form.cleaned_data['mine']
            rec.coal_type=form.cleaned_data['coal_type']
            rec.qrcode=qrcode
            rec.save()
            return redirect('/work/detail?qrcode='+str(rec.qrcode))
    form=NewForm(Mine.objects.filter(user=user))
    return render(request,'work/new.html',{
        'form':form
    })

#@permission_required('work.mine',raise_exception=True)
#def create(request):
#    car_no=request.POST.get('car_no')
#    driver_name=request.POST.get('driver_name')
#    contact_info=request.POST.get('contact_info')
#    mine_id=request.POST.get('mine_id')
#    coal_type_id=request.POST.get('coal_type_id')
#    if not car_no or not driver_name or not contact_info or not mine_id or not coal_type_id:
#        return HttpResponse('info not full')
#    rec=TransRec()
#    try:
#        mine=Mine.objects.get(pk=long(mine_id))
#    except ObjectDoesNotExist:
#        return HttpResponse('no such mine')
#    try:
#        coal_type=CoalType.objects.get(pk=long(coal_type_id))
#    except ObjectDoesNotExist:
#        return HttpResponse('no such coal type')
#    qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
#    while TransRec.objects.filter(qrcode=qrcode).exists():
#        qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
#    rec.qrcode=qrcode
#    rec.car_no=car_no
#    rec.driver_name=driver_name
#    rec.contact_info=contact_info
#    rec.mine=mine
#    rec.coal_type=coal_type
#    rec.save()
#    return redirect('/work/detail?qrcode='+str(rec.qrcode))

def detail(request):
    qrcode=request.GET.get('qrcode')
    try:
        rec=TransRec.objects.get(qrcode=qrcode)
    except ObjectDoesNotExist:
        return HttpResponse('no such qrcode')
    return render(request,'work/detail.html',{'rec':rec})

def scan(request):
    user=request.user
    if user.has_perm('work.scale'):
        action='/work/arrive'
    elif user.has_perm('work.account'):
        action='/work/pay'
    else:
        raise PermissionDenied
    form=ScanForm()
    return render(request,'work/scan.html',{
        'form':form,
        'action':action
    })

@permission_required('work.scale',raise_exception=True)
def arrive(request):
    if request.method=='POST':
        form=ArriveForm(None,request.POST)
        if form.is_valid():
            qrcode=form.cleaned_data['qrcode']
            try:
                rec=TransRec.objects.get(qrcode=qrcode)
            except ObjectDoesNotExist:
                return HttpResponse('no such qrcode')
            rec.setoff_amount=form.cleaned_data['setoff_amount']
            rec.arrive_amount=form.cleaned_data['arrive_amount']
            rec.arrive_time=datetime.datetime.now()
            rec.scale=request.user.scale
            shipment=Shipment.objects.get(coal_type=rec.coal_type,mine=rec.mine,scale=rec.scale)
            rec.unit=shipment.unit
            rec.save()
            return HttpResponse('scaled')

    qrcode=request.GET.get('qrcode')
    form=ArriveForm(qrcode)
    try:
        rec=TransRec.objects.get(qrcode=qrcode)
    except ObjectDoesNotExist:
        return HttpResponse('no such qrcode')
    return render(request,'work/arrive.html',{'form':form,'rec':rec})

#@permission_required('work.scale',raise_exception=True)
#def weight(request):
#    user=request.user
#    scale=user.userinfo.scale
#    setoff_amount=request.POST.get('setoff_amount')
#    arrive_amount=request.POST.get('arrive_amount')
#    qrcode=request.POST.get('qrcode')
#    if not setoff_amount or not arrive_amount or not qrcode:
#        return HttpResponse('info not full')
#    try:
#        rec=TransRec.objects.get(qrcode=qrcode)
#    except ObjectDoesNotExist:
#        return HttpResponse('no such qrcode')
#    if rec.arrive_amount:
#        return HttpResponse('already weighted')
#    rec.setoff_amount=setoff_amount
#    rec.arrive_amount=arrive_amount
#    rec.arrive_time=datetime.datetime.now()
#    rec.scale=scale
#    rec.save()
#    return HttpResponse('scaled')

#@permission_required('work.account',raise_exception=True)
#def cal(request):
#    qrcode=request.GET.get('qrcode')
#    try:
#        rec=TransRec.objects.get(qrcode=qrcode)
#    except ObjectDoesNotExist:
#        return HttpResponse('no such qrcode')
#    if not rec.arrive_amount:
#        return HttpResponse('not weighted')
#    #total=float(rec.coal_type.unit)*rec.arrive_amount
#    return render(request,'work/cal.html',{'rec':rec,'total':total})

@permission_required('work.account',raise_exception=True)
def pay(request):
    if request.method=='POST':
        form=PayForm(request.POST)
        if form.is_valid():
            qrcode=form.cleaned_data['qrcode']
            try:
                rec=TransRec.objects.get(qrcode=qrcode)
            except ObjectDoesNotExist:
                return HttpResponse('no such qrcode')
            total=rec.unit*rec.arrive_amount
            payfor=form.cleaned_data['payfor']
            if payfor=='both':
                if rec.card_payed or rec.cash_payed:
                    return HttpResponse('already payed one')
                card=form.cleaned_data['card']
                if card.value>total:
                    return HttpResponse('more than total')
                if card.balance==0:
                    return HttpResponse('no enough card')
                cash=total-card.value
                balance=Balance.objects.all()[0]
                if cash>balance:
                    return HttpResponse('no enough balance')
                rec.card=card
                rec.card_payed=True
                rec.cash=cash
                rec.cash_payed=True
                rec.save()
                balance-=cash
                balance.save()
                if card.value>0:
                    card.balance-=1
                    card.save()
                return HttpResponse('pay success')
            elif payfor=='card':
                if rec.card_payed:
                    return HttpResponse('already payed')
                card=form.cleaned_data['card']
                if rec.cash_payed:
                    cash=rec.cash
                else:
                    cash=0
                if cash+card.value>total:
                    return HttpResponse('more than total')
                rec.card=card
                rec.card_payed=True
                rec.save()
                return HttpResponse('success')
            elif payfor=='cash':
                if rec.cash_payed:
                    return HttpResponse('already payed')
                if rec.card_payed:
                    card=rec.card
                else:
                    card=form.cleaned_data['card']
                cash=total-card.value
                if cash<0:
                    return HttpResponse('more than total')
                rec.cash=cash
                rec.cash_payed=True
                rec.save()
                return HttpResponse('success')
        else:
            return HttpResponse('not valid')
    else:
        qrcode=request.GET.get('qrcode')
        try:
            rec=TransRec.objects.get(qrcode=qrcode)
        except ObjectDoesNotExist:
            return HttpResponse('no such qrcode')
        total=rec.unit*rec.arrive_amount
        form=PayForm(initial={'qrcode':qrcode})
        return render(request,'work/pay.html',{'form':form,'rec':rec,'total':total})
