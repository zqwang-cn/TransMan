from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^list$', views.list, name='list'),
    url(r'^b$', views.b, name='b'),
    url(r'^c$', views.c, name='c'),
    url(r'^create$', views.create, name='create'),
    url(r'^detail$', views.detail, name='detail'),
    url(r'^new$', views.new, name='new'),
    url(r'^arrive$', views.arrive, name='arrive'),
    url(r'^scan$', views.scan, name='scan'),
    url(r'^weight$', views.weight, name='weight'),
]

