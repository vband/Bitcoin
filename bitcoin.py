import urllib.request
import time
import telepot
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

#---------------------------------------------------
# Função que retorna a média aritmética de uma lista
#---------------------------------------------------
def media_aritmetica(lista):
        n = len(lista)
        m = 0
        for i in range(n):
                m = m + lista[i]
        m = m / n
        return m

#-------------------------------------------------------------------------------------------
# Processamento principal
#
# Parâmetros:
# 1. Lista com a cotação de Bitcoin
# 2. Valor numérico do Threshold (usado para antecipar o delay experimentado nas transações)
#-------------------------------------------------------------------------------------------
def processamento(fechamentos, threshold):

        # Parâmetros
        n_dias_curto_prazo = 12
        n_dias_longo_prazo = 26
        n_dias_macd = 9
		
        #---------------------
	# Tratamento dos dados
	#---------------------

        fechamentos = str(fechamentos)

        fechamentos = fechamentos[4:-3]

        fechamentos = fechamentos.split("],[")

        for i in range(len(fechamentos)):
            fechamentos[i] = fechamentos[i].split(",")
            for j in range(len(fechamentos[i])):
                fechamentos[i][j] = float(fechamentos[i][j])
		
        # Invertendo a lista para percorrê-la do fechamento mais antigo para o mais atual
		
        fechamentos.reverse()

        #-----------------------------------------
        # Cálculo das primeiras médias aritméticas
        #-----------------------------------------

        primeira_media_curto_prazo = 0

        for i in range(n_dias_curto_prazo):
                primeira_media_curto_prazo = primeira_media_curto_prazo + fechamentos[i][2]
        primeira_media_curto_prazo = primeira_media_curto_prazo / n_dias_curto_prazo

        primeira_media_longo_prazo = 0

        for i in range(n_dias_longo_prazo):
                primeira_media_longo_prazo = primeira_media_longo_prazo + fechamentos[i][2]
        primeira_media_longo_prazo = primeira_media_longo_prazo / n_dias_longo_prazo

        #---------------------------------
        # Cálculo das médias (curto prazo)
        #---------------------------------

        medias_curto_prazo = []
        multiplicador_curto_prazo = (2 / (n_dias_curto_prazo + 1) )

        for i in range(len(fechamentos)):
                # Preenche os primeiros valores com None
                if i < n_dias_curto_prazo-1:
                        medias_curto_prazo.append(None)
                # Inicializa a primeira média com a média aritmética
                elif i == n_dias_curto_prazo-1:
                        medias_curto_prazo.append(primeira_media_curto_prazo)
                # Calcula a média exponencial
                else:
                        medias_curto_prazo.append((fechamentos[i][2] - medias_curto_prazo[i-1]) * multiplicador_curto_prazo + medias_curto_prazo[i-1])
                        
        #---------------------------------
        # Cálculo das médias (longo prazo)
        #---------------------------------

        medias_longo_prazo = []
        multiplicador_longo_prazo = (2 / (n_dias_longo_prazo + 1) )

        for i in range(len(fechamentos)):
                # Preenche os primeiros valores com None
                if i < n_dias_longo_prazo-1:
                        medias_longo_prazo.append(None)
                # Inicializa a primeira média com a média aritmética
                elif i == n_dias_longo_prazo-1:
                        medias_longo_prazo.append(primeira_media_longo_prazo)
                # Calcula a média exponencial
                else:
                        medias_longo_prazo.append((fechamentos[i][2] - medias_longo_prazo[i-1]) * multiplicador_longo_prazo + medias_longo_prazo[i-1])

        #----------------
        # Cálculo do MACD
        #----------------

        macd = []

        for i in range(len(fechamentos)):
                if medias_longo_prazo[i] != None:
                        macd.append(medias_curto_prazo[i] - medias_longo_prazo[i])
                else:
                        macd.append(None)

        #------------------
        # Cálculo do signal
        #------------------

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

        #----------------------
        # Cálculo do histograma
        #----------------------

        histograma = []

        for i in range(len(fechamentos)):
                if signal[i] != None and macd[i] != None:
                        histograma.append(macd[i] - signal[i])
                else:
                        histograma.append(None)

        precos = []
        for i in range(len(fechamentos)):
            precos.append(fechamentos[i][2])

        #--------------------------------------------------------------------
        # Cálculo do vetor de compra (true caso compra, false caso contrário)
        # Cálculo do vetor de venda (true caso venda, false caso contrário)
        #--------------------------------------------------------------------

        compra = []
        venda = []
        preco_ultima_op = precos[0]

        for i in range(len(fechamentos)):
                # Inicialização
                if histograma[i] == None or histograma[i-1] == None or signal[i] == None:
                        compra.append(False)
                        venda.append(False)
                # Condições
                else:
                        # Compra
##                        if histograma[i] > -0.5 and histograma[i] < 0 and histograma[i-1] < histograma[i] * 2:
##                        if histograma[i] > 0 and histograma[i-1] < 0:
##                        if (macd[i] > 0 and macd[i-1] < 0) and (precos[i] < preco_ultima_op):
                        if (histograma[i] > -threshold and histograma[i-1] < -threshold) and (precos[i] < preco_ultima_op):
                                compra.append(True)
                                preco_ultima_op = precos[i]
                        else:
                                compra.append(False)
                        # Venda
##                        if histograma[i] < 0.5 and histograma[i] > 0 and histograma[i-1] > histograma[i] * 2:
##                        if histograma[i] < 0 and histograma[i-1] > 0:
##                        if (macd[i] < 0 and macd[i-1] > 0) and (precos[i] > preco_ultima_op):
                        if (histograma[i] < threshold and histograma[i-1] > threshold) and (precos[i] > preco_ultima_op):
                                venda.append(True)
                                preco_ultima_op = precos[i]
                        else:
                                venda.append(False)

##        print("Venda: %s" %(venda[-1]))
##        print("Compra: %s" %(compra[-1]))
		
        #-----------------------------
        # Envia mensagem pelo Telegram
        #-----------------------------
		
        bot = telepot.Bot('703200255:AAF5ym-tGJSOIaTDyu5XKi605-Uq6GWtWow')
        #bot.sendMessage(-260640827, "Venda: %s" %(venda[-1])) # Grupo de Análise de Risco
        #bot.sendMessage(-260640827, "Compra: %s" %(compra[-1]))
		
        bot.sendMessage(149282401, "Venda: %s" %(venda[-1])) # Meu privado
        bot.sendMessage(149282401, "Compra: %s" %(compra[-1]))
		
        #---------------------------
        # Desenha o gráfico na tela
        #---------------------------
		
        # Constrói o eixo X como sendo as datas e os horários
        
##        tempos = []
##        locations = [0, 250, 500, 750, 999]
##        for i in range(len(fechamentos)):
##                if i in locations:
##                        ts = int(fechamentos[i][0])
##                        ts /= 1000
##                        tempos.append(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
##                        #tempos.append(datetime.utcfromtimestamp(ts).strftime('%H:%M:%S'))

##        valores_i = range(1000)

        fig, ax = plt.subplots()

##        plt.xticks(locations, tempos)
##        fig.autofmt_xdate()
        
        plt.xlabel('Tempo')
        plt.ylabel('Preço ($)')
        plt.legend(['Fechamento', 'Média de curto prazo', 'Média de longo prazo'])
        
        #----------
        # Simulação
        #----------
        
        # Sub-intervalo da cotação do bitcoin a ser considerado. Deve ser no mínimo 0 e no máximo 999
        iteracao_ini = 0
        iteracao_fim = 999

        # Parâmetros
        carteira_dolar = 10000                                    # Valor inicial da carteira de dólar a ser simulada
        carteira_bitcoin = carteira_dolar / precos[iteracao_ini]  # Valor inicial da carteira de bitcoin a ser simulada
        porcentagem_venda = 0.5                                   # Porcentagem da carteira que será usada nas vendas
        porcentagem_compra = 0.5                                  # Porcentagem da carteira que será usada nas compras

        # Variáveis usadas para comparar o dinheiro inicial com o dinheiro final
        carteira_dolar_ini = carteira_dolar
        carteira_bit_ini = carteira_bitcoin
        dinheiro_tot_ini = carteira_dolar + carteira_bitcoin * precos[iteracao_ini]

        # Contadores
        cont_venda = 0
        cont_compra = 0

        for i in range(iteracao_ini, iteracao_fim + 1):
                # Venda
                if venda[i] == True and compra[i] == False:
                        carteira_dolar += carteira_bitcoin * porcentagem_venda * precos[i]
                        carteira_bitcoin -= carteira_bitcoin * porcentagem_venda
                        cont_venda += 1
                        if histograma[i-2] == None:
                                print("%d. Vendeu. Preço: %.2f. Histograma[-1]: %.5f. Histograma: %.5f. Carteira Dólar: %.2f. Carteira Bitcoin: %.2f" %(i, precos[i], histograma[i-1], histograma[i], carteira_dolar, carteira_bitcoin))
                        else:
                                print("%d. Vendeu. Preço: %.2f. Histograma[-2]: %.5f. Histograma[-1]: %.5f. Histograma: %.5f. Carteira Dólar: %.2f. Carteira Bitcoin: %.2f" %(i, precos[i], histograma[i-2], histograma[i-1], histograma[i], carteira_dolar, carteira_bitcoin))
                # Compra
                elif compra[i] == True and venda[i] == False:
                        carteira_bitcoin += (carteira_dolar * porcentagem_compra) / precos[i]
                        carteira_dolar -= carteira_dolar * porcentagem_compra
                        cont_compra += 1
                        if histograma[i-2] == None:
                                print("%d. Comprou. Preço: %.2f. Histograma[-1]: %.5f. Histograma: %.5f. Carteira Dólar: %.2f. Carteira Bitcoin: %.2f" %(i, precos[i], histograma[i-1], histograma[i], carteira_dolar, carteira_bitcoin))
                        else:
                                print("%d. Comprou. Preço: %.2f. Histograma[-2]: %.5f. Histograma[-1]: %.5f. Histograma: %.5f. Carteira Dólar: %.2f. Carteira Bitcoin: %.2f" %(i, precos[i], histograma[i-2], histograma[i-1], histograma[i], carteira_dolar, carteira_bitcoin))
                # Erro - não é possível vender e comprar ao mesmo tempo!
                elif compra[i] == True and venda[i] == True:
                        print("Erro: fórmula errada!")

        # Variáveis usadas para comparar o dinheiro inicial com o dinheiro final
        carteira_dolar_fim = carteira_dolar
        carteira_bit_fim = carteira_bitcoin
        dinheiro_tot_fim = carteira_dolar + carteira_bitcoin * precos[iteracao_fim]

        # Apresentação dos resultados
        print("")
        print("Foram realizadas %d vendas e %d compras." %(cont_venda, cont_compra))
        print("Carteira Dólar Inicial: %.2f" %(carteira_dolar_ini))
        print("Carteira Dólar Final: %.2f" %(carteira_dolar_fim))
        print("Carteira Bitcoin Inicial: %.2f" %(carteira_bit_ini))
        print("Carteira Bitcoin Final: %.2f" %(carteira_bit_fim))
        print("Dinheiro Total Inicial: %.2f" %(dinheiro_tot_ini))
        print("Dinheiro Total Final: %.2f" %(dinheiro_tot_fim))

        # -----------------------------------------
        # Desenha os pontos de interesse no gráfico
        #------------------------------------------

        # Determina a localização dos pontos de venda
        locations_venda = []
        for i in range(len(venda)):
                if venda[i] == True:
                        plt.annotate('Venda', xy=(i, precos[i]), xytext=(i+2, precos[i]), arrowprops=dict(facecolor='green', shrink=0.05))
                        locations_venda.append(i)

        # Determina a localização dos pontos de compra
        locations_compra = []
        for i in range(len(compra)):
                if compra[i] == True:
                        plt.annotate('Compra', xy=(i, precos[i]), xytext=(i+2, precos[i]), arrowprops=dict(facecolor='red', shrink=0.05))
                        locations_compra.append(i)

        locations_all = list(set().union(locations_compra, locations_venda))
        locations_all.sort()

        # Mostra o gráfico na tela
        plt.plot(precos, color='b', marker='o', markevery=locations_all)
        plt.plot(medias_curto_prazo, color='g')
        plt.plot(medias_longo_prazo, color='r')
        plt.show()

        # Retorna o dinheiro total final obtido pela simulação
        return dinheiro_tot_fim
                
#------------
# Função Main
#------------
if __name__ == "__main__":

        # Obtenção dos dados
        fechamentos = urllib.request.urlopen("https://api.bitfinex.com/v2/candles/trade:6h:tBTCUSD/hist?limit=1000").read()

        # Opção 1: Loop principal
        while True:
                processamento(fechamentos, 1) # Parâmetros: 1. Lista da cotação do Bitcoin; 2. Valor numérico do Threshold
                time.sleep(3600 * 6)

        # Opção 2: Loop para determinar o valor ideal do Threshold para o corrente momento
##        threshold_ini = 0
##        threshold_fim = 99
##        passo = 0.1
##        dinheiro_tot_ideal = -1
##        threshold_ideal = None

##        threshold = threshold_ini
##        while threshold <= threshold_fim:
##                dinheiro = processamento(fechamentos, threshold)
##                print("Dinheiro: %.2f. Threshold: %.1f" %(dinheiro, threshold))
##                if dinheiro > dinheiro_tot_ideal:
##                        dinheiro_tot_ideal = dinheiro
##                        threshold_ideal = threshold
##                threshold += passo
##        print("Threshold ideal: %.1f. Dinheiro_tot_ideal: %.2f" %(threshold_ideal, dinheiro_tot_ideal))
