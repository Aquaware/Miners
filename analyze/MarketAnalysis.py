# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../private'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../common'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../XM'))



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
    
    
def breakout(signal, ts, param, stops):
    BUY = 1
    SELL = -1
    CLOSE = 2
    END = 3
    
    date = ts.time[0]
    #print(date)
    
    ohlcv = ts.dataList(OHLCV)
    [buy_threshold, sell_threshold, ma_window, limit] = param
    level_max = len(stops)
    level = 0
    
    ma = Filters.movingAverage2(signal, ma_window)
    #dif = Filters.dif(ma, 5)
    
    flag = []
    status = 0
    matches = []
    indices = []
    profit = 0
    
    count = -1
    longOrShort = None
    prices = []
    for t, s, o, h, l, c in zip(ts.time, signal, ohlcv[0], ohlcv[1], ohlcv[2], ohlcv[3]):
        count += 1
        #if t.hour <= 20 and t.hour >= 8:
        #    continue
        
        
        if len(matches) >= limit:
            status = END
            flag.append(0)
            continue
            
        if status == 0:
            [stop_profit, stop_loss] = stops[level]
            if s >= buy_threshold and (c - o) > 10.0:
                stop_profit_price = c + stop_profit
                stop_loss_price = c + stop_loss
                flag.append(BUY)
                status = BUY
                longOrShort = BUY
                prices = [c]
                indices = [count]
            elif s <= sell_threshold and (c - o) < -10.0:
                stop_profit_price = c - stop_profit
                stop_loss_price = c - stop_loss
                flag.append(SELL)
                status = SELL
                longOrShort = SELL
                prices = [c]
                indices = [count]
            else:
                flag.append(0)
        elif status == BUY:
            profit = c - prices[0]
            if stop_profit_price >= l and stop_profit_price <= h:
                while level < level_max:
                    [stop_profit, stop_loss] = stops[level]
                    stop_profit_price = prices[0] + stop_profit
                    stop_loss_price = prices[0] + stop_loss
                    if h > stop_profit_price:
                        break
                    level += 1
                if stop_profit_price >= l and stop_profit_price <= h:
                    flag.append(CLOSE)
                    prices.append(stop_profit_price)
                    indices.append(count)
                    matches.append([longOrShort, prices, indices])
                    longOrShort = 0
                    status = 0
                    level = 0
                else:
                    flag.append(0)
            elif stop_loss_price >= l and stop_loss_price <= h:
                prices.append(stop_loss_price)
                flag.append(CLOSE)
                indices.append(count)
                matches.append([longOrShort, prices, indices])
                status = 0
                longOrShort = 0
                level = 0
        elif status == SELL:
            if stop_profit_price >= l and stop_profit_price <= h:
                while level < level_max:
                    [stop_profit, stop_loss] = stops[level]
                    stop_profit_price = prices[0] - stop_profit
                    stop_loss_price = prices[0] - stop_loss
                    if l > stop_profit_price:
                        break
                    level += 1
                if stop_profit_price >= l and stop_profit_price <= h:
                    flag.append(CLOSE)
                    prices.append(stop_profit_price)
                    indices.append(count)
                    matches.append([longOrShort, prices, indices])
                    status = 0
                    longOrShort = 0
                    level = 0
                else:
                    flag.append(0)
            elif stop_loss_price >= l and stop_loss_price <= h:
                prices.append(stop_loss_price)
                flag.append(CLOSE)
                indices.append(count)
                matches.append([longOrShort, prices, indices])
                status = 0
                longOrShort = 0
                level = 0
        else:
            flag.append(0)
    
    if len(prices) == 1:
        prices.append(ohlcv[3][-1])    
        indices.append(len(ohlcv[0]) - 1)
        matches.append([longOrShort, prices, indices])
        
    profits = []
    for [lors, pr, idx] in matches:
        if lors == BUY:
            profit = pr[1] - pr[0]
        else:
            profit = pr[0] - pr[1]
        profits.append(profit)                
    return (profits, matches, flag)

def purchasePower(ts):
    ohlcv = ts.dataList(OHLCV)
    power = []
    psum = []
    s = 0.0
    for o, h, l, c, v in zip(ohlcv[0], ohlcv[1], ohlcv[2], ohlcv[3], ohlcv[4]):
        p = v * (c - o)
        power.append(p)
        s += p
        psum.append(s)
    return (power, psum)  

def drawGraph(title, ts, date, power, psum, result, param):
    op = ts.data('open')
    cl = ts.data('close')
    
    [buy_threshold, sell_threshold, ma_window, limit] = param
    
    width = ts.length / 8
    [minvalue, maxvalue] = ts.minmax(OHLC)
    maxmin = maxvalue - minvalue
    height1 = maxmin / 100
    height2 = (np.max(psum) - np.min(psum)) / 50000
    height = height1 + height2
    ratio = height2 / height1
         
    fig1 = plt.figure(figsize=(width, height))
    grid = GridSpec(nrows=2, ncols=1, height_ratios=[1, ratio])
    grid1 = GridSpecFromSubplotSpec(nrows=1, ncols=1, subplot_spec=grid[0, 0])
    ax1 = fig1.add_subplot(grid1[:, :])
    grid2 = GridSpecFromSubplotSpec(nrows=1, ncols=1, subplot_spec=grid[1, 0])
    ax2 = fig1.add_subplot(grid2[:, :]) 
        
    graph1 = CandleChart(ax1, ts.time, 'HM')
    graph1.plotOHLC([op, ts.data('high'), ts.data('low'), cl])
    title_str = title + '    '  + date.strftime('%Y-%m-%d (%A)') + ' ~   Range:' + "{:.1f}".format(maxmin)
    graph1.setTitle(title_str, '', '')
    #graph1.bars(volume, colors, np.max(volume) * 5, 0.01)
    graph1.grid()
    
    ma = Filters.movingAverage(psum, ma_window)
    dif = Filters.dif(ma, 5)
    graph2 = CandleChart(ax2, ts.time, 'HM')
    graph2.plot(psum, 0, 1)
    graph2.plot(ma, 1, 1)
    #graph2.plot(dif, 7, 1)
    graph2.drawLegend([{'label': 'PurchasePower', 'color':'red'}, {'label': 'MA' + str(ma_window), 'color':'blue'}], None)
    graph2.grid()
    
    graph2.hline(param[0:2], ['orange', 'violet'], 2)
    profits, matches, flag = result
    profit_str = ''
    for profit, match in zip(profits, matches):
        longOrShort, prices, indices = match
        graph1.box([graph1.time[indices[0]], graph1.time[indices[1]]], prices, 0, 0.2)
        graph1.point([graph1.time[indices[0]], prices[0]], 'o', 'blue', 0.7, 80)
        graph1.point([graph1.time[indices[1]], prices[1]], 'o', 'orange', 0.7, 80)
        profit_str += str(profit) + '  '
    if len(profits) > 0:
        graph1.text(graph1.time[0], graph1.yRange()[1] - 40, 'Profit: ' + profit_str, 'blue', 16)

        
    #if should_save:
    #    path = './output/' + str(num).zfill(5) +  title + '_' + date.strftime('%Y-%m-%d(%A)') + '.png'
    #    plt.savefig(path)
    return


def simulation(number, title, ts_list, param, stops, should_draw, should_save):
    [buy_threshold, sell_threshold, ma_window, limit] = param
    print (title, 'Buy threshold: ', buy_threshold, 'Sell threshold: ', sell_threshold,  'MA window: ', ma_window, 'StopProfit: ', stops[0][0], 'StopLoss: ', stops[0][1])
    
    out = []
    num = 0
    profit_sum = 0.0
    equity = []
    for tsvalue in ts_list:
        [date, ts] = tsvalue
        #print('length:', ts.length)
        if ts.length < 100:
            continue
    
        num += 1
        (power, psum) = purchasePower(ts)
        result = breakout(psum, ts, param, stops)
        profits, matches, flag = result
        for profit, match in zip(profits, matches):
            #print(title, ' ... Profit', profit, 'Prices', prices, '(', indices, ')')
            longOrShort, prices, indices = match
            out.append([num, date, longOrShort, profit, prices, indices])
            profit_sum += profit
            equity.append(profit_sum)

        if should_draw:
            drawGraph(title, ts, date, power, psum, result, param)
            
    if should_save:
        path = './' + str(number).zfill(5) + '_' + title + '.csv'
        df = pd.DataFrame(out, columns=['No', 'Date', 'Long_Short', 'Profit', 'Price', 'Index'])
        df.to_csv(path, index=False)
        
    drawdown = np.min(equity)
    print('*', param, stops, '*    Profit: ', profit_sum, '  DrawDown:', drawdown)
    return (equity, profit_sum, drawdown)  
   
    
def dataSource():
    now = Now()
    begin1 = datetime(2019, 3, 1)
    end1 = datetime(2020, 2, 28)
    begin2 = datetime(2020, 1, 1)
    server = MT5Bind('US30Cash')
    ts_list = []
    t = begin1
    while t <= end1:
        t0 = jstTime(t.year, t.month, t.day, 19, 0)
        tmp = t0 + DeltaDay(1)
        t1 = jstTime(tmp.year, tmp.month, tmp.day, 5, 30)
        data = server.scrapeRange('M5', t0, t1)
        ts = TimeSeries(data, DATA_TYPE_XM, names=OHLCV, index=[1, 2, 3, 4, 5])
        #print(t, 'length:', ts.length)
        if ts.length > 20:
            ts_list.append([t, ts])
        t += DeltaDay(1)
    server.close()
    return ts_list    
    

    
def evaluate1(should_draw, should_save):
    header = 'No, BuyTh, SellTh, StopProfit, StopLos, Profit, Drawdown'
    path = './evaluation1.csv'

    if os.path.exists(path):
        file = open(path, 'a')
    else:
        file = open(path, 'w')
        file.write(header + '\n')
    ts_list = dataSource()
    
    stops_list = [[[180, -180]],
                  [[180, -180], [250, 150], [300, 200], [350, 250], [400, 300], [450, 350], [500, 400]],
                  [[100, -100], [150, 50], [200, 120], [250, 170], [300, 220], [350, 270], [400, 320], [450, 370], [500, 420]],
                  [[50, -50], [100, 20], [150, 80], [200, 140], [250, 180], [300, 230], [350, 280], [400, 330], [450, 380], [500, 430]] ]
    num = 1
    for buy_threshold in range(10000, 30001, 1000):
        for sell_threshold in range(-10000, -30001, -1000):
            k = 1
            for stops in stops_list:
                equity, profit, drawdown = simulation(num, 'DJI-M5', ts_list, [buy_threshold, sell_threshold], stops, should_draw, should_save)
                s = str(num) + ',' + str(buy_threshold) + ',' + str(sell_threshold) + ',' + str(k) + ',' + str(profit) + ',' + str(drawdown)
                file.write(s + '\n')
                k += 1
                num += 1
    file.close()
    print('*** All Done ***')
    return

def evaluate2(should_draw, should_save):
    header = 'No, BuyTh, SellTh, ma_window, stop_profit, stop_loss, Profit, Drawdown'
    path = './evaluation5.csv'
    if os.path.exists(path):
        file = open(path, 'a')
    else:
        file = open(path, 'w')
        file.write(header + '\n')
    ts_list = dataSource()
    
    stops_list= []
    for a in range(50, 410, 50):
        for b in range(50, 410, 50):
            if a > b:
                stops_list.append( [[a, -b]] )
    
    num = 1
    limit = 1
    for buy_threshold in range(10000, 30001, 5000):
        for sell_threshold in range(-10000, -30001, -5000):
            for ma in [1]:
                k = 1
                for stops in stops_list:
                    equity, profit, drawdown = simulation(num, 'DJI-M5', ts_list, [buy_threshold, sell_threshold, ma, limit], stops, should_draw, should_save)
                    s = str(num) + ',' + str(buy_threshold) + ',' + str(sell_threshold) + ',' + str(ma) + ',' + str(stops[0][0]) + ',' + str(stops[0][1]) + ',' + str(profit) + ',' + str(drawdown)
                    file.write(s + '\n')
                    k += 1
                    num += 1
    file.close()
    print('*** All Done ***')
    return

    
def test():
    ts_list = dataSource()
    param = [25000, -15000, 7, 1]
    #stops = [[100, -100], [150, 90], [200, 140], [250, 190]]
    stops = [[400, -350]]
    equity, profit, drawdown = simulation(1, 'DJI-M5', ts_list, param, stops, True, True)
    fig, ax = makeFig(1, 1, (15, 5))
    graph = Graph(ax)
    prop = {'color':'green', 'style':'solid', 'width':1}
    graph.plot(range(len(equity)), equity, prop)
    graph.setTitle('Equity Curve', '', '')
    print(profit, drawdown)
    return
                        
if __name__ == '__main__':
    #evaluate2(False, False)
    test()