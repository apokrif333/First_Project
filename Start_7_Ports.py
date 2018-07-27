import pandas as pd
import numpy as np
import os
import datetime as dt
import statistics as stat
import math
from dateutil.relativedelta import relativedelta
from datetime import datetime

nMomentumValue = 12
numTickersMaxValue = 4
Quarters = [3, 6, 9, 12]
movingValueL = [25, 50, 75, 100, 125, 150, 175, 200, 250, 300]
StartCapital = 10000


def date_check(x):
    try:
        x["Date"] = pd.to_datetime(x["Date"], format="%Y-%m-%d")
    except:
        x["Date"] = pd.to_datetime(x["Date"], format="%m/%d/%Y")


# Переменые для записи в файл
File = []
CAGR = []
StDev = []
DrawDown = []
Sharpe = []
MaR = []
SM = []

# Перебор файлов
for m in range(1, nMomentumValue+1):
    for n in range(1, numTickersMaxValue+1):
        for ma in movingValueL:
            # Пемеренные для текущего модуля
            Cng = []
            Down = []

            NewFile = pd.read_csv('Temp/final_capital Mom_'+str(m)+' T_'+str(n)+' SMA_'+str(ma)+".csv")
            print('Mom_' + str(m) + ' T_' + str(n) + ' SMA_' + str(ma))
            date_check(NewFile)

            # Считаем девиацию и просадки
            High = NewFile['Capital'][0]
            for i in range(1, len(NewFile["Capital"])):
                Cng.append((NewFile["Capital"][i]-NewFile["Capital"][i-1]) / NewFile["Capital"][i-1] * 100)

                if NewFile['Capital'][i] > High:
                    High = NewFile['Capital'][i]
                Down.append(NewFile['Capital'][i] / High - 1)

            # Создаём данные для таблицы
            File.append('Mom_' + str(m) + ' T_' + str(n) + ' SMA_' + str(ma))
            CAGR.append(((NewFile["Capital"].iloc[-1] / NewFile["Capital"].iloc[0]) **
                         (1 / (NewFile["Date"].iloc[-1].year - NewFile["Date"].iloc[0].year)) - 1) * 100)
            StDev.append(stat.stdev(Cng) * math.sqrt(252))
            DrawDown.append(min(Down))
            Sharpe.append(CAGR[-1] / StDev[-1])
            MaR.append(abs(CAGR[-1] / (DrawDown[-1] * 100)))
            SM.append(Sharpe[-1] * MaR[- 1])

exportTable = pd.DataFrame({"File": File,
                            "CAGR": CAGR,
                            "StDev": StDev,
                            "DrawDown": DrawDown,
                            "Sharpe": Sharpe,
                            "MaR": MaR,
                            "SM": SM},
                           columns=["File", "CAGR", "StDev", "DrawDown", "Sharpe", "MaR", "SM"]
                           )

exportTable.to_csv("Temp/AllPort_Data.csv")