#coding:utf-8
from django.shortcuts import render,redirect
from .models import TransRec,Mine,Shipment,Balance,Card,OutRec,CoalType,Scale
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import random,string,datetime
from django.contrib.auth.decorators import permission_required,login_required
from django.core.exceptions import ObjectDoesNotExist,PermissionDenied
from .forms import ScanForm,NewForm,ArriveForm,SelectCardForm,PayForm,OutForm
from django.db.models import Sum,F

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
        all_recs=TransRec.objects.order_by('-id').all()
        perm='account'
    elif user.has_perm('work.mine'):
        all_recs=TransRec.objects.filter(mine__user=user).order_by('-id')
        perm='mine'
    elif user.has_perm('work.scale'):
        all_recs=TransRec.objects.filter(scale__user=user).order_by('-id')
        perm='scale'
        
    paginator=Paginator(all_recs,10)
    page=request.GET.get('page')
    try:
        recs=paginator.page(page)
    except PageNotAnInteger:
        recs=paginator.page(1)
    except EmptyPage:
        recs=paginator.page(paginator.num_pages)

    return render(request,'work/list.html',{'recs':recs,'perm':perm})

def listout(request):
    user=request.user
    qrcode=request.GET.get('qrcode')
    if user.has_perm('work.scale'):
        perm='scale'
        if qrcode:
            all_recs=OutRec.objects.filter(scale=request.user.scale,qrcode=qrcode).order_by('-id')
        else:
            all_recs=OutRec.objects.filter(scale=request.user.scale).order_by('-id')
        payed=None
    elif user.has_perm('work.account'):
        perm='account'
        if qrcode:
            all_recs=OutRec.objects.filter(qrcode=qrcode).order_by('-id')
        else:
            all_recs=OutRec.objects.order_by('-id').all()
        if all_recs.exists() and not all_recs[0].payed:
            payed=False
        else:
            payed=True
    else:
        raise PermissionDenied
    paginator=Paginator(all_recs,10)
    page=request.GET.get('page')
    try:
        recs=paginator.page(page)
    except PageNotAnInteger:
        recs=paginator.page(1)
    except EmptyPage:
        recs=paginator.page(paginator.num_pages)
    return render(request,'work/listout.html',{'recs':recs,'qrcode':qrcode,'perm':perm,'payed':payed})

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

@permission_required('work.scale',raise_exception=True)
def out(request):
    if request.method=='POST':
        form=OutForm(request.POST)
        if form.is_valid():
            qrcode=form.cleaned_data['qrcode']
            if qrcode:
                recs=OutRec.objects.filter(scale=request.user.scale,qrcode=qrcode)
                if recs.exists():
                    rec=recs[0]
                    if rec.payed:
                        return render(request,'work/info.html',{'title':'错误','content':'二维码已作废'})
                    rec.amount=form.cleaned_data['amount']
                    rec.pk=None
                    rec.save()
                    scale=request.user.scale
                    scale.amount_out+=form.cleaned_data['amount']
                    scale.amount_balance-=form.cleaned_data['amount']
                    scale.save()
                    return redirect('/work/listout?qrcode='+rec.qrcode)
                else:
                    return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
            else:
                rec=form.save(commit=False)
                rec.scale=request.user.scale
                rec.unit=request.user.scale.out_unit
                rec.qrcode=randqr()
                rec.save()
                scale=request.user.scale
                scale.amount_out+=form.cleaned_data['amount']
                scale.amount_balance-=form.cleaned_data['amount']
                scale.save()
                return redirect('/work/outdetail?id='+str(rec.id))
        else:
            return render(request,'work/info.html',{'title':'错误','content':'表格填写错误'})
    form=OutForm()
    return render(request,'work/out.html',{
        'form':form
    })

@login_required
def detail(request):
    qrcode=request.GET.get('qrcode')
    try:
        rec=TransRec.objects.get(qrcode=qrcode)
    except ObjectDoesNotExist:
        return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
    return render(request,'work/detail.html',{'rec':rec})

@permission_required('work.scale',raise_exception=True)
def outdetail(request):
    id=request.GET.get('id')
    try:
        rec=OutRec.objects.get(id=id)
    except ObjectDoesNotExist:
        return render(request,'work/info.html',{'title':'错误','content':'无此id'})
    return render(request,'work/outdetail.html',{'rec':rec})

@permission_required('work.account',raise_exception=True)
def payout(request):
    qrcode=request.GET.get('qrcode')
    recs=OutRec.objects.filter(qrcode=qrcode)
    if recs.exists():
        sum=0.0
        for rec in recs:
            if rec.payed:
                continue
            sum+=rec.unit*rec.amount
            rec.payed=True
            rec.save()
        balance=Balance.objects.get(pk=1)
        balance.balance-=sum
        balance.save()
        return render(request,'work/info.html',{'title':'成功','content':'付款成功'})
    else:
        return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})

def scan(request):
    user=request.user
    if user.has_perm('work.scale') or user.has_perm('work.account'):
        action=request.GET.get('action')
        form=ScanForm()
        return render(request,'work/scan.html',{
            'form':form,
            'action':action
        })
    else:
        raise PermissionDenied

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
            scale=request.user.scale
            scale.amount_in+=form.cleaned_data['arrive_amount']
            scale.amount_balance+=form.cleaned_data['arrive_amount']
            scale.save()
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
        if not rec.arrive_amount:
            return render(request,'work/info.html',{'title':'错误','content':'未到货称重'})
        if rec.card:
            return redirect('/work/pay?qrcode='+str(qrcode))
        total=rec.unit*rec.arrive_amount
        form=SelectCardForm(initial={'qrcode':qrcode})
        return render(request,'work/selectCard.html',{'form':form,'rec':rec,'total':total})

@permission_required('work.account',raise_exception=True)
def balance(request):
    all_recs=TransRec.objects
    mines=Mine.objects.all()
    coal_types=CoalType.objects.all()
    sumins=[]
    sumins_total=0.0
    for mine in mines:
        sumin={'sumin':[],'total':0.0,'mine':mine}
        for coal_type in coal_types:
            sum=all_recs.filter(mine=mine,coal_type=coal_type).aggregate(Sum('arrive_amount'))['arrive_amount__sum']
            if not sum:
                sum=0.0
            sumin['sumin'].append(sum)
            sumin['total']+=sum
        sumins_total+=sumin['total']
        sumins.append(sumin)

    scales=Scale.objects.all()
    scales_amount=[]
    for scale in scales:
        scales_amount.append({'name':scale.name,'in':scale.amount_in,'out':scale.amount_out,'balance':scale.amount_balance})

    cards=Card.objects.all()
    card_sums=[]
    card_balances=[]
    for card in cards:
        if card.value!=0:
            card_sums.append((card.value,TransRec.objects.filter(card=card,card_payed=True).count()))
            card_balances.append((card.value,card.balance))

    cash_sumin=TransRec.objects.filter(cash_payed=True).aggregate(Sum('cash'))['cash__sum']
    cash_sumout=OutRec.objects.filter(payed=True).annotate(total=F('unit')*F('amount')).aggregate(Sum('total'))['total__sum']
    cash_balance=Balance.objects.get(pk=1).balance
    return render(request,'work/balance.html',{
        'sumins':sumins,
        'sumins_total':sumins_total,
        'scales_amount':scales_amount,
        'card_sums':card_sums,
        'card_balances':card_balances,
        'cash_sumin':cash_sumin,
        'cash_sumout':cash_sumout,
        'cash_balance':cash_balance,
        'coal_types':coal_types,
    })
