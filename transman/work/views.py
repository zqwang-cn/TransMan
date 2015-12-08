from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import TransRec

# Create your views here.
def a(request):
    return render(request,'work/new.html',{})

def b(request):
    return HttpResponse('b')

def c(request):
    return HttpResponse('c')

def create(request):
    car_no=request.POST.get('car_no')
    driver_name=request.POST.get('driver_name')
    contact_info=request.POST.get('contact_info')
    if not car_no or not driver_name or not contact_info:
        return HttpResponse('info not full')
    rec=TransRec()
    rec.car_no=car_no
    rec.driver_name=driver_name
    rec.contact_info=contact_info
    rec.save()
    return redirect('/work/view?id='+str(rec.id))

def view(request):
    id=long(request.GET.get('id'))
    rec=TransRec.objects.get(pk=id)
    return render(request,'work/view.html',{'rec':rec})
