#coding:utf-8
from django.shortcuts import render,redirect
from .models import TransRec,CoalType,Mine,Scale,Shipment,Balance,Card,OutRec
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import random,string,datetime
from django.contrib.auth.decorators import permission_required,login_required
from django.core.exceptions import ObjectDoesNotExist,PermissionDenied
from .forms import ScanForm,NewForm,ArriveForm,SelectCardForm,PayForm,OutForm
from django.db.models import Sum

def randqr():
    qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
    while TransRec.objects.filter(qrcode=qrcode).exists() or OutRec.objects.filter(qrcode=qrcode).exists():
        qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
    return qrcode

# Create your views here.
@login_required
def list(request):
    user=request.user
    if user.has_perm('work.account'):
        all_recs=TransRec.objects.filter().order_by('-id').all()
    elif user.has_perm('work.mine'):
        all_recs=TransRec.objects.filter(mine__user=user).order_by('-id')
    elif user.has_perm('work.scale'):
        all_recs=TransRec.objects.filter(mine__isnull=False,scale__user=user).order_by('-id')
    paginator=Paginator(all_recs,5)
    page=request.GET.get('page')
    try:
        recs=paginator.page(page)
    except PageNotAnInteger:
        recs=paginator.page(1)
    except EmptyPage:
        recs=paginator.page(paginator.num_pages)

    if not user.has_perm('work.account'):
        return render(request,'work/list.html',{'recs':recs,'showsum':False})
    arrive_amount_sum=all_recs.aggregate(Sum('arrive_amount'))['arrive_amount__sum']
    cards=Card.objects.all()
    card_sums=[]
    card_balances=[]
    for card in cards:
        if card.value!=0:
            card_sums.append((card.value,TransRec.objects.filter(card=card,card_payed=True).count()))
            card_balances.append((card.value,card.balance))
    cash_sum=TransRec.objects.filter(cash_payed=True).aggregate(Sum('cash'))['cash__sum']
    cash_balance=Balance.objects.get(pk=1).balance
    return render(request,'work/list.html',{
        'recs':recs,
        'showsum':True,
        'arrive_amount_sum':arrive_amount_sum,
        'card_sums':card_sums,
        'card_balances':card_balances,
        'cash_sum':cash_sum,
        'cash_balance':cash_balance,
    })

@permission_required('work.account',raise_exception=True)
def listout(request):
    all_recs=OutRec.objects.order_by('-id').all()
    paginator=Paginator(all_recs,5)
    page=request.GET.get('page')
    try:
        recs=paginator.page(page)
    except PageNotAnInteger:
        recs=paginator.page(1)
    except EmptyPage:
        recs=paginator.page(paginator.num_pages)
    return render(request,'work/listout.html',{'recs':recs})

@permission_required('work.mine',raise_exception=True)
def new(request):
    user=request.user
    if request.method=='POST':
        form=NewForm(Mine.objects.filter(user=user),request.POST)
        if form.is_valid():
            rec=form.save(commit=False)
            rec.qrcode=randqr()
            shipment=Shipment.objects.get(coal_type=rec.coal_type,mine=rec.mine,scale=rec.scale)
            rec.unit=shipment.unit
            rec.save()
            return redirect('/work/detail?qrcode='+str(rec.qrcode))
    form=NewForm(Mine.objects.filter(user=user))
    return render(request,'work/new.html',{'form':form})

@permission_required('work.account',raise_exception=True)
def out(request):
    if request.method=='POST':
        form=OutForm(request.POST)
        if form.is_valid():
            qrcode=form.cleaned_data['qrcode']
            if not qrcode:
                rec=form.save(commit=False)
                rec.unit=request.user.scale.out_unit
                rec.qrcode=randqr()
                rec.save()
                return render(request,'work/info.html',{'title':'成功','content':'出货成功'})
            else:
                if OutRec.objects.filter(qrcode=qrcode).exists():
                    pass
                else:
                    return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
        else:
            return render(request,'work/info.html',{'title':'错误','content':'表格填写错误'})
    form=OutForm()
    return render(request,'work/out.html',{
        'form':form
    })

def detail(request):
    qrcode=request.GET.get('qrcode')
    try:
        rec=TransRec.objects.get(qrcode=qrcode)
    except ObjectDoesNotExist:
        return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
    return render(request,'work/detail.html',{'rec':rec})

def scan(request):
    user=request.user
    if user.has_perm('work.scale'):
        action='/work/arrive'
    elif user.has_perm('work.account'):
        action='/work/selectCard'
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
                return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
            if rec.scale!=request.user.scale:
                return render(request,'work/info.html',{'title':'错误','content':'目标磅房非此磅房'})
            rec.setoff_amount=form.cleaned_data['setoff_amount']
            rec.arrive_amount=form.cleaned_data['arrive_amount']
            rec.arrive_time=datetime.datetime.now()
            rec.save()
            return render(request,'work/info.html',{'title':'成功','content':'操作成功'})
        else:
            return render(request,'work/info.html',{'title':'错误','content':'表格填写错误'})
    qrcode=request.GET.get('qrcode')
    try:
        rec=TransRec.objects.get(qrcode=qrcode)
    except ObjectDoesNotExist:
        return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
    if rec.scale!=request.user.scale:
        return render(request,'work/info.html',{'title':'错误','content':'目标磅房非此磅房'})
    form=ArriveForm(qrcode)
    return render(request,'work/arrive.html',{'form':form,'rec':rec})

@permission_required('work.account',raise_exception=True)
def pay(request):
    if request.method=='POST':
        form=PayForm(request.POST)
        if form.is_valid():
            qrcode=form.cleaned_data['qrcode']
            try:
                rec=TransRec.objects.get(qrcode=qrcode)
            except ObjectDoesNotExist:
                return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
            payfor=form.cleaned_data['payfor']
            if payfor=='card':
                rec.card_payed=True
                rec.card.balance-=1
                rec.card.save()
            elif payfor=='cash':
                rec.cash_payed=True
                balance=Balance.objects.get(pk=1)
                balance.balance-=rec.cash
                balance.save()
            elif payfor=='both':
                rec.card_payed=True
                rec.card.balance-=1
                rec.card.save()
                rec.cash_payed=True
                balance=Balance.objects.get(pk=1)
                balance.balance-=rec.cash
                balance.save()
            else:
                return render(request,'work/info.html',{'title':'错误','content':'无此命令'})
            rec.save()
            return render(request,'work/info.html',{'title':'成功','content':'操作成功'})
        else:
            return render(request,'work/info.html',{'title':'错误','content':'表格填写错误'})
    else:
        qrcode=request.GET.get('qrcode')
        try:
            rec=TransRec.objects.get(qrcode=qrcode)
        except ObjectDoesNotExist:
            return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
        if not rec.card:
            return redirect('/work/selectCard?qrcode='+str(qrcode))
        total=rec.unit*rec.arrive_amount
        card=rec.card.value
        cash=rec.cash
        form=PayForm(initial={'qrcode':qrcode})
        return render(request,'work/pay.html',{'form':form,'rec':rec,'total':total,'card':card,'cash':cash})

@permission_required('work.account',raise_exception=True)
def selectCard(request):
    if request.method=='POST':
        form=SelectCardForm(request.POST)
        if form.is_valid():
            qrcode=form.cleaned_data['qrcode']
            try:
                rec=TransRec.objects.get(qrcode=qrcode)
            except ObjectDoesNotExist:
                return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
            total=rec.unit*rec.arrive_amount
            card=form.cleaned_data['card']
            if card.value>total:
                return render(request,'work/info.html',{'title':'错误','content':'付款多于总运费'})
            cash=total-card.value
            rec.cash=cash
            rec.card=card
            rec.save()
            return redirect('/work/pay?qrcode='+str(qrcode))
    else:
        qrcode=request.GET.get('qrcode')
        try:
            rec=TransRec.objects.get(qrcode=qrcode)
        except ObjectDoesNotExist:
            return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
        if rec.card:
            return redirect('/work/pay?qrcode='+str(qrcode))
        total=rec.unit*rec.arrive_amount
        form=SelectCardForm(initial={'qrcode':qrcode})
        return render(request,'work/selectCard.html',{'form':form,'rec':rec,'total':total})
