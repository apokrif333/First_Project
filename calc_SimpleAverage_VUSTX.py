import pandas as pd
import numpy as np
import os
from datetime import datetime

movingValueL=[25,50,75,100,125,150,175,200,250,300]

def DateCheck(x):
        try:
            x["Date"] = pd.to_datetime(x["Date"], format="%Y-%m-%d")
        except:
            x["Date"] = pd.to_datetime(x["Date"], format="%m/%d/%Y")

tickerData = pd.read_csv("datafeed/VUSTX.csv")
DateCheck(tickerData)

#Строим мувинги для VUSTX
for m in movingValueL:
    movingAveragesL = []
    for i in range(0,len(tickerData)):
        #Если i позволяет посчитать мувинг, так как достаточно даты
        if i>=m-1:
            #Сформируй таблицу для расчёта средней
            curTickerData = tickerData.head(i+1)
            curTickerData = curTickerData.tail(m)
            movingAverage = np.average(curTickerData["Close"].tolist()) #Создай массив со средней
            movingAveragesL.append(movingAverage)
        #Если данных не хватает, укажи 0
        else:
            movingAverage = 0
            movingAveragesL.append(movingAverage)
    #В tickerData добавить столбцы со всеми полученными МА
    tickerData["MA_"+str(m)] = movingAveragesL
    print(tickerData.tail(5))
    #Полученную tickerData записать в файл
    tickerData.to_csv("exportTables/VUSTX"+str(m)+".csv")