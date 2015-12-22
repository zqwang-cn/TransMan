#coding:utf-8
from django.shortcuts import render,redirect
from django.contrib import auth

# Create your views here.
def home(request):
    if request.user.is_authenticated():
        return redirect('/work/list')
    else:
        return redirect('/auth/login')

def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return redirect('/auth/login')

def login(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        if not username or not password:
            return render(request,'auth/error.html',{'errmsg':'请输入用户名和密码'})
        user=auth.authenticate(username=username,password=password)
        if user is None:
            return render(request,'auth/error.html',{'errmsg':'用户名或密码错误'})
        auth.login(request,user)
        return redirect('/')
    else:
        return render(request,'auth/login.html',{})
