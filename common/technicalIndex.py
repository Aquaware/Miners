# -*- coding: utf-8 -*-
import os
import sys
sys.path.append('../XM')
sys.path.append('../private')

from datetime import datetime
import json
from MT5Bind import MT5Bind
import pandas as pd

def dic2array(dic):
    name = dic['name']
    timeframe = dic['timeframe']
    length = dic['length']
    data = dic['data']
    if len(data) == 0:
        return [name, timeframe, 0, {}]
    d = data[0]
    keys = d.keys()
    vectors = {}
    for key in keys:
        v = []
        for i in range(len(data)):
            d = data[i]
            v.append(d[key])
        vectors[key] = v
    return [name, timeframe, length, vectors]

def toTimeList(array):
    form = '%Y/%m/%d %H:%M:%S'
    out = []
    for s in array:
        t = datetime.strptime(s, form) 
        out.append(t)
    return out

def sma(array, window=5):
    return list(pd.Series(array).rolling(window).mean())

def ema(array, window=5):
    a = pd.Series(array)
    sma = a.rolling(window).mean()[:window]
    return list(pd.concat([sma, a[window:]]).ewm(span=window, adjust=False).mean())


def test():
    server = MT5Bind('JP225Cash')
    dic = server.scrapeWithDic('M5', 150)
    [name, timeframe, length, vectors] = dic2array(dic)
    
    time = toTimeList(vectors['time'])
    close = vectors['close']
    
    ma = sma(close, window = 20)
    
if __name__ == '__main__':
    test()

