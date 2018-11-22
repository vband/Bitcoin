import urllib.request
import time
import telepot
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

# Função que retorna a média aritmética de uma lista
def media_aritmetica(lista):
        n = len(lista)
        m = 0
        for i in range(n):
                m = m + lista[i]
        m = m / n
        return m

# Processamento principal
def processamento():

        # Parâmetros

        n_dias_curto_prazo = 12
        n_dias_longo_prazo = 26
        n_dias_macd = 9

        # Obtenção dos preços

        fechamentos = urllib.request.urlopen("https://api.bitfinex.com/v2/candles/trade:6h:tBTCUSD/hist?limit=1000").read()
		
		# Tratamento dos dados

        fechamentos = str(fechamentos)

        fechamentos = fechamentos[4:-3]

        fechamentos = fechamentos.split("],[")

        for i in range(len(fechamentos)):
            fechamentos[i] = fechamentos[i].split(",")
            for j in range(len(fechamentos[i])):
                fechamentos[i][j] = float(fechamentos[i][j])
		
        # Invertendo a lista para percorrê-la do fechamento mais antigo para o mais atual
		
        fechamentos.reverse()

        ##print(fechamentos)

        # Cálculo das primeiras médias aritméticas

        primeira_media_curto_prazo = 0

        for i in range(n_dias_curto_prazo):
                primeira_media_curto_prazo = primeira_media_curto_prazo + fechamentos[i][2]
        primeira_media_curto_prazo = primeira_media_curto_prazo / n_dias_curto_prazo

        primeira_media_longo_prazo = 0

        for i in range(n_dias_longo_prazo):
                primeira_media_longo_prazo = primeira_media_longo_prazo + fechamentos[i][2]
        primeira_media_longo_prazo = primeira_media_longo_prazo / n_dias_longo_prazo

        # Cálculo das médias (curto prazo)

        medias_curto_prazo = []
        multiplicador_curto_prazo = (2 / (n_dias_curto_prazo + 1) )

        for i in range(len(fechamentos)):
                # Preenche os primeiros valores com None
                if i < n_dias_curto_prazo-1:
                        medias_curto_prazo.append(None)
                # Inicializa a primeira média com a média aritmética
                elif i == n_dias_curto_prazo-1:
                        medias_curto_prazo.append(primeira_media_curto_prazo)
                # Calcula a média
                else:
                        medias_curto_prazo.append((fechamentos[i][2] - medias_curto_prazo[i-1]) * multiplicador_curto_prazo + medias_curto_prazo[i-1])

        ##print(medias_curto_prazo)

        # Cálculo das médias (longo prazo)

        medias_longo_prazo = []
        multiplicador_longo_prazo = (2 / (n_dias_longo_prazo + 1) )

        for i in range(len(fechamentos)):
                # Preenche os primeiros valores com None
                if i < n_dias_longo_prazo-1:
                        medias_longo_prazo.append(None)
                # Inicializa a primeira média com a média aritmética
                elif i == n_dias_longo_prazo-1:
                        medias_longo_prazo.append(primeira_media_longo_prazo)
                # Calcula a média
                else:
                        medias_longo_prazo.append((fechamentos[i][2] - medias_longo_prazo[i-1]) * multiplicador_longo_prazo + medias_longo_prazo[i-1])

        ##print(medias_longo_prazo)

        # Cálculo do MACD

        macd = []

        for i in range(len(fechamentos)):
                if medias_longo_prazo[i] != None:
                        macd.append(medias_curto_prazo[i] - medias_longo_prazo[i])
                else:
                        macd.append(None)

        ##print(macd)

        # Cálculo do signal

        signal = []
        multiplicador_signal = (2 / (n_dias_macd + 1) )

        for i in range(len(fechamentos)):
                # Preenche os primeiros valores com None
                if i < (n_dias_longo_prazo + n_dias_macd - 2):
                        signal.append(None)
                # Inicializa o primeiro signal com a média aritmética dos 9 primeiros MACDs
                elif i == (n_dias_longo_prazo + n_dias_macd - 2):
                        signal.append(media_aritmetica(macd[i-n_dias_macd+1 : i+1]))
                # Calcula o signal
                else:
                        signal.append((macd[i] - signal[i-1]) * multiplicador_signal + signal[i-1])

        ##print(signal)

        # Cálculo do histograma

        histograma = []

        for i in range(len(fechamentos)):
                if signal[i] != None and macd[i] != None:
                        histograma.append(macd[i] - signal[i])
                else:
                        histograma.append(None)

        ##print(histograma)

        # Cálculo do vetor de compra (true caso compra, false caso contrário)

        compra = []

        for i in range(len(fechamentos)):
                if histograma[i] == None or histograma[i-1] == None or signal[i] == None:
                        compra.append(False)
                else:
                        if histograma[i] > 0 and histograma[i-1] < 0 and signal[i] < 0:
                                compra.append(True)
                        else:
                                compra.append(False)

        ##print(compra)

        # Cálculo do vetor de venda (true caso venda, false caso contrário)

        venda = []

        for i in range(len(fechamentos)):
                if histograma[i] == None or histograma[i-1] == None:
                        venda.append(False)
                else:
                        if histograma[i] < 0 and histograma[i-1] > 0:
                                venda.append(True)
                        else:
                                venda.append(False)

        print("Venda: %s" %(venda[-1]))
        print("Compra: %s" %(compra[-1]))
		
		##print(venda)
		
        # Envia mensagem pelo Telegram
		
        bot = telepot.Bot('703200255:AAF5ym-tGJSOIaTDyu5XKi605-Uq6GWtWow')
        #bot.sendMessage(-260640827, "Venda: %s" %(venda[-1])) # Grupo de Análise de Risco
        #bot.sendMessage(-260640827, "Compra: %s" %(compra[-1]))
		
        bot.sendMessage(149282401, "Venda: %s" %(venda[-1])) # Meu privado
        bot.sendMessage(149282401, "Compra: %s" %(compra[-1]))
		
        # Desenha gráficos na tela
		
        tempos = []
        locations = [0, 250, 500, 750, 999]
        for i in range(len(fechamentos)):
                if i in locations:
                        ts = int(fechamentos[i][0])
                        ts /= 1000
                        tempos.append(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
                        #tempos.append(datetime.utcfromtimestamp(ts).strftime('%H:%M:%S'))

        precos = []
        for i in range(len(fechamentos)):
            precos.append(fechamentos[i][2])

        fig, ax = plt.subplots()
		
        plt.plot(precos, 'C0')
        plt.plot(medias_curto_prazo, 'C1')
        plt.plot(medias_longo_prazo, 'C2')

        plt.xticks(locations, tempos)
        fig.autofmt_xdate()
        
        plt.xlabel('Tempo')
        plt.ylabel('Dinheiro')
        plt.legend(['Fechamento', 'Média de curto prazo', 'Média de longo prazo'])
        plt.show()

if __name__ == "__main__":
        while True:
                processamento()
                time.sleep(3600 * 6)
