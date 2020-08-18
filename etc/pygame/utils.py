# -*- coding: utf-8 -*-
#
# Created by Ikuo Kudo  18 August, 2020

import numpy as np
from datetime import datetime, timedelta

MINUTE = 'M';
HOUR = 'H';
DAY = 'D';



def minmaxOfArray(array):
    if len(array) == 0:
        return [np.nan, np.nan]
    
    minvalue = np.nan
    maxvalue = np.nan
    for  i  in range(len(array)):
        if np.isnan(array[i]): 
            if np.isnan(minvalue) or np.isnan(maxvalue):
                minvalue = array[i]
                maxvalue = array[i]
            else:
                if array[i] < minvalue:
                    minvalue = array[i]
                if array[i] > maxvalue:
                    maxvalue = array[i]
    return [minvalue, maxvalue]

def separate(value):
    if value == 0.0:
        return [0.0, 0.0]
    
    if value >= 1.0 and value < 10.0:
        return [value, 1.0]
    
    if value >= 10.0:
        for base in range(1, 100):
            v =  value / 10 ** base
            if v < 10.0:
                return [v, 10 ** base]
    else:
        for base in range(1, 100):
            v = value * 10 ** base
            if v >= 1.0:
                return [v, 1.0 / 10 ** base]
    return [0.0, 0.0];

def nice(niceNumbers, value):
    [mantissa, exponent] = separate(value)
    dif = []
    for num in niceNumbers:
        dif.append(np.abs(mantissa - num))
    index = np.argmin(dif)
    return niceNumbers[index] * exponent

def niceRange(a, b, divide):
    niceNumbers = [1.0, 2.0, 2.5, 5.0, 10.0]
    d = np.abs((a - b) / divide)
    division = nice(niceNumbers, d)
    aa = int(a / division) * division
    if aa >= a:
        aa -= division
    bb = int(b / division) * division
    if bb <= b:
        bb += division
    array = []
    for v in range(aa, bb + 1, division):
        if v >= a and v <= b:
            array.append(v)
    return array

def date2Str (date, timeframe):
    [value, unit, minutes] = timeframe
    if unit == DAY:
        format1 = "%m-%d"
        format2 = "%Y"
    elif unit == HOUR:
        format1 = "%m-%d %H"
        format2 = "%Y"
    elif unit == MINUTE:
        format1 = '%H:%M'
        format2 = "%m-%d"
    str1 = dateFormat(date, format1)
    str2 = dateFormat(date, format2)
    return [str1, str2]


def roundValue(value, digit):
    p = 10 ** digit
    return (value * p * 2 + 1) // 2 / p

def nearest1(value, nears):
    dif = []
    for v in nears:
        dif.append(np.abs(value - v))
    index = np.argmin(dif)
    return nears[index]

def nearest2(value, begin, delta):
    difmin = None
    minv = None
    for v in range(begin, begin + 1000 * delta,  delta):
        dif = np.abs(value - v)
        if v == begin:
            difmin = dif
            minv = v
        
        if dif > difmin:
            break       
    return minv

def roundMinute(time, minutes):
    array = []
    for  m in minutes:
        t = datetime(time.year(), time.month(), time.day(), time.hour(), m);
        array.push(t);
        array.push(t - timedelta(hours=1))
        array.push(t + timedelta(hours=1))
    
    dif = []
    for v in array:
        dif.push(np.abs(time.timestamp() - v.timestamp()))
    
    index = np.argmin(dif)
    return array[index]


def roundHour(time, hours):
    array = []
    for h in hours:
        t = datetime(time.year(), time.month(), time.day(), h);
        array.push(t);
        array.push(t - timedelta(days=1))
        array.push(t + timedelta(dayss=1))
    
    dif = []
    for v in array:
        dif.push(np.abs(time.timestamp() - v.timestamp()))
    
    index = np.argmin(dif)
    return array[index]

def roundDay(time, days):
    array = []
    for d in days:
        t = datetime(time.year(), time.month(), d);
        array.push(t);
        array.push(t - timedelta(days=1))
        array.push(t + timedelta(dayss=1))
    
    dif = []
    for v in array:
        dif.push(np.abs(time.timestamp() - v.timestamp()))
    
    index = np.argmin(dif)
    return array[index]    

def niceTimeRange(iMin, iMax, timelist, timeframe, divide):
    [value, unit, minutes] = timeframe
    division = int(iMax / divide)

    if unit == DAY:
        delta = nearest2(division, 10, 10)
        tbegin = timelist[0];
        array = []
        for i in range(0, iMax + 1, int(delta)):
            array.push([i, timelist[i]])
        return array
    
    if unit == MINUTE:
        if value == 1:
            delta = nearest1(division, [5, 10, 15])
            tbegin = roundMinute(timelist[0], [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        else:
            delta = nearest2(division, value * 6, 30)
            tbegin = roundMinute(timelist[0], [0, 15, 30, 45])
        interval = timedelta(minutes=delta)
        
    elif unit == HOUR:
        delta = nearest2(division, value * 6, 12)
        interval = timedelta(hours=delta)
        tbegin = timelist[0] #roundHour(time[0], [0, 4, 8, 12, 16, 20])
        
    array = []
    t = tbegin
    for i in range(division + 1):
        t += interval
        if t >= timelist[-1]:
            array.append([array[-1][0] + delta / value, None])
            break
        
        for j in range(len(timelist)):
            if t == timelist[j]:
                if i == 0:
                    ibefore = j - int(delta / value)
                    if ibefore >= iMin:
                        array.append([ibefore, t - interval])
                    array.append([j, t]);
    return array
