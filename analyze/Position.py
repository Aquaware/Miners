#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 19:58:49 2030

@author: iku
"""
import numpy as np

INITIAL = 1
TRAILING = 2
FINISH = 3

class Position:
    """
        No trailing Stop
        stops = [ [(profit), (losscut)]]
        
        Trailing Stop
        stops = [ [(initial profit), (initial losscut) ],
                  [ (second profit),  (second losscut) ],
                  [  (delta profit),    (delta loscut) ] ]
    """
    def __init__(self, index, open_price, is_long, stops):
        self.open_index = index
        self.open_price = open_price
        self.current_price = open_price
        self.is_long = is_long
        self.stops = stops
        if len(self.stops) == 1:
            self.trailing = False
        else:
            self.trailing = True
            
        if is_long:
            self.take_profit_price = open_price  + stops[0][0]
            self.stop_loss_price = open_price + stops[0][1]
        else:
            self.take_profit_price = open_price - stops[0][0]
            self.stop_loss_price = open_price - stops[0][1]
            
        self.state = INITIAL
        pass
    
    def currentStopPrice(self):
        return [self.take_profit_price, self.stop_loss_price]
                
    def update(self, index, values):
        if self.state == FINISH:
            return self.state
        
        if self.stopLoss(index, values):
            return self.state        
            
        if self.trailing:
            self.updateStop(values)
        else:
            self.stopProfit(index, values)            
        return self.state
    
    def stopLoss(self, index, values):
        minvalue = np.min(values)
        maxvalue = np.max(values)
        
        if self.is_long:
            if self.stop_loss_price >= minvalue:
                self.close_index = index
                self.close_price = self.stop_loss_price
                self.state = FINISH
                return True
            else:
                return False
        else:
            if self.stop_loss_price <= maxvalue:
                self.close_index = index
                self.close_price = self.stop_loss_price
                self.state = FINISH
                return True
            else:
                return False
            
    def stopProfit(self, index, values):
        minvalue = np.min(values)
        maxvalue = np.max(values)        

        if self.is_long:
            if self.take_profit_price <= maxvalue:
                self.close_price = self.take_profit_price
                self.close_index = index
                self.state = FINISH
                return True
        else:
            if self.take_profit_price >= minvalue:
                self.close_price = self.take_profit_price
                self.close_index = index
                self.state = FINISH
                return True
        return False
        
    def updateStop(self, values):
        minvalue = np.min(values)
        maxvalue = np.max(values)        

        if self.is_long:
            if self.take_profit_price >= minvalue:
                return
        else:
            if self.take_profit_price <= maxvalue:
                return
        
        # update profit
        
        if self.state == INITIAL:
            if self.is_long:
                self.take_profit_price = self.open_price + self.stops[1][0]
                self.stop_loss_price  = self.open_price + self.stops[1][1]
            else:
                self.take_profit_price = self.open_price - self.stops[1][0]
                self.stop_loss_price = self.open_price - self.stops[1][1]
            self.state = TRAILING
        elif self.state == TRAILING:
            if self.is_long:
                while self.take_profit_price <= maxvalue:
                    self.take_profit_price += self.stops[2][0]
                    self.stop_loss_price = self.take_profit_price + self.stops[2][1]
            else:
                while self.take_profit_price >= minvalue:
                    self.take_profit_price -= self.stops[2][0]
                    self.stop_loss_price = self.take_profit_price - self.stops[2][1]
        return
    
def test1():
    stops = [[100, -50]]
    data = [10, 20, 30, 70, 110, 80, 90]
    pos = Position(0, data[0], True, stops)
    for i in range(1, len(data)):
        print(i, data[i], pos.update(i, data[i]))
    
def test2():
    stops = [[100, -50]]
    data = [60, 70, 20, 10, 110, 80, 90]
    pos = Position(0, data[0], True, stops)
    for i in range(1, len(data)):
        print(i, data[i], pos.update(i, data[i]))

def test3():
    stops = [[100, -50], [150, 50], [50, 50]]
    data = [50, 80, 100, 120, 140, 160, 180, 200, 250, 300, 500, 400, 200]
    pos = Position(0, data[0], True, stops)
    print(0, data[0], 0, pos.currentStopPrice())
    for i in range(1, len(data)):
        ret = pos.update(i, data[i])
        print(i, data[i], ret, pos.currentStopPrice())
        
def test4():
    stops = [[100, -50], [150, 100], [20, 20]]
    data = [500, 450, 400, 380, 360, 350, 340, 310, 300, 290, 250, 210, 200, 190, 200, 210, 250, 270, 280, 290, 300, 310, 320, 330]
    pos = Position(0, data[0], False, stops)
    print(0, data[0], 0, pos.currentStopPrice())
    for i in range(1, len(data)):
        ret = pos.update(i, data[i])
        print(i, data[i], ret, pos.currentStopPrice())


def test5():
    stops = [[70, -20]]
    h = [10, 20, 30, 80, 110, 80, 90]
    l = [7, 18, 24, 60, 100, 70, 80]
    pos = Position(0, h[0], True, stops)
    for i in range(1, len(h)):
        ret = pos.update(i, [h[i], l[i]])
        print(i, [h[i], l[i]], ret, pos.currentStopPrice())
        
def test6():
    stops = [[50, -20]]
    h = [100, 80, 120, 60, 30, 80, 90]
    l = [90, 70, 70, 50, 20, 70, 80]
    pos = Position(0, h[0], False, stops)
    for i in range(1, len(h)):
        ret = pos.update(i, [h[i], l[i]])
        print(i, [h[i], l[i]], ret, pos.currentStopPrice())
        
def test7():
    stops = [[50, -20], [0, 40], [20, -20]]
    h = [0, 30, 50, 60, 80, 100, 150, 200, 300, 400, 400]
    l = [10, 20, 40, 70, 70, 90, 140, 180, 290, 390,  50]
    pos = Position(0, h[0], True, stops)
    for i in range(1, len(h)):
        ret = pos.update(i, [h[i], l[i]])
        print(i, [h[i], l[i]], ret, pos.currentStopPrice())

def test8():
    stops = [[50, -20], [0, 40], [20, -20]]
    h = [0, -30, -50, -60,- 80, -100, -150, -200, -300, -400, -400]
    l = [0, -20, -40, -70, -70, -90, -140, -180, -290, -390,  -50]
    pos = Position(0, h[0], False, stops)
    for i in range(1, len(h)):
        ret = pos.update(i, [h[i], l[i]])
        print(i, [h[i], l[i]], ret, pos.currentStopPrice())
        
if __name__ == '__main__':
    #evaluate2(False, False)
    test8()