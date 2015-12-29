from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list$', views.list, name='list'),
    url(r'^listout$', views.listout, name='listout'),
    url(r'^detail$', views.detail, name='detail'),
    url(r'^new$', views.new, name='new'),
    url(r'^arrive$', views.arrive, name='arrive'),
    url(r'^scan$', views.scan, name='scan'),
    url(r'^selectCard$', views.selectCard, name='selectCard'),
    url(r'^pay$', views.pay, name='pay'),
    url(r'^payout$', views.payout, name='payout'),
    url(r'^out$', views.out, name='out'),
    url(r'^outdetail$', views.outdetail, name='outdetail'),
    url(r'^balance$', views.balance, name='balance'),
    url(r'^search$', views.search, name='search'),
]

