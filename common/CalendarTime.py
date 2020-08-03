# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone

zone = timezone('UTC') 


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

def toNaive(time):
    try:
        ja = timezone('Asia/Tokyo')
        t = ja.localize(time)
        return t
    except:
        return time
    
def toAware(naive_time):
    t = datetime.datetime(naive_time.year, naive_time.month, naive_time.day, naive_time.hour, naive_time.minute, naive_time.second)
    return t

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
    