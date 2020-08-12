# -*- coding: utf-8 -*-
#import sys
#sys.path.append("./mpl_finance")
import numpy as np
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from datetime import datetime 

#from pandas.plotting import register_matplotlib_converters
#register_matplotlib_converters()


YMD = 'YMD'
MD = 'MD'
YMDHM = 'YMDHM'
MDHM = 'MDHM'
HM = 'HM'

time_labels = {YMDHM: '%Y-%m-%d %H:%M', YMD: '%Y-%m-%d', MDHM: '%m-%d %H:%M', MD: '%m-%d', HM: '%H:%M'}

def makeFig(rows, cols, size):
    fig, ax = plt.subplots(rows, cols, figsize=(size[0], size[1]))
    return (fig, ax)

def color(index):
    colors = [ mcolors.CSS4_COLORS['red' ], mcolors.CSS4_COLORS['blue'], mcolors.CSS4_COLORS['green'],
               mcolors.CSS4_COLORS['magenta' ], mcolors.CSS4_COLORS['pink'], mcolors.CSS4_COLORS['gold' ], mcolors.CSS4_COLORS['orangered'],
               mcolors.CSS4_COLORS['yellowgreen' ], mcolors.CSS4_COLORS['cyan'], mcolors.CSS4_COLORS['darkgrey' ], mcolors.CSS4_COLORS['blue']]
    return colors[int(index % len(colors))]

def lineStyle(index):
    style = ['solid', 'dashed', 'dashdot']
    return style[int(index % len(style))]

def style(index):
    c = color(index)
    style = lineStyle(int(index / 10))
    return [c, style]


def toNaive(time_list):
    out = []
    for time in time_list:
        naive = datetime(time.year, time.month, time.day, time.hour, time.minute, time.second)
        out.append(naive)
    return out

class CandleChart:
    
    def __init__(self, ax, aware_pytime, time_label_type):
        self.ax = ax
        self.pytime = aware_pytime
        time_list = toNaive(aware_pytime)
        self.time = mdates.date2num(time_list)
        self.time_label_type = time_label_type
        self.length = len(aware_pytime)
        self.color_up = 'green'
        self.color_down = 'red'
        self.width = 0.002
        
        pass
    
    def plotOHLC(self, ohlc, bar_width = 1.0):
        #time = mdates.date2num(tohlc[0])
        n = len(self.time)
        data = []
        for i in range(n):
            data.append([self.time[i], ohlc[0][i], ohlc[1][i], ohlc[2][i], ohlc[3][i]])
            
        w = self.length / 50000 * bar_width
        candlestick_ohlc(self.ax, data, width=w, colorup=self.color_up, colordown=self.color_down)
        self.ax.grid()
        self.ax.xaxis_date()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter(time_labels[self.time_label_type])) # '%m-%d %H:%M'))
        pass
    
    def setTitle(self, title, xlabel, ylabel):
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        pass
    
    def scatter(self, value, color_index, line_width):
        self.ax.scatter(self.time, value, c = color(color_index), lw = line_width)
        pass
    
    def plot(self, value, style_index, line_width):
        sty = style(style_index)
        self.ax.plot(self.time, value, color = sty[0], linestyle=sty[1], lw = line_width)
        pass
    
    def box(self, xrange, yrange, color_index, alpha):
        if yrange is None:
            bottom, top = self.ax.get_ylimi()
            d = yrange[0] - bottom
            y0 = d / (top - bottom)
            d = yrange[1] - bottom
            y1 = d / (top - bottom)
        self.ax.axvspan(xrange[0], xrange[1], y0, y1, color = color(color_index), alpha = alpha)
        pass
    
    def point(self, point, marker, color, alpha, size):
        self.ax.scatter(point[0], point[1], s = size , alpha = alpha, marker= marker, c = color)
        pass
    
    def xLimit(self, xrange):
        self.ax.set_xlim(xrange[0], xrange[1])
        
    def yLimit(self, yrange):
        self.ax.set_ylim(yrange[0], yrange[1])
        pass
    
    def drawLegend(self, lines, markers):
        elements = []
        if markers is not None:
            for marker in markers:
                e = Line2D([0], [0], marker = marker['marker'], color= marker['color'], linewidth = 0, label = marker['label'], markersize = marker['size'] / 10)
                elements.append(e)
        if lines is not None:
            for line in lines:
                e = Line2D([0], [0], marker = 'o', color = line['color'], linewidth = 5, label=line['label'], markerfacecolor=line['color'], markersize = 0)
                elements.append(e)
        self.ax.legend(handles=elements, bbox_to_anchor= (1.05, 1.0), loc='upper left', borderaxespad= 0)
        pass
    
    def markingWithFlag(self, y, mark_flag, markers):
        for marker in markers:
            for i in range(len(y)):
                if mark_flag[i] == marker['status']:
                    self.point([self.time[i], y[i]], marker['marker'], marker['color'], marker['alpha'] , marker['size'])
        pass
    
    def markingWithTime(self, values, mark_time, marker):
        if mark_time is None:
            return
        if len(mark_time) == 0:
            return
        times = mdates.date2num(mark_time)
        for tpy, v in zip(self.pytime, values):
            for tmark, time in zip(mark_time, times):
                if tmark == tpy:
                    self.point([time, v], marker['marker'], marker['color'], marker['alpha'], marker['size'])
        pass
    
    def hline(self, values, colors, width):
        for i in range(len(values)):
            value = values[i]
            if len(values) == len(colors):
                c = colors[i]
            else:
                c = colors[0]
            y = np.full(self.length, value)
            self.ax.plot(self.time, y, color = c, linewidth=width)
        pass
    
    def text(self, x, y, text, color, size):
        self.ax.text(x, y, text, color = color, size = size)
            
    
if __name__ == '__main__':
    brand = 'vix'
    dji = Market.Market(brand, 1, Market.UNIT_MINUTE, False)
    dji.importFromSQLite('./data/click_sec/' + brand + '_1min.db', brand)
    print('Imported data size ...', len(dji.df), 'From ', dji.beginTime(), ' To: ', dji.endTime())
    tbegin = Market.DTime(2019, 8, 5, 16, 30)
    market = dji.timeRangeFilter(tbegin, tbegin + Market.DeltaHour(12))
    df = market.df

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1)
    graph = CandleChart(ax, market.pytime())
    graph.setTitle('2019/8/5', '', 'VIX')
    graph.plotOHLC(market.ohlcArray())