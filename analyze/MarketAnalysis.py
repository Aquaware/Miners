# -*- coding: utf-8 -*-
import sys
sys.path.append("../common")
sys.path.append("../XM")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#plt.style.use('seaborn-whitegrid')
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

from CandleChart import CandleChart, makeFig
from Graph import Graph
import Filters
from CalendarTime import DTime, DeltaDay, DeltaHour, Today
from TimeSeries import TimeSeries, OHLCV, DATA_TYPE_XM
from datetime import datetime
from analyzers import adf

from MT5Bind import MT5Bind, jstTime

def toDatetimeList(str_list, format):
    out = []
    for s in str_list:
        t = datetime.strptime(s, format)
        out.append(t)
    return out
        
def analyze1():
    server = MT5Bind('US30Cash')
    t0 = jstTime(2019, 8, 5, 7, 0)
    t1 = jstTime(2019, 8, 6, 5, 0)
    t0 = server.roundMinute(t0, 'M5')
    print(t0, t1)
    t1 = server.roundMinute(t1, 'M5')
    
    data = server.scrapeRange('M5', t0, t1)
   
    ts = TimeSeries(data, DATA_TYPE_XM, names=OHLCV, index=[1, 2, 3, 4, 5])
    df = ts.toDataFrame()
    df.to_csv('./dji_M5.csv', index=False)
    
    fig, ax = makeFig(1, 1, (15, 5))
    graph = CandleChart(ax, ts.time, 'MDHM')
    graph.plotOHLC([ts.dic['open'], ts.dic['high'], ts.dic['low'], ts.dic['close']])

    data = server.scrapeRange('M1', t0, t1)
    ts = TimeSeries(data, DATA_TYPE_XM, names=OHLCV, index=[1, 2, 3, 4, 5])
    df = ts.toDataFrame()
    df.to_csv('./dji_M1.csv', index=False)
    
    server.close()

    
if __name__ == '__main__':
    analyze1()