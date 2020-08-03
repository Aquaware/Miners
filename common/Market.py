# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime
import sqlite3
import os
import glob
import shutil
import zipfile

#from plotly.offline import iplot
#from plotly import figure_factory as FF
import Graph
import CalendarTime
import matplotlib.dates as mdates

#import SQLite
import FileUtility as fileutil
import Filters
import Parameters


COLUMNS = ['time', 'open', 'high', 'low', 'close', 'volume']
UNIT_MINUTE = 'MINUTE'
UNIT_HOUR = 'HOUR'
UNIT_DAY = 'DAY'


def DeltaDay(days):
    return datetime.timedelta(days=days)

def DeltaHour(hours):
    return datetime.timedelta(hours=hours)

def DeltaMinute(minutes):
    return datetime.timedelta(minutes=minutes)

def DTime(year, month, day, hour, minute):
    return datetime.datetime(year, month, day, hour, minute)

def indexOfTime(times, time):
    index = -1
    count = 0
    for t in times:
        tpy = t.to_pydatetime()
        tt = DTime(tpy.year, tpy.month, tpy.day, time.hour, time.minute)
        if tpy >= tt:
            index = count
            break
        count += 1
    return index
    
def timeRangeFilter(df, time_range):
    df0 = df[df.index >= time_range[0]]
    df1 = df0[df0.index <= time_range[1]]
    return df1
    
def timeZoneFilter(df, time_range):
    time = pd.to_datetime(df.index)
    values = df.values.tolist()
    t_out = []
    data = []
    for t, value in zip(time, values):
        if isInRange(t, time_range):
            data.append(value)
            t_out.append(t)
    out = pd.DataFrame(data=data, columns = df.columns, index=t_out)
    return out

def isInRange(time, time_range):
    if time_range[0] < time_range[2]:
        tbegin = DTime(time.year, time.month, time.day, time_range[0], time_range[1])
        tend = DTime(time.year, time.month, time.day, time_range[2], time_range[3])
        if time >= tbegin and time <= tend:
            return True
    else:
        tbegin = DTime(time.year, time.month, time.day, time_range[0], time_range[1])
        tend = DTime(time.year, time.month, time.day, 23, 59, 59)
        if time >= tbegin and time <= tend:
            return True
        tbegin = DTime(time.year, time.month, time.day, 0, 0)
        tend = DTime(time.year, time.month, time.day, time_range[2], time_range[3])
        tend += datetime.timedelta(days = 1)
        if time >= tbegin and time <= tend:
            return True
    return False

def baseTime(time, time_range):
    tbegin = DTime(time.year, time.month, time.day, time_range[0], time_range[1])
    tend = DTime(time.year, time.month, time.day, time_range[2], time_range[3])
    if tend < tbegin:
        tend += datetime.timedelta(days=1)
    return (tbegin, tend)

def timeZoneArrange(df, time_range):
    time = pd.to_datetime(df.index)
    if len(time) == 0:
        return (None, None)
    
    values = df.values.tolist()
    tbegin = baseTime(time[0], time_range)
    t0 = tbegin[0]
    dfs = []
    t_out= []
    data = []
    tbase = None
    old_dates = []
    old_date = None
    for t, value in zip(time, values):
        if tbase is None:
            tbase = baseTime(t, time_range)
        if t > tbase[1]:
            if len(data) > 0:
                df = pd.DataFrame(data= data, columns=df.columns, index = t_out)
                old_dates.append(old_date)
                dfs.append(df)
                t_out = []
                data = []
                old_date = None
            tbase = baseTime(t, time_range)
        else:
            the_time = pd.datetime(t0.year, t0.month, t0.day, t.hour, t.minute)
            if the_time < t0:
                the_time += datetime.timedelta(days=1)
            t_out.append(the_time)
            if old_date is None:
                old_date = t
            data.append(value)
            
    return (dfs, old_dates)

def normalize(df):
    dic = {}
    for column in df.columns:
        s = df[column]
        if s.dtype == 'float64' or s.dtype == 'int64':
            norm = np.array(s.values.tolist()) / s[0]
            dic[column] = norm
        else:
            dic[column] = s.values.tolist()
    df = pd.DataFrame(data = dic, index = df.index)
    return df

class Markets:
    
    def __init__(self, name,  interval, unit, marketss):
        self.name = name
        self.interval = interval
        self.unit = unit
        df, columns = self.compose(marketss)
        self.df = df
        self.columns = columns
        pass
 
    def compose(self, markets):
        dfs = []
        value_columns = {}
        for market in markets:
            df = market.df
            dic = {}
            for i in range(1, len(COLUMNS)):
                column = COLUMNS[i]
                name = market.name + '.' + column
                dic[column] = name
                value_columns[name] = [market.name, column]
            df = df.rename(columns=dic)
            dfs.append(df)
        df1 = pd.concat(dfs, axis=1)
        keys = list(value_columns.keys())
        df2 =df1[keys]
        df2['time'] = df2.index
        columns = ['time'] + keys
        out = df2[columns]
        return (out, value_columns)
    
class Market:
    
    def __init__(self, name, interval, unit, is_volume):
        self.name = name
        self.interval = interval
        self.unit = unit
        self.is_volume = is_volume
        self.df = pd.DataFrame(columns = COLUMNS)
        pass
    
    def setDataFrame(self, df):
        self.df = df
            
    def beginTime(self):
        t = self.df.iloc[0].time
        return t
    
    def endTime(self):
        t = self.df.iloc[-1].time
        return t
    
    def timeRangeFilter(self, begin, end):
        d0 = self.df[self.df['time'] >= begin]
        d1 = d0[d0['time'] <= end]
        return d1
    
    def tohlcvList(self):
        times = self.pytime()
        #times = self.df['time'].strftime('%Y-%m-%d %H:%M:%S')
        oo = self.df['open'].values.tolist()
        hh = self.df['high'].values.tolist()
        ll = self.df['low'].values.tolist()
        cc = self.df['close'].values.tolist()
        vv = np.zeros(len(oo))
        data = []
        for t, o, h, l, c, v in zip(times, oo, hh, ll, cc, vv):
            data.append([t, o, h, l, c, v])
        return data
    
    def tohlcList(self):
        times = self.pytime()
        #times = self.df['time'].strftime('%Y-%m-%d %H:%M:%S')
        oo = self.df['open'].values.tolist()
        hh = self.df['high'].values.tolist()
        ll = self.df['low'].values.tolist()
        cc = self.df['close'].values.tolist()
        data = []
        for t, o, h, l, c in zip(times, oo, hh, ll, cc):
            data.append([t, o, h, l, c])
        return data
    
    def ohlcArray(self):
        o = self.df['open'].values.tolist()
        h = self.df['high'].values.tolist()
        l = self.df['low'].values.tolist()
        c = self.df['close'].values.tolist()
        data = [o, h, l, c]
        return np.array(data).T
    
    def ohlcvArray(self):
        o = self.df['open'].values.tolist()
        h = self.df['high'].values.tolist()
        l = self.df['low'].values.tolist()
        c = self.df['close'].values.tolist()
        if self.is_volume:
            v = self.df['volume'].values.tolist()
        else:
            v = np.zeros(len(o))
        data = [o, h, l, c, v]
        return np.array(data).T
    
    def ohlc(self):
        o = self.df['open'].values.tolist()
        h = self.df['high'].values.tolist()
        l = self.df['low'].values.tolist()
        c = self.df['close'].values.tolist()
        return [o, h, l, c]
    
    def length(self):
        return len(self.df)
    
    def pdtime(self):
        return self.df.time
    
    def pytime(self):
        times = []
        for time in self.df.time:
            t = time.to_pydatetime()
            times.append(t)
        return times
    
    def timeStr(self, form = '%Y-%m-%d %H:%M:%S'):
        return self.df['time'].strftime(form)
    
    def tohlc(self):
        return [self.df.time, self.df.open, self.df.high, self.df.low, self.df.close]
    
    def importFromSQLite(self, db_filepath, table_name):
        db = SQLite.SQLite(db_filepath)
        df = db.fetch(table_name)
        self.setDataFrame(df)
        return df
        
    def importFromCsv(self, filepath):
        df0 = pd.read_csv(filepath, encoding = 'shiftjis')
        df = self.convert(df0, self.str2datetime1)
        self.df = df
        pass        
    
    def importClickSecFiles(self, file_list):
        for file in file_list:
            df = self.importClicSecFile(file)
            print(len(df), '... done')
            self.df = self.df.append(df, ignore_index=True)
        print('<<< end')
        pass
    
    def exportToSQLight(self, filepath, table_name):
        db = SQLite.SQLite(filepath)
        db.create(table_name)
        db.insert(table_name, self.df.values)
        pass
    
    def convert(self, df, func):
        tlist = df.iloc[:, 0].values.tolist()
        time = []
        for t in tlist:
            tt = func(str(t))
            time.append(tt)
        values = {}
        for i in range(len(COLUMNS)):
            column = COLUMNS[i]
            if i == 0:
                values[column] = time
            else:
                if self.is_volume == False and i == len(COLUMNS) -1:
                    values[column] = np.zeros(len(time)).tolist()
                else:
                    values[column] = df.iloc[:, i].values.tolist()
        out = pd.DataFrame(data = values, columns =COLUMNS, index = time)
        return out
            
    def str2datetime1(self, text):
        t = datetime.datetime.strptime(text, '%Y/%m/%d %H:%M:%S')
        return t
    
    def str2datetime2(self, text):
        s = text[0:4] + '-' + text[4:6] + '-' + text[6:8] + ' ' + text[8:10] + ':' + text[10:12]
        return pd.to_datetime(s)
        
    # for cfd
    def importClicSecFile(self, filepath):
        df0 = pd.read_csv(filepath, encoding='shiftjis')
        table = df0.values.tolist()
        df = self.tableToDf(table)
        return df

    def tableToDf(self, table):
        out = pd.DataFrame(columns = COLUMNS)
        for data in table:
            dic = {}
            if type(data[0]) is int or type(data[0]) is float:
                t = self.str2datetime2(str(int(data[0])))
            else:
                t = self.str2datetime1(str(data[0]))
            dic[COLUMNS[0]] = t
            dic[COLUMNS[1]] = float(data[1])
            dic[COLUMNS[2]] = float(data[2])
            dic[COLUMNS[3]] = float(data[3])
            dic[COLUMNS[4]] = float(data[4])
            if self.is_volume:
                dic[COLUMNS[5]] = float(data[5])
            else:
                dic[COLUMNS[5]] = 0.0
            out = out.append(pd.Series(dic), ignore_index = True)
        return out

    def roundTime(self, time, interval, unit):
        if unit == UNIT_MINUTE:
            t = datetime.datetime(time.year, time.month, time.day, time.hour, 0, 0)
        elif unit == UNIT_HOUR:
            t = datetime.datetime(time.year, time.month, time.day, 0, 0, 0)
        elif unit == UNIT_DAY:
            t = datetime.datetime(time.year, time.month, time.day, 0, 0, 0)
            return t
        if t == time:
            return t
        
        while t < time:
            if unit == UNIT_MINUTE:
                t += datetime.timedelta(minutes = interval)
            elif unit == UNIT_HOUR:
                t += datetime.timedelta(hours = interval)
        return t
    
    def candlePrice(self, time, data):
        o = data[0][0]
        c = data[-1][3]
        h = None
        l = None
        v = 0
        for d in data:
            v += d[4]
            if h is None:
                h = d[1]
                l = d[2]
            else:
                if d[1] > h:
                    h = d[1]
                if d[2] < l:
                    l = d[2]
        return [time, o, h, l, c, v]
    
    def resample(self, interval, unit):
        current_time = None
        table = self.df[['time', 'open', 'high', 'low', 'close', 'volume']].values.tolist()
        out = []
        data = []
        times = []
        for d in table:
            t = pd.to_datetime(d[0])
            round_t = self.roundTime(t, interval, unit)
            values = d[1:6]
            if current_time is None:
                current_time = round_t
                data = [values]
            else:
                if round_t == current_time:
                    data.append(values)
                else:
                    dd = self.candlePrice(current_time, data)
                    times.append(current_time)
                    out.append(dd)
                    current_time = round_t
                    data = [values]  
        df = pd.DataFrame(out, columns = COLUMNS, index = times)
        p = Market(self.name, interval, unit, self.is_volume)
        p.setDataFrame(df)
        return p
    
    def timeRangeFilter(self, begin, end):
        d0 = self.df[self.df['time'] >= begin]
        d1 = d0[d0['time'] <= end]
        p = Market(self.name, self.interval, self.unit, self.is_volume)
        p.setDataFrame(d1)
        return p
    
    def plotCandleChart(self):
        fig = FF.create_candlestick(self.df.Open, self.df.High, self.df.Low, self.df.Close, dates=self.df.Time)
        iplot(fig)
        return

# ------
        
def importClickSec(name, db_path, data_dir):
    #name = 'audjpy'
    market = Market(name, 1, UNIT_MINUTE, False)
    market.importClickSecFiles(data_dir)
    #path = './data/click_sec/' + name + '.db'
    db = SQLite.SQLite(db_path)
    if os.path.isfile(db_path) == False:
        db.create(name)
    db.insert(name, market.tohlcvList())
    
    #gold.df.to_csv('./data/click_sec/gold2019-1min.csv', index=False)
    pass
    
def openMarket(brand, interval_minutes):
    market = Market(brand, interval_minutes, UNIT_MINUTE, False)
    market.importFromSQLite('./data/click_sec/' + brand + '_' + str(interval_minutes) + 'min.db', brand)
    return market

def convert():
    dji = Market(1)
    dji.importFromCsv('./data/click-sec/dji2019-1min.csv')
    d = dji.resample(15)
    d.df.to_csv('./data/click-sec/dji2019-15min.csv', index=False)
    d = dji.resample(30)
    d.df.to_csv('./data/click-sec/dji2019-30min.csv', index=False)
    
    d = dji.resample(60)
    d.df.to_csv('./data/click-sec/dji2019-1h.csv', index=False)
    d = dji.resample(60 * 4)
    d.df.to_csv('./data/click-sec/dji2019-4h.csv', index=False)
    d = dji.resample(60 * 24)
    d.df.to_csv('./data/click-sec/dji2019-24h.csv', index=False)
    pass


def test():
    dji = Market(30)
    dji.importFromCsv('./data/click-sec/dji2019-30min.csv')
    print('imported data size ...', len(dji.df))
    begin = datetime.datetime(2019, 10, 1)
    end = datetime.datetime(2019, 10, 5)
    #end = dji.endTime()
    print(begin, end)
    d = dji.dfWithTimeRange(begin, end)
    print(len(d))
    
def open_time(brand):
    dji = Market(brand, 1, UNIT_MINUTE, False)
    dji.importFromSQLite('./data/click_sec/'+ brand + '.db', brand)
    
    
    for year in range(2015, 2020):
        month_list = CalendarTime.monthList(2019)
        month = month_list[2: 10]
        for i in range(len(month)):
            df = timeRangeFilter(dji.df, month[i])
            open_range = timeZoneFilter(df, [21, 0, 23, 59])
            dfs, old_dates = timeZoneArrange(open_range, [21, 0, 23, 59])
            c = 0
            lines = []
            fig, ax = Graph.makeFig(1, 1, [12, 8])
            for df, date in zip(dfs, old_dates):
                t = pd.to_datetime(df.index)
                norm = normalize(df)
                y0 = norm['close']
                graph = Graph.Graph(ax)
                graph.plot(t, y0, c, 1)
                lines.append([c, date])
                c += 1
            graph.drawLegend(lines, None)
            graph.setTitle(str(year) + '/' + str(i + 3) , 'Time', 'DJI Close')
            graph.yLimit([0.98, 1.02])
    pass
    
    
def open_time2(brand):
    market = Market(brand, 1, UNIT_MINUTE, False)
    market.importFromSQLite('./data/click_sec/' + brand + '.db', brand)
    print('imported data size ...', len(market.df))
    years = [2016, 2017, 2018, 2019]
    month = [2, 10]
    t0 = DTime(2019, 1, 1, 22, 20)
    t1 = DTime(2019, 1, 1, 22, 50)
    for year in years:
        samples = []
        month_list = CalendarTime.monthList(year)[month[0]:month[1]]
        for i in range(len(month_list)):    
            df = timeRangeFilter(market.df, month_list[i])
            open_range = timeZoneFilter(df, [21, 0, 23, 59])
            dfs, old_dates = timeZoneArrange(open_range, [21, 0, 23, 59])
            if dfs is None:
                continue
            c = 0
            lines = []
            #fig, ax = Graph.makeFig(1, 1, [10, 4])
            for df, date in zip(dfs, old_dates):
                times = pd.to_datetime(df.index)
                norm = normalize(df)
                y0 = norm['close']
                #graph = Graph.Graph(ax)
                #graph.plot(times, y0, c, 2)
                lines.append([c, date])
                
                index0 = indexOfTime(times, t0)
                index1 = indexOfTime(times, t1)
                cl = df['close']
                if index0 >= 0 and index1 >= 0:
                    samples.append([cl[index1] - cl[index0], cl[-1] - cl[index1]])
                c += 1
            #graph.drawLegend(lines, None)
            #graph.setTitle(str(year) + '/' + str(i + 3) , 'Time', brand + ' Close')
            
        if len(samples) > 0:
            x = []
            y = []
            for sample in samples:
                x.append(sample[0])
                y.append(sample[1])
            fig2, ax2 = Graph.makeFig(1, 1, [5, 5])
            graph2 = Graph.Graph(ax2)
            graph2.scatter(x, y, 1, 1)
            graph2.setTitle(str(year), 'initial', 'profit')    
            graph2.xLimit([-300, 300])
            graph2.yLimit([-300, 300])
        
    pass


def test2(name):
    dji = openMarket(name, 5)
    data = dji.tohlcList()
    for t, o, h, l, c in data:
        print(t, o, h, l, c)
    pass

def resample():
    brands = ['audjpy', 'audusd', 'cadjpy', 'chfjpy', 'eurchf', 'eurgbp', 'eurjpy', 'eurusd', 'gbpjpy', 'gbpusd', 'jp225', 'nasdaq', 'nzdjpy', 'spi', 'usdjpy', 'vix']
    #brands = ['us30']
    for brand in brands:
        dji = Market(brand, 1, UNIT_MINUTE, False)
        dji.importFromSQLite('./data/click_sec/' + brand + '_1min.db', brand)
        dji1day = dji.resample(5, UNIT_MINUTE)
        dji1day.exportToSQLight('./data/click_sec/' + brand + '_5min.db', brand)


def arrange():
    brands = ['audjpy', 'audusd', 'cadjpy', 'chfjpy', 'eurchf', 'eurgbp', 'eurjpy', 'eurusd', 'gbpjpy', 'gbpusd', 'jp225', 'nasdaq', 'nzdjpy', 'spi', 'usdjpy', 'vix']
    brands = ['dji']
    for brand in brands:
        dji = Market(brand, 1, UNIT_MINUTE, False)
        dji.importFromSQLite('./data/click_sec/' + brand + '.db', brand)
        dji.exportToSQLight('./data/click_sec/' + brand + '_1min.db')    
    
def importCsv():
    brands = ['audusd', 'cadjpy', 'chfjpy', 'eurchf', 'eurgbp', 'eurjpy', 'eurusd', 'gbpjpy', 'gbpusd', 'jp225', 'nasdaq', 'nzdjpy', 'spi', 'usdjpy', 'vix']
    brands= ['us30']
    root = './data/click_sec/'
    save_dir = root + 'old'
    #os.mkdir(save_dir)
    for brand in brands:
        db_filename = brand + '_1min.db'
        source_path = save_dir + '/' + db_filename
        shutil.move(root + db_filename, source_path)
        market = Market(brand, 1, UNIT_MINUTE, False)
        market.importFromSQLite(source_path, brand)
        file_list = expandZip(brand)
        market.importClickSecFiles(file_list)
        market.exportToSQLight(root + db_filename, brand)
        
        
def expandZip(brand):        
    file_list =  glob.glob('./data/tmp/' + brand + '*.zip', recursive=True)
    data_dir = './data/tmp/' + brand
    os.mkdir(data_dir)
    for path in file_list:
        shutil.move(path, data_dir)
        
    file_list =  glob.glob(data_dir + '/*.zip', recursive=True)
    for path in file_list:
        with zipfile.ZipFile(path) as zf:
            zf.extractall(data_dir)
                
    file_list = glob.glob(data_dir + '/*/' + brand.upper() + '*.csv', recursive=True)
    for path in file_list:
        if path.find('EX') < 0:
            print(path)
    
    return file_list
            
def debug():
    
    market = Market('dji', 1, UNIT_MINUTE, False)
    market.importFromSQLite('./data/click_sec/dji_1min.db', 'dji')
    market.exportToSQLight('./data/click_sec/us30_1min.db', 'us30')
    
    
    
if __name__ == "__main__":
    #debug()
    #importCsv()
    resample()
    #arrange()
    
    #open_time('dji')
    #test2('dji')
    
    #name = 'jp225'
    #data_dir = './data/jp225/'
    #db_path = './data/click_sec/jp225.db'
    #importClickSec(name, db_path, data_dir)
    