# -*- coding: utf-8 -*-

import numpy as np
import statsmodels.api as sm

def adf(data):
    return sm.tsa.adfuller(data, regression='nc')