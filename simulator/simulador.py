import random
from math import log
# from scipy.stats import t, chi2
from math import sqrt

class Statistics:
    @staticmethod
    def media_amostral(X):
        n = len(X)
        soma = 0
        for i in range(n):
            soma += X[i]
        return soma/n
    @staticmethod
    def var_amostral(X):
        mi_chapeu = Statistics.media_amostral(X)
        n = len(X)
        soma = 0
        for i in range(n):
            soma += (X[i] - mi_chapeu)**2
        return soma/(n-1)

class AmostradorExponencial:
    def __init__(self, lamb):
        self.lamb = lamb
        random.seed(13)
    def gerar_amostra(self):
        u0 = random.uniform(0,1)
        x0 = log(u0)/(-self.lamb)
        return x0

class Fregues:
    def __init__(self, instante_chegada):
        self.instante_chegada = instante_chegada

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
        
    def agendar_chegada(self, instante):
        demora_chegar = self.amostrador_chegada.gerar_amostra()
        instante_ocorrencia = instante + demora_chegar
        self.eventos.agendar_evento(Chegada(instante_ocorrencia, Fregues(instante_ocorrencia)))
        
    def agendar_partida(self, instante, fregues):
        demora_partir = self.amostrador_servico.gerar_amostra()
        instante_ocorrencia = instante + demora_partir
        self.eventos.agendar_evento(Partida(instante_ocorrencia, fregues))
        
    def simular(self, disciplina='FCFS', kmin=3000):
        tempos_espera = []
        nq = 0
        t_rodada = self.instante_atual
        if (len(self.eventos.eventos) == 0):
            self.agendar_chegada(self.instante_atual)
        coletas = 0
        while(True):
            evento = self.eventos.proximo_evento()
            dt = self.instante_atual
            self.instante_atual = evento.instante # avança o tempo para instante do evento
            dt = self.instante_atual - dt            
            nq += len(self.fila)*dt
            if (evento.tipo == 'chegada'):                
                if(self.servidor_ocupado):
                    if (disciplina == 'FCFS'):
                        self.fila.append(evento.fregues)
                    else:
                        self.fila.insert(0, evento.fregues)
                else: # serve fregues
                    self.servidor_ocupado = True
                    tempos_espera.append(0)
                    coletas += 1
                    self.agendar_partida(self.instante_atual, evento.fregues)
                self.agendar_chegada(self.instante_atual)
            else: #partida
                self.servidor_ocupado = False
                if (len(self.fila) > 0):
                    self.servidor_ocupado = True
                    fregues = self.fila.pop(0)
                    tempos_espera.append(self.instante_atual-fregues.instante_chegada)                    
                    coletas += 1
                    self.agendar_partida(self.instante_atual, fregues)
            if (coletas >= kmin):
                t_rodada = self.instante_atual - t_rodada
                return nq/t_rodada, tempos_espera
            
            
