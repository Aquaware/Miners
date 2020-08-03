# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from scipy.signal import argrelmax

UP = 1
DOWN = -1

def detectThrust(ohlcv_array, threshold):
    n = len(ohlcv_array)
    flag = np.zeros(n)
    counts = []
    for i in range(1, n):
        h0 = ohlcv_array[i - 1, 1]
        c1 = ohlcv_array[i, 3]
        if c1 > h0 and (c1 - h0) > threshold:
            flag[i] = UP
            counts.append([UP, i, c1 - h0])
        
        l0 = ohlcv_array[i - 1, 2]
        if c1 < l0 and (l0 - c1) > threshold:
            flag[i] = DOWN
            counts.append([DOWN, i, c1 - l0])
    return (flag, counts, ['ThrustUp(' + str(threshold) + ')', 'ThrustDown(' + str(threshold) + ')'])

def detectRunway(ohlcv_array, width):
    n = len(ohlcv_array)
    flag = np.zeros(n)
    counts = []
    for i in range(width, n - width):
        highs0 = ohlcv_array[i - width: i, 1]
        lows0 = ohlcv_array[i - width: i, 2]
        highs1 = ohlcv_array[i + 1: i + width + 1, 1]
        lows1 = ohlcv_array[i + 1: i + width + 1, 2]
        price = ohlcv_array[i: 3]
        # Up
        if  np.max(highs0) > price and np.min(lows1) > price:
            flag[i] = UP
            counts.append([UP, i, price])
        # Down
        if np.min(lows0) > price and np.max(highs1) > price:
            flag[i] = DOWN
            counts.append([DOWN, i, price])
    return (flag, counts, ['RunwayUp(w=' + str(width) + ')', 'RunwayDown(w=' + str(width) + ')'])

def rangeValue(ohlcv):
    out = ohlcv[:, 3] - ohlcv[:, 2]
    return out

def spike(ohlcv):
    n = len(ohlcv)
    upper = np.zeros(n)
    lower = np.zeros(n)
    for i in range(n):
        if ohlcv[i, 3] > ohlcv[i, 0]:
            upper[i] = ohlcv[i, 1] - ohlcv[i, 3]
            lower[i] = ohlcv[i, 2] - ohlcv[i, 0]
        else:
            upper[i] = ohlcv[i, 1] - ohlcv[i, 0]
            lower[i] = ohlcv[i, 2] - ohlcv[i, 3]
    return (upper, lower)

def isInclude(range1, range2):
    if range1[0] > range1[1]:
        h1 = range1[0]
        l1 = range1[1]
    else:
        h1 = range1[1]
        l1 = range1[0]
        
    if range2[0] > range2[1]:
        h2 = range2[0]
        l2 = range2[1]
    else:
        h2 = range2[1]
        l2 = range2[0]
    
    if l2 >= l1 and h2 <= h1:
        return True
    
    if l2 >= l1 and l2 <= h1:
        return True
    
    if h2 >= l1 and h2 <= h1:
        return True
    return False
    
def distribution(ohlcv, band_width):
    l = ohlcv[:, 2]
    h = ohlcv[:, 1]
    begin = np.min(l)
    end = np.max(h)
    step = band_width / 2
    size = int((end - begin) / step + 0.5)
    steps = np.zeros(size)
    for i in range(size):
        steps[i] = begin + i * step
    counts = np.zeros(size)
    for i in range(size):
        center = steps[i]
        lower = center - band_width
        upper = center + band_width
        count = 0
        for o, h, l, c, v in ohlcv:
            if isInclude([lower, upper], [o, l]):
                count += 1
        counts[i] = count
    return (steps, counts)

def peakPrices(ohlc, delta, max_size, price_low, price_high):
    prices, cnts = priceDistribution(ohlc, delta)
    if len(cnts) == 0:
        return []
    
    center = []
    counts = []
    for price, c in zip(prices, cnts):
        if price >= price_low and price <= price_high:
            center.append(price)
            counts.append(c)
    
    indices = argrelmax(np.array(counts))
    
    count_values = []
    peak_indices = []
    for index in indices[0]:
        peak_indices.append(index)
        count_values.append(counts[index])
    
    rank = ranking(count_values)
    count = 0
    out = []
    for r in range(1, max_size):
        for i in range(len(rank)):
            if rank[i] == r:
                index = peak_indices[i]
                out.append(center[index])
                count += 1
                if count > max_size:
                    break
    return out

def priceDistribution(ohlc, delta):  
    o = ohlc[:, 0]
    h = ohlc[:, 1]
    l = ohlc[:, 2]
    c = ohlc[:, 3]
    try:
        d = np.max([o, c]) - np.min([o , c])
    except:
        return ([], [])
    
    prices = np.arange(np.min([o, c]), np.max([o, c]) + 1, delta)
    size = len(prices) - 1
    counts = np.zeros(size)
    for oo, cc in zip(o, c):
        if oo >= cc:
            upper = oo
            lower = cc
        else:
            upper = cc
            lower = oo
        begin = -1
        for i in range(len(prices)):
            if prices[i] >= lower:
                begin = i
                break
        if begin < 0:
            begin = 0
        end = -1
        for i in range(len(prices) - 1, -1, -1):
            if prices[i] < upper:
                end = i
                break
        if end < 0 or end >= len(counts):
            end = len(counts) - 1
            
        #print(lower, begin, upper, end)    
        for i in range(begin, end + 1):
            counts[i] += 1
    
    center = []
    for i in range(1, size + 1):
        center.append((prices[i - 1] + prices[i]) / 2)       
    return (center, counts)
    

def continueFilter(vector, value, min_width, rate):
    if min_width < 3:
        return None
    
    n = len(vector)
    status = np.zeros(n)
    for i in range(n):
        if vector[i] == value:
            status[i] = 1
    flag = status.copy()
    for i in range(min_width - 1, n - min_width):
        d = status[i - min_width + 1 : i + 1]
        if np.sum(d) >= min_width * rate:
            for j in range(i - min_width + 2, i):
                flag[j] = 1
    begin = -1
    terms = []
    for i in range(n):
        if flag[i] > 0:
            if begin < 0:
                begin = i
        else:
            if begin >= 0:
                terms.append([begin, i - 1, i - begin])
                begin = -1
    if begin > 0:
        terms.append([begin, n - 1, n - begin])
    return terms

def seekValue( vector, start, value):
    for i in range(len(vector)):
        if vector[i] == value:
            return i
    return -1

def crossPoint(ohlc, values, band_width):
    o = ohlc[:, 0]
    c = ohlc[:, 3]
    points = []
    n = len(o)
    for value in values:
        state = np.zeros(n)
        for i in range(n):
            if value < (c[i] - band_width) and value < (o[i] - band_width):
                state[i] = -1
            elif value > (c[i] + band_width) and value > (o[i] + band_width):
                state[i] = 1
                
        index = seekValue(state, 0, -1)
        while(index >= 0):
            index = seekValue(state, index + 1, 1)
            if index > 0:
                points.append([UP, index, value])
                index = seekValue(state, index + 1, -1)
                
        index = seekValue(state, 0, 1)
        while(index >= 0):
            index = seekValue(state, index + 1, -1)
            if index > 0:
                points.append([DOWN, index, value])
                index = seekValue(state, index + 1, 1)
    return points

def integration(vector):
    out = np.zeros(len(vector))
    s = 0
    for i in range(len(vector)):
        s += vector[i]
        out[i] = s
    return out

def movingAverage(vector, window):
    half = int(window / 2)
    n = len(vector)
    out = np.full(n, np.nan)
    for i in range(half, n - half):
        d = vector[i - half: i - half + window]
        out[i] = np.mean(d)
    return out

def ranking(values):
    d = pd.Series(values)
    ranked = d.rank(method="min", ascending=False)
    l = []
    for v in ranked.values:
        l.append(int(v))
    return l


if __name__ == "__main__":
    
    data = [ 1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    ma1 = movingAverage(data, 4)
    ma2 = movingAverage(data, 5)
        
    
    