# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone

zone = timezone('UTC') 

TIME_FORMAT1 = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT2 = '%Y-%m-%d %H:%M:%S%z'


def DeltaMonth(months):
    return relativedelta(months = months)

def DeltaDay(days):
    return datetime.timedelta(days=days)

def DeltaHour(hours):
    return datetime.timedelta(hours=hours)

def DeltaMinute(minutes):
    return datetime.timedelta(minutes=minutes)

def DTime(year, month, day, hour, minute):
    ja = timezone('Asia/Tokyo')
    return datetime.datetime(year, month, day, hour, minute, tzinfo=ja)

def toAware(time):
    try:
        ja = timezone('Asia/Tokyo')
        t = ja.localize(time)
        return t
    except:
        return time
    
def toNaive(aware_time):
    t = datetime.datetime(aware_time.year, aware_time.month, aware_time.day, aware_time.hour, aware_time.minute, aware_time.second)
    return t

def fromUtcStr(time_str, format=TIME_FORMAT2):
    i = time_str.find('+')
    if i >= 0:
        s1 = time_str[0:i]
        s2 = time_str[i:]
        s = s1 + s2.replace(':', '')
    else:
        s = time_str + '+0900'
    t = datetime.datetime.strptime(s, format)
    return t

def toDateTimeList(str_list):
    out = []
    for s in str_list:
        t = fromUtcStr(s)
        out.append(t)
    return out
    
def Now():
    t = datetime.datetime.now()
    return t

def Today():
    now = Now()
    return DTime(now.year, now.month, now.day, 0, 0)

def Yesterday():
    return Today() - DeltaDay(1)

def Tomorrow():
    return Today() + DeltaDay(1)

def monthList(year):
    month = [  [DTime(year, 1, 1, 0, 0), DTime(year, 1, 31, 23, 59)],
               [DTime(year, 2, 10, 0, 0), DTime(year, 2, 28, 23, 59)],
               [DTime(year, 3, 1, 0, 0), DTime(year, 3, 31, 23, 59)],
               [DTime(year, 4, 1, 0, 0), DTime(year, 4, 30, 23, 59)],
               [DTime(year, 5, 1, 0, 0), DTime(year, 5, 31, 23, 59)],
              [DTime(year, 6, 1, 0, 0), DTime(year, 6, 30, 23, 59)],
              [DTime(year, 7, 1, 0, 0), DTime(year, 7, 31, 23, 59)],
              [DTime(year, 8, 1, 0, 0), DTime(year, 8, 31, 23, 59)],
              [DTime(year, 9, 1, 0, 0), DTime(year, 9, 30, 23, 59)],
              [DTime(year, 10, 1, 0, 0), DTime(year, 10, 31, 23, 59)],
              [DTime(year, 11, 1, 0, 0), DTime(year, 11, 30, 23, 59)],
              [DTime(year, 12, 1, 0, 0), DTime(year, 12, 31, 23, 59)]
             ]
    return month
    