from django.urls import path, re_path
from . import views

app_name='simulator'

urlpatterns = [
    path('', views.main, name='main'),
    path('animacao', views.animacao, name='animacao'),
    path('transiente', views.transiente, name='transiente'),
    path('kmin', views.kmin, name='kmin'),
    re_path(r'^simular/(?P<rho>[0-9][.][0-9])/(?P<disciplina>[\w-]+)/(?P<kmin>[0-9]+)/(?P<rodadas>[0-9]+)/(?P<seed_esperta>[0-1])/$', views.simular_background, name='simular'),
    re_path(r'^simular_kmin/(?P<rho>[0-9][.][0-9])/(?P<disciplina>[\w-]+)/(?P<rodadas>[0-9]+)/(?P<seed_esperta>[0-1])/$', views.simular_background2, name='simular_kmin'),
    re_path(r'^simulartoplot/(?P<rho>[0-9][.][0-9])/(?P<disciplina>[\w-]+)/(?P<kmin>[0-9]+)/(?P<rodadas>[0-9]+)/(?P<seed_esperta>[0-1])/$', views.simular_toplot, name='simular_toplot'),
    re_path(r'^simulardeterministico/(?P<disciplina>[\w-]+)/$',  views.simular_deterministic, name='simular_deterministic'),
    path('rodada', views.rodada, name='rodada'),    
    path('status', views.status_simulacao, name='status'),    
    path('resultado', views.resultado_simulacao, name='resultado'),    
    path('limpar', views.limpar_arquivos_simulacao, name='limpar'),
]