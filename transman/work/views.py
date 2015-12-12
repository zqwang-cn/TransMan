from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import TransRec,CoalType,Mine
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import random,string,datetime
from decimal import Decimal
from django.contrib.auth.decorators import permission_required,login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from .forms import ScanForm

# Create your views here.
@login_required
def list(request):
    user=request.user
    if not hasattr(user,'userinfo'):
        all_recs=TransRec.objects.order_by('-id').all()
    elif user.userinfo.mine:
        all_recs=TransRec.objects.filter(mine=user.userinfo.mine).order_by('-id')
    elif user.userinfo.scale:
        all_recs=TransRec.objects.filter(scale=user.userinfo.scale).order_by('-id')
    paginator=Paginator(all_recs,5)
    page=request.GET.get('page')
    try:
        recs=paginator.page(page)
    except PageNotAnInteger:
        recs=paginator.page(1)
    except EmptyPage:
        recs=paginator.page(paginator.num_pages)
    return render(request,'work/list.html',{'recs':recs})

@permission_required('work.mine',raise_exception=True)
def new(request):
    user=request.user
    try:
        mine=user.userinfo.mine
    except ObjectDoesNotExist:
        return HttpResponse('user not assigned a mine')
    coal_types=CoalType.objects.all()
    return render(request,'work/new.html',{
        'mine':mine,
        'coal_types':coal_types
    })

@permission_required('work.mine',raise_exception=True)
def create(request):
    car_no=request.POST.get('car_no')
    driver_name=request.POST.get('driver_name')
    contact_info=request.POST.get('contact_info')
    mine_id=request.POST.get('mine_id')
    coal_type_id=request.POST.get('coal_type_id')
    if not car_no or not driver_name or not contact_info or not mine_id or not coal_type_id:
        return HttpResponse('info not full')
    rec=TransRec()
    try:
        mine=Mine.objects.get(pk=long(mine_id))
    except ObjectDoesNotExist:
        return HttpResponse('no such mine')
    try:
        coal_type=CoalType.objects.get(pk=long(coal_type_id))
    except ObjectDoesNotExist:
        return HttpResponse('no such coal type')
    qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
    while TransRec.objects.filter(qrcode=qrcode).exists():
        qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
    rec.qrcode=qrcode
    rec.car_no=car_no
    rec.driver_name=driver_name
    rec.contact_info=contact_info
    rec.mine=mine
    rec.coal_type=coal_type
    rec.save()
    return redirect('/work/detail?qrcode='+str(rec.qrcode))

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
        action='/work/cal'
    else:
        raise PermissionDenied
    #if request.method=='POST':
    #    form=ScanForm(request.POST)
    #    if form.is_valid():
    #        return HttpResponse(form.cleaned_data['qrcode'])
    #else:
    form=ScanForm()
    return render(request,'work/scan.html',{
        'form':form,
        'action':action
    })

@permission_required('work.scale',raise_exception=True)
def arrive(request):
    qrcode=request.GET.get('qrcode')
    try:
        rec=TransRec.objects.get(qrcode=qrcode)
    except ObjectDoesNotExist:
        return HttpResponse('no such qrcode')
    return render(request,'work/arrive.html',{'rec':rec})

@permission_required('work.scale',raise_exception=True)
def weight(request):
    user=request.user
    scale=user.userinfo.scale
    setoff_amount=request.POST.get('setoff_amount')
    arrive_amount=request.POST.get('arrive_amount')
    qrcode=request.POST.get('qrcode')
    if not setoff_amount or not arrive_amount or not qrcode:
        return HttpResponse('info not full')
    try:
        rec=TransRec.objects.get(qrcode=qrcode)
    except ObjectDoesNotExist:
        return HttpResponse('no such qrcode')
    if rec.arrive_amount:
        return HttpResponse('already weighted')
    rec.setoff_amount=setoff_amount
    rec.arrive_amount=arrive_amount
    rec.arrive_time=datetime.datetime.now()
    rec.scale=scale
    rec.save()
    return HttpResponse('scaled')

@permission_required('work.account',raise_exception=True)
def cal(request):
    qrcode=request.GET.get('qrcode')
    try:
        rec=TransRec.objects.get(qrcode=qrcode)
    except ObjectDoesNotExist:
        return HttpResponse('no such qrcode')
    if not rec.arrive_amount:
        return HttpResponse('not weighted')
    total=float(rec.coal_type.unit)*rec.arrive_amount
    return render(request,'work/cal.html',{'rec':rec,'total':total})

@permission_required('work.account',raise_exception=True)
def pay(request):
    qrcode=request.POST.get('qrcode')
    try:
        rec=TransRec.objects.get(qrcode=qrcode)
    except ObjectDoesNotExist:
        return HttpResponse('no such qrcode')
    if rec.payed:
        return HttpResponse('already payed')
    total=float(rec.coal_type.unit)*rec.arrive_amount
    rec.mine.balance-=Decimal(total)
    rec.payed=True
    rec.save()
    return HttpResponse('pay success')
