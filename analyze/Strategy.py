# -*- coding: utf-8 -*-
import numpy as np
from datetime import datetime
from Position import Position
from CandleChart import CandleChart, gridFig
import Filters

BREAK_UP = 1
BREAK_DOWN = -1
class Strategy:
    
    def __init__(self):
        self.current = None
        self.times = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.length = 0
        pass
    
    def updateData(self, tohlcv):
        self.times.append(tohlcv[0])
        self.opens.append(tohlcv[1])
        self.highs.append(tohlcv[2])
        self.lows.append(tohlcv[3])
        self.closes.append(tohlcv[4])
        self.volumes.append(tohlcv[5])
        if self.current is None:
            self.current = 0
        else:
            self.current += 1
        self.length = self.current + 1
        return
    
    def breakout(self, width, threshold):
        power, psum = self.purchasePower()
        br = self.rangeBreak(psum, width, threshold)
        return br[-1]
    
    def purchasePower(self):
        power = []
        psum = []
        s = 0.0
        for o, h, l, c, v in zip(self.opens, self.highs, self.lows, self.closes, self.volumes):
            p = v * (c - o)
            power.append(p)
            s += p
            psum.append(s)
        return (power, psum)
    
    def volatility(self, window_width):
        maxmin = []
        spikes = []
        ranges = []
        for o, h, l, c, v in zip(self.opens, self.highs, self.lows, self.closes, self.volumes):
            r = h - l
            if r == 0.0:
                noise = 1 - np.abs(c - o) / r
            else:
                noise = 1.0
            maxmin.append(r)
            spikes.append(noise)
            ranges.append(c - o)
    
        volatility = np.full(self.length, np.nan)
        for i in range(self.length):
            if i < window_width + 1:
                volatility[i] = ranges[i]
            else:
                noise = spikes[i - window_width - 1: i]
                mean = np.nanmean(noise)
                volatility[i] = maxmin[i] * mean
        return volatility
        
    
    def rangeBreak(self, signal, window_width, threshold, ignore_break_down=False):
        n = len(signal)
        flag = np.zeros(n)
        for i in range(window_width, n):
            v = signal[i - window_width: i]
            minv = np.min(v)
            maxv = np.max(v)
            if signal[i] > maxv + np.abs(maxv - minv) * threshold:
                flag[i] = BREAK_UP
            elif ignore_break_down == False and signal[i] < minv - np.abs(maxv - minv) * threshold:
                flag[i] = BREAK_DOWN
        return flag
    
    
    
# -----
        
def log(vector):
    out = []
    for v in vector:
        if v >= 0:
            out.append(np.log(v))
        else:
            out.append(-np.log(-v))
    return out
        
def test(ts):
    t = ts.time
    values = ts.values_in_time
    strategy = Strategy()
    for i in range(len(t)):
        strategy.updateData(values[i])
        bo = strategy.breakout(15, 1.0)
        #print(i, bo)
    power, psum = strategy.purchasePower()
    pplog = log(psum)
    pp_bo = strategy.rangeBreak(psum, 5, 3.0)
    
    volatility = strategy.volatility(15)
    ma = Filters.movingAverage(volatility, 7)
    bo_vol = strategy.rangeBreak(ma, 3, 5.0, ignore_break_down=True)
    
    fig, axes = gridFig(14, [8, 2, 1, 2])
    graph1 = CandleChart(axes[0], t, 'HM')
    graph1.plotOHLC(ts.values)
    graph1.grid()
    
    graph2 = CandleChart(axes[1], t, 'HM')
    graph2.plot(psum, 0, 1)
    graph3 = CandleChart(axes[2], t, 'HM')
    graph3.plot(pp_bo, 2, 1)
    
    props = [ {'value':BREAK_UP, 'marker':'o', 'color':'blue', 'alpha': 0.5, 'size': 120},
              {'value':BREAK_DOWN, 'marker':'o', 'color':'orange', 'alpha': 0.5, 'size': 120}]
    graph1.plotFlag(pp_bo, ts.data('open'), props)
    props = [ {'value':BREAK_UP, 'marker':',', 'color':'gray', 'alpha': 0.5, 'size': 120},
              {'value':BREAK_DOWN, 'marker':',', 'color':'orange', 'alpha': 0.5, 'size': 120}]
    graph1.plotFlag(bo_vol, ts.data('close'), props)
    
    graph4 = CandleChart(axes[3], t, 'HM')
    graph4.plot(volatility, 2, 1)
    
    return
    
if __name__ == "__main__":
    import pandas as pd
    from TimeSeries import TimeSeries, DATA_TYPE_PANDAS, OHLCV
    df = pd.read_csv('./dji_M5.csv')
    ts = TimeSeries(df, DATA_TYPE_PANDAS, names=OHLCV)
    #ts = ts.timeRangeFilter(datetime(2019, 8, 6, 1, 0), None)
    test(ts)