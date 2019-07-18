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
def simular(request, rho, disciplina, kmin, rodadas):
    context = {
        'e_w': -1,
        'v_w': -1,
        'e_nq': -1,
        'v_nq': -1
    }
    rho = float(rho)
    simulador = Simulador(rho)
    rodadas = int(rodadas)
    disciplina = str(disciplina)
    kmin = int(kmin)
    w_means = []
    w_vars = []
    nq_s = []
    for i in range(rodadas):
        nq, wj_s = simulador.simular(disciplina, kmin)
        w_means.append(Statistics.media_amostral(wj_s))
        w_vars.append(Statistics.var_amostral(wj_s))
        nq_s.append(nq)
        print(i)
    context['EWs'] = w_means
    context['VWs'] = w_vars
    context['e_w'] = Statistics.media_amostral(w_means)
    context['v_w'] = Statistics.media_amostral(w_vars)
    context['e_nq'] = Statistics.media_amostral(nq_s)
    context['v_nq'] = Statistics.media_amostral(nq_s)
    print('end')
    return HttpResponse(json.dumps(context))

def testTransient(request, rho, disciplina, kmin):
    simulador = Simulador(rho)

    tempos_espera = []
        nq = 0
        t_rodada = simulador.instante_atual
        if (len(simulador.eventos.eventos) == 0):
            simulador.agendar_chegada(simulador.instante_atual)
        coletas = 0
        while(True):
            evento = simulador.eventos.proximo_evento()
            dt = simulador.instante_atual
            simulador.instante_atual = evento.instante # avança o tempo para instante do evento
            dt = simulador.instante_atual - dt 
            tam_fila           
            nq += len(simulador.fila)*dt
            if (evento.tipo == 'chegada'):                
                if(simulador.servidor_ocupado):
                    if (disciplina == 'FCFS'):
                        simulador.fila.append(evento.fregues)
                    else:
                        simulador.fila.insert(0, evento.fregues)
                else: # serve fregues
                    simulador.servidor_ocupado = True
                    tempos_espera.append(0)
                    coletas += 1
                    simulador.agendar_partida(simulador.instante_atual, evento.fregues)
                simulador.agendar_chegada(simulador.instante_atual)
            else: #partida
                simulador.servidor_ocupado = False
                if (len(simulador.fila) > 0):
                    simulador.servidor_ocupado = True
                    fregues = simulador.fila.pop(0)
                    tempos_espera.append(simulador.instante_atual-fregues.instante_chegada)                    
                    coletas += 1
                    simulador.agendar_partida(simulador.instante_atual, fregues)
            if (coletas >= kmin):
                t_rodada = simulador.instante_atual - t_rodada
                return nq/t_rodada, tempos_espera


