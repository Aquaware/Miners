# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import statsmodels.api as sm

def adf(vector):
    df = pd.DataFrame(data=vector, columns=['y'])
    ret =  sm.tsa.adfuller(vector, regression='ct')
    dfout = pd.Series(ret[0:4], index=['Test Static', 'p-value', '#Lags Used', 'Number of Observations Used'])
    for key, value in ret[4].items():
        dfout['Ciritical Value (%s)'%key] = value
    return dfout