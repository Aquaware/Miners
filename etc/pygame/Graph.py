# -*- coding: utf-8 -*-
#
# Created by Ikuo Kudo  18 August, 2020

import numpy as np
from utils import line, text, rect, rgbColor,  date2Str, niceRange, niceTimeRange
from datetime import datetime, timedelta

LINEAR = 'linear'
BAR = 'bar'
DATETIME = 'datetime'

def parseTimeframe(timeframe):
    unit = timeframe[0:1]
    figure = int(timeframe[1:])
    if unit == 'M':
        minutes = figure
    elif unit == 'H':
        minutes = figure * 60
    elif unit == 'D':
        minutes = figure * 24 * 60
    return [figure, unit, minutes]
    
def timeframe2timedelta(timeframe):
    figure, unit, minutes = parseTimeframe(timeframe)
    delta = timedelta(Minutes=minutes)
    return delta

class Scale:
    
    def __init__(self, domain, value_range, scale_type=LINEAR, time=None, timeframe=None):
        self.domain = domain
        self.value_range = value_range
        self.scale_type = scale_type
        if scale_type == LINEAR or scale_type == BAR:
            delta1 = value_range[1] - value_range[0]
            delta2 = domain[1] - domain[0]
            if delta1 == 0.0 or delta2 == 0.0:
                self.rate = 1.0
            else:
                self.rate = delta1 / delta2
            
        elif scale_type == DATETIME:
            delta1 = value_range[1] - value_range[0]
            delta2 = domain[1].timestamp() - domain[0].timestamp()
            if delta1 == 0.0 or delta2 == 0.0:
                self.rate = 0.0
            else:
                self.rate = delta1 / delta2

        if scale_type == BAR:
            self.time = time
            self.timeframe = timeframe
        else:
            self.time = None
            self.timeframe = None
    
    def pos(self, value):
        if self.scale_type == LINEAR or self.scale_type == BAR:
            # pos = (value - real0) * (screen1 - screen0) / (real1 - real0) + screen0
            v = value - self.domain[0]
            return v * self.rate + self.value_range[0]
        elif self.type == DATETIME: 
            v = value.timestamp() - self.domain[0].timestamp()
            return v * self.rate + self.value_range[0]

    def value(self, pos):
        if self.scale_type == LINEAR or self.scale_type == BAR:
            # value = (pos - screen0) / (screen1 - screen0) * (real1 - real0) + real0
            if self.rate == 0.0:
                return 0.0
            v = (pos - self.value_range[0]) / self.rate + self.domain[0]
            if self.scale_type == BAR:
                return int(v + 0.5);
            else:
                return v
        elif self.scale_type == DATETIME:
            v = (pos - self.range[0]) / self.rate + self.domain[0].timestamp()
            return datetime.fromtimestmp(v)
        
    def rangeWidth(self):
        w = np.abs(self.range[0] - self.range[1])
        return w

    def domainWidth(self):
        w = np.abs(self.domain[0] - self.domain[1])
        return w

    def rangeLowerUpper(self):
        lower = self.value_range[0]
        upper = self.value_range[1]
        if upper < lower:
            tmp = lower
            lower = upper
            upper = tmp
        return [lower, upper]

    def domainLowerUpper(self):
        lower = self.domain[0]
        upper = self.domain[1]
        if upper < lower:
            tmp = lower
            lower = upper
            upper = tmp
        return [lower, upper]
     
# -----    
    
class Candle:
    
    def __init__(self, context, index, time, open, high, low, close, show_length, prop):
        self.context = context
        self.index = index
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.show_length = show_length
        self.prop = prop
        self.positive_color = 'green'
        self.nagative_color = 'red'
        pass
    
    def draw(self, xScale, yScale):
        width = self.candleWidth(xScale.rangeWidth(), self.show_length)
        x = xScale.pos(self.index)
        x0 = x - width / 2
        if self.open < self.close:
            upper = yScale.pos(self.close)
            lower = yScale.pos(self.open)
            body_color = "#007744"
            line_color = "green"
        else:
            upper = yScale.pos(self.open)
            lower = yScale.pos(self.close)
            body_color = "red"
            line_color = "pink"    
        
        rect(self.context, [x0, lower], [width, upper -lower], body_color) 
        #upper line
        line(self.context, [x, yScale.pos(self.high)], [x, upper], line_color)
        # lower line
        line(self.context, [x, lower], [x, yScale.pos(self.low)], line_color)
        return

    def candleWidth(self, value_range, barSize):
        w = int(value_range / barSize / 2)
        if w < 0:
            w = 1
        elif w > 10:
            w = 10
        return w
    
# -----
    
class Axis:
    
    def __init__(self, scale, level, main_division, sub_division, is_horizontal, time, timeframe):
        self.scale = scale
        self.level = level
        self.main_division = main_division
        self.sub_division = sub_division
        self.is_horizontal = is_horizontal
        if time is None:
            self.time = None
            self.timeframe = None
        else:
            self.time = time
            self.timeframe = self.parseTimeframe(timeframe)
        pass

    def draw(self, context):
        color  = "black"
        if self.scale.scale_type == LINEAR:
            lower = self.scale.domain[0]
            upper = self.scale.domain[1]
            if upper < lower:
                tmp = lower
                lower = upper
                upper = tmp
        elif self.scale.scale_type == DATETIME:
            lower = self.scale.domain[0].timestamp()
            upper = self.scale.domain[1].timestamp()
        

        # grid
        context.font = 'bold 10px Times Roman'
        color = "grey"
        if self.scale.scale_type == LINEAR:
            value_range = niceRange(lower, upper, self.main_division)
        elif self.scale.scale_type == BAR:
            value_range = niceTimeRange(self.scale.domain[0], self.scale.domain[1], self.time, self.timeframe, self.main_division)
        elif self.scale.scale_type == DATETIME:
            value_range = niceTimeRange(self.scale.domain[0], self.scale.domain[1])
        
        for  v in value_range:
            if self.scale.scale_type == LINEAR:
                value = self.scale.pos(v);
            elif self.scale.scale_type == BAR:
                value = self.scale.pos(v[0])
            elif self.scale.scale_type == DATETIME:
                value = self.scale.pos(datetime.fromtimestamp(v))
            
            if self.is_horizontal:
                label_margin = 5
                line(context, [value, self.level[0]], [value, self.level[1]])
                s = [None, None]
                if self.scale.scale_type == LINEAR:
                    s = [str(v).zfill(3), ""]
                elif self.scale.type == BAR:
                    if v[1] is not None:
                        s = date2Str(v[1], self.timeframe)
                    else:
                        s = ""
                elif self.scale.scale_type == DATETIME:
                    s = date2Str(datetime.fromtimestamp(v), "HH:mm")
                
                if s[0] is not None:
                    text(s[0], value, self.level[0] + label_margin)
                
                if s[1]:
                    text(s[1], value, self.level[0] + label_margin + 15);
                
            else:
                line(context, [self.level[0], value], [self.level[1], value])
                text(context, number2Str(v), self.level[0], value)

        if self.is_horizontal:
            line(context, [self.scale.value_range[0], self.level[0]], [self.scale.range[1], self.level[0]], 2.0)
            line(context, [self.scale.value_range[0], self.level[1]], [self.scale.range[1], self.level[1]], 2.0)
        else:
            line(context, [self.level[0], self.scale.value_range[0]], [self.level[0], self.scale.value_range[1]], 2.0)
            line(context, [self.level[1], self.scale.value_range[0]], [self.level[1], self.scale.value_range[1]], 2.0)

# -----
        
class Graph:
    
    def __init__(self, context, time_scale, scales):
        self.context = context
        self.time_scale = time_scale
        self.scales = scales
        pass
    
    def draw(self, index, graphicObject):
        graphicObject.draw(self.context, self.time_scale, self.scales[index])

    def drawAxis(self):
        time = self.time_scale.time
        timeframe = self.time_scale.timeframe;
        for scale in self.scales:
            xAxis = Axis(self.time_scale, scale.value_range, 5, 2, True, time, timeframe)
            xAxis.draw(self.context)
            yAxis = Axis(scale, self.time_scale.value_range, 5, 2, False);
            yAxis.draw(self.context)
            
class Canvas:
    def __init__(self, context, canvas_size, chart_margin):
        self.context = context
        self.width = canvas_size[0]
        self.height = canvas_size[1]
        self.margin_left = chart_margin[0]
        self.margin_right = chart_margin[1]
        self.margin_top = chart_margin[2]
        self.margin_bottom = chart_margin[3]        
        self.chart_origin = [self.margin_left, self.margin_top]
        self.chart_width = self.width - self.margin_left - self.margin_right
        self.chart_heigt = self.height - self.margin_top - self.marign.bottom
        pass

    def drawGraph(self, title, tohlcv, timeframe, bar_num, minmax):
        bar_left_margin = 5
        bar_right_margin = 10
        if len(tohlcv) == 0:
            return

        time, ohlc, volume = self.sliceData(tohlcv, bar_num)
        time_scale = Scale([-bar_left_margin, bar_num + bar_right_margin],
                           [self.chart_origin[0], self.width - self.margin_right],
                           scale_type=BAR,
                           time=time,
                           timeframe=timeframe)
        h = self.height - self.margin.bottom - self.margin.top
        y = self.margin_top
        scale = Scale(minmax, [y + self.chart_height, y])
        graph = Graph(self.context, time_scale, scale)
        
        self.render(time, ohlc)
        return graph
            
    def sliceData(self, tohlcv, timeframe, size):
        time = []
        ohlc = []
        volume = []
        n = len(tohlcv)
        for i in range(size):
            if i < n:
                t = tohlcv[0][i]
                time.append(tohlcv[0][i])
                ohlc.append([tohlcv[1][i], tohlcv[2][i], tohlcv[3][i], tohlcv[4][i]])
                volume.append(tohlcv[5][i])
            else:
                t += timeframe2timedelta(timeframe)
                time.append(t)
                ohlc.append(None)
                volume.append(None)
        return (time, ohlc, volume)
    
    def render(self, time, ohlc_list):
        candles = []
        prop = {"color": "green", "opacity": 0.5}
        n = len(ohlc_list)
        for i in range(n):
            t = time[i]
            ohlc = ohlc_list[i]
            if ohlc is not None:
                candle = Candle(i, t, ohlc, prop)
                candles.append(candle)
                self.graph.draw(0, candle)
        self.candles = candles
        self.drawTitle(self.name + ' [' + self.timeframe + ']', {})
        self.graph.drawAxis()

# -----
def test(ts):
    import pygame
    pygame.display.set_caption('Test')
    success, failure = pygame.init()
    print("Initializing pygame: {0} success and {1} failure.".format(success, failure))
    window_size = [1280, 800]
    context = pygame.display.set_mode(window_size)
    clock = pygame.time.Clock()
    context.fill(rgbColor('white'))
    pygame.event.pump()
    loop = True
    while(loop):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
                break
        render(context, window_size)
        pygame.display.update()
        pygame.time.delay(60)
    pygame.quit()
    return
    
def render(context, window_size, ts):
    
    canvas = Canvas(context, window_size, [50, 50, 50, 50])
    canvas.drawGraph('DJI')
    
    line(context, [(0,0), (100, 100)], 'red', alpha= 0.5)
    rect(context, (50, 100), (10, 60), 'blue', alpha=0.6)
    text(context, (200, 100), 'Great', 'green', alpha=0.1)
    return

if __name__ == "__main__":
    import pandas as pd
    from TimeSeries import TimeSeries, DATA_TYPE_PANDAS, OHLCV
    df = pd.read_csv('./dji_M5.csv')
    ts0 = TimeSeries(df, DATA_TYPE_PANDAS, names=OHLCV)
    ts = ts0.timeRangeFilter(datetime(2019, 8, 6, 1, 0), None)
    test(ts)  
