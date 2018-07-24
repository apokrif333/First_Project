import pandas as pd
import numpy as np
import os
from datetime import datetime

#Основные переменные
nMomentumValue = 12
numTickersMaxValue = 4
Quarters = [3,6,9,12]
movingValueL=[25,50,75,100,125,150,175,200,250,300] #,100,125,150,175,200,250,300

# Определяем стартовую дату из разных файлов
filesList=os.listdir("datafeed") #Считываем папку

dateList=[]
for file in filesList:
    curFileTable=pd.read_csv("datafeed/"+str(file)) #Считываем файлы по порядку и корректируем формат даты
    try:
        curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%Y-%m-%d")
    except:
        curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%m/%d/%Y")
    dateList.append(curFileTable["Date"].iloc[0])

startDate=max(dateList) #Определяем максимальную дату
startDateIndex=curFileTable["Date"].tolist().index(startDate) #Находим номер строки startDate
startDate=curFileTable["Date"].iloc[startDateIndex+movingValueL[-1]] #Прибалвяем к номеру строки самый последний период МА

#Создаём файл со всеми тикерами и начинающийся с нужной даты
lenTables=[]
for file in filesList:
    curFileTable=pd.read_csv("datafeed/"+str(file))
    try:
        curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%Y-%m-%d")
    except:
        curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%m/%d/%Y")
    curFileTableStartDate=curFileTable.loc[(curFileTable["Date"]>=startDate)]
    lenTables.append(len(curFileTableStartDate))

#Записываем в lastDateinMonth дату последненго дня месяца
lastDateinMonth=[]
for i in range(0,len(curFileTableStartDate)):
    curDate = curFileTableStartDate["Date"].iloc[i]
    if i<len(curFileTableStartDate)-1:
        nextDate=curFileTableStartDate["Date"].iloc[i+1]
        curMonth=curDate.month
        nexMonth=nextDate.month
        if curMonth!=nexMonth:
            lastDateinMonth.append(curDate)
    else:
        lastDateinMonth.append(curDate)

#Используя lastDateinMonth создаём файл только с тремя столбцами со всеми тикерами
tickerL=[]
datesL=[]
closesL=[]
for file in filesList:
    ticker=file.replace(".csv","") #Берём тикер из имени файла
    curFileTable=pd.read_csv("datafeed/"+str(file))
    try:
        curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%Y-%m-%d")
    except:
        curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%m/%d/%Y")
    for date in lastDateinMonth:
        tickerL.append(ticker)
        datesL.append(date)
        curDateFileTable=curFileTable.loc[curFileTable["Date"]==date]
        closesL.append(curDateFileTable["Close"].iloc[0])

#Создаём таблицу из полученных ранее 3-ёх массивов
lastMonthCloses=pd.DataFrame({"Ticker":tickerL,
                              "Date":datesL,
                              "Close":closesL})

#Полученную таблицу выше, заносим в файл
lastMonthCloses.to_csv("lastMonthCloses.csv")

#Из созданного lastMonthCloses высчитываем Gain, создаём 12 моментумов и 12 вариантов лучших тикеров за месяц
lastMonthClosesBase = pd.read_csv("lastMonthCloses.csv")
lastDateinMonth = lastMonthClosesBase["Date"].unique()
tickerL = lastMonthClosesBase["Ticker"].unique()

for nMomentum in range(1,nMomentumValue+1):
    gainL = []
    for ticker in tickerL:
        lastMonthCloses = lastMonthClosesBase.loc[lastMonthClosesBase["Ticker"] == ticker] #Создаём таблицу по определённому тикеру
        for i in range(0, len(lastMonthCloses)):
            if i < nMomentum:
                gainL.append(0)
            else:index
                gainL.append((lastMonthCloses["Close"].iloc[i] - lastMonthCloses["Close"].iloc[i - nMomentum]) / lastMonthCloses["Close"].iloc[i - nMomentum]) #Рассчитываем Gain
    lastMonthClosesBase["Gain"] = gainL
    lastMonthClosesBase.to_csv("exportTables/lastMonthClosesGain_" + str(nMomentum) + ".csv") #Создаём файл с добавленным Gain и количество файлов зависит от nMomentum

    #Вводим количество тикеров
    for numTickers in range(1,numTickersMaxValue+1):

        #Формируем массив рискон тикеров и добавляем тикер рискОфф и тикер кеш
        riskOnL=["VTSMX","VEURX","VPACX","VEIEX"]
        riskOff="VUSTX"
        riskOffOff="VFISX"

        #Формируем таблицу лучших перформеров месяца среди рискон активов. Когда нет активов которые показали положительный прирост добавляем в массив риск-офф актив
        bestTickersL = []
        bestTickersDatesL = []
        for date in lastDateinMonth:
            try:
                formatDate = pd.to_datetime(date, format="%Y-%m-%d") #Снова корректируем формат даты, так как из csv файла она извлекается в виде текста
            except:
                formatDate = pd.to_datetime(date, format="%m/%d/%Y")
            curMonth=formatDate.month
            curDateLastMonthCloses=lastMonthClosesBase.loc[(lastMonthClosesBase["Date"]==date)&(lastMonthClosesBase["Ticker"].isin(riskOnL))] #Записываем в массив все данные по риск-он тикерам на текущую дату
            curDateLastMonthCloses=curDateLastMonthCloses.sort_values("Gain",ascending=False) #Сортируем полученный ранее массив по Gain
            curDateLastMonthCloses=curDateLastMonthCloses.head(numTickers) #Берём нужное количество лидеров по Gain, исходя из numTickers
            #В curDateLastMonthCloses теперь такое количество, строк, сколько в numTickers
            for l in range(0,len(curDateLastMonthCloses)):
                if curMonth in Quarters:
                    if curDateLastMonthCloses["Gain"].iloc[l]>0: #Проверяем поcтрочно каждый Gain, если сейчас конец квартала
                        bestTickersL.append(curDateLastMonthCloses["Ticker"].iloc[l])
                        bestTickersDatesL.append(curDateLastMonthCloses["Date"].iloc[l])
                    else:
                        bestTickersL.append(riskOff) #Если в какой-либо строке Gain отрицательный, заменяем его на riskOff
                        bestTickersDatesL.append(curDateLastMonthCloses["Date"].iloc[l])
                else:
                    if len(bestTickersL)<numTickers:
                        bestTickersL.append(riskOffOff) #В самом начале, пока bestTickersL пуст, мы садимся в кэш
                        bestTickersDatesL.append(curDateLastMonthCloses["Date"].iloc[l])
                    else:
                        bestTickersL.append(bestTickersL[-1*numTickers]) #Берём предыдущие строчки исходя из numTickers, если сейчас не конец квартала
                        bestTickersDatesL.append(curDateLastMonthCloses["Date"].iloc[l])

            positionL = []
            for p in range(0,len(bestTickersDatesL)):
                if p == 0:
                    positionL.append(1)
                else:
                    if bestTickersDatesL[p] == bestTickersDatesL[p-1]:
                        positionL.append(positionL[-1]+1)
                    else:
                        positionL.append(1)

        bestMonthPerf=pd.DataFrame({"Date":bestTickersDatesL,
                                    "Ticker":bestTickersL,
                                   "Position":positionL})
        print(bestMonthPerf)
        # #Выводим таблицу лучшего перформера в файл
        #bestMonthPerf.to_csv("exportTables/bestMonthPerf_"+str(nMomentum)+"_"+str(numTickers)+".csv")

        bestMonthPerfClosesL=[]
        bestMonthPerfWithCloses=pd.DataFrame({})
        #Считываем файл с днями недели
        allDates = pd.read_csv("lastWeekDays.csv")
        #Приводим текстовый формат, в формат даты
        try:
            allDates["Date"] = pd.to_datetime(allDates["Date"], format="%Y-%m-%d")
        except:
            allDates["Date"] = pd.to_datetime(allDates["Date"], format="%m/%d/%Y")
        #Считываем предыдущую таблицу с лучшими тикерами за месяц
        for t in range(0,len(bestMonthPerf)):
            curTicker = bestMonthPerf["Ticker"].iloc[t]  # Текущий тикер
            curPosition = bestMonthPerf["Position"].iloc[t]
            curDate = bestMonthPerf["Date"].iloc[t]  # Текущий месяц
            #Текстовые даты из bestMonthPerf по текущему тикеру приводим в формат даты
            curTickerTable = pd.read_csv("datafeed/" + str(curTicker) + ".csv")
            try:
                curTickerTable["Date"] = pd.to_datetime(curTickerTable["Date"], format="%Y-%m-%d")
            except:
                curTickerTable["Date"] = pd.to_datetime(curTickerTable["Date"], format="%m/%d/%Y")

            if t+numTickers<len(bestMonthPerf):
                nextDate=bestMonthPerf["Date"].iloc[t+numTickers] #Следующий месяц
                betweenDay=allDates.loc[(allDates["Date"]>=curDate)&(allDates["Date"]<nextDate)]  #Задаём массив с датами между концом текущего месяца и концом следующего
                dateColumn=betweenDay["Date"].tolist() #Извлекаем дату из предыдущего массива
                lenDateColumn=len(dateColumn) #Извлекаем длинну
                tickerColumn=[curTicker]*lenDateColumn #Делаем так, чтобы строчки с текущум тикером продублировались столько раз, сколько даты есть в текущем массиве даты
                positionColumn = [curPosition]*lenDateColumn

                curTickerTableBetweenDays=curTickerTable.loc[(curTickerTable["Date"]>=curDate)&(curTickerTable["Date"]<nextDate)]
                curCloseBD=curTickerTableBetweenDays["Close"].tolist() #Извлекаем клоузы между концом текущего месяца и концом следующего

                #Создаём таблицу с тикером и датами
                curTable=pd.DataFrame({"Date":dateColumn,
                                       "Ticker":tickerColumn,
                                       "Close":curCloseBD,
                                       "Position":positionColumn})
                bestMonthPerfWithCloses=pd.concat([bestMonthPerfWithCloses,curTable],ignore_index=True) #Сшиваем предыдущие таблицы с текущей при каждой итерации
            #Если дошли до последнего месяца, то просто вставить текущий тикер, дату и клоуз
            else:
                curCloseTable=curTickerTable.loc[curTickerTable["Date"]==curDate]
                curClose = curCloseTable["Close"].iloc[0]
                curTable = pd.DataFrame({"Date":[curDate],
                                         "Ticker":[curTicker],
                                         "Close":[curClose],
                                         "Position":[curPosition]})
                bestMonthPerfWithCloses = pd.concat([bestMonthPerfWithCloses, curTable], ignore_index=True)

        #Перебираем МА
        for MA in movingValueL:
            movingAverageL = []
            for m in range(0, len(bestMonthPerfWithCloses)):
                curTicker = bestMonthPerfWithCloses["Ticker"].iloc[m]
                curDate = bestMonthPerfWithCloses["Date"].iloc[m]
                #Считываем тикеры по порядку
                curTickerTable = pd.read_csv("datafeed/" + str(curTicker) + ".csv")
                try:
                    curTickerTable["Date"] = pd.to_datetime(curTickerTable["Date"], format="%Y-%m-%d")
                except:
                    curTickerTable["Date"] = pd.to_datetime(curTickerTable["Date"], format="%m/%d/%Y")

                curTickerTableMA = curTickerTable.loc[curTickerTable["Date"] <= curDate] #Построить все даты, до даты текущией
                curTickerTableMA = curTickerTableMA.tail(MA) #Взять такой массив элементов, который соотвествует текущей МА
                movingAverage = np.average(curTickerTableMA["Close"].tolist()) #Считаем МА
                movingAverageL.append(movingAverage) #Создаём массив с МА
            bestMonthPerfWithCloses["MA_" + str(MA)] = movingAverageL  #Добавляем столбцы с МА

        # ------выводим таблицу по дням c лучшими перформерами текущего квартала(тайминга) в файл
        bestMonthPerfWithCloses.to_csv(
            "exportTables/bestMonthPerfWithCloses_" + str(nMomentum) + "_" + str(numTickers) + ".csv")