# -*- coding: utf-8 -*-

from CalendarTime import DTime, DeltaHour, DeltaDay, toNaive
import numpy as np
import pandas as pd


OHLC = ['open', 'high', 'low', 'close'] 
OHLCV = ['open', 'high', 'low', 'close', 'volume'] 

class TimeSeries:
    
    def __init__(self, time, values, names=OHLC):
        self.time = []
        for t in time:
            self.time.append(toNaive(t))
            
        self.values = values
        self.length = len(time)
        self.names = names
        
        if self.length > 0:
            self.size = len(values)
        else:
            self.size = 0
            
        self.array = None
        self.dic = {}
        if self.size != len(names):
            return

        for i in range(len(names)):
            name = names[i]
            self.dic[name] = values[i]
            
        ary = np.zeros((self.length, self.size))
        for r in range(self.length):
            for c in range(self.size):
                ary[r, c] = values[c][r]
        self.array = ary
        return
    
    def toDataFrame(self):
        if len(self.names) < 4:
            return None
        data = []
        for t, value in zip(self.time, self.values):
            data.append([t, value[0], value[1], value[2], value[3]])
        df = pd.DataFrame(data= data, columns= ['time'] + OHLC)
        return df
    
    def timeRangeFilter(self, begin_time, end_time):
        begin_time = toNaive(begin_time)
        end_time = toNaive(end_time)
        
        time = []
        values = []
        
        if begin_time is None:
            begin_time = self.time[0]
        if end_time is None:
            end_time = self.time[-1]
            
        n1 = len(self.time)
        n2 = len(self.values)
        
        for j in range(self.size):
            array = []     
            for i in range(self.length):
                if self.time[i] >= begin_time and self.time[i] <= end_time:
                    if j == 0:
                        time.append(self.time[i])
                    array.append(self.values[j][i])
            values.append(array)
        return TimeSeries(time, values, names=self.names)

    def valueWithIndices(self, indices):
        out = []
        for value in self.values:
            d = []
            for index in indices:
                d.append(value[index])
            out.append(d)

        names = []
        for index in indices:
            names.append(self.names[index])
        return TimeSeries(self.time, out, names=names)


    def indexOfTime(self, time):
        for i in range(self.length):
            if self.time[i] >= time:
                return i
        return -1
    
    def indexRangeFilter(self, i_begin, i_end):
        if i_begin > i_end:
            tmp = i_begin
            i_begin = i_end
            i_end = tmp
            
        if i_begin < 0:
            i_begin = 0
        if i_begin >= self.length:
            return None
        
        if i_end < 0:
            i_end = self.length - 1
        
        time = []
        values = []
        for i in range(i_begin, i_end + 1):
                time.append(self.time[i])
                values.append(self.values[i])
        return TimeSeries(time, values)
    
    def indexRangeSizeFilter(self, i_begin, size):
        if i_begin >= 0:
            i_end = i_begin + size
            if i_end > self.length -1:
                i_end = self.length - 1
        else:
            i_end = self.length - 1
            i_begin = i_end - size + 1
            if i_begin < 0:
                i_begin = 0
        return self.indexRangeFilter(i_begin, i_end)
       
    def slice(self, begin, stop):
        if begin is None:
            begin = 0
        if begin < 0:
            begin = self.length + stop
            
        if stop is None:
            stop = self.length
            
        if stop < 0:
            stop = self.length + stop
        
        
        if abs(begin) > self.length:
            return None
        
        if abs(stop) > self.length:
            return None
        
        time = []
        values = []
        if stop >= begin:
            for i in range(begin, stop):
                time.append(self.time[i])
                values.append(self.values[i])
        else:
            for i in range(begin, stop, -1):
                time.append(self.time[i])
                values.append(self.values[i])
        return TimeSeries(time, values, name=self.names)    
        