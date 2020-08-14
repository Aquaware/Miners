# -*- coding: utf-8 -*-

from CalendarTime import DTime, DeltaHour, DeltaDay, toNaive, toDateTimeList
import numpy as np
import pandas as pd


TIME = 'time'
OHLC = ['open', 'high', 'low', 'close'] 
OHLCV = ['open', 'high', 'low', 'close', 'volume']
PV = ['price', 'volume']

DATA_TYPE_PANDAS = 0
DATA_TYPE_XM = 1

class TimeSeries:
    
    def __init__(self, data, data_type, names=OHLC, index=None):
        values = []
        if data_type == DATA_TYPE_PANDAS:
            time = toDateTimeList(list(data[TIME].values))
            dic = {}
            values = []
            for name in names:
                dic[name] = data[name]
                values.append(data[name])
        elif data_type == DATA_TYPE_XM:
            time = []
            for d in data:
                time.append(toNaive(d[0]))
            values = []
            dic = {}
            for name, i in zip(names, index):
                value = []
                for d in data:
                    value.append(d[i])
                values.append(value)
                dic[name] = value
            
        self.time = time
        self.values = values
        self.dic = dic
        self.length = len(time)
        self.names = names
        return
    
    def data(self, name):
        return self.dic[name]
    
    def dataList(self, names):
        out = []
        for name in names:
            out.append(self.dic[name])
        return out
    
    def minmax(self, names):
        mins = []
        maxs = []
        for name in names:
            mins.append(self.dic[name])
            maxs.append(self.dic[name])
        return [np.min(mins), np.max(maxs)]
    
    
    
    def toDataFrame(self):
        if len(self.names) < 4:
            return None
        data = []
        for i in range(len(self.time)):
            v = [self.time[i]]
            for name in self.names:
                v.append(self.dic[name][i])
            data.append(v)
        df = pd.DataFrame(data= data, columns= ['time'] + self.names)
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
        