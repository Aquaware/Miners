# -*- coding: utf-8 -*-
#
# Created by Ikuo Kudo  18 August, 2020
import numpy as np
from utils import line, text, rect, rgbColor, number2Str, date2Str, niceRange, niceTimeRange
from datetime import datetime

LINEAR = 'linear'
BAR = 'bar'
DATETIME = 'datetime'

class SCale:
    
    def __init__(self, domain, value_range, scale_type, time, timeframe):
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
    
class CandleStick:
    
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
        

    def parseTimeframe(self, timeframe):
        unit = timeframe[0:1]
        figure = int(timeframe[1:])
        if unit == 'M':
            minutes = figure
        elif unit == 'H':
            minutes = figure * 60
        elif unit == 'D':
            minutes = figure * 24 * 60
        return [figure, unit, minutes]
    

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
                    s = [number2Str(v), ""]
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
    
    def __init__(self, context, timescale, scales):
        self.context = context
        self.timescale = timescale
        self.scales = scales
        pass

    def updateScaleDomain(self, index, domain):
        old_scale = self.scales[index]
        scale = Scale(domain, old_scale.value_range, old_scale.scale_type)
        self.scales[index] = scale
    

    def draw(self, index, graphicObject):
        graphicObject.draw(self.context, self.timeScale, self.scales[index])

    def drawAxis(self):
        time = self.time_scale.time
        timeframe = this.timescale.timeframe;
        for i in range(len(scales)):
            scale = self.scales[i]
            xAxis = Axis(self.timescale, scale.value_range, 5, 2, True, time, timeframe)
            xAxis.draw(self.context)
            yAxis = Axis(scale, self.timescale.value_range, 5, 2, False);
            yAxis.draw(self.context)
            
class Chart:
    def __init__(self, context, canvas_size, chart_size, draw):
        self.context = context
        self.canvas_size = canvas_size
        self.width = chart_size[0]
        self.height = chart_size[1]
        self.margin = chart_size[2]
        self.timeframe = None;
        self.show_length = 30;
        pass

    def setBarNumber(self, number):
        self.show_length = number
        self.update()
        return

    def draw(name, tohlcv, timeframe):
        self.name = name;
        self.tohlcv = tohlcv
        self.timeframe = timeframe
        self.render()
    
    def createGraph(self, data, minmax):
        bar_left_margin = 5
        bar_right_margin = 10
        if data is None:
            return
        if len(data) == 0:
            return

        length = len(data)
        time = data[0]
        time_scale = Scale([-bar_left_margin, length + bar_right_margin], [this.margin.left, this.width - this.margin.right], "bartime", time, this.timeframe);
        height = self.height - self.margin.bottom - self.margin.top;
        y = self.margin.top
        scales = [];
        padding = 50;
        for (let i = 0; i < this.graphHeights.length; i++) {
            let rate = this.graphHeights[i];
            let h = rate * height;
            if (i == 0) {
                let scale = new Scale(minmax, [y + h, y]);
                scales.push(scale);
            } else {
                let scale = new Scale([0, 1], [y + h, y + padding]);
                scales.push(scale);
            }
            y += h;
        }
        let graph = new Graph(this.context, timeScale, scales);
        return graph;
    }

    render() {
        if (!this.tohlc) {
            return;
        }
        let end = this.tohlc.length - 1;
        let begin = end - this.showLength + 1;
        let data = slice(this.tohlc, begin, end);
        if (!data) {
            return;
        }
        //this.currentIndex = this.showLength - data.length;
        this.graph = this.createGraph(data, minmax(data, 100));
        this.context.clearRect(0, 0, this.width, this.height);
        let candles = []
        let prop = {"color": "green", "opacity": 0.5};
        
        for (var i = 0; i < data.length; i++){
            let value = data[i];
            if (value) {
                let candle = new Candle(i, value.time, value.open, value.high, value.low, value.close, this.showLength, prop);
                candles.push(candle);
                this.graph.draw(0, candle);
            }
        }
        //let time = keyListOfJson(data, "time");
        this.candles = candles;
        this.drawTitle(this.name + ' [' + this.timeframe + ']', {});
        //this.drawXtitle("Time", {});

        this.graph.drawAxis();
        
        if (candles.length > 0) {
            this.graph.drawCursor(0, candles[candles.length - 1]);
        }
        if (this.crossPoint) {
            let index = this.graph.isInner(this.crossPoint);
            if (index == 0) {
                this.graph.drawCross(0, this.crossPoint, candles);
            }
        }

        this.drawMA(20);
        this.drawRSI(14);
    }

    drawPoints(points, prop) {
        let width = 10;
        let height = 10;
        for(let p of points) {
            let point = new Square(this.context, this.xScale, this.yScale);
            point.draw(p[0], p[1], width, height, prop);
        }
    }

    drawTitle(title, prop) {
        this.context.font = "20px Arial";
        this.context.textAlign = "left";
        this.context.textBaseline = "top";
        this.context.fillStyle = "#444444";
        this.context.fillRect(this.margin.left, this.margin.top, 160, 30);
        this.context.fillStyle = "#ffffff";
        this.context.fillText(title, this.margin.left + 5, this.margin.top + 5);
        this.context.globalAlpha = 1.0;
        
    }

    drawXtitle(title, prop) {
        this.context.textAlign = "center";
        this.context.textBaseline = "top";
        this.context.globalAlpha = 1.0;
        this.context.fillText(title, this.canvas.width / 2, this.height - 50);
    }

    eventControl(){
        this.canvas.onmousemove = e => {
            let rect = this.canvas.getBoundingClientRect();
            let point = [e.clientX - rect.left, e.clientY - rect.top];
            this.updateCurorPoint(point);
        };
    }

    updateCurorPoint(point) {
        this.crossPoint = point;
        for (let i = 0; i < this.graph.scales.length; i++) {
            let index = this.graph.isInner(point);
            if (index == 0) {
                this.crossPoint = point;
                break;
            }
        } 
    }

    drawMA(windowWidth) {
        var close = []
        for (let v of this.tohlc) {
            close.push(v.close);
        }
        let ma0 = MA(close, windowWidth);
        let end = this.tohlc.length - 1;
        let begin = end - this.showLength + 1;
        let ma = slice(ma0, begin, end);

        var points = [];
        for (let i = 0; i < ma.length; i++) {
            let value = ma[i];
            if (value) {
                points.push([i, value]);
            }
        }

        let lines = new PolyLine(points, {opacity: 0.5, lineColor: "red", lineWidth: 2.0});
        this.graph.draw(0, lines);
    }

    drawRSI(windowWidth) {
        var close = []
        for (let v of this.tohlc) {
            close.push(v.close);
        }
        let rsi0 = RSI(close, windowWidth);
        let end = this.tohlc.length - 1;
        let begin = end - this.showLength + 1;
        let rsi = slice(rsi0, begin, end);
        var points = [];
        for (let i = 0; i < rsi.length; i++) {
            let value = rsi[i];
            if (value) {
                points.push([i, value]);
            }
        }
        let lines = new PolyLine(points, {opacity: 0.5, lineColor: "blue", lineWidth: 2.0});
        let domain = minmaxOfArray(rsi);
        this.graph.updateScaleDomain(1, domain);
        this.graph.draw(1, lines);
    }
}



    
