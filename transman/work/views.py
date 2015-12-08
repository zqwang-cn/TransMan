from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def a(request):
    return render(request,'work/new.html',{})

def b(request):
    return HttpResponse('b')

def c(request):
    return HttpResponse('c')

def create(request):
    carno=request.POST.get('carno')
    drivername=request.POST.get('drivername')
    contactinfo=request.POST.get('contactinfo')
    print carno
    return HttpResponse('created')
