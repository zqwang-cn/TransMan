from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^a$', views.a, name='a'),
    url(r'^b$', views.b, name='b'),
    url(r'^c$', views.c, name='c'),
    url(r'^create$', views.create, name='create'),
    url(r'^view$', views.view, name='view'),
]

