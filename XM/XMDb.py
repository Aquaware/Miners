# -*- coding: utf-8 -*-
import os
import sys
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append('../common')
sys.path.append('../private')

import pandas as pd
import pytz
from Postgres import Postgres, Structure
import setting_xm as setting
import account_db as account
from CalendarTime import toNaive, toAware
from TimeSeries import TimeSeries, OHLC, OHLCV

TIME = 'time'
OPEN = 'open'
HIGH = 'high'
LOW = 'low'
CLOSE = 'close'
VOLUME = 'volume'
SPREAD = 'spread'

STOCK = 'stock'
TIMEFRAME = 'timeframe'
TBEGIN = 'tbegin'
TEND = 'tend'

COLUMNS = [TIME, OPEN, HIGH, LOW, CLOSE, VOLUME, SPREAD]
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
MANAGE_TABLE_NAME = 'manage'

def ManageTable(name=MANAGE_TABLE_NAME):
    struct = {STOCK:'varchar(30)', TIMEFRAME:'varchar(10)', TBEGIN:'timestamp', TEND:'timestamp'}
    table = Structure(name, [STOCK, TIMEFRAME], struct)
    return table

def PriceTable(stock, timeframe):
    name = stock + '_' + timeframe
    struct = {TIME: 'timestamp', OPEN:'real', HIGH:'real', LOW:'real', CLOSE:'real', VOLUME:'real', SPREAD:'real'}
    table = Structure(name, [TIME], struct)
    return table

class XMDb(Postgres):
    
    def __init__(self):
        super().__init__(setting.DB_NAME, account.DB_USER, account.DB_PASSWORD, account.DB_PORT)
        pass
    
    def fetchItem(self, table, where=None):
        array = self.fetch(table, where)
        return self.value2dic(table, array)

    def fetchAllItem(self, table, asc_order_column):
        array = self.fetchAll(table, asc_order_column)
        return self.values2dic(table, array)
 
    def value2dic(self, table, values):
        dic = {}
        if len(values) == 0:
            return dic
        for (column, value) in zip(table.all_columns, values[0]):
            if table.typeOf(column) == 'timestamp':
                t1 = value.astimezone(pytz.timezone('Asia/Tokyo'))
                dic[column] = t1
            else:
                dic[column] = value
        return dic
    
    def values2dic(self, table, values):
        dic = {}
        for i in range(len(table.columns)):
            column = table.columns[i]
            d = []
            for v in values:
                d.append(v[i])
            if table.typeOf(column) == 'timestamp':
                dic[column] = self.time2pyTime(d)
            else:
                dic[column] = d
        return dic
    
    def dataTimeRange(self, stock, timeframe):
        table = ManageTable()
        where = {STOCK:stock, TIMEFRAME:timeframe} 
        dic = self.fetchItem(table, where=where)
        return (dic[TBEGIN], dic[TEND])
        
    def priceRange(self, stock, timeframe, begin_time, end_time):
        table = PriceTable(stock, timeframe)
        if begin_time is not None:
            where1 = TIME + " >= cast('" + str(toAware(begin_time)) + "' as timestamp) "
        else:
            where1 = ''
        if end_time is not None:
            where2 = TIME + " <= cast('" + str(toAware(end_time)) + "' as timestamp) "
        else:
            where2 = ''
        if begin_time is not None and end_time is not None:
            where = where1 + ' AND ' + where2
        else:
            where = where1 + where2
            
        items = self.fetchItemsWhere(table, where, TIME)
        time = []
        values = []
        for item in items:
            time.append(toNaive(item[0]))
            values.append(item[1:6])
        return TimeSeries(time, values, OHLCV)
    
    def time2pyTime(self, time_list):
        time = []
        for t in time_list:
            #t0 = datetime.datetime.strptime(tstr, TIME_FORMAT)
            t1 = t.astimezone(pytz.timezone('Asia/Tokyo'))
            time.append(t1)
        return time
# -----
def save(stock, timeframe):
    table = PriceTable(stock, timeframe)
    db = XMDb()
    time_range = db.dataTimeRange(stock, timeframe)
    data = db.fetchAllItem(table, TIME)
    t = data[TIME]
    o = data[OPEN]
    h = data[HIGH]
    l = data[LOW]
    c = data[CLOSE]
    v = data[VOLUME]
    s = data[SPREAD]
    
    d = []
    for tt, oo, hh, ll, cc, vv, ss in zip(t, o, h, l, c, v, s):
        d.append([tt.strftime('%Y-%m-%d %H:%M:%S'), oo, hh, ll, cc, vv, ss])
    df = pd.DataFrame(data=d, columns=COLUMNS)
    df.to_csv('./' + stock + '_' + timeframe + '.csv', index=False)
    
    
    print(time_range)
   
if __name__ == '__main__':
 
    save('US30Cash', 'H4')     
