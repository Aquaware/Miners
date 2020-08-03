# -*- coding: utf-8 -*-
import pandas as pd
import TimeSeries

def CandleFigure(time_series):
    INCREASING_COLOR = '#ff8888'
    DECREASING_COLOR = '#9999ff'

    df = time_series.toDataFrame()
    data = [ dict(type = 'candlestick',
                    open = df.open,
                    high = df.high,
                    low = df.low,
                    close = df.close,
                    x = df.time,
                    yaxis = 'y2',
                    name = 'GS',
                    increasing = dict( line = dict( color = INCREASING_COLOR ) ),
                    decreasing = dict( line = dict( color = DECREASING_COLOR ) )) ]

    layout=dict()
    figure = dict(data=data, layout=layout)
    figure['layout'] = dict()
    figure['layout']['plot_bgcolor'] = 'rgb(120, 120, 120)'
    figure['layout']['xaxis'] = dict( rangeselector = dict( visible = True ) )
    figure['layout']['yaxis'] = dict( domain = [0, 0.2], showticklabels = False )
    figure['layout']['yaxis2'] = dict( domain = [0.2, 0.8] )
    figure['layout']['legend'] = dict( orientation = 'h', y=0.9, x=0.3, yanchor='bottom' )
    figure['layout']['margin'] = dict( t=40, b=40, r=40, l=40 )
    return figure