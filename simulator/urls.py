from django.urls import path, re_path
from . import views

app_name='simulator'

urlpatterns = [
    path('main', views.main, name='main'),
    path('animacao', views.animacao, name='animacao'),
    path('transiente', views.transiente, name='transiente'),
    re_path(r'^simular/(?P<rho>[0-9][.][0-9])/(?P<disciplina>[\w-]+)/(?P<kmin>[0-9]+)/(?P<rodadas>[0-9]+)/$', views.simular_background, name='simular'),
    re_path(r'^simulartoplot/(?P<rho>[0-9][.][0-9])/(?P<disciplina>[\w-]+)/(?P<kmin>[0-9]+)/(?P<rodadas>[0-9]+)/$', views.simular_toplot, name='simular_toplot'),
    path('rodada', views.rodada, name='rodada'),
    
]