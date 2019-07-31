import random
from math import log
# from scipy.stats import t, chi2
from math import sqrt
import time

class Statistics:
    @staticmethod
    def media_amostral(X): #estimador media
        n = len(X)
        soma = 0
        for i in range(n):
            soma += X[i]
        return soma/n

    @staticmethod
    def media_incremental(media_j, x, i): #estimador media incremental
        if(i>0):
            return media_j + (x - media_j)/i
        else:
            return x

    @staticmethod
    def var_amostral(X, mi_chapeu): #estimador variancia
        n = len(X)
        if ((n-1) == 0):
            return 0
        soma = 0
        for i in range(n):
            soma += (X[i] - mi_chapeu)**2
        return soma/(n-1)

    @staticmethod
    def media_pmf(pmf, total):
        media = 0
        pn_s = []
        for key in pmf.keys():
            pn = 0
            for i in range(len(pmf[key])):
                pn += pmf[key][i]
            pn = pn/total
            media += key*pn
        return media

    @staticmethod
    def var_pmf(pmf, total):
        media = Statistics.media_pmf(pmf, total)
        segundo_momento = 0
        for key in pmf.keys():
            pn = 0
            for i in range(len(pmf[key])):
                pn += pmf[key][i]
            pn = pn/total
            segundo_momento += (key**2)*pn
        var = segundo_momento - media**2
        return var

    @staticmethod
    def var_incremental(var_j, media_i, x, media_j, i): #estimador variancia incremental
        if(i>0):
            return ((i-1)*var_j + (x - media_i)*(x - media_j))/i
        else:
            return 0

    @staticmethod
    def intervalo_de_confianca_tstudent(michapeu, sigma2chapeu, n, ic): #calcula IC aplicando formula
        alpha = (1 - ic)
        # t_student = t.ppf(1 - alpha/2, n-1)
        t_student = 1.9607 
        mul = sqrt(sigma2chapeu / n)
        superior = michapeu + t_student * mul
        inferior = michapeu - t_student * mul
        precisao = (superior - inferior)/(superior + inferior)
        centro = (superior + inferior)/2
        return centro, inferior, superior, precisao
  
    @staticmethod
    def intervalo_de_confianca_chi2(sigma2chapeu, n, ic): #calcula IC aplicando formula
        alpha = (1 - ic)
        # chi2_sup = chi2.ppf(alpha/2, n - 1)
        chi2_sup = 3044.13
        # chi2_inf = chi2.ppf(1 - alpha/2, n - 1)
        chi2_inf = 3357.65
        inferior = ((n - 1) * sigma2chapeu) / chi2_inf
        superior = ((n - 1) * sigma2chapeu) / chi2_sup
        precisao = (chi2_inf - chi2_sup) / (chi2_inf + chi2_sup)
        centro = (superior + inferior) / 2
        return centro, inferior, superior, precisao

class AmostradorExponencial:
    def __init__(self, lamb):
        self.lamb = lamb
        random.seed(13)
    def gerar_amostra(self):
        u0 = random.uniform(0,1)
        x0 = log(u0)/(-self.lamb)
        return x0

class AmostradorDeterministico:
    def __init__(self):
        self.momentosChegada = [0, 5, 8, 15, 17, 18, 0, 5, 8, 15, 17, 18, 0, 5, 8, 15, 17, 18]
    def getChegada(self, index):
        return self.momentosChegada[index]

class Fregues:
    def __init__(self, instante_chegada, cor):
        self.instante_chegada = instante_chegada
        self.cor = cor

class Evento:
    def __init__(self, tipo, instante, fregues):
        self.tipo = tipo
        self.instante = instante              
        self.fregues = fregues

class Chegada(Evento):
    def __init__(self, instante, fregues):
        Evento.__init__(self, "chegada", instante, fregues)    

class Partida(Evento):
    def __init__(self, instante, fregues):
        Evento.__init__(self, "partida", instante, fregues)

class Eventos:
    def __init__(self):
        self.eventos = []
    def proximo_evento(self):
        return self.eventos.pop(0)
    def agendar_evento(self, evento):
        achou_posicao = False
        for i in range(len(self.eventos)):
            if (evento.instante <= self.eventos[i].instante):
                self.eventos.insert(i, evento)
                achou_posicao = True
                break
        if (not achou_posicao):
            self.eventos.append(evento)  

class Simulador:
    def __init__(self, rho = 0.8):
        self.eventos = Eventos()
        self.amostrador_chegada = AmostradorExponencial(rho) # lambda = rho se tempo de serviço = 1
        self.amostrador_servico = AmostradorExponencial(1) # mi = 1
        self.fila = []
        self.servidor_ocupado = False
        self.instante_atual = 0
        self.staticts = Statistics
        self.rodada_atual = 0
        self.estado_randomico = None
        
    def agendar_chegada(self, instante):
        demora_chegar = self.amostrador_chegada.gerar_amostra()
        instante_ocorrencia = instante + demora_chegar
        self.eventos.agendar_evento(Chegada(instante_ocorrencia, Fregues(instante_ocorrencia, self.rodada_atual)))
        
    def agendar_partida(self, instante, fregues):
        demora_partir = self.amostrador_servico.gerar_amostra()
        instante_ocorrencia = instante + demora_partir
        self.eventos.agendar_evento(Partida(instante_ocorrencia, fregues))
        
    def simular(self, disciplina='FCFS', kmin=3000):
        tempos_espera = []
        area_nq = 0 # ou primeiro momento
        seg_momento_nq = 0
        pmf_nq = {}
        nq_medias = []
        media_tempo_espera = 0
        variancia_tempo_espera = 0
        t_rodada = self.instante_atual
        if (len(self.eventos.eventos) == 0):
            self.agendar_chegada(self.instante_atual)
        coletas = 0
        while(True):
            evento = self.eventos.proximo_evento()
            dt = self.instante_atual
            self.instante_atual = evento.instante # avança o tempo para instante do evento
            dt = self.instante_atual - dt            
            area_nq += len(self.fila)*dt
            seg_momento_nq += (len(self.fila)**2)*dt
            # if (len(self.fila) in pmf_nq.keys()):
            #     pmf_nq[len(self.fila)].append(dt)
            # else:
            #     pmf_nq[len(self.fila)] = [dt]
            # # nq_medias.append(Statistics.media_pmf(pmf_nq, self.instante_atual))
            if (evento.tipo == 'chegada'):                
                if(self.servidor_ocupado):
                    if (disciplina == 'FCFS'):
                        self.fila.append(evento.fregues)
                    else:
                        self.fila.insert(0, evento.fregues)
                else: # serve fregues
                    self.servidor_ocupado = True
                    if (evento.fregues.cor == self.rodada_atual):
                        tempos_espera.append(0)
                        coletas += 1
                    self.agendar_partida(self.instante_atual, evento.fregues)
                    # lastmedia_tempo = media_tempo_espera
                    # media_tempo_espera = self.staticts.media_incremental(media_tempo_espera, tempos_espera[coletas-1], coletas)
                    # variancia_tempo_espera = self.staticts.var_incremental(variancia_tempo_espera, media_tempo_espera, tempos_espera[coletas-1], lastmedia_tempo, coletas)
                self.agendar_chegada(self.instante_atual)
            else: #partida
                self.servidor_ocupado = False
                if (len(self.fila) > 0):
                    self.servidor_ocupado = True
                    fregues = self.fila.pop(0)
                    if (fregues.cor == self.rodada_atual):
                        tempos_espera.append(self.instante_atual-fregues.instante_chegada)                    
                        coletas += 1
                    self.agendar_partida(self.instante_atual, fregues)
                    # lastmedia_tempo = media_tempo_espera
                    # media_tempo_espera = self.staticts.media_incremental(media_tempo_espera, tempos_espera[coletas-1], coletas)
                    # variancia_tempo_espera = self.staticts.var_incremental(variancia_tempo_espera, media_tempo_espera, tempos_espera[coletas-1], lastmedia_tempo, coletas)
            if (coletas >= kmin):
                self.rodada_atual += 1
                t_rodada = self.instante_atual - t_rodada
                media_tempo_espera = self.staticts.media_amostral(tempos_espera)
                variancia_tempo_espera = self.staticts.var_amostral(tempos_espera, media_tempo_espera)
                self.estado_randomico = random.getstate()
                return area_nq/t_rodada, (seg_momento_nq/t_rodada-(area_nq/t_rodada)**2), media_tempo_espera, variancia_tempo_espera
            
class SimuladorDeterministico:
    def __init__(self):
        self.eventos = Eventos()
        self.amostrador_chegada = AmostradorDeterministico()
        self.amostrador_servico = AmostradorDeterministico()
        self.fila = []
        self.servidor_ocupado = False
        self.chegadas = 0
        self.instante_atual = 0
        self.staticts = Statistics
        self.rodada_atual = 0
        
    def agendar_chegada(self, instante):
        instante_ocorrencia = self.amostrador_chegada.getChegada(instante)
        self.eventos.agendar_evento(Chegada(instante_ocorrencia, Fregues(instante_ocorrencia, self.rodada_atual)))
        
    def agendar_partida(self, instante, fregues):
        demora_partir = 5
        instante_ocorrencia = instante + demora_partir
        self.eventos.agendar_evento(Partida(instante_ocorrencia, fregues))
        
    def simular(self, disciplina='FCFS'):
        tempos_espera = []
        area_nq = 0 # ou primeiro momento
        seg_momento_nq = 0
        media_tempo_espera = 0
        variancia_tempo_espera = 0
        t_rodada = self.instante_atual
        if (len(self.eventos.eventos) == 0):
            self.agendar_chegada(self.chegadas)
        coletas = 0
        while(self.instante_atual < 35):
            evento = self.eventos.proximo_evento()
            dt = self.instante_atual
            self.instante_atual = evento.instante # avança o tempo para instante do evento
            dt = self.instante_atual - dt
            time.sleep(dt)
            print(self.instante_atual)
            area_nq += len(self.fila)*dt
            seg_momento_nq += (len(self.fila)**2)*dt
            # if (len(self.fila) in pmf_nq.keys()):
            #     pmf_nq[len(self.fila)].append(dt)
            # else:
            #     pmf_nq[len(self.fila)] = [dt]
            # # nq_medias.append(Statistics.media_pmf(pmf_nq, self.instante_atual))
            if (evento.tipo == 'chegada'):                
                if(self.servidor_ocupado):
                    if (disciplina == 'FCFS'):
                        self.fila.append(evento.fregues)
                    else:
                        self.fila.insert(0, evento.fregues)
                else: # serve fregues
                    self.servidor_ocupado = True
                    if (evento.fregues.cor == self.rodada_atual):
                        tempos_espera.append(0)
                        coletas += 1
                    self.agendar_partida(self.instante_atual, evento.fregues)
                    # lastmedia_tempo = media_tempo_espera
                    # media_tempo_espera = self.staticts.media_incremental(media_tempo_espera, tempos_espera[coletas-1], coletas)
                    # variancia_tempo_espera = self.staticts.var_incremental(variancia_tempo_espera, media_tempo_espera, tempos_espera[coletas-1], lastmedia_tempo, coletas)
                self.chegadas += 1
                if(self.chegadas < 6):
                    self.agendar_chegada(self.chegadas)
            else: #partida
                self.servidor_ocupado = False
                if (len(self.fila) > 0):
                    self.servidor_ocupado = True
                    fregues = self.fila.pop(0)
                    if (fregues.cor == self.rodada_atual):
                        tempos_espera.append(self.instante_atual-fregues.instante_chegada)                    
                        coletas += 1
                    self.agendar_partida(self.instante_atual, fregues)
                    # lastmedia_tempo = media_tempo_espera
                    # media_tempo_espera = self.staticts.media_incremental(media_tempo_espera, tempos_espera[coletas-1], coletas)
                    # variancia_tempo_espera = self.staticts.var_incremental(variancia_tempo_espera, media_tempo_espera, tempos_espera[coletas-1], lastmedia_tempo, coletas)
            if (len(self.eventos.eventos) == 0):
                self.instante_atual += 5
                time.sleep(5000)
        self.rodada_atual += 1
        t_rodada = self.instante_atual - t_rodada
        media_tempo_espera = self.staticts.media_amostral(tempos_espera)
        variancia_tempo_espera = self.staticts.var_amostral(tempos_espera, media_tempo_espera)
        return area_nq/t_rodada, (seg_momento_nq/t_rodada-(area_nq/t_rodada)**2), media_tempo_espera, variancia_tempo_espera

            
            
def get_equilibrio(rho, disciplina):
    k = 0
    if disciplina == 'FCFS':
        if rho == 0.2:
            k = 4500
        elif rho == 0.4:
            k = 4500
        elif rho == 0.6:
            k = 4500
        elif rho == 0.8:
            k = 4500
        elif rho == 0.9:
            k = 4500
    else: # LCFS
        if rho == 0.2:
            k = 5000
        elif rho == 0.4:
            k = 5000
        elif rho == 0.6:
            k = 4500
        elif rho == 0.8:
            k = 4500
        elif rho == 0.9:
            k = 4500
    simulador = Simulador(rho)
    simulador.simular(disciplina, k)
    print("equilibrio uhul")
    return simulador
        