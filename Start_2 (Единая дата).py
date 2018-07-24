import pandas as pd
import numpy as np
import os
from datetime import datetime

filelist = os.listdir("datafeed")
print(filelist)

dateList = []
for file in filelist:
    print(str(file))
    curFileTable=pd.read_csv("datafeed/"+str(file))
    print(curFileTable.head(1))
    try:
        curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%Y-%m-%d")
    except:
        curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%m/%d/%Y")
    dateList.append(curFileTable["Date"].iloc[0])
    print("--------------")

print(dateList)
startDate = max(dateList)
endDate = datetime(2008, 1, 1)


lenTables = []
for file in filelist:
    curFileTable = pd.read_csv("datafeed/"+str(file))
    try:
        curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%Y-%m-%d")
    except:
        curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%m/%d/%Y")
    curFileTableStartDate = curFileTable.loc[(curFileTable["Date"]>=startDate) & (curFileTable["Date"]<endDate)]
    lenTables.append(len(curFileTableStartDate))
    print(str(file))
    print(curFileTableStartDate.head(1))
    print(curFileTableStartDate.tail(1))
    curFileTableStartDate.to_csv(str(file))
print(lenTables)