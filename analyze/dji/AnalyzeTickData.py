# -*- coding: utf-8 -*-
import sys
sys.path.append("../../common")

import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
#plt.style.use('seaborn-whitegrid')

from TimeSeries import TimeSeries, PV
from Graph import Graph, makeFig

# -----   
    
def readCsv():
    files = glob.glob("./jpxdata/*/*.csv", recursive=True)
    df = None
    for path in files:
        tmp = pd.read_csv(path)
        if df is None:
            df = tmp
        else:
            df = pd.concat([df, tmp])
            
    df1 = df.sort_values(['Make_Date', 'Time'])
    date = list(df1['Make_Date'].values)
    time = list(df1['Time'].values)
    price = list(df1['Trade_Price'].values)
    volume = list(df1['Trade_Volume'].values)
    
    data = []
    for d, t, p, v in zip(date, time, price, volume):
        year = int(d / 10000)
        d -= year * 10000
        month = int(d / 100)
        d -= month * 100
        day = d
        hour = int(t / 10000000
                   )
        t -= hour * 10000000
        minute = int(t / 100000)
        t -= minute * 100000
        sec = int(t / 1000)
        t -=  sec * 1000
        msec = t
        
        dt = datetime(year, month, day, hour, minute, sec, msec)
        if hour == 15 and minute > 15:
            dt += timedelta(days=1)
        elif hour > 15 and hour <= 23:
            dt += timedelta(days=1)
        elif hour >= 0 and hour <= 7:
            dt += timedelta(days=1)
        
        data.append([dt, dt.timestamp(), p, v])
        
    df2 = pd.DataFrame(data = data, columns = ['Time', 'Timestamp', 'Price', 'Volume'])
    df3 = df2.sort_values('Timestamp')
    timestamp = list(df3['Timestamp'])
    pytime = []
    for t in timestamp:
        pytime.append(datetime.fromtimestamp(t))
    price = list(df3['Price'])
    volume = list(df3['Volume'])
        
    timeseries = TimeSeries(pytime, [price, volume], names=PV)
    ts = timeseries.timeRangeFilter(datetime(2019, 8, 5), datetime(2019, 8, 7))
    
    fig, ax = makeFig(1, 1, (20, 5))
    graph = Graph(ax)
    graph.setDateFormat(form ='%m-%d %H:%M')
    prop = {'color':'red', 'style':'solid', 'width':1}
    graph.scatter(ts.time, ts.values[0], prop)
    
    return
    
def dji():
    print('dji')
    readCsv()
    return
    
if __name__ == '__main__':
    dji()