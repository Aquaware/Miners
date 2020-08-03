# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.dates import date2num
from matplotlib.dates import DateFormatter


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

def makeFig(rows, cols, size):
    fig, ax = plt.subplots(rows, cols, figsize=(size[0], size[1]))
    return (fig, ax)


class Graph:
    
    def __init__(self, ax):
        self.ax = ax
        pass
    
    def setDateFormat(self, form ='%H:%M'):
        xaxis_ = self.ax.xaxis
        xaxis_.set_major_formatter(DateFormatter(form))
        pass
    
    def setTitle(self, title, xlabel, ylabel):
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        pass
    
    def scatter(self, x, y, color_index, line_width):
        self.ax.scatter(x, y, c = color(color_index), lw = line_width)
        pass
    
    def plot(self, x, y, prop):
        self.ax.plot(x, y, color = prop['color'], linestyle=prop['style'], lw = prop['width'])
        pass
    
    def box(self, xrange, yrange, color_index, alpha):
        if yrange is None:
            y0 = 0
            y1 = 0
        bottom, top = self.ax.get_ylimi()
        d = yrange[1] - bottom
        y0 = d / (top - bottom)
        d = yrange[1] - bottom
        y1 = d / (top - bottom)
        self.ax.vspan(xrange[0], xrange[1], y0, y1, color = color(color_index), alpha = alpha)
        pass
    
    def point(self, point, color, alpha, size):
        self.ax.scatter(point[0], point[1], s = size , marker= 'o', c = color)
        pass
    
    def xLimit(self, xrange):
        self.ax.set_xlim(xrange[0], xrange[1])
        
    def yLimit(self, yrange):
        self.ax.set_ylim(yrange[0], yrange[1])
        pass
    
    def drawLegend(self, lines, markers):
        elements = []
        if markers is not None:
            for (color_index, label, marker_type) in markers:
                e = Line2D([0], [0], marker = marker_type, color= color(color_index), label = label)
                elements.append(e)
        if lines is not None:
            for (style_index, label) in lines:
                sty = style(style_index)
                e = Line2D([0], [0], marker = 'o', color = sty[0], linestyle=sty[1], linewidth = 5, label=label, markerfacecolor=sty[0], markersize = 0)
                elements.append(e)
        self.ax.legend(handles=elements, bbox_to_anchor= (1.05, 1.0), loc='upper left', borderaxespad= 0)
        pass
    
    def marking(self, x, y, mark_flag, prop):
        for status, color, alpha, size in prop:
            for i in range(len(y)):
                if mark_flag[i] == status:
                    self.point([x[i], y[i]], color, alpha, size)
        pass
        
        