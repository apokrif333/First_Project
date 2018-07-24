import pandas as pd
import numpy as np
import os
from datetime import datetime

#Основные переменные
nMomentumValue = 12
numTickersMaxValue = 4
Quarters = [3, 6, 9, 12]
movingValueL = [25, 50, 75, 100, 125, 150, 175, 200, 250, 300] #,100,125,150,175,200,250,300


def DateCheck(x):
    try:
        x["Date"] = pd.to_datetime(x["Date"], format="%Y-%m-%d")
    except:
        x["Date"] = pd.to_datetime(x["Date"], format="%m/%d/%Y")

filesList = os.listdir("exportTables") #Считываем папку
lastWeekDays = pd.read_csv("lastWeekDays.csv") #Считываем последнии дни недели
DateCheck(lastWeekDays) #Корректируем по дате
lastWeekDays = lastWeekDays.loc[lastWeekDays["LastWeekDay"] == 1] #Записываем строчки с последними днями
lastWeekDays = lastWeekDays["Date"].tolist() #Даты с последними днями в лист

curFileTableStartDate = pd.read_csv("exportTables/bestMonthPerfWithCloses_1_1.csv") # Считываем файл с построенными МА
DateCheck(curFileTableStartDate)
lastDateinMonth = []
for i in range(0, len(curFileTableStartDate)):
    curDate = curFileTableStartDate["Date"].iloc[i] #Создаём лист со всеми датами
    if i < len(curFileTableStartDate)-1:
        #Записываем последний день в квартале в lastDateinMonth
        nextDate = curFileTableStartDate["Date"].iloc[i+1]
        curMonth = curDate.month
        nextMonth = nextDate.month
        if curMonth != nextMonth and curMonth in Quarters:
            lastDateinMonth.append(curDate)
    #Записывем конец файла, как последний день квартала
    else:
        lastDateinMonth.append(curDate)

vustxMA = pd.read_csv("exportTables/VUSTX_MA.csv")
DateCheck(vustxMA)

for m in range(1, nMomentumValue+1): #Перебор моментумов количества тикеров
    for n in range(1, numTickersMaxValue+1):
        curPortTable = pd.read_csv("exportTables/bestMonthPerfWithCloses_"+str(m)+"_"+str(n)+".csv") #Таблица с МА для тикеров на текущий месяц и с датами на каждый день
        DateCheck(curPortTable)

        #Перебор мувингов
        for ma in movingValueL:
            exportTable = pd.DataFrame({})

            #Перебирай то количество w, сколько раз заканчивались кварталы
            for w in range(1, len(lastDateinMonth)):
                startDate = lastDateinMonth[w-1] #Стартовая дата - предыдущий квартал
                endDate = lastDateinMonth[w] #Конечная дата - текущий квартал
                curPeriodPortTable = curPortTable.loc[(curPortTable["Date"] >= startDate) & (curPortTable["Date"] < endDate)] #Создать таблицу из дат выше
                curTickers = curPeriodPortTable["Position"].unique() #Считать все уникальные тикеры из таблицы выше
                curTickers = list(set(curTickers)) #Массив с тикерами заведи в лист, чтобы у каждого тикера был свой индекс

                #Для каждого тикера из текущей таблицы
                for position in curTickers:
                    curTickerPeriodPortTable = curPeriodPortTable.loc[curPeriodPortTable["Position"] == position]
                    ticker = curTickerPeriodPortTable["Ticker"].iloc[0]
                    curTickerCloses = pd.read_csv("datafeed/"+str(ticker)+".csv") #Обратиться к базовому файлу и считать все цены
                    DateCheck(curTickerCloses)

                    #Задать массивы для будущей таблицы
                    dateL = []
                    tickerL = []
                    closesL = []
                    positionL = []

                    #Для каждого тикера в текущем квартале
                    for i in range(0, len(curTickerPeriodPortTable)):
                        curTableClose = curTickerPeriodPortTable["Close"].iloc[i]
                        curTableMA = curTickerPeriodPortTable["MA_"+str(ma)].iloc[i]
                        curDate = curTickerPeriodPortTable["Date"].iloc[i] #Даты по текущему тикеру
                        curVUSTXClose = vustxMA.loc[vustxMA["Date"] == curDate]["Close"].iloc[0]
                        curTickerClose = curTickerCloses.loc[curTickerCloses["Date"] == curDate]["Close"].iloc[0]
                        tickerIndex = position

                        #Если конец прошлого квартала...
                        if i == 0:
                            if curTableClose < curTableMA:
                                tickerL.append("VUSTX") #... сядь в VUSTX, если текущий тикер ниже МА
                                dateL.append(curDate)
                                closesL.append(curVUSTXClose) #Присвой цену VUSTX на текущую дату
                                positionL.append(tickerIndex) #Укажи, какой индекс у исследуемого тикера из списка тикеров

                            else:
                                tickerL.append(ticker) #...возьми тот тикер, который должен взять, согласно моментуму
                                dateL.append(curDate)
                                closesL.append(curTickerClose) #Присвой цену текущему тикеру на текущую дату
                                positionL.append(tickerIndex)

                        #Если это не конец прошлого квартала...
                        else:
                            #Если текущая дата конец недели
                            if curDate in lastWeekDays:
                                if curTableClose < curTableMA and tickerL[-1] != "VUSTX":
                                    tickerL.append(tickerL[-1]) #... если тикер ниже МА, запииши его
                                    dateL.append(curDate)
                                    positionL.append(tickerIndex)
                                    closesL.append(curTickerClose)

                                    # ... после того, как записал тикер который ниже МА, добавь VUSTX и его данные
                                    tickerL.append("VUSTX")
                                    dateL.append(curDate)
                                    closesL.append(curVUSTXClose)
                                    positionL.append(tickerIndex)

                                #Если до этого сидели в VUSTX
                                elif curTableClose < curTableMA:
                                    tickerL.append("VUSTX")
                                    dateL.append(curDate)
                                    closesL.append(curVUSTXClose)
                                    positionL.append(tickerIndex)

                                #Если сейчас тикер выше МА
                                else:
                                    if tickerL[-1] == "VUSTX":
                                        #Если до этого сидели в VUSTX, внести данные по нему и потом по тикеру в который возвращаемся
                                        tickerL.append("VUSTX")
                                        dateL.append(curDate)
                                        closesL.append(curVUSTXClose)
                                        positionL.append(tickerIndex)

                                        tickerL.append(ticker)
                                        dateL.append(curDate)
                                        closesL.append(curTickerClose)
                                        positionL.append(tickerIndex)
                                    else:
                                        #Если до этого мы не были в VUSTX продолжить вносить данные по текущему тикеру
                                        tickerL.append(tickerL[-1])
                                        dateL.append(curDate)
                                        closesL.append(curTickerClose)
                                        positionL.append(tickerIndex)

                            #Если текущая дата не конец недели
                            else:
                                tickerL.append(tickerL[-1])
                                dateL.append(curDate)
                                positionL.append(tickerIndex)
                                #Если мы сидим не в текущем тикере, а в VUSTX, впиши цены VUSTX
                                if tickerL[-1] == "VUSTX":
                                    closesL.append(curVUSTXClose)
                                else:
                                    closesL.append(curTickerClose)

                        #Если это последний день квартала, запиши сюда данные об этом дне
                        if i == len(curTickerPeriodPortTable)-1:
                            dateL.append(endDate)
                            tickerL.append(tickerL[-1])
                            positionL.append(tickerIndex)
                            if tickerL[-1] == "VUSTX":
                                closesL.append(vustxMA.loc[vustxMA["Date"] == endDate]["Close"].iloc[0])
                            else:
                                closesL.append(curTickerCloses.loc[curTickerCloses["Date"] == endDate]["Close"].iloc[0])

                    #Создать табилцу по текущему, обработанному тикеру
                    curExportTable = pd.DataFrame({"Date": dateL,
                                                 "Ticker": tickerL,
                                                 "Close": closesL,
                                                 "Position": positionL})
                    #Присоединить свежесозданную таблицу, к предыдущей созданной таблице, если она была
                    exportTable = pd.concat([exportTable, curExportTable], ignore_index=True)

            #Когда переберёшь все кварталы за историю за текущие моментум, количество тикеров и МА - выгрузи накопленные данные в файл
            exportTable.to_csv("exportTables/finalPort_"+str(m)+"_"+str(n)+"_"+str(ma)+".csv")
            print("finalPort_"+str(m)+"_"+str(n)+"_"+str(ma)+".csv")