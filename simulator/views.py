from django.shortcuts import render
from .simulador import *
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@csrf_exempt
def main(request):    

    return render(request, 'simulator/main.html', {})
    
@csrf_exempt
def simular(request, rho):
    context = {
        'e_w': -1,
        'v_w': -1,
        'e_nq': -1,
        'v_nq': -1
    }
    print(rho)
    rho = float(rho)
    simulador = Simulador(rho)
    rodadas = 300
    w_means = []
    w_vars = []
    nq_s = []
    for i in range(rodadas):
        nq, wj_s = simulador.simular('FCFS', 3000)
        w_means.append(Statistics.media_amostral(wj_s))
        w_vars.append(Statistics.var_amostral(wj_s))
        nq_s.append(nq)
        print(i)
    context['e_w'] = Statistics.media_amostral(w_means)
    context['v_w'] = Statistics.media_amostral(w_vars)
    context['e_nq'] = Statistics.media_amostral(nq_s)
    context['v_nq'] = Statistics.media_amostral(nq_s)
    print('end')
    return HttpResponse(json.dumps(context))



