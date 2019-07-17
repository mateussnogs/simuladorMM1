from django.urls import path, re_path
from . import views

app_name='simulator'

urlpatterns = [
    path('', views.main, name='main'),
    re_path(r'^simular/(?P<rho>[0-9][.][0-9])/$', views.simular, name='simular')
]
#/(?P<disciplina>[\w-]+)/(?P<kmin>[0-9]+)/(?P<rodadas>[0-9]+)