import pandas as pd
import numpy as np
import os
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


# Перебор файлов
for m in range(1, nMomentumValue+1):
    for n in range(1, numTickersMaxValue+1):
        for ma in movingValueL:

            # Создаём новую таблицу для работы. Из старой таблицы считываем, уникальные даты, тикеры и позиции
            NewFile = pd.DataFrame({})

            BaseFile = pd.read_csv("Temp/finalPort_" + str(m) + "_" + str(n) + "_"+str(ma)+".csv")
            date_check(BaseFile)
            print("finalPort_" + str(m) + "_" + str(n) + "_" + str(ma) + ".csv")

            StartDate = BaseFile["Date"].iloc[0]
            Tickers = BaseFile["Ticker"].unique()
            Position = BaseFile["Position"].unique()

            # Вшиваем уникальные даты
            NewFile["Date"] = BaseFile["Date"].unique()

            for t in Tickers:
                # Вшиваем цены для каждого тикера
                TempTable = pd.read_csv("datafeed/"+str(t)+".csv")
                date_check(TempTable)

                TempTable = TempTable["Close"].loc[(TempTable["Date"] >= StartDate)&(TempTable["Date"] < "2018/04/30")]
                TempTable.index = pd.RangeIndex(len(NewFile.index))
                NewFile[str(t)] = TempTable

                # Вшиваем дивы для каждого тикера
                TempTable = pd.read_csv("datafeed/" + str(t) + "_div" + ".csv")
                date_check(TempTable)

                Div = []
                s = set(TempTable["Date"])
                for i in range(len(NewFile["Date"])):
                    if NewFile["Date"][i] in s:
                        TempTableIndex = TempTable["Date"].tolist().index(NewFile["Date"][i])
                        Div.append(TempTable["Dividends"][TempTableIndex])
                    else:
                        Div.append(0)
                NewFile[str(t) + " Div"] = Div

                '''Вшиваем дивы, исходя из индексов
                from os import listdir
                from os.path import isfile, join
                
                #Считываем файл, в котором уже есть все тикеры с ценами по столбцам
                enter_table = pd.read_csv("Temp/Enter.csv")
                date_check(enter_table)
                enter_table.set_index("Date", inplace=True) #Теперь индексы равны дате
                
                #Считываем все файлы в папке
                OnlyFiles = [f for f in listdir("datafeed") if isfile(join("datafeed", f))]
                #Оставляем в листе только те файлы, которые отвечают за дивы
                for t in range(0, len(OnlyFiles), 2):
                   OnlyFiles[t] = ""
                OnlyFiles = list(filter(None, OnlyFiles))
                
                #Перебираем див. файлы
                for file in OnlyFiles:
                    cur_div_file = pd.read_csv("datafeed/"+str(file))
                    date_check(cur_div_file)
                    div_column_name = file.replace(".csv","") #Создаём переменную для будущего имени колонки
                    cur_div_file.set_index("Date",inplace=True) #Теперь индексы в див. файле равны дате
                    cur_div_file.columns = [str(div_column_name)]
                    print(cur_div_file)
                    enter_table = enter_table.join(cur_div_file) #Добавить к изначальному файлу, колонку так, чтобы индексы совпадали
                enter_table=enter_table.fillna(0) #Все пустые значения в изначальном файле заменить на 0
                enter_table.to_csv("enter_table_with_divs.csv")
                '''

            # Вшиваем количество позиций и создаём столбики с долями и капиталом
            for p in Position:
                NewColumn = BaseFile["Ticker"].loc[(BaseFile["Position"] == p)]
                NewColumn.index = pd.RangeIndex(len(NewFile.index))

                NewFile["Enter "+str(p)] = NewColumn
                NewFile["Shares "+str(p)] = 0
            NewFile["Capital"] = 0

            # Таблица сформирована. Работам с капиталом и долями
            PartCapital = StartCapital / len(Position)
            for i in range(len(NewFile["Date"])):
                TempCapital = 0.0

                # Текущая дата, это конец квартала?
                if i != len(NewFile["Date"])-1 and NewFile["Date"][i].month in Quarters and NewFile["Date"][i].month !=\
                        NewFile["Date"][i+1].month:
                    EndQuarter = True
                else:
                    EndQuarter = False

                # Перебираем каждую позицию на каждый день и присваиваем доли
                for count in Position:

                    # Параметры вчерашнего тикера
                    if i != 0:
                        PriceOld = NewFile[NewFile["Enter "+str(count)][i-1]][i]
                        DivOld = NewFile[NewFile["Enter "+str(count)][i-1]+str(' Div')][i]
                    else:
                        PriceOld = 0
                        DivOld = 0
                    # Параметры текущего тикера
                    Price = NewFile[NewFile["Enter "+str(count)][i]][i]
                    Div = NewFile[NewFile["Enter "+str(count)][i]+str(' Div')][i]

                    # Если это начало таблицы
                    if i == 0:
                        NewFile.loc[i, 'Shares '+str(count)] = PartCapital/Price
                        TempCapital = NewFile['Shares '+str(count)][i] * Price + TempCapital

                    #Если текущий тикер отличается от вчерашнего
                    elif NewFile['Enter '+str(count)][i] != NewFile['Enter '+str(count)][i-1] and not EndQuarter:
                        NewFile.loc[i, 'Shares ' + str(count)] = NewFile['Shares '+str(count)][i-1] * PriceOld * \
                                                                 (1+DivOld/PriceOld) / Price
                        TempCapital = NewFile['Shares '+str(count)][i] * Price + TempCapital

                    # Если это конец квартала, рассчитай данные по старым тикерам и в дальнейшем переназначим значения
                    # новыми
                    elif EndQuarter:
                        NewFile.loc[i, 'Shares ' + str(count)] = NewFile['Shares '+str(count)][i-1] * (1+DivOld/PriceOld)
                        TempCapital = NewFile['Shares '+str(count)][i] * PriceOld + TempCapital

                    # Если никакое событие выше не наступило
                    else:
                        NewFile.loc[i, 'Shares ' + str(count)] = NewFile['Shares '+str(count)][i-1] * (1+Div/Price)
                        TempCapital = NewFile['Shares '+str(count)][i] * Price + TempCapital

                # Добавляем капитал и рассчитываем конец квартала
                NewFile.loc[i, 'Capital'] = TempCapital
                if EndQuarter:
                    for count in Position:
                        NewFile.loc[i, 'Shares ' + str(count)] = NewFile['Capital'][i] / len(Position) / \
                                                                 NewFile[NewFile["Enter "+str(count)][i]][i]
            # Финальная выгрузка в файл
            NewFile.to_csv('Temp/final_capital Mom_'+str(m)+' T_'+str(n)+' SMA_'+str(ma)+".csv")
            print(NewFile)