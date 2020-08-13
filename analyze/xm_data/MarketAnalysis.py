# -*- coding: utf-8 -*-
import sys
sys.path.append("../../common")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#plt.style.use('seaborn-whitegrid')
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

from CandleChart import CandleChart
from Graph import Graph
import Filters
from CalendarTime import DTime, DeltaDay, DeltaHour, Today
from TimeSeries import TimeSeries
from datetime import datetime
from analyzers import adf

def toDatetimeList(str_list, format):
    out = []
    for s in str_list:
        t = datetime.strptime(s, format)
        out.append(t)
    return out
        
class MarketAnalysis:
    
    def __init__(self, market, time_series):
        self.market = market
        self.time_series = time_series
        self.time = time_series.time
        return

    def plot(self):
        timeseries = self.time_series
        
        if timeseries.length < 0:
            return

        time = timeseries.time
        ohlcv = timeseries.values
        ohlcv_array = timeseries.array
        ohlc_array = ohlcv_array[:, 0:4]
        minval, maxval, maxmin, mean, stdev = self.statics(ohlc_array)
                
        width = 20
        height = 7
                
        fig1 = plt.figure(figsize=(width, height))
        ratio = 0.2
        grid = GridSpec(nrows=2, ncols=1, height_ratios=[1, ratio])
        grid1 = GridSpecFromSubplotSpec(nrows=1, ncols=1, subplot_spec=grid[0, 0])
        ax1 = fig1.add_subplot(grid1[:, :])
                
        graph1 = CandleChart(ax1, time, 'YMD'
                             )
        title = 'US30Cash'
        #graph1.text(graph1.time[0], maxval - maxmin / 10, text, 'blue', 12)
        graph1.setTitle(title, 'Time', self.market)
        graph1.plotOHLC(ohlc_array, bar_width = 0.4)
        return
    
    def plotHours(self, date, hours):
        end_date = date + DeltaHour(hours)
        time_series = self.time_series.timeRangeFilter(date, end_date)
        
        if time_series.length < 20:
            return

        time = time_series.time
        ohlcv = time_series.values
        ohlcv_array = time_series.array
        ohlc_array = ohlcv_array[:, 0:4]
        minval, maxval, maxmin, mean, stdev = self.statics(ohlc_array)

        # Runaway
        runway_flag, runways, runway_labels = Filters.detectRunway(ohlc_array, 3)
                
        # Thrust 
        thrust_flag, thrusts, thrust_labels = Filters.detectThrust(ohlc_array, 15)
        thrust_vector = np.zeros(len(ohlcv))
        integ = np.zeros(len(ohlcv))
        for thrust in thrusts:
            state = thrust[0]
            index = thrust[1]
            v = thrust[2]
            thrust_vector[index] = v
            integ = Filters.integration(thrust_vector)
                
        width = len(ohlcv) / 20 / hours * 24
        height = maxmin / 50
                
        fig1 = plt.figure(figsize=(width, height))
        ratio = 1 / maxmin * 100 * (np.max(integ) - np.min(integ)) / 100
        if ratio < 0.2:
            ratio = 0.2
        grid = GridSpec(nrows=2, ncols=1, height_ratios=[1, ratio])
        grid1 = GridSpecFromSubplotSpec(nrows=1, ncols=1, subplot_spec=grid[0, 0])
        ax1 = fig1.add_subplot(grid1[:, :])
                
        graph1 = CandleChart(ax1, time)
        title = date.strftime('%Y/%m/%d %A') + '  Range:' + "{:.1f}".format(maxmin) + ' Volatililty: ' + "{:.1f}".format(mean) + ' Stdev: ' + "{:.1f}".format(stdev)
        #graph1.text(graph1.time[0], maxval - maxmin / 10, text, 'blue', 12)
        graph1.setTitle(title, 'Time', self.market)
        graph1.plotOHLC(ohlc_array, bar_width = 0.4)
        prop1 = {'status': Filters.UP, 'label': runway_labels[0], 'marker':'^', 'color':'orange', 'alpha':0.4, 'size':70}
        prop2 = {'status': Filters.DOWN, 'label': runway_labels[1],'marker':'v', 'color':'green', 'alpha':0.4, 'size':70}
        graph1.markingWithFlag(ohlc_array, runway_flag, [prop1, prop2])
        prop3 = {'status': Filters.UP, 'label': thrust_labels[0], 'marker':'o', 'color':'magenta', 'alpha':0.5, 'size':40}
        prop4 = {'status': Filters.DOWN, 'label': thrust_labels[1],'marker':'o', 'color':'cyan', 'alpha':0.5, 'size':40}
        graph1.markingWithFlag(ohlc_array[:, 3], thrust_flag, [prop3, prop4])            
        graph1.drawLegend(None, [prop1, prop2, prop3, prop4])
            
        passed = self.time_series.timeRangeFilter(end_date - DeltaDay(30) , end_date)
        prices = Filters.peakPrices(passed.array[:,0:4], 20, 10, np.min(ohlc_array), np.max(ohlc_array))
        graph1.hline(prices, ['green'], 1)
        text = '  Range:' + "{:.1f}".format(maxmin) + ' Volatililty: ' + "{:.1f}".format(mean) + ' Stdev: ' + "{:.1f}".format(stdev)
        #graph1.text(graph1.time[0], maxval - maxmin / 10, text, 'blue', 12)
        
        return
    
        grid2 = GridSpecFromSubplotSpec(nrows=1, ncols=1, subplot_spec=grid[1, 0])
        ax2 = fig1.add_subplot(grid2[:, :])
                
        graph2 = Graph(ax2)
        graph2.setDateFormat()
        graph2.plot(time, integ, {'color':'red', 'style': 'solid', 'width':2})
        for runaway in runways:
            direction = runways[0]
            index = runways[1]
            value = runways[2]
            graph2.point([time[index], value], 'blue', 0.7, 50)
        pass

    def jump(self, market, year, months, hour, threshold):
        begin = market.beginTime()
        end = market.endTime()
        for month in months:
            for day in range(1, 32):
                try:
                    date = DTime(year, month, day, hour, 0)
                except:
                    continue
                end_date = date + DeltaDay(1)
                m = market.timeRangeFilter(date, end_date)
                if m.length() > 0:
                    jump_up = []
                    jump_down = []
                    for t, o, h, l, c in m.tohlcList():
                        if (c - o) >= threshold:
                            jump_up.append(t)
                        if (c - o) <= - threshold:
                            jump_down.append(t)
                        
                    if len(jump_up) == 0 and len(jump_down) == 0:
                        continue
                               
                    m2 = market.timeRangeFilter(date, date + DeltaDay(3))
                    if m2.length() > 0:
                        ohlc = m2.ohlcArray()
                        minmax = np.max(ohlc) - np.min(ohlc)
                        width = len(ohlc) / 15 / 4
                        height = minmax / 50 / 8
                        fig1 = plt.figure(figsize=(width, height))
                        ax1 = fig1.add_subplot(1, 1, 1)
                    
                        graph1 = CandleChart.CandleChart(ax1, m2.pytime())
                        graph1.setTitle(date.strftime('%Y/%m/%d %A'), '', market.name)
                        graph1.plotOHLC(ohlc, bar_width = 0.2)

                        graph1.markingWithTime(ohlc[:, 3], jump_up, 'magenta', 0.5, 100)
                        graph1.markingWithTime(ohlc[:, 3], jump_down, 'cyan', 0.5, 100)
                        graph1.drawLegend(None, [['JumpUp(' + str(threshold) + ')', 'magenta', 'o', 5], ['JumpDown(' + str(threshold) + ')', 'cyan', 'o', 5]])

    def statics(self, ohlc_array):
        maxval = np.max(ohlc_array)
        minval = np.min(ohlc_array)
        maxmin = maxval - minval 
        hl = []
        rows = ohlc_array.shape[0]
        for r in range(rows):
            hl.append(ohlc_array[r, 1] - ohlc_array[r, 2])            
        mean = np.mean(np.array(hl))
        stdev = np.std(np.array(hl))
        return (minval, maxval, maxmin, mean, stdev)

def xmAnalyze():
    name = 'US30Cash'
    timeframe = 'D1'
    df = pd.read_csv('./US30Cash_D1.csv')
    timestr = list(df['Time'].values)
    time = toDatetimeList(timestr, '%Y/%m/%d %H:%M:%S')
    values = [list(df['Open']), list(df['High']), list(df['Low']), list(df['Close'])]
    timeseries = TimeSeries(time, values)
    ts = timeseries.timeRangeFilter(datetime(2012, 12, 1), datetime(2013, 6, 1))
    ana = MarketAnalysis(name, ts)
    ana.plot()
    print(adf(ts.dic['close']))
    

    
if __name__ == '__main__':
    xmAnalyze()