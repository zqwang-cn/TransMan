#coding:utf-8
from django.shortcuts import render,redirect
from .models import TransRec,Mine,Balance,Card,OutRec,CoalType,Scale
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
import random,string,datetime
from django.contrib.auth.decorators import permission_required,login_required
from django.core.exceptions import ObjectDoesNotExist,PermissionDenied
from .forms import ScanForm,NewForm,ArriveForm,SelectCardForm,PayForm,OutForm,SearchForm,SearchOutForm
from django.db.models import Sum,F
from django.http import HttpResponse
import xlwt

def randqr():
    qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
    while TransRec.objects.filter(qrcode=qrcode).exists() or OutRec.objects.filter(qrcode=qrcode).exists():
        qrcode=''.join([random.choice(string.digits+string.lowercase) for i in range(10)])
    return qrcode

# Create your views here.
@login_required
def list(request):
    all_recs=TransRec.objects
    user=request.user
    if user.has_perm('work.mine'):
        all_recs=all_recs.filter(mine__user=user)
        perm='mine'
    elif user.has_perm('work.scale'):
        all_recs=all_recs.filter(scale=user.userscaleinfo.scale)
        perm='scale'
    elif user.has_perm('work.account'):
        perm='account'
    else:
        raise PermissionDenied

    setoff_time_begin=request.GET.get('setoff_time_begin')
    setoff_time_end=request.GET.get('setoff_time_end')
    arrive_time_begin=request.GET.get('arrive_time_begin')
    arrive_time_end=request.GET.get('arrive_time_end')
    car_no=request.GET.get('car_no')
    opscale=request.GET.get('opscale')
    opaccount=request.GET.get('opaccount')
    if setoff_time_begin:
        all_recs=all_recs.filter(setoff_time__gt=setoff_time_begin)
    if setoff_time_end:
        setoff_time_end+=' 23:59:59'
        all_recs=all_recs.filter(setoff_time__lt=setoff_time_end)
    if arrive_time_begin:
        all_recs=all_recs.filter(arrive_time__gt=arrive_time_begin)
    if arrive_time_end:
        arrive_time_end+=' 23:59:59'
        all_recs=all_recs.filter(arrive_time__lt=arrive_time_end)
    if car_no:
        all_recs=all_recs.filter(car_no=car_no)
    if opscale:
        all_recs=all_recs.filter(opscale=opscale)
    if opaccount:
        all_recs=all_recs.filter(opaccount=opaccount)


    download=request.GET.get('download')
    if download:
        xls=xlwt.Workbook(encoding='utf8',style_compression={})
        sheet=xls.add_sheet('Sheet1')
        style=xlwt.easyxf('align: horiz right')
        labels=['ID','车牌号','驾驶员姓名','联系方式','出发煤矿','煤类型','到达磅房','出发时间','矿发量','实收量','单价','到达时间','总价']
        for i in range(len(labels)):
            sheet.write(0,i,labels[i],style=style)
        row=1
        sum=0.0
        for rec in all_recs.all():
            sheet.write(row,0,rec.id,style=style)
            sheet.write(row,1,rec.car_no,style=style)
            sheet.write(row,2,rec.driver_name,style=style)
            sheet.write(row,3,rec.contact_info,style=style)
            sheet.write(row,4,rec.mine.name,style=style)
            sheet.write(row,5,rec.coal_type.name,style=style)
            sheet.write(row,6,rec.scale.name,style=style)
            sheet.write(row,7,rec.setoff_time.strftime('%Y-%m-%d %H:%M:%S'),style=style)
            setoff_amount=rec.setoff_amount if rec.setoff_amount else '---'
            sheet.write(row,8,setoff_amount,style=style)
            arrive_amount=rec.arrive_amount if rec.arrive_amount else '---'
            sheet.write(row,9,arrive_amount,style=style)
            sheet.write(row,10,rec.unit,style=style)
            arrive_time=rec.arrive_time.strftime('%Y-%m-%d %H:%M:%S') if rec.arrive_time else '-----'
            sheet.write(row,11,arrive_time,style=style)
            if rec.arrive_amount:
                total=(rec.unit*rec.arrive_amount)//10*10
                sum+=total
            else:
                total='---'
            sheet.write(row,12,total,style=style)
            row+=1
        sheet.write(row,0,'合计',style=style)
        sheet.write(row,12,sum,style=style)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=list.xls'
        xls.save(response)
        return response

    params=''
    for k,v in request.GET.items():
        if k!='page':
            params+=k+'='+v+'&'

    all_recs=all_recs.order_by('-id')

    paginator=Paginator(all_recs,10)
    page=request.GET.get('page')
    try:
        recs=paginator.page(page)
    except PageNotAnInteger:
        recs=paginator.page(1)
    except EmptyPage:
        recs=paginator.page(paginator.num_pages)
    begin=recs.number-5/2
    if begin<1:begin=1
    end=recs.number+5/2
    if end>paginator.num_pages:end=paginator.num_pages
    pr=range(begin,end+1)
    
    form=SearchForm()
    return render(request,'work/list.html',{'recs':recs,'perm':perm,'pr':pr,'params':params,'form':form})

def listout(request):
    all_recs=OutRec.objects
    user=request.user
    if user.has_perm('work.scale'):
        perm='scale'
        all_recs=all_recs.filter(scale=request.user.userscaleinfo.scale)
    elif user.has_perm('work.account'):
        perm='account'
    else:
        raise PermissionDenied

    payed=None
    sum=None
    qrcode=request.GET.get('qrcode')
    if qrcode:
        all_recs=all_recs.filter(qrcode=qrcode)
        if not all_recs.exists():
            return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
        if all_recs[0].payed:
            payed=True
        else:
            payed=False
            sum=0.0
            for rec in all_recs:
                sum+=rec.unit*rec.amount
            sum=sum//10*10

    setoff_time_begin=request.GET.get('setoff_time_begin')
    setoff_time_end=request.GET.get('setoff_time_end')
    car_no=request.GET.get('car_no')
    if setoff_time_begin:
        all_recs=all_recs.filter(setoff_time__gt=setoff_time_begin)
    if setoff_time_end:
        setoff_time_end+=' 23:59:59'
        all_recs=all_recs.filter(setoff_time__lt=setoff_time_end)
    if car_no:
        all_recs=all_recs.filter(car_no=car_no)

    all_recs=all_recs.order_by('-id')

    params=''
    for k,v in request.GET.items():
        if k!='page':
            params+=k+'='+v+'&'

    paginator=Paginator(all_recs,10)
    page=request.GET.get('page')
    try:
        recs=paginator.page(page)
    except PageNotAnInteger:
        recs=paginator.page(1)
    except EmptyPage:
        recs=paginator.page(paginator.num_pages)
    begin=recs.number-5/2
    if begin<1:begin=1
    end=recs.number+5/2
    if end>paginator.num_pages:end=paginator.num_pages
    pr=range(begin,end+1)

    form=SearchOutForm()
    return render(request,'work/listout.html',{'recs':recs,'qrcode':qrcode,'perm':perm,'payed':payed,'pr':pr,'sum':sum,'params':params,'form':form})

@permission_required('work.mine',raise_exception=True)
def new(request):
    user=request.user
    if request.method=='POST':
        form=NewForm(Mine.objects.filter(user=user),request.POST)
        if form.is_valid():
            rec=form.save(commit=False)
            rec.qrcode=randqr()
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
                recs=OutRec.objects.filter(scale=request.user.userscaleinfo.scale,qrcode=qrcode)
                if recs.exists():
                    rec=recs[0]
                    if rec.payed:
                        return render(request,'work/info.html',{'title':'错误','content':'二维码已作废'})
                    rec.pk=None
                    rec.amount=form.cleaned_data['amount']
                    rec.unit=form.cleaned_data['unit']
                    rec.save()
                    return redirect('/work/listout?qrcode='+rec.qrcode)
                else:
                    return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
            else:
                rec=form.save(commit=False)
                rec.scale=request.user.userscaleinfo.scale
                rec.qrcode=randqr()
                rec.save()
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
        sum=sum//10*10
        balance=Balance.objects.get(pk=1)
        balance.balance-=sum
        balance.save()
        return render(request,'work/info.html',{'title':'成功','content':'付款成功'})
    else:
        return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})

@login_required
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
            if rec.scale!=request.user.userscaleinfo.scale:
                return render(request,'work/info.html',{'title':'错误','content':'目标磅房非此磅房'})
            rec.setoff_amount=form.cleaned_data['setoff_amount']
            rec.arrive_amount=form.cleaned_data['arrive_amount']
            rec.arrive_time=datetime.datetime.now()
            rec.opscale=request.user
            rec.save()
            return render(request,'work/info.html',{'title':'成功','content':'操作成功'})
        else:
            return render(request,'work/info.html',{'title':'错误','content':'表格填写错误'})
    qrcode=request.GET.get('qrcode')
    try:
        rec=TransRec.objects.get(qrcode=qrcode)
    except ObjectDoesNotExist:
        return render(request,'work/info.html',{'title':'错误','content':'无法识别此二维码'})
    if rec.scale!=request.user.userscaleinfo.scale:
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
                rec.save()
            elif payfor=='cash':
                rec.cash_payed=True
                rec.save()
                balance=Balance.objects.get(pk=1)
                balance.balance-=rec.cash
                balance.save()
            elif payfor=='both':
                rec.card_payed=True
                rec.card.balance-=1
                rec.card.save()
                rec.cash_payed=True
                rec.save()
                balance=Balance.objects.get(pk=1)
                balance.balance-=rec.cash
                balance.save()
            else:
                return render(request,'work/info.html',{'title':'错误','content':'无此命令'})
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
        total=(rec.unit*rec.arrive_amount)//10*10
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
            total=(rec.unit*rec.arrive_amount)//10*10
            card=form.cleaned_data['card']
            if card.value>total:
                return render(request,'work/info.html',{'title':'错误','content':'付款多于总运费'})
            cash=total-card.value
            rec.cash=cash
            rec.card=card
            rec.opaccount=request.user
            if card.value==0:
                rec.card_payed=True
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
        total=(rec.unit*rec.arrive_amount)//10*10
        form=SelectCardForm(initial={'qrcode':qrcode})
        return render(request,'work/selectCard.html',{'form':form,'rec':rec,'total':total})

@permission_required('work.account',raise_exception=True)
def balance(request):
    mines=Mine.objects.all()
    coal_types=CoalType.objects.all()
    scales=Scale.objects.all()
    all_recs=TransRec.objects
    out_recs=OutRec.objects

    mine_table=[]
    for mine in mines:
        row=[]
        for coal_type in coal_types:
            s=all_recs.filter(mine=mine,coal_type=coal_type).aggregate(Sum('arrive_amount'))['arrive_amount__sum']
            if not s:
                s=0.0
            row.append(s)
        row.append(sum(row))
        row.insert(0,mine.name)
        mine_table.append(row)
    mine_total=sum([row[-1] for row in mine_table])

    scale_table=[]
    for scale in scales:
        row=[]
        for coal_type in coal_types:
            s=all_recs.filter(scale=scale,coal_type=coal_type).aggregate(Sum('arrive_amount'))['arrive_amount__sum']
            if not s:
                s=0.0
            row.append(s)
        row.append(sum(row))
        s=out_recs.filter(scale=scale).aggregate(Sum('amount'))['amount__sum']
        if not s:
            s=0.0
        row.append(s)
        row.append(row[-2]-row[-1])
        row.insert(0,scale.name)
        scale_table.append(row)
    in_total=sum([row[-3] for row in scale_table])
    out_total=sum([row[-2] for row in scale_table])
    balance_total=sum([row[-1] for row in scale_table])

    cards=Card.objects.all()
    cards_info=[]
    for card in cards:
        if card.value!=0:
            card_info=[]
            card_info.append(card.value)
            card_info.append(TransRec.objects.filter(card=card,card_payed=True).count())
            card_info.append(card.balance)
            cards_info.append(card_info)

    cash_sumin=TransRec.objects.filter(cash_payed=True).aggregate(Sum('cash'))['cash__sum']
    cash_sumout=OutRec.objects.filter(payed=True).annotate(total=F('unit')*F('amount')).aggregate(Sum('total'))['total__sum']
    cash_balance=Balance.objects.get(pk=1).balance
    cash_info=[cash_sumin,cash_sumout,cash_balance]

    return render(request,'work/balance.html',{
        'mine_table':mine_table,
        'mine_total':mine_total,
        'scale_table':scale_table,
        'in_total':in_total,
        'out_total':out_total,
        'balance_total':balance_total,
        'cards_info':cards_info,
        'cash_info':cash_info,
        'coal_types':coal_types,
    })
