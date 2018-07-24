import pandas as pd
import numpy as np
import os
from datetime import datetime

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

#Создаём файл с датами, начиная с самой старой для всех файлов
dateFile = pd.read_csv("datafeed/"+str(filesList[0]))
try:
    dateFile["Date"] = pd.to_datetime(dateFile["Date"], format="%Y-%m-%d")
except:
    dateFile["Date"] = pd.to_datetime(dateFile["Date"], format="%m/%d/%Y")

dateFile=dateFile.loc[dateFile["Date"]>=startDate]
allDatesList=dateFile["Date"].tolist()

#Исключаем 11 сентября
exceptionDate = pd.to_datetime("2001-09-10",format="%Y-%m-%d")

lastWeekDayL=[]
numDaysWeekL=[]
for i in range (0,len(allDatesList)):
    numDaysWeekL.append(allDatesList[i].weekday()) #Задать для каждой даты день недели
    if i+1<len(allDatesList):
        if allDatesList[i]==exceptionDate: #Если это исключение - то это не конец недели
            lastWeekDayL.append(0)
        else:
            delta = allDatesList[i+1]-allDatesList[i] #Если между днями, промежуток больше двух дней, то это конец недели lastWeekDayL
            if delta.days>2:
                lastWeekDayL.append(1)
            else:
                lastWeekDayL.append(0)
    else:
        lastWeekDayL.append(0)

#Создать таблицу. С датой, днём недели и конец недели.
lastWeekDays=pd.DataFrame({"Date":allDatesList,
                           "LastWeekDay":lastWeekDayL,
                           "NumWeekDay":numDaysWeekL})

#Заносим таблицу в файл
lastWeekDays.to_csv("lastWeekDays.csv")
print(lastWeekDays)
