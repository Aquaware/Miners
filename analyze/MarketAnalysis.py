# -*- coding: utf-8 -*-
import sys
sys.path.append("../common")
sys.path.append("../XM")
sys.path.append("../private")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#plt.style.use('seaborn-whitegrid')
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

from CandleChart import CandleChart, makeFig
from Graph import Graph
import Filters
from CalendarTime import Now, DTime, DeltaDay, DeltaHour, Today
from TimeSeries import TimeSeries, OHLCV, OHLC, DATA_TYPE_XM
from datetime import datetime
from analyzers import adf

from MT5Bind import MT5Bind, jstTime

        
def test1():
    server = MT5Bind('US30Cash')
    t0 = jstTime(2019, 3, 5, 20, 0)
    t1 = jstTime(2019, 3, 6, 8, 0)
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
    
    
def breakout(signal, ohlc, param):
    BUY = 1
    SELL = -1
    CLOSE = 2
    
    
    [buy_threshold, sell_threshold, stop_profit_price, stop_loss_price] = param
    
    flag = []
    status = 0
    prices = []
    indices = []
    profit = 0
    
    count = 0
    longOrShort = None
    for s, o, h, l, c in zip(signal, ohlc[0], ohlc[1], ohlc[2], ohlc[3]):
        if status == 0:
            if s >= buy_threshold:
                flag.append(BUY)
                status = BUY
                longOrShort = BUY
                prices.append(c)
                indices.append(count)
            elif s <= sell_threshold:
                flag.append(SELL)
                status = SELL
                longOrShort = SELL
                prices.append(c)
                indices.append(count)
            else:
                flag.append(0)
        elif status == BUY:
            profit = c - prices[0]
            if profit > stop_profit_price or profit < -stop_loss_price:
                prices.append(c)
                flag.append(CLOSE)
                status = CLOSE
                indices.append(count)
            else:
                flag.append(0)
        elif status == SELL:
            profit = prices[0] - c
            if profit > stop_profit_price or profit < -stop_loss_price:
                prices.append(c)
                flag.append(CLOSE)
                status = CLOSE
                indices.append(count)
            else:
                flag.append(0)
        else:
            flag.append(0)
            
        count += 1
    return (longOrShort, profit, prices, indices, flag)
                
def analyze(title, ts_list, breakout_param, should_save):
   
    out = []
    num = 0
    profit_sum = 0.0
    total = []
    for tsvalue in ts_list:
        [date, ts] = tsvalue
        op = ts.data('open')
        cl = ts.data('close')
        volume = ts.data('volume')
    
        #print('length:', ts.length)
        if ts.length < 30:
            continue
    
        colors = []
        power = []
        psum = []
        s = 0.0
        for o, c, v in zip(op, cl, volume):
            p = v * (c - o)
            power.append(p)
            s += p
            psum.append(s)
            if c > o:
                colors.append('green')
            elif c < o:
                colors.append('red')
            else:
                colors.append('black')
    
        num += 1
        width = ts.length / 8
        [minvalue, maxvalue] = ts.minmax(OHLC)
        maxmin = maxvalue - minvalue
        height1 = maxmin / 100
        height2 = (np.max(psum) - np.min(psum)) / 50000
        height = height1 + height2
        ratio = height2 / height1
         
        """    
        fig1 = plt.figure(figsize=(width, height))
        grid = GridSpec(nrows=2, ncols=1, height_ratios=[1, ratio])
        grid1 = GridSpecFromSubplotSpec(nrows=1, ncols=1, subplot_spec=grid[0, 0])
        ax1 = fig1.add_subplot(grid1[:, :])
        grid2 = GridSpecFromSubplotSpec(nrows=1, ncols=1, subplot_spec=grid[1, 0])
        ax2 = fig1.add_subplot(grid2[:, :]) 
        
        graph1 = CandleChart(ax1, ts.time, 'HM')
        graph1.plotOHLC([op, ts.data('high'), ts.data('low'), cl])
        title_str = title + '    '  + t0.strftime('%Y-%m-%d (%A)') + ' ~   Range:' + "{:.1f}".format(maxmin)
        graph1.setTitle(title_str, '', '')
        graph1.bars(volume, colors, np.max(volume) * 5, 0.01)
        graph1.grid()
                             
        graph2 = CandleChart(ax2, ts.time, 'HM')
        graph2.plot(power, 0, 1)
        graph2.plot(psum, 1, 1)
        graph2.drawLegend([{'label': 'Power', 'color':'red'}, {'label': 'PowerSum', 'color':'blue'}], None)
        graph2.grid()
        """
    
        if should_save:
            path = './output/' + str(num).zfill(5) +  title + '_' + date.strftime('%Y-%m-%d(%A)') + '.png'
            plt.savefig(path)
        
        data_list = ts.dataList(OHLC)
        ret  = breakout(psum, data_list, breakout_param)
        (longOrShort, profit, prices, indices, flag) = ret
        #print(title, ' ... Profit', profit, 'Prices', prices, '(', indices, ')')
    
        if len(prices) == 2:
            out.append([num, date, longOrShort, profit, prices, indices])
            profit_sum += profit
            total.append(profit_sum)
            
    print('*', breakout_param, '*    Profit: ', profit_sum)
    return (profit_sum, np.min(total))  
   
def evaluate(should_save):
    now = Now()
    t = datetime(2019, 3, 1)
    server = MT5Bind('US30Cash')
    ts_list = []
    while t <= now:
        t0 = jstTime(t.year, t.month, t.day, 19, 0)
        tmp = t0 + DeltaDay(1)
        t1 = jstTime(tmp.year, tmp.month, tmp.day, 5, 30)
        data = server.scrapeRange('M5', t0, t1)
        ts = TimeSeries(data, DATA_TYPE_XM, names=OHLCV, index=[1, 2, 3, 4, 5])
        print(t, 'length:', ts.length)
        if ts.length > 20:
            ts_list.append([t, ts])
        t += DeltaDay(1)
    server.close()
    
    num = 1
    out = []
    for buy_threshold in range(20000, 500001, 5000):
        for sell_threshold in range(-20000, -500001, -5000):
            for stop_profit in range(50, 601, 50):
                for stop_loss in range(50, 301, 50):
                    param = [buy_threshold, sell_threshold, stop_profit, stop_loss]
                    profit, drawdown = analyze('DJI-M5', ts_list, param, should_save)
                    out.append([num, buy_threshold, sell_threshold, stop_profit, stop_loss, profit, drawdown])
                    num += 1
    df = pd.DataFrame(data=out, columns = ['No', 'BuyTh', 'SellTh', 'StopProfit', 'StopLos', 'Profit', 'Drawdown'])
    df.to_excel('./evaluation.xls', index=False)
    
    return
    
if __name__ == '__main__':
    evaluate(False)