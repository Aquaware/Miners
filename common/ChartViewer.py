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

from CalendarTime import DTime, DeltaDay, DeltaHour, DeltaMinute, Today, Now
from MT5Bind import MT5Bind

DATE_FORMAT_TIME = '%H:%M'
DATE_FORMAT_DAY = '%m-%d'
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
    
class CandleGraphic:
    def __init__(self, py_time, ohlc):
        self.config()
        t = awarePyTime2Float(py_time)
        open = ohlc[0]
        high = ohlc[1]
        low = ohlc[2]
        close = ohlc[3]
        if close >= open:
            color = self.color_positive
            line_color = self.box_line_color_positive
            box_low = open
            box_high = close
            height = close - open
        else:
            color = self.color_negative
            line_color = self.box_line_color_negative
            box_low = close
            box_high = open
            height = open - close
            
        line_upper = Line2D([(t, t)],[(box_high, high)],
                            color=line_color,
                            linewidth=self.line_width,
                            antialiased=True)
        line_lower = Line2D(xdata=(t, t),
                            ydata=(box_low, low),
                            color=line_color,
                            linewidth=self.line_width,
                            antialiased=True)

        rect = Rectangle(xy=(t - self.box_width / 2, box_low),
                         width=self.box_width,
                         height=height,
                         facecolor=color,
                         edgecolor=line_color)
        rect.set_alpha(self.alpha)

        self.line_upper = line_upper
        self.line_lower = line_lower
        self.rect = rect
        return
    
    def setObject(self, ax):
        ax.add_line(self.line_lower)
        ax.add_line(self.line_upper)
        ax.add_patch(self.rect)
        return
    
    def config(self):
        self.box_width = 0.002
        self.alpha = 1.0
        self.color_positive = 'pink'
        self.color_negative = 'cyan'
        self.box_line_color_positive = 'red'
        self.box_line_color_negative = 'blue'
        self.line_width = 1
        return
# -----
    
class ChartViewer:
    def __init__(self, fig, ax, title, date_format=DATE_FORMAT_TIME):
        self.fix = fig
        self.ax = ax
        self.title = title
        self.ax.grid()
        self.ax.xaxis_date()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        pass
        
    def drawChart(self, timeseries):
        self.ax.set_title(self.title)
        n = timeseries.length
        self.graphic_objects = []
        for i in range(n):
            t = timeseries.time[i]
            ohlc = timeseries.values[i]
            obj = CandleGraphic(t, ohlc)
            obj.setObject(self.ax)
            self.graphic_objects.append(obj)  
        self.ax.autoscale_view()
        return
        
#-----------
    
def test():
    stock = 'JP225Cash'
    server = MT5Bind(stock)
    data = server.scrape('M5', 300)
    d = server.toTimeSeries(data)
    df = d.toDataFrame()
    print(df)
    
    fig = plt.figure(figsize=(15, 8))
    ax = fig.add_subplot(1, 1, 1)
    view = ChartViewer(fig, ax, stock + '-M5')
    view.drawChart(d)

    
    
if __name__ == '__main__':
    test()


