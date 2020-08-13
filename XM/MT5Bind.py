# -*- coding: utf-8 -*-
import sys
sys.path.append("../private")
sys.path.append("../common")

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta, timezone
import calendar
import setting_xm as setting
import pytz
from TimeSeries import TimeSeries, OHLC, OHLCV


TIMEZONE_TOKYO = pytz.timezone('Asia/Tokyo')

def dayOfLastSunday(year, month):
    '''dow: Monday(0) - Sunday(6)'''
    dow = 6
    n = calendar.monthrange(year, month)[1]
    l = range(n - 6, n + 1)
    w = calendar.weekday(year, month, l[0])
    w_l = [i % 7 for i in range(w, w + 7)]
    return l[w_l.index(dow)]

def nowUtc():
    now = datetime.now(pytz.timezone('UTC'))
    return now

def nowXm():
    now = nowUtc()
    zone = xmTimezone(now)
    return datetime.now(zone)

def nowJst():
    now = datetime.now(TIMEZONE_TOKYO)
    return now

def toJst(time):
    return time.astimezone(TIMEZONE_TOKYO)

def toXm(time):
    zone = xmTimezone(time)
    return time.astimezone(zone)

def utcTime(year, month, day, hour, minute):
    local = datetime(year, month, day, hour, minute)
    return pytz.timezone('UTC').localize(local)

def jstTime(year, month, day, hour, minute):
    local = datetime(year, month, day, hour, minute)
    return TIMEZONE_TOKYO.localize(local)

def xmTime(year, month, day, hour, minute):
    t0 = utcTime(year, month, day, hour, minute)
    timezone = xmTimezone(t0)
    t = datetime(year, month, day, hour, minute, tzinfo=timezone)
    return t

def timestamp2jst(timestamp):
    t1 = datetime.utcfromtimestamp(timestamp)
    zone = timezone(timedelta(hours=9), name='XM')
    t2 = t1.astimezone(zone)
    t3 = xm2jst(t2)
    return t3

def isXmSummerTime(date_time):
    day0 = dayOfLastSunday(date_time.year, 3)
    tsummer0 = utcTime(date_time.year, 3, day0, 0, 0)
    day1 = dayOfLastSunday(date_time.year, 10)
    tsummer1 = utcTime(date_time.year, 10, day1, 0, 0)
    if date_time > tsummer0 and date_time < tsummer1:
        return True
    else:
        return False
def xmTimezone(date_time):
    if isXmSummerTime(date_time):
        # summer time
        h = 3
    else:
        h = 2
    return timezone(timedelta(hours=h), name='XM')

def xm2jst(time):
    if isXmSummerTime(time):
        t = time + deltaHour(6)
    else:
        t = time + deltaHour(7)
    return toJst(t)

def jst2xm(time):
    if isXmSummerTime(time):
        t = time - deltaHour(6)
    else:
        t = time - deltaHour(7)
    return toXm(t)

def deltaDay(days):
    return timedelta(days=days)

def deltaHour(hours):
    return timedelta(hours=hours)

def deltaMinute(minutes):
    return timedelta(minutes=minutes)

def delta(timeframe, size):
    value, unit = setting.timeframeTime(timeframe)
    if unit == setting.MINUTE:
        return deltaMinute(value * size)
    elif unit == setting.HOUR:
        return deltaHour(value * size)
    elif unit == setting.DAY:
        return deltaDay(value * size)
    return None
def time2str(time):
    s = str(time.year) + '/' + str(time.month) + '/' + str(time.day)
    s += ' ' + str(time.hour) + ':' + str(time.minute) + ':' + str(time.second)
    return s
    
    
class MT5Bind:
    def __init__(self, stock):
        self.stock = stock
        if not mt5.initialize():
            print("initialize() failed")
            mt5.shutdown()
        #print('Version: ', mt5.version())
        pass    
    
    def close(self):
        mt5.shutdown()
        pass

    def getPrices(self, timeframe, begin_time, end_time):
        t0 = toXm(begin_time)
        t1 = toXm(end_time)
        if setting.timeframeUnit(timeframe) == setting.DAY:
            return self.getDay(timeframe, t0, t1)        
        elif setting.timeframeUnit(timeframe) == setting.HOUR:
            return self.getHour(timeframe, t0, t1)
        elif setting.timeframeUnit(timeframe) == setting.MINUTE:
            return self.getMinute(timeframe, t0, t1)

    def getTicks(self, time, size):
        t = toXm(time)
        ticks = mt5.copy_ticks_from(self.stock, t, size, mt5.COPY_TICKS_ALL) 
        data = []
        for tick in ticks:
            t = tick.time
            bid = tick.bid
            ask = tick.ask
            data.append([t, bid, ask])
        return data
    
    def getDay(self, timeframe, begin_time, end_time):
        begin = xmTime(begin_time.year, begin_time.month, begin_time.day, 0, 0)
        end = xmTime(end_time.year, end_time.month, end_time.day, 0, 0)
        data = mt5.copy_rates_range(self.stock, setting.timeframeConstant(timeframe), begin, end) 
        return self.convert2Array(data)
    
    def cutUnderHour(self, time, offset):
        t = xmTime(time.year, time.month, time.day, time.hour, 0) + deltaHour(1)
        return t
    
    def getHour(self, timeframe, begin_time, end_time):
        begin = self.cutUnderHour(begin_time, 0)
        end = self.cutUnderHour(end_time, 1)
        data = mt5.copy_rates_range(self.stock, setting.timeframeConstant(timeframe), begin, end) 
        return self.convert2Array(data)
    
    def convert2Array(self, data):
        out = []
        if data is None:
            return []
        for d in data:
            value = list(d)
            time = timestamp2jst(value[0])
            out.append([time] + value[1:7])
        return out
        
    def roundMinute(self, time, timeframe):
        dt = setting.timeframeTime(timeframe)
        t = xmTime(time.year, time.month, time.day, time.hour, time.minute)
        t += deltaMinute(dt[0] - 1)
        minute = int(t.minute / dt[0]) * dt[0]
        t1 = xmTime(t.year, t.month, t.day, t.hour, minute)
        return t1

    def getMinute(self, timeframe, begin_time, end_time):
        begin = self.roundMinute(begin_time, timeframe)
        end = self.roundMinute(end_time, timeframe)
        tf = setting.timeframeConstant(timeframe)
        data = mt5.copy_rates_range(self.stock, tf , begin, end) 
        return self.convert2Array(data)
     
    def scrape(self, timeframe, size=99999):
        d = mt5.copy_rates_from_pos(self.stock, setting.timeframeConstant(timeframe) , 0, size) 
        data = self.convert2Array(d)
        return data
    
    def scrapeWithTimeSeries(self, timeframe, size=99999):
        d = mt5.copy_rates_from_pos(self.stock, setting.timeframeConstant(timeframe) , 0, size) 
        data = self.convert2Array(d)
        return self.toTimeSeries(data)
    
    def scrapeWithDic(self, timeframe, size=99999):
        d = mt5.copy_rates_from_pos(self.stock, setting.timeframeConstant(timeframe) , 0, size) 
        data = self.convert2Array(d)
        array = self.toDicArray(data)
        dic = {}
        dic['name'] = self.stock
        dic['timeframe'] = timeframe
        dic['length'] = len(data)
        dic['data'] = array
        return dic
    
    def scrapeRange(self, timeframe, begin_jst, end_jst):
        # タイムゾーンをUTCに設定する
        timezone = pytz.timezone("Etc/UTC")
        # create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
        
        if isXmSummerTime(end_jst):
            delta = deltaHour(6)
        else:
            delta = deltaHour(7)
        utc_from = datetime(begin_jst.year, begin_jst.month, begin_jst.day, begin_jst.hour, begin_jst.minute, 0, tzinfo=timezone) - delta
        utc_to = datetime(end_jst.year, end_jst.month, end_jst.day, end_jst.hour, end_jst.minute, 0, tzinfo=timezone) - delta
        d = mt5.copy_rates_range(self.stock, setting.timeframeConstant(timeframe) , utc_from, utc_to) 
        data = self.convert2Array(d)
        return data
    
    def scrapeTicks(self, timeframe, from_jst, size=100000):
        # タイムゾーンをUTCに設定する
        timezone = pytz.timezone("Etc/UTC")
        # create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
        
        if isXmSummerTime(from_jst):
            delta = deltaHour(6)
        else:
            delta = deltaHour(7)
        utc_from = datetime(from_jst.year, from_jst.month, from_jst.day, from_jst.hour, from_jst.minute, 0, tzinfo=timezone) - delta
        d = mt5.copy_ticks_from(self.stock, setting.timeframeConstant(timeframe) , utc_from, size, mt5.COPY_TICKS_ALL) 
        data = self.convert2Array(d)

        #df = pd.DataFrame(data = out, columns=['Time', 'Bid', 'Ask'])
        #df.to_csv(market + '_' + str(year) +'-' + str(month) + '-' + str(day) + '.csv', index=False)
        return data
    
    def toTimeSeries(self, data, data_type=OHLC):
        time = []
        values = []
        for v in data:
            time.append(v[0])
            if data_type == OHLCV:
                values.append(v[1:6])
            elif data_type == OHLC:
                values.append(v[1:5])
        return TimeSeries(time, values, names=data_type)

    def toDicArray(self, data, data_type=OHLC):
        array = []
        for v in data:
            dic = {}
            dic['time'] = time2str(v[0])
            for i in range(len(data_type)):
                name = data_type[i]
                dic[name] = v[i + 1]
            array.append(dic)
        return array

    def toDi2(self, data, data_type=OHLC):
        time = []
        dic = {}
        for v in data:
            time.append(time2str(v[0]))
        dic['time'] = time
        for i in range(len(data_type)):
            values = []
            for v in data:
                values.append(v[i + 1])
            dic[data_type[i]] = values
        return dic
    
# -----
    
def test0():
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
    print('Version:', mt5.version())    

    t1 = nowXm() 
    t0 = t1 - deltaMinute(5)
    values = mt5.copy_rates_range("US30Cash", mt5.TIMEFRAME_M1, t0, t1)
    for value in values:
        t = pd.to_datetime(value[0], unit='s')
        pytime = t.to_pydatetime()
        print(t, pytime, toXm(pytime), value)

    mt5.shutdown()
    pass


def test():
    # connect to MetaTrader 5
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
    print('Version:', mt5.version())
    
    
    #dji = mt5.copy_rates_range('US30Cash', mt5.TIMEFRAME_M30, Now() - DeltaDay(2), Now())
    #print(dji)
 
    # request 1000 ticks from EURAUD
    euraud_ticks = mt5.copy_ticks_from("US30Cash", datetime(2020,4,17,23), 1000, mt5.COPY_TICKS_ALL)
    # request ticks from AUDUSD within 2019.04.01 13:00 - 2019.04.02 13:00
    audusd_ticks = mt5.copy_ticks_range("AUDUSD", datetime(2020,1,27,13), datetime(2020,1,28,13), mt5.COPY_TICKS_ALL)
 
    # get bars from different symbols in a number of ways
    eurusd_rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_M1, datetime(2020,1,28,13), 1000)
    eurgbp_rates = mt5.copy_rates_from_pos("EURGBP", mt5.TIMEFRAME_M1, 0, 1000)
    eurcad_rates = mt5.copy_rates_range("EURCAD", mt5.TIMEFRAME_M1, datetime(2020,1,27,13), datetime(2020,1,28,13))
    #print(eurusd_rates)
    # shut down connection to MetaTrader 5
    mt5.shutdown()
    return

def test1():
    server = MT5Bind('US30Cash')
    t1 = nowXm()
    t0 = t1 - deltaDay(1)
    data = server.getPrices('M1',t0, t1)
    server.close()  
    print('T0=', t0, xm2jst(t0))
    print('T1=', t1, xm2jst(t1))
    for d in data:
        print(d)
    print('n=', len(data))
  
    
    
def test2(stock, timeframe):
    server = MT5Bind(stock)
    data = server.scrape(timeframe, size=100)
    server.close()  
    print(stock)
    for d in data:
        print(d)
    print('n=', len(data))
    
def test3():
    server = MT5Bind('US30Cash')
    t0 = jstTime(2019, 8, 5, 7, 0)
    t1 = jstTime(2019, 8, 6, 5, 0)
    t0 = server.roundMinute(t0, 'M5')
    print(t0, t1)
    t1 = server.roundMinute(t1, 'M5')
    
    data = server.scrapeRange('M5', t0, t1)
    server.close()
    print(data)
    
    
def test4():
    
    now = nowUtc()
    jst = toJst(now)
    xm = toXm(now)
    print('JST', jst)
    print('XM', nowXm())
    print('JST2', toJst(now))
    
    jst = jstTime(2020, 4, 8, 22, 13)
    print('XM2', toXm(jst))
    
    
def test5(size):
    server = MT5Bind('US30Cash')
    d =  server.scrape('M5', size=size) 
    print(d)
    
def test6():
    server = MT5Bind('US30Cash')
    jst = nowJst() - deltaHour(1)
    d =  server.scrapeTicks('M5', jst, size=100) 
    print(d)
    
if __name__ == "__main__":
    test3()