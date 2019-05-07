from ib_insync import *
import pandas as pd
import numpy as np
from fbprophet import Prophet

#util.startLoop()
ib=IB()

def profinit(idnum,  ipaddr='127.0.0.1', socknum=7497):
    ib.connect(ipaddr, socknum, clientId=idnum)

def doprof(contract, hist='50 D', freq='1 hour', freq2='1H', lookahead=24, include_history=True):
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr=hist,
        barSizeSetting=freq,
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1)
    df = util.df(bars)
    prodf = df[['date', 'average']]
    prodf.columns = ['ds', 'y']
    prodf.y = np.log(prodf.y)
    pp = Prophet(changepoint_prior_scale=0.001)
    pp.fit(prodf)
    future = pp.make_future_dataframe(periods=lookahead, freq=freq2, include_history=include_history)
    forecast = pp.predict(future)
    #return pd.concat([prodf, forecast], axis=1)
    return forecast.tail(1).yhat.iloc[0]-prodf.tail(1).y.iloc[0]

