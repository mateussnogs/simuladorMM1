from django.shortcuts import render
from .simulador import *
# Create your views here.


def main(request):    

    return render(request, 'simulator/main.html', {})

def simular(request):
    simulador = Simulador(0.8, 50000)
    print("simulando")
    nq, wjs = simulador.simular('FCFS', 10000)
    print(nq)
    return render(request, 'simulator/main.html', {})



