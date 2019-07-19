from django.shortcuts import render
from .simulador import *
import time
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@csrf_exempt
def main(request):    
    return render(request, 'simulator/main.html', {})
@csrf_exempt
def animacao(request):    
    return render(request, 'simulator/animacao.html', {})
@csrf_exempt
def transiente(request):    
    return render(request, 'simulator/transiente.html', {})
    
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
    W = []
    Vw = []
    Nq = []
    for i in range(rodadas):
        nqi, wi, vi_w = simulador.simular(disciplina, kmin)
        W.append(wi) #Conjunto de variaveis aleatorias {Wi}
        Vw.append(vi_w) #Conjunto de variaveis aleatorias {Vi}
        Nq.append(nqi) #Conjunto de variaveis aleatorias {Nqi}
        print(i)
    #Variaveis para ICs        
    mi_chapeu_w = Statistics.media_amostral(W)
    mi_chapeu_vw = Statistics.media_amostral(Vw)
    mi_chapeu_nq = Statistics.media_amostral(Nq)
    sigma_chapeu2_w = Statistics.var_amostral(W, mi_chapeu_w)
    sigma_chapeu2_vw = Statistics.var_amostral(Vw, mi_chapeu_vw)
    sigma_chapeu2_nq = Statistics.var_amostral(Nq, mi_chapeu_nq)

    #ic medias
    ic_w = Statistics.intervalo_de_confianca_tstudent(mi_chapeu_w, sigma_chapeu2_w, rodadas, 0.95)
    ic_nq = Statistics.intervalo_de_confianca_tstudent(mi_chapeu_nq, sigma_chapeu2_nq, rodadas, 0.95)
    #ic variancias pela tstudent
    ic_vwt = Statistics.intervalo_de_confianca_tstudent(mi_chapeu_vw, sigma_chapeu2_vw, rodadas, 0.95)
    ic_vwchi = Statistics.intervalo_de_confianca_chi2(mi_chapeu_vw, rodadas, 0.95)
    context['e_w'] = mi_chapeu_w
    context['v_w'] = mi_chapeu_vw
    context['ic_ew_low'] = ic_w[1]
    context['ic_ew_high'] = ic_w[2]
    context['ic_vwt_low'] = ic_vwt[1]
    context['ic_vwt_high'] = ic_vwt[2]
    context['ic_vwchi_low'] = ic_vwchi[1]
    context['ic_vwchi_high'] = ic_vwchi[2]
    print('end')
    return HttpResponse(json.dumps(context))

@csrf_exempt
def simular_toplot(request, rho, disciplina, kmin, rodadas):
    rho = float(rho)
    simulador = Simulador(rho)
    rodadas = int(rodadas)
    disciplina = str(disciplina)
    kmin = int(kmin)    
    tempos_espera = []
    mespera = []
    vespera = []
    nq = 0
    medias_moveis_w = []
    medias_moveis_v = []
    media_tempo_espera = 0
    variancia_tempo_espera = 0
    t_rodada = simulador.instante_atual
    context = {
        'V': [],
        'W': []
    }
    if (len(simulador.eventos.eventos) == 0):
        simulador.agendar_chegada(simulador.instante_atual)
    coletas = 0
    t_end = time.time() + 5
    while time.time() < t_end:
        evento = simulador.eventos.proximo_evento()
        dt = simulador.instante_atual
        simulador.instante_atual = evento.instante # avança o tempo para instante do evento
        dt = simulador.instante_atual - dt            
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
                lastmedia_tempo = media_tempo_espera
                media_tempo_espera = simulador.staticts.media_incremental(media_tempo_espera, tempos_espera[coletas-1], coletas)
                mespera.append(media_tempo_espera)
                variancia_tempo_espera = simulador.staticts.var_incremental(variancia_tempo_espera, media_tempo_espera, tempos_espera[coletas-1], lastmedia_tempo, coletas)
                vespera.append(variancia_tempo_espera)
                if(coletas>3000):
                    sumw = 0
                    sumv = 0
                    for k in range(coletas-3000, coletas):
                        sumw += mespera[k]
                        sumv += vespera[k]
                    medias_moveis_w.append(sumw/3000)
                    medias_moveis_v.append(sumv/3000)     
                else:
                    medias_moveis_w.append(0)
                    medias_moveis_v.append(0)
            simulador.agendar_chegada(simulador.instante_atual)
        else: #partida
            simulador.servidor_ocupado = False
            if (len(simulador.fila) > 0):
                simulador.servidor_ocupado = True
                fregues = simulador.fila.pop(0)
                tempos_espera.append(simulador.instante_atual-fregues.instante_chegada)                    
                coletas += 1
                simulador.agendar_partida(simulador.instante_atual, fregues)
                lastmedia_tempo = media_tempo_espera
                media_tempo_espera = simulador.staticts.media_incremental(media_tempo_espera, tempos_espera[coletas-1], coletas)
                mespera.append(media_tempo_espera)
                variancia_tempo_espera = simulador.staticts.var_incremental(variancia_tempo_espera, media_tempo_espera, tempos_espera[coletas-1], lastmedia_tempo, coletas)
                vespera.append(variancia_tempo_espera)
                if(coletas>3000):
                    sumw = 0
                    sumv = 0
                    for k in range(coletas-3000, coletas):
                        sumw += mespera[k]
                        sumv += vespera[k]
                    medias_moveis_w.append(sumw/3000)
                    medias_moveis_v.append(sumv/3000)     
                else:
                    medias_moveis_w.append(0)
                    medias_moveis_v.append(0)
                    #t_rodada = simulador.instante_atual - t_rodada
                    #media_tempo_espera = self.staticts.media_amostral(tempos_espera)
                    #variancia_tempo_espera = self.staticts.var_amostral(tempos_espera)
    context['V'] = vespera
    context['MMV'] = medias_moveis_v
    context['W'] = mespera
    context['MMW'] = medias_moveis_w
    #return nq/t_rodada, media_tempo_espera, variancia_tempo_espera
    return HttpResponse(json.dumps(context))