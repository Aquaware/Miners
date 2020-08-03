# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../XM'))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D
import matplotlib.dates as mdates
from datetime import datetime 

import matplotlib.animation as animation
import Filters

from CalendarTime import DTime, DeltaDay, DeltaHour, DeltaMinute, Today, Now
from MT5Bind import MT5Bind

DATE_FORMAT_TIME = '%H:%M'
DATE_FORMAT_DAY = '%m/%d'
DATE_FORMAT_DAY_TIME = '%m-%d %H:%M'

def awarePytime2naive(time):
    naive = datetime(time.year, time.month, time.day, time.hour, time.minute, time.second)
    return naive

def awarePyTime2Float(time):
    naive = awarePytime2naive(time)
    t = mdates.date2num([naive])
    return t[0]

def awarePyTimeList2Float(aware_pytime_list):
    naives = []
    for time in aware_pytime_list:
        naive = awarePytime2naive(time)
        naives.append(naive)
    return mdates.date2num(naives)


def list2array(values):
    rows = len(values)
    cols = len(values[0])
    a = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            a[r, c] = values[r][c]
    return a
    
class DynamicChartViewer(animation.TimedAnimation):

    def __init__(self, fig, ax, server, timeframe, download_size):
        self.config()
        self.fix = fig
        self.ax = ax
        self.server = server
        self.timeframe = timeframe
        self.download_size = download_size
        
        # data set
        self.length, self.time, self.timef, self.ohlc = self.downloadData()
        if self.length < 2:
            return

        self.new_bar_count = 0
    
        self.ax.set_title(server.stock + '[' + timeframe +']')
        self.setChartProperty(self.timef, self.ohlc)

        # create candle objects
        self.candles = self.createGraphicObjects()
        animation.TimedAnimation.__init__(self, fig, interval=1000 * 2, blit=True)
        return

    def createGraphicObjects(self):
        candles = []
        for i in range(self.length):
            rect = Rectangle((0, 0), width=self.box_width, height=0, facecolor='blue', edgecolor='blue')
            line_upper = Line2D([], [], color='blue', linewidth=self.line_width, antialiased=True)
            line_lower = Line2D([], [], color='blue', linewidth=self.line_width, antialiased=True)
            self.ax.add_patch(rect)
            self.ax.add_line(line_upper)
            self.ax.add_line(line_lower)
            candles.append((rect, line_upper, line_lower))
        return candles

    def removeAllGraphicObjects(self):
        for candle in self.candles:
            for obj in candle:
                obj.remove()
        return

    def setChartProperty(self, timef, ohlc):
        margin = 0
        t0 = timef[0]
        t1 = timef[-1]
        dt = t1 - t0
        self.ax.set_xlim(t0 - dt * 0.05, t1 + dt * 0.1 )

        h = np.max(ohlc)
        l = np.min(ohlc)
        self.ax.set_ylim(l - margin, h + margin)
        self.ax.grid()
        self.ax.xaxis_date()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter(DATE_FORMAT_DAY))
        self.ax.set_xlabel(self.time[0].strftime('%Y/%m/%d') + ' ~ ' + self.time[-1].strftime('%Y/%m/%d'))
        return
    
    def downloadData(self):
        timeseries = self.server.scrapeWithTimeSeries(self.timeframe, self.download_size)
        length = timeseries.length
        time = timeseries.time
        timef = awarePyTimeList2Float(time)
        ohlc = timeseries.values
        return (length, time, timef, ohlc)
        
    def config(self):
        self.box_width = 0.002
        self.alpha = 1.0
        self.color_box_positive = 'red'
        self.color_box_negative = 'blue'
        self.color_line_positive = 'pink'
        self.color_line_negative = 'cyan'
        self.line_width = 1
        return

    def candleValue(self, ohlc):
        open = ohlc[0]
        high = ohlc[1]
        low = ohlc[2]
        close = ohlc[3]
        if close >= open:
            box_color = self.color_box_positive
            line_color = self.color_line_positive
            box_low = open
            box_high = close
            height = close - open
        else:
            box_color = self.color_box_negative
            line_color = self.color_line_negative
            box_low = close
            box_high = open
            height = open - close
        return (box_color, line_color, low, high, box_low, box_high, height)

    # --- override ---
    def _init_draw(self):
        for i in range(self.length):
            t = self.timef[i]
            self._updateCandle(self.candles[i], t, self.ohlc[i])

        prices = Filters.peakPrices(list2array(self.ohlc), 0.0005, 20, np.min(self.ohlc), np.max(self.ohlc))
        for i in range(len(prices)):
            price = prices[i]
            width = len(prices) - i
            self.hline([[price, 'green', width / 4]])
        return
    
    def _draw_frame(self, framedata):
        length, time, timef, ohlc = self.downloadData()
        if self.length != length:
            return
        
        print('Data Updated', self.time[-1], self.ohlc[-1], ohlc[-1])
        self.ohlc = ohlc
        if self._checkTime(time):
            self._updateCandle(self.candles[-1], self.timef[-1], self.ohlc[-1])            
        else:
            self.time = time
            self.timef = timef
            self.new_bar_count += 1
            if self.new_bar_count > 50:
                self.removeAllGraphicObjects()
                self.ax.clear()
                self.candles = self.createGraphicObjects()
                self.setChartProperty(self.timef, self.ohlc)
                self.new_bar_count = 0
            for i in range(self.length):
                self._updateCandle(self.candles[i], self.timef[i], self.ohlc[i])
        self._setObjects(self.candles)
        return

    def new_frame_seq(self):
        return iter(range(self.length))

    # ---

    def _updateCandle(self, candle, timef, ohlc):
        (box_color, line_color, low, high, box_low, box_high, height) = self.candleValue(ohlc)
        box, line_upper, line_lower = candle
        box.set_xy((timef - self.box_width / 2, box_low))
        box.set_height(box_high - box_low)
        box.set_color(box_color)
        box.set_edgecolor(box_color)
        line_upper.set_data([(timef, timef)], [(box_high, high)])
        line_lower.set_data([(timef, timef)], [(box_low, low)])
        line_upper.set_color(line_color)
        line_lower.set_color(line_color)
        return

    def _resetCandle(self, candle):
        (box, line_upper, line_lower) = candle
        box.set_height(0)
        line_upper.set_data([], [])
        line_lower.set_data([], [])
        return

    def _checkTime(self, time):
        if self.length != len(time):
            return False
        count = 0
        for t1, t2 in zip(self.time, time):
            if t1 != t2:
                count += 1
        if count == 0:
            return True
        else:
            return False
        
    def _setObjects(self, candles):
        objects = []
        for candle in candles:
            for obj in candle:
                objects.append(obj)
        self._drawn_artists = objects
        return
    
    #[[value, color, line_width]]
    def hline(self, values):
        for value, color, line_width in values:
            self.ax.axhline(y=value, xmin=0, xmax=1, color = color, linewidth=line_width)
        pass
    
#-----------
    
def test():
    stock = 'EURCHFmicro'
    server = MT5Bind(stock)

    fig = plt.figure(figsize=(20, 8))
    ax = fig.add_subplot(1, 1, 1)
    view = DynamicChartViewer(fig, ax, server, 'H8', 300)
    plt.show()

if __name__ == '__main__':
    test()


