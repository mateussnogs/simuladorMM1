from django.urls import path
from . import views

app_name='simulator'

urlpatterns = [
    path('', views.main, name='main'),
    path('simular', views.simular, name='simular')
]