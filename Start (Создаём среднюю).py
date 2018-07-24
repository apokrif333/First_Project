import pandas as pd
import numpy as np
import matplotlib as mp
import datetime
import pandas_datareader as web
from datetime import datetime

'''Выкачиваем базу
start = datetime.strptime("01/01/1990", "%m/%d/%Y")
end = datetime.strptime("01/01/2018", "%m/%d/%Y")
closeBase = web.DataReader("SPY", "morningstar", start, end)
'''


closeBase = pd.read_csv("VUSTX.csv")
closeList = closeBase["Close"].tolist()
print(len(closeList))

'''Способ1
average=[]
for i in range(0, len(closeList)):
    if i>=199:
        average.append(np.average(closeList[i-199:i+1]))
    else:
        average.append(0)

closeBase["Average"] = average
closeBase.to_csv("VUSTXaverage.csv")
print(closeBase)
'''


average2=[]
for i in range(0,len(closeBase)):
    curTable=closeBase.head(i+1)
    curTable=curTable.tail(200)
    if i>=199:
            average2.append(np.average(curTable["Close"].tolist()))
    else:
            average2.append(0)
closeBase["Average2"]=average2
closeBase.to_csv("VUSTXaverage.csv")

print(curTable)

'''Особенности массивов
print(closeBase.tail(10))
DateList = closeBase["Date"].tolist()
print(DateList[3437:3441])
print(len(DateList))
'''