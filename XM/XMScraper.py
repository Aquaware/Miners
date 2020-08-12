# -*- coding: utf-8 -*-
import pandas as pd
from MT5Bind import MT5Bind
from XMDb import XMDb, ManageTable, PriceTable
from MT5Bind import nowJst, deltaMinute
import setting_xm as setting

class XMScraper:
    def __init__(self, stock):
        self.stock = stock
        pass
    
    def buildDb(self, timeframe):
        server = MT5Bind(self.stock)
        data = server.scrape(timeframe)
        if len(data) > 0:
            self.uploadFirst(timeframe, data)
            begin = data[0][0]
            end = data[-1][0]
            print(timeframe, 'length:', len(data), 'begin:', begin, 'end:', end)
        return
    
    def uploadFirst(self, timeframe, values):
        table = PriceTable(self.stock, timeframe)
        db = XMDb()
        db.create(table)
        ret = db.insert(table, values)
        if ret == False:
            print('DB Insert error1')
            return False
        stored = db.fetchAllItem(table, 'time')
        times = stored['time']
        begin = values[0][0]
        end = values[-1][0]
        
        if times[0] != begin or times[-1] != end:
            print('DB Insert error3')
            return False
        
        manage = ManageTable()
        ret = db.create(manage)
        if ret == False:
            print('Management DB create Error!')
            return False
        ret = db.update(manage, [self.stock, timeframe, begin, end])
        if ret == False:
            print('Management DB update Error!')
            return False
        
        return True
    
    def update(self, timeframe):
        begin, end = self.rangeOfTime(timeframe)
        if end is None:
            return
        t0 = end + setting.deltaTimeFrame(timeframe)
        t1 = nowJst() - deltaMinute(1)
        server = MT5Bind(self.stock)
        data = server.scrapeRange(timeframe, t0, t1)
        if len(data) == 0:
            return -1
        
        
        if len(data) == 1:
            return 0
        
        # remove last data
        data = data[:len(data) - 1]
        
        table = PriceTable(self.stock, timeframe)
        db = XMDb()
        ret = db.insert(table, data)
        if ret == False:
            print('DB Insert error1')
            return -1
        stored = db.fetchAllItem(table, 'time')
        times = stored['time']
        tbegin = times[0]
        tend = times[-1]
        
        manage = ManageTable()
        db = XMDb()
        ret = db.create(manage)
        if ret == False:
            print('Management DB create Error!')
            return -1
        ret = db.update(manage, [self.stock, timeframe, None, tend])
        if ret == False:
            print('Management DB update Error!')
            return -1
        
        return len(data)
        
    def rangeOfTime(self, timeframe):
        db = XMDb()
        manage = ManageTable()
        item = db.fetchItem(manage, {'stock':self.stock, 'timeframe':timeframe})
        if len(item) == 0:
            print('Management DB update Error!')
            return (None, None)
        begin = item['tbegin']
        end = item['tend']
        return (begin, end)    
            
# ------

def build(stocks):
    
    for stock in stocks:
        db = XMScraper(stock)
        timeframes = setting.timeframeSymbols()
        for timeframe in timeframes:
            db.buildDb(timeframe)
            begin, end = db.rangeOfTime(timeframe)
            print('Done...', stock, timeframe, begin, end)
    pass


def update():
    for stock in setting.indexStock() + setting.fx() + setting.comodity():
        db = XMScraper(stock)
        timeframes = setting.timeframeSymbols()
        for timeframe in timeframes:
            n = db.update(timeframe)
            begin, end = db.rangeOfTime(timeframe)
            print('['+stock + ' ' +  timeframe + ']', 'n=', n, begin, end)
    print('Done')
            
def test():
    stock = 'US30Cash'
    timeframe = 'M1'
    db = XMDbHandler(stock)
    db.update(timeframe)
    begin, end = db.rangeOfTime(timeframe)
    print('Done...', stock, timeframe, begin, end)
            
def test1():
    t1 = nowJst() 
    t0 = t1 - deltaMinute(30)
    server = MT5Bind('US30Cash')
    data = server.scrapeRange('M5', t0, t1)
    if len(data) > 0:
        print(data)

def save(stock, timeframe):
    server = MT5Bind(stock)
    dic = server.scrapeWithDic(timeframe)
    values = dic['data']
    d = []
    for value in values:
        d.append([value['time'], value['open'], value['high'], value['low'], value['close']])
    df = pd.DataFrame(data=d, columns=['Time', 'Open', 'High', 'Low', 'Close'])
    df.to_csv('./' + stock + '_' + timeframe + '.csv', index=False)
    
    
if __name__ == '__main__':
    #build(setting.fx() + setting.indexStock() + setting.comodity())
    update()
    #test()
    #save('US30Cash', 'D1')


        
