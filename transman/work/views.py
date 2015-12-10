from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import TransRec,CoalType,UserMine,Mine
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import random,string,datetime
from decimal import Decimal
from django.contrib.auth.decorators import permission_required

# Create your views here.
@permission_required('work.mine',raise_exception=True)
def list(request):
    all_recs=TransRec.objects.all()
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
    coal_types=CoalType.objects.all()
    mine=UserMine.objects.get(user=request.user).mine
    mine_id=mine.id
    return render(request,'work/new.html',{
        'mine_id':mine_id,
        'coal_types':coal_types
    })

@permission_required('work.mine',raise_exception=True)
def create(request):
    car_no=request.POST.get('car_no')
    driver_name=request.POST.get('driver_name')
    contact_info=request.POST.get('contact_info')
    mine=Mine.objects.get(pk=long(request.POST.get('mine_id')))
    coal_type=CoalType.objects.get(pk=long(request.POST.get('coal_type_id')))
    if not car_no or not driver_name or not contact_info:
        return HttpResponse('info not full')
    rec=TransRec()
    rec.car_no=car_no
    rec.driver_name=driver_name
    rec.contact_info=contact_info
    rec.qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
    rec.mine=mine
    rec.coal_type=coal_type
    rec.save()
    return redirect('/work/detail?qrcode='+str(rec.qrcode))

@permission_required('work.mine',raise_exception=True)
def detail(request):
    qrcode=request.GET.get('qrcode')
    rec=TransRec.objects.get(qrcode=qrcode)
    return render(request,'work/detail.html',{'rec':rec})

def scan(request):
    user=request.user
    if user.has_perm('work.scale'):
        action='/work/arrive'
    elif user.has_perm('work.account'):
        action='/work/cal'
    return render(request,'work/scan.html',{'action':action})

@permission_required('work.scale',raise_exception=True)
def arrive(request):
    qrcode=request.GET.get('qrcode')
    rec=TransRec.objects.get(qrcode=qrcode)
    return render(request,'work/arrive.html',{'rec':rec})

@permission_required('work.scale',raise_exception=True)
def weight(request):
    setoff_amount=request.POST.get('setoff_amount')
    arrive_amount=request.POST.get('arrive_amount')
    arrive_time=datetime.datetime.now()
    qrcode=request.POST.get('qrcode')
    rec=TransRec.objects.get(qrcode=qrcode)
    rec.setoff_amount=setoff_amount
    rec.arrive_amount=arrive_amount
    rec.arrive_time=arrive_time
    rec.save()
    return HttpResponse('success')

@permission_required('work.account',raise_exception=True)
def cal(request):
    qrcode=request.GET.get('qrcode')
    rec=TransRec.objects.get(qrcode=qrcode)
    total=float(rec.coal_type.unit)*rec.arrive_amount
    return render(request,'work/cal.html',{'rec':rec,'total':total})

@permission_required('work.account',raise_exception=True)
def pay(request):
    qrcode=request.POST.get('qrcode')
    rec=TransRec.objects.get(qrcode=qrcode)
    total=float(rec.coal_type.unit)*rec.arrive_amount
    rec.mine.balance-=Decimal(total)
    rec.payed=True
    rec.save()
    return HttpResponse('pay success')
