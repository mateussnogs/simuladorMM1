import random
import matplotlib.pyplot as plt
from math import log
import numpy as np
from scipy.stats import t, chi2
from math import sqrt
import scipy.stats as st

class Metricas:

    def calcula_media(self, X):
        som = 0
        n = len(X)
        for xi in X:
            som = som + xi
        med = som/n
        return med

    def calcula_variancia(self, X, mi_chapeu):
        som = 0
        n = len(X)
        for xi in X:
            som = som + (xi - mi_chapeu)**2
        var = som/(n-1) # estimador variancia nao tendencioso
        return var

    def calcula_variancia_rodada(self, X):
        xsom = 0
        som = 0
        k = len(X)
        for i in X:
            for j in X:
                xsom = xsom + j
            xsom = xsom/k
            som = som + (i - xsom)**2
        var = som/(k-1)
        return var
  
    def intervalo_de_confianca_tstudent(self, michapeu, sigma2chapeu, n, ic):
        alpha = (1 - ic)
        t_student = t.ppf(1 - alpha/2, n-1) #ignora isso e poe valor de tabela
        mul = sqrt(sigma2chapeu / n)
        superior = michapeu + t_student * mul
        inferior = michapeu - t_student * mul
        precisao = (superior - inferior)/(superior + inferior)
        centro = (superior + inferior)/2
        return centro, inferior, superior, precisao
  
    def intervalo_de_confianca_chi2(self, michapeu, sigma2chapeu, k, n, ic):
        alpha = (1 - ic)
        chi2_sup = chi2.ppf(alpha/2, n - 1)
        chi2_inf = chi2.ppf(1 - alpha/2, n - 1)
        inferior = (n - 1) * sigma2chapeu * k / chi2_inf
        superior = (n - 1) * sigma2chapeu * k / chi2_sup
        precisao = (chi2_inf - chi2_sup) / (chi2_inf + chi2_sup)
        centro = (superior + inferior) / 2
        return centro, inferior, superior, precisao

    def cov_rodadas_sucessivas(self, Xi1, Xi2, mi_chapeu):
        n = len(Xi2)
        som = 0
        for i in range(n-1): #Xi2 vai ter uma amostra a mais
            som += (Xi1[i] - mi_chapeu) * (Xi2[i] - mi_chapeu)
        covariancia = som/(n-2)
        return covariancia

class AmostradorExponencial:
    def __init__(self, lamb):
        self.lamb = lamb
        random.seed(13)
    def gerar_amostra(self):
        u0 = random.uniform(0,1)
        x0 = log(u0)/(-self.lamb)
        return x0

class Fregues:
    def __init__(self, instante_chegada, num):
        self.instante_chegada = instante_chegada
        self.num = num

class Evento:
    def __init__(self, tipo, instante, offset, fregues):
        self.tipo = tipo
        self.instante = instante
        self.offset = offset                
        self.fregues = fregues
    def instante_ocorrencia(self):
        return self.instante + self.offset

class Chegada(Evento):
    def __init__(self, instante, offset, fregues):
        Evento.__init__(self, "chegada", instante, offset, fregues)
    
class Partida(Evento):
    def __init__(self, instante, offset, fregues):
        Evento.__init__(self, "partida", instante, offset, fregues)

class Eventos:
    def __init__(self):
        self.eventos = []
    def proximo_evento(self):
        return self.eventos.pop(0)
    def agendar_evento(self, evento):
        achou_posicao = False
        for i in range(len(self.eventos)):
            if (evento.instante_ocorrencia() <= self.eventos[i].instante_ocorrencia()):
                self.eventos.insert(i, evento)
                achou_posicao = True
                break
        if (not achou_posicao):
            self.eventos.append(evento)            

class Simulador:
    def __init__(self, rho = 0.8, min_estabilidade = 10000):
        self.fila = []
        self.rho = rho
        self.servidor_ocupado = False
        self.instante_atual = 0
        self.n_fregues = 0
        self.amostrador_chegada = AmostradorExponencial(rho)
        self.amostrador_servico = AmostradorExponencial(1)
        #self.amostrador_chegada_determ = AmostradorDeterministico(2)
        #self.amostrador_servico_determ = AmostradorDeterministico(4)
        self.eventos = Eventos()
        self.tempos_espera = []
        self.areas = 0 # armazena a soma das areas Nq x dT
        self.fase_transiente = True
        self.coletas = 0
        self.min_estabilidade = min_estabilidade
    
    def agendar_chegada(self, instante_atual):
        demora_chegar = self.amostrador_chegada.gerar_amostra()        
        instante_chegada = instante_atual+demora_chegar
        fregues = Fregues(instante_chegada, self.n_fregues)
        self.eventos.agendar_evento(Chegada(instante_atual, demora_chegar, fregues))
        
    def agendar_partida(self, instante_atual, fregues):
        demora_partir = self.amostrador_servico.gerar_amostra()
        self.eventos.agendar_evento(Partida(instante_atual, demora_partir, fregues))
    
    def simular(self, disciplina='FCFS', kmin = 1000): #default = FCFS
#         self.__init__(self.rho)
        self.coletas = 0
        self.servidor_ocupado = False
        if (self.instante_atual == 0):
            self.agendar_chegada(self.instante_atual) # primeira chegada que começa em 0(agora)+offset da chegada
        while(True):
            evento = self.eventos.proximo_evento()            
            self.instante_atual = evento.instante_ocorrencia() # avança o tempo para o instante do evento
            self.areas += len(self.fila)*evento.offset # acumula Nq x dT
            if (evento.tipo == 'chegada'):
                self.n_fregues += 1 # chegou mais um fregues
                if (self.servidor_ocupado):
                    index = 0
                    if(disciplina == 'FCFS'):
                        index = len(self.fila)
                    elif(disciplina == 'LCFS'):
                        index = 0
                    self.fila.insert(index, evento.fregues) # fregues espera na fila
                else: # vai para o servidor
                    self.servidor_ocupado = True # fregues sendo servido
                    self.tempos_espera.append(0) # se chegou e foi direto para o servidor, tempo de espera é zero
                    self.coletas += 1
                    self.agendar_partida(self.instante_atual, evento.fregues) # agenda uma partida a partir do instante atual
                self.agendar_chegada(self.instante_atual) # agenda uma nova chegada
            else: # partida
                self.servidor_ocupado = False # fregues servido
                if (len(self.fila) > 0):
                    fregues = self.fila.pop(0) # serve o primeiro fregues da fila 
                    self.tempos_espera.append(self.instante_atual - fregues.instante_chegada) # tempo de espera do fregues na fila              
                    self.coletas += 1
                    self.agendar_partida(self.instante_atual, fregues)
                    self.servidor_ocupado = True
            if (self.fase_transiente and self.coletas >= self.min_estabilidade):
                print("Fase transiente atingida.")
                print("Nq:", len(self.fila))
                print("len(w)", len(self.tempos_espera))
                print(self.areas/self.instante_atual/2)
                print(np.mean(self.tempos_espera))
                #limpa tudo
                self.n_fregues = 0
#                 self.tempos_espera = []
#                 self.areas = 0 # armazena a soma das areas Nq x dT
                self.coletas = 0
                self.fase_transiente = False
            if (not self.fase_transiente and self.coletas >= kmin):
                
                return self.areas/self.instante_atual/2, self.tempos_espera