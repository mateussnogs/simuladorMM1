from django.shortcuts import render
from .simulador import *
import time
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

#variável global para controle da rodada atual
rodada_atual = 0

@csrf_exempt
def main(request):    
    return render(request, 'simulator/main.html', {})
@csrf_exempt
def animacao(request):    
    return render(request, 'simulator/animacao.html', {})
@csrf_exempt
def transiente(request):    
    return render(request, 'simulator/transiente.html', {})
    
def rodada(request):
    global rodada_atual
    context = {
        'rodada_atual': rodada_atual
    }
    print(context['rodada_atual'])
    return HttpResponse(json.dumps(context))

@csrf_exempt
def simular(request, rho, disciplina, kmin, rodadas):
    global rodada_atual
    rodada_atual = 0
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
    Vnq = []
    for i in range(rodadas):
        nqi, vi_nq, wi, vi_w = simulador.simular(disciplina, kmin)
        W.append(wi) #Conjunto de variaveis aleatorias {Wi}
        Vw.append(vi_w) #Conjunto de variaveis aleatorias {Vi}
        Nq.append(nqi) #Conjunto de variaveis aleatorias {Nqi}
        Vnq.append(vi_nq)
        rodada_atual = i
    #Variaveis para ICs        
    mi_chapeu_w = Statistics.media_amostral(W)
    mi_chapeu_vw = Statistics.media_amostral(Vw)
    mi_chapeu_nq = Statistics.media_amostral(Nq)
    mi_chapeu_vnq = Statistics.media_amostral(Vnq)
    sigma_chapeu2_w = Statistics.var_amostral(W, mi_chapeu_w)
    sigma_chapeu2_vw = Statistics.var_amostral(Vw, mi_chapeu_vw)
    sigma_chapeu2_nq = Statistics.var_amostral(Nq, mi_chapeu_nq)
    sigma_chapeu2_vnq = Statistics.var_amostral(Vnq, mi_chapeu_vnq)

    #ic medias
    ic_w = Statistics.intervalo_de_confianca_tstudent(mi_chapeu_w, sigma_chapeu2_w, rodadas, 0.95)
    ic_nq = Statistics.intervalo_de_confianca_tstudent(mi_chapeu_nq, sigma_chapeu2_nq, rodadas, 0.95)
    #ic variancias pela tstudent
    ic_vwt = Statistics.intervalo_de_confianca_tstudent(mi_chapeu_vw, sigma_chapeu2_vw, rodadas, 0.95)
    ic_vnqt = Statistics.intervalo_de_confianca_tstudent(mi_chapeu_vnq, sigma_chapeu2_vnq, rodadas, 0.95)    
    #ic variancias pela chi2
    ic_vwchi = Statistics.intervalo_de_confianca_chi2(mi_chapeu_vw, rodadas, 0.95)
    ic_vnqchi = Statistics.intervalo_de_confianca_chi2(mi_chapeu_vnq, rodadas, 0.95)
    
    context['e_w'] = mi_chapeu_w
    context['ic_ew_low'] = ic_w[1]
    context['ic_ew_high'] = ic_w[2]
    context['ic_ew_pres'] = ic_w[3]
    
    context['v_w'] = mi_chapeu_vw
    context['ic_vwt_low'] = ic_vwt[1]
    context['ic_vwt_high'] = ic_vwt[2]
    context['ic_vwt_pres'] = ic_vwt[3]
    context['ic_vwchi_low'] = ic_vwchi[1]
    context['ic_vwchi_high'] = ic_vwchi[2]
    context['ic_vwchi_pres'] = ic_vwchi[3]

    context['e_nq'] = mi_chapeu_nq
    context['ic_enq_low'] = ic_nq[1]
    context['ic_enq_high'] = ic_nq[2]
    context['ic_enq_pres'] = ic_nq[3]
    
    context['v_nq'] = mi_chapeu_vnq
    context['ic_vnqt_low'] = ic_vwt[1]
    context['ic_vnqt_high'] = ic_vnqt[2]
    context['ic_vnqt_pres'] = ic_vnqt[3]
    context['ic_vnqchi_low'] = ic_vnqchi[1]
    context['ic_vnqchi_high'] = ic_vnqchi[2]
    context['ic_vnqchi_pres'] = ic_vnqchi[3]
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
    pmf_nq = {}
    nq_medias = []
    nq_vars = []
    medias_tempo_espera = []
    vars_tempo_espera = []
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
        if (len(simulador.fila) in pmf_nq.keys()):
            pmf_nq[len(simulador.fila)].append(dt)
        else:
            pmf_nq[len(simulador.fila)] = [dt]
        nq_medias.append(Statistics.media_pmf(pmf_nq, simulador.instante_atual))
        nq_vars.append(Statistics.var_pmf(pmf_nq, simulador.instante_atual))
        if (evento.tipo == 'chegada'):                
            if(simulador.servidor_ocupado):
                if (disciplina == 'FCFS'):
                    simulador.fila.append(evento.fregues)
                else:
                    simulador.fila.insert(0, evento.fregues)
            else: # serve fregues
                simulador.servidor_ocupado = True
                tempos_espera.append(0)
                medias_tempo_espera.append(Statistics.media_amostral(tempos_espera))
                vars_tempo_espera.append(Statistics.var_amostral(tempos_espera, Statistics.media_amostral(tempos_espera)))
                coletas += 1
                simulador.agendar_partida(simulador.instante_atual, evento.fregues)
                lastmedia_tempo = media_tempo_espera
                media_tempo_espera = simulador.staticts.media_incremental(media_tempo_espera, tempos_espera[coletas-1], coletas)
                mespera.append(media_tempo_espera)
                variancia_tempo_espera = simulador.staticts.var_incremental(variancia_tempo_espera, media_tempo_espera, tempos_espera[coletas-1], lastmedia_tempo, coletas)
                vespera.append(variancia_tempo_espera)
                if(coletas>8000):
                    sumw = 0
                    sumv = 0
                    for k in range(coletas-8000, coletas):
                        sumw += mespera[k]
                        sumv += vespera[k]
                    medias_moveis_w.append(sumw/8000)
                    medias_moveis_v.append(sumv/8000)     
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
                medias_tempo_espera.append(Statistics.media_amostral(tempos_espera))
                vars_tempo_espera.append(Statistics.var_amostral(tempos_espera, Statistics.media_amostral(tempos_espera)))                  
                coletas += 1
                simulador.agendar_partida(simulador.instante_atual, fregues)
                lastmedia_tempo = media_tempo_espera
                media_tempo_espera = simulador.staticts.media_incremental(media_tempo_espera, tempos_espera[coletas-1], coletas)
                mespera.append(media_tempo_espera)
                variancia_tempo_espera = simulador.staticts.var_incremental(variancia_tempo_espera, media_tempo_espera, tempos_espera[coletas-1], lastmedia_tempo, coletas)
                vespera.append(variancia_tempo_espera)
                if(coletas>8000):
                    sumw = 0
                    sumv = 0
                    for k in range(coletas-8000, coletas):
                        sumw += mespera[k]
                        sumv += vespera[k]
                    medias_moveis_w.append(sumw/8000)
                    medias_moveis_v.append(sumv/8000)     
                else:
                    medias_moveis_w.append(0)
                    medias_moveis_v.append(0)
                    #t_rodada = simulador.instante_atual - t_rodada
                    #media_tempo_espera = self.staticts.media_amostral(tempos_espera)
                    #variancia_tempo_espera = self.staticts.var_amostral(tempos_espera)
    # context['V'] = vespera
    # context['MMV'] = medias_moveis_v
    # context['W'] = mespera
    # context['MMW'] = medias_moveis_w
    context['W'] = medias_tempo_espera
    context['V'] = vars_tempo_espera
    context['ENq'] = nq_medias
    context['VNq'] = nq_vars
    #return nq/t_rodada, media_tempo_espera, variancia_tempo_espera
    return HttpResponse(json.dumps(context))