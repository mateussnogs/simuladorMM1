from django.shortcuts import render
from .simulador import *
import time
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from background_task import background
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from ast import literal_eval
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
    
def limpar_arquivos_simulacao(request):
    file_status = open("status_simulacao.txt", "w") # abre para apagar/reiniciar status apenas
    file_status.close()

    file_rodada = open("rodada_atual.txt", "w")
    file_rodada.close()

    file_res_simulacao = open("res_simulacao.txt", "w")
    file_res_simulacao.close()
    return HttpResponse("Arquivos limpos.")

def rodada(request):
    try:
        file_rodada = open("rodada_atual.txt", "r")
        rodadas = file_rodada.readlines()
        file_rodada.close()
    except:
        rodadas = []
    
    context = {
        'rodada_atual': int(rodadas[-1]) if (len(rodadas) > 0) else 0
    }
    return HttpResponse(json.dumps(context))

def status_simulacao(request):
    try:
        file_status = open("status_simulacao.txt", "r")
        status = file_status.readlines()
        file_status.close()
    except:
        status = []
    
    context = {
        'status': status[-1] if (len(status) > 0) else 0
    }
    return HttpResponse(json.dumps(context))

def resultado_simulacao(request):
    try:
        file_status = open("status_simulacao.txt", "w") # abre para apagar/reiniciar status apenas
        file_status.close()

        file_res = open("res_simulacao.txt", "r")
        return HttpResponse(file_res)
    except:
        return HttpResponse("Falha simulação")

@csrf_exempt
def simular_background(request, rho, disciplina, kmin, rodadas, seed_esperta):
    print("chamando simular em background...")
    simular(rho, disciplina, kmin, rodadas, seed_esperta)
    return render(request, 'simulator/main.html', {})

@csrf_exempt
def simular_background2(request, rho, disciplina, rodadas, seed_esperta):
    print("chamando simular em background...")
    simular_kmin(rho, disciplina, rodadas, seed_esperta)
    return render(request, 'simulator/main.html', {})
       
@csrf_exempt
@background(schedule=timezone.now())
def simular(rho, disciplina, kmin, rodadas, seed_esperta):
    file_rodada = open("rodada_atual.txt", "w") # esvazia arquivo caso esteja cheio
    file_rodada.close()
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
    if (seed_esperta == '1'):
        print("seed esperta!")
        try:
            file_random_state = open("random_state.txt", "r")        
            random_state = file_random_state.readline()
            if (len(random_state) > 0):
                random.setstate(literal_eval(random_state))
            file_random_state.close()
        except:
            pass
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
        if (i%501==0): #debug n rodada
            print(i)
        file_rodada = open("rodada_atual.txt", "a")
        file_rodada.write(str(i)+"\n")
        file_rodada.close()
    file_rodada = open("rodada_atual.txt", "w") # esvazia arquivo ja que simulacao acabou
    file_rodada.close()
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
    context['ic_vnqt_low'] = ic_vnqt[1]
    context['ic_vnqt_high'] = ic_vnqt[2]
    context['ic_vnqt_pres'] = ic_vnqt[3]
    context['ic_vnqchi_low'] = ic_vnqchi[1]
    context['ic_vnqchi_high'] = ic_vnqchi[2]
    context['ic_vnqchi_pres'] = ic_vnqchi[3]

    file_random_state = open("random_state.txt", "w")
    file_random_state.write(str(simulador.estado_randomico))
    file_random_state.close()

    context['toplot_EW'] = W
    context['toplot_VW'] = Vw
    context['toplot_ENq'] = Nq
    context['toplot_VNq'] = Vnq
    
    print('end')
    file_status = open("status_simulacao.txt", "w")
    file_status.write("ended")
    file_status.close()
    print('salvando resultado simulação')
    file_res_simulacao = open("res_simulacao.txt", "w")
    file_res_simulacao.write(json.dumps(context))
    print("resultado salvo")
    file_res_simulacao.close()
    return HttpResponse(json.dumps(context))

@csrf_exempt
@background(schedule=timezone.now())
def simular_kmin(rho, disciplina, rodadas, seed_esperta):
    file_rodada = open("rodada_atual.txt", "w") # esvazia arquivo caso esteja cheio
    file_rodada.close()
    context = {
        'e_w': -1,
        'v_w': -1,
        'e_nq': -1,
        'v_nq': -1,
        'ic_ew': [],
        'ic_enq': [],
        'ic_vwt': [],
        'ic_vwchi': [],
        'ic_vnqt': [],
        'ic_vnqchi': [],
        'kmins': []
    }
    analiticoF = {
        'EW': {'0.2': 0.2500, '0.4': 0.6667, '0.6': 1.5000, '0.8': 4.0000, '0.9': 9.0000 },
        'VW': {'0.2': 0.5625, '0.4': 1.7778, '0.6': 5.2500, '0.8': 24.0000, '0.9': 99.0000},
        'ENq': {'0.2': 0.0500, '0.4': 0.2667, '0.6': 0.9000, '0.8': 3.2000, '0.9': 8.1000},
        'VNq': {'0.2': 0.0725, '0.4': 0.5511, '0.6': 2.7900, '0.8': 18.5600, '0.9': 88.2900}
    }
    analiticoL = {
        'EW': {'0.2': 0.2500, '0.4': 0.6667, '0.6': 1.5000, '0.8': 4.0000, '0.9': 9.0000 },
        'VW': {'0.2': 0.7187, '0.4': 3.2592, '0.6': 16.5000, '0.8': 184.0000, '0.9': 1719.0000},
        'ENq': {'0.2': 0.0500, '0.4': 0.2667, '0.6': 0.9000, '0.8': 3.2000, '0.9': 8.1000},
        'VNq': {'0.2': 0.0725, '0.4': 0.5511, '0.6': 2.7900, '0.8': 18.5600, '0.9': 88.2900}
    }
    rho = float(rho)
    simulador = Simulador(rho)
    rodadas = int(rodadas)
    disciplina = str(disciplina)
    if(disciplina == 'FCFS'):
        analitico = analiticoF
    else:
        analitico = analiticoL
    if (seed_esperta == '1'):
        print("seed esperta!")
        try:
            file_random_state = open("random_state.txt", "r")        
            random_state = file_random_state.readline()
            if (len(random_state) > 0):
                random.setstate(literal_eval(random_state))
            file_random_state.close()
        except:
            pass

    kmin_w = [0, 0]
    kmin_nq = [0, 0]
    kmin_vnq = [0, 0]
    kmin_vw = [0, 0]
    analiticoin_w = False
    analiticoin_nq = False
    analiticoin_vnq = False
    analiticoin_vw = False
    k = 5
    while(k>0):
        print(k)
        W = []
        Vw = []
        Nq = []
        Vnq = []
        for i in range(rodadas):
            nqi, vi_nq, wi, vi_w = simulador.simular(disciplina, k)
            W.append(wi) #Conjunto de variaveis aleatorias {Wi}
            Vw.append(vi_w) #Conjunto de variaveis aleatorias {Vi}
            Nq.append(nqi) #Conjunto de variaveis aleatorias {Nqi}
            Vnq.append(vi_nq)
            if (i%501==0): #debug n rodada
                print(i)
            file_rodada = open("rodada_atual.txt", "a")
            file_rodada.write(str(i)+"\n")
            file_rodada.close()
        file_rodada = open("rodada_atual.txt", "w") # esvazia arquivo ja que simulacao acabou
        file_rodada.close()
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

        if(ic_w[3] <= 0.05 and kmin_w[0] == 0):
            kmin_w[0] = k
            print('precisao ok!')
        if(ic_nq[3] <= 0.05 and kmin_nq[0] == 0):
            kmin_nq[0] = k
            print('precisao ok!')
        if(ic_vwt[3] <=0.05 and kmin_vw[0] == 0):
            kmin_vw[0] = k
            print('precisao ok!')
        if(ic_vnqt[3] <= 0.05 and kmin_vnq[0] == 0):
            kmin_vnq[0] = k
            print('precisao ok!')
        if(kmin_w[0] > 0 and kmin_nq[0] > 0 and kmin_vw[0] > 0 and kmin_vnq[0] > 0):
            analiticoAux = analitico['EW']
            if((analiticoAux[str(rho)] < ic_w[1] or analiticoAux[str(rho)] > ic_w[2]) and (not analiticoin_w)):
                print(ic_w[1], analiticoAux[str(rho)], ic_w[2])
                context['ic_ew'].append([ic_w[1], ic_w[2]])
            else:
                if(not analiticoin_w):
                    context['ic_ew'].append([ic_w[1], ic_w[2]])
                    analiticoin_w = True
                    kmin_w[1] = k
                print('ic ok!')
            analiticoAux = analitico['ENq']
            if((analiticoAux[str(rho)] < ic_nq[1] or analiticoAux[str(rho)] > ic_nq[2]) and (not analiticoin_nq)):
                print(ic_nq[1], analiticoAux[str(rho)], ic_nq[2])
                context['ic_enq'].append([ic_nq[1], ic_nq[2]])
            else:
                if(not analiticoin_nq):
                    context['ic_enq'].append([ic_nq[1], ic_nq[2]])
                    analiticoin_nq = True
                    kmin_nq[1] = k
                print('ic ok!')
            analiticoAux = analitico['VW']
            if((analiticoAux[str(rho)] < ic_vwchi[1] or analiticoAux[str(rho)] > ic_vwchi[2]) and (not analiticoin_vw)):
                print(ic_vwchi[1], analiticoAux[str(rho)], ic_vwchi[2])
                context['ic_vwt'].append([ic_vwt[1], ic_vwt[2]])
                context['ic_vwchi'].append([ic_vwchi[1], ic_vwchi[2]])
            else:
                if(not analiticoin_vw):
                    context['ic_vwt'].append([ic_vwt[1], ic_vwt[2]])
                    context['ic_vwchi'].append([ic_vwchi[1], ic_vwchi[2]])
                    analiticoin_vw = True
                    kmin_vw[1] = k
                print('ic ok!')
            analiticoAux = analitico['VNq']
            if((analiticoAux[str(rho)] < ic_vnqchi[1] or analiticoAux[str(rho)] > ic_vnqchi[2]) and (not analiticoin_vnq)):
                print(ic_vnqchi[1], analiticoAux[str(rho)], ic_vnqchi[2])
                context['ic_vnqt'].append([ic_vnqt[1], ic_vnqt[2]])
                context['ic_vnqchi'].append([ic_vnqchi[1], ic_vnqchi[2]])
            else:
                if(not analiticoin_vnq):
                    context['ic_vnqt'].append([ic_vnqt[1], ic_vnqt[2]])
                    context['ic_vnqchi'].append([ic_vnqchi[1], ic_vnqchi[2]])
                    analiticoin_vnq = True
                    kmin_vnq[1] = k
                print('ic ok!')
            if(analiticoin_w and analiticoin_nq and analiticoin_vw and analiticoin_vnq):
                k = -1
            else:
                if(k >= 10000):
                    k += 5000
                else:
                    if(k >= 1000):
                        k += 1000
                    else:
                        if(k%100 == 0):
                            k += 100
                        else:
                            k = 100
        else: 
            if(k==1):
                k = 5
            else:
                k += 5

    context['kmins'].append([kmin_w[0], kmin_w[1]])
    context['kmins'].append([kmin_nq[0], kmin_nq[1]])
    context['kmins'].append([kmin_vw[0], kmin_vw[1]])
    context['kmins'].append([kmin_vnq[0], kmin_vnq[1]])

    file_random_state = open("random_state.txt", "w")
    file_random_state.write(str(simulador.estado_randomico))
    file_random_state.close()
    
    print('end')
    file_status = open("status_simulacao.txt", "w")
    file_status.write("ended")
    file_status.close()
    print('salvando resultado simulação')
    file_res_simulacao = open("res_simulacao.txt", "w")
    file_res_simulacao.write(json.dumps(context))
    print("resultado salvo")
    file_res_simulacao.close()
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
    #medias_tempo_espera = []
    #vars_tempo_espera = []
    medias_moveis_w = []
    medias_moveis_v = []
    medias_moveis_vnq = []
    medias_moveis_nq = []
    media_tempo_espera = 0
    variancia_tempo_espera = 0
    #t_rodada = simulador.instante_atual
    context = {
        'V': [],
        'W': []
    }
    if (len(simulador.eventos.eventos) == 0):
        simulador.agendar_chegada(simulador.instante_atual)
    coletas = 0
    t_end = time.time() + 60
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
        if (evento.tipo == 'chegada'):                
            if(simulador.servidor_ocupado):
                if (disciplina == 'FCFS'):
                    simulador.fila.append(evento.fregues)
                else:
                    simulador.fila.insert(0, evento.fregues)
            else: # serve fregues
                simulador.servidor_ocupado = True
                tempos_espera.append(0)
                #medias_tempo_espera.append(Statistics.media_amostral(tempos_espera))
                #vars_tempo_espera.append(Statistics.var_amostral(tempos_espera, Statistics.media_amostral(tempos_espera)))
                coletas += 1
                simulador.agendar_partida(simulador.instante_atual, evento.fregues)
                lastmedia_tempo = media_tempo_espera
                media_tempo_espera = simulador.staticts.media_incremental(media_tempo_espera, tempos_espera[coletas-1], coletas)
                mespera.append(media_tempo_espera)
                variancia_tempo_espera = simulador.staticts.var_incremental(variancia_tempo_espera, media_tempo_espera, tempos_espera[coletas-1], lastmedia_tempo, coletas)
                vespera.append(variancia_tempo_espera)
                nq_medias.append(Statistics.media_pmf(pmf_nq, simulador.instante_atual))
                nq_vars.append(Statistics.var_pmf(pmf_nq, simulador.instante_atual))
                if(coletas>500):
                    sumw = 0
                    sumv = 0
                    sumnq = 0
                    sumvnq = 0  
                    for k in range(coletas-500, coletas):
                        sumw += mespera[k]
                        sumv += vespera[k]
                        sumnq += nq_medias[k]
                        sumvnq += nq_vars[k]
                    medias_moveis_nq.append(sumnq/500)    
                    medias_moveis_vnq.append(sumvnq/500)  
                    medias_moveis_w.append(sumw/500)
                    medias_moveis_v.append(sumv/500)    
                else:
                    medias_moveis_w.append(0)
                    medias_moveis_v.append(0)
                    medias_moveis_nq.append(0)    
                    medias_moveis_vnq.append(0)  
            simulador.agendar_chegada(simulador.instante_atual)
        else: #partida
            simulador.servidor_ocupado = False
            if (len(simulador.fila) > 0):
                simulador.servidor_ocupado = True
                fregues = simulador.fila.pop(0)
                tempos_espera.append(simulador.instante_atual-fregues.instante_chegada)  
                #medias_tempo_espera.append(Statistics.media_amostral(tempos_espera))
                #vars_tempo_espera.append(Statistics.var_amostral(tempos_espera, Statistics.media_amostral(tempos_espera)))                  
                coletas += 1
                simulador.agendar_partida(simulador.instante_atual, fregues)
                lastmedia_tempo = media_tempo_espera
                media_tempo_espera = simulador.staticts.media_incremental(media_tempo_espera, tempos_espera[coletas-1], coletas)
                mespera.append(media_tempo_espera)
                variancia_tempo_espera = simulador.staticts.var_incremental(variancia_tempo_espera, media_tempo_espera, tempos_espera[coletas-1], lastmedia_tempo, coletas)
                vespera.append(variancia_tempo_espera)
                nq_medias.append(Statistics.media_pmf(pmf_nq, simulador.instante_atual))
                nq_vars.append(Statistics.var_pmf(pmf_nq, simulador.instante_atual))
                if(coletas>500):
                    sumw = 0
                    sumv = 0
                    sumnq = 0
                    sumvnq = 0  
                    for k in range(coletas-500, coletas):
                        sumw += mespera[k]
                        sumv += vespera[k]
                        sumnq += nq_medias[k]
                        sumvnq += nq_vars[k]
                    medias_moveis_nq.append(sumnq/500)    
                    medias_moveis_vnq.append(sumvnq/500)  
                    medias_moveis_w.append(sumw/500)
                    medias_moveis_v.append(sumv/500)    
                else:
                    medias_moveis_w.append(0)
                    medias_moveis_v.append(0)
                    medias_moveis_nq.append(0)    
                    medias_moveis_vnq.append(0)  
                    #t_rodada = simulador.instante_atual - t_rodada
                    #media_tempo_espera = self.staticts.media_amostral(tempos_espera)
                    #variancia_tempo_espera = self.staticts.var_amostral(tempos_espera)
    context['MMV'] = medias_moveis_v
    context['MMW'] = medias_moveis_w
    context['MMVNq'] = medias_moveis_vnq
    context['MMNq'] = medias_moveis_nq
    context['W'] = mespera
    context['V'] = vespera
    context['ENq'] = nq_medias
    context['VNq'] = nq_vars
    #return nq/t_rodada, media_tempo_espera, variancia_tempo_espera
    return HttpResponse(json.dumps(context))

@csrf_exempt
def simular_deterministic(request, disciplina):
    context = {
        'e_w': -1,
        'v_w': -1,
        'e_nq': -1,
        'v_nq': -1
    }
    simulador = SimuladorDeterministico()
    disciplina = str(disciplina)
    
    nq, v_nq, w, v_w = simulador.simular(disciplina)

    context['e_w'] = w
    context['v_w'] = v_w
    context['e_nq'] = nq
    context['v_nq'] = v_nq
    print('run')
    return HttpResponse(json.dumps(context))
