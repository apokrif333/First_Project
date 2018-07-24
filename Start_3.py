import pandas as pd
import numpy as np
import os
from datetime import datetime

# filelist = os.listdir("datafeed")
# print(filelist)
#
# dateList = []
# for file in filelist:
#     print(str(file))
#     curFileTable=pd.read_csv("datafeed/"+str(file))
#     print(curFileTable.head(1))
#     try:
#         curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%Y-%m-%d")
#     except:
#         curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%m/%d/%Y")
#     dateList.append(curFileTable["Date"].iloc[0])
#     print("--------------")
#
# startDate = max(dateList)
# endDate = datetime(2008, 1, 1)
#
# lenTables = []
# for file in filelist:
#     curFileTable = pd.read_csv("datafeed/"+str(file))
#     try:
#         curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%Y-%m-%d")
#     except:
#         curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%m/%d/%Y")
#     curFileTableStartDate = curFileTable.loc[(curFileTable["Date"]>=startDate)]
#     lenTables.append(len(curFileTableStartDate))
#     # print(str(file))
#     # print(curFileTableStartDate.head(1))
#     # print(curFileTableStartDate.tail(1))
#     curFileTableStartDate.to_csv(str(file))
# # print(lenTables)
#
# lastDateinMonth=[]
# for i in range (0,len(curFileTableStartDate)):
#     if i<len(curFileTableStartDate)-1:
#         curDate = curFileTableStartDate["Date"].iloc[i]
#         nextDate = curFileTableStartDate["Date"].iloc[i+1]
#         curMonth = curDate.month
#         nextMonth = nextDate.month
#         if curMonth!=nextMonth:
#             lastDateinMonth.append(curDate)
#         # print(curDate)
#         # print(nextMonth)
#     else:
#         lastDateinMonth.append(curDate)
# # print(lastDateinMonth)
#
# tickerL=[]
# datesL=[]
# closesL=[]
#
# for file in filelist:
#     ticker = file.replace(".csv","")
#     curFileTable = pd.read_csv("datafeed/"+str(file))
#     try:
#         curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%Y-%m-%d")
#     except:
#         curFileTable["Date"] = pd.to_datetime(curFileTable["Date"], format="%m/%d/%Y")
#     for date in lastDateinMonth:
#         tickerL.append(ticker)
#         datesL.append(date)
#         curDateFileTable = curFileTable.loc[curFileTable["Date"]==date]
#         closesL.append(curDateFileTable["Close"].iloc[0])
#         # print(file)
#         # print(curDateFileTable)
#         # print("--------")
#
# # print(datesL)
# # print(tickerL)
# # print(closesL)
#
# lastMonthCloses = pd.DataFrame({"Ticker":tickerL,
#                                 "Date":datesL,
#                                 "Close":closesL})
#
# # lastMonthCloses.to_csv("lastMonthCloses.csv")
# # print(lastMonthCloses)
#
# gainL=[]
# for i in range(0,len(lastMonthCloses)):
#     curTicker = lastMonthCloses["Ticker"].iloc[i]
#     prTicker = lastMonthCloses["Ticker"].iloc[i-1]
#     if i==0 or curTicker!=prTicker:
#        gainL.append(0)
#     else:
#         gainL.append(lastMonthCloses["Close"].iloc[i]/lastMonthCloses["Close"].iloc[i-1]-1)
#
# lastMonthCloses["Gain"]=gainL
# lastMonthCloses.to_csv("lastMonthCloses.csv")

lastMonthCloses = pd.read_csv("lastMonthCloses.csv")
try:
    lastMonthCloses["Date"] = pd.to_datetime(lastMonthCloses["Date"], format="%Y-%m-%d")
except:
    lastMonthCloses["Date"] = pd.to_datetime(lastMonthCloses["Date"], format="%m/%d/%Y")

dateList = lastMonthCloses["Date"].unique()

riskOnL=["VTSMX","VEURX","VPACX","VEIEX"]
riskOff="VUSTX"
riskOffF="VFISX"

bestTickersL=[]
for date in dateList:
    curDateLastMonthCloses=lastMonthCloses.loc[(lastMonthCloses["Date"]==date) & (lastMonthCloses["Ticker"].isin(riskOnL))]
    curDateLastMonthCloses = curDateLastMonthCloses.sort_values("Gain",ascending=False)
    curDateLastMonthCloses=curDateLastMonthCloses.head(1)
    if curDateLastMonthCloses["Gain"].iloc[0]>0:
        bestTickersL.append(curDateLastMonthCloses["Ticker"].iloc[0])
    else:
        bestTickersL.append(riskOff)
    print(curDateLastMonthCloses)

bestMonthPerf = pd.DataFrame({"Date":dateList,
                              "Ticker":bestTickersL})
print(bestMonthPerf)
bestMonthPerf.to_csv("bestMonthPerf.csv")