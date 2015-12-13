from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list$', views.list, name='list'),
    url(r'^detail$', views.detail, name='detail'),
    url(r'^new$', views.new, name='new'),
    url(r'^arrive$', views.arrive, name='arrive'),
    url(r'^scan$', views.scan, name='scan'),
    url(r'^weight$', views.weight, name='weight'),
    url(r'^cal$', views.cal, name='cal'),
    url(r'^pay$', views.pay, name='pay'),
]

