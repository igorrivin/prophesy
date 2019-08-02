from ib_insync import *
import pandas as pd
import numpy as np
from fbprophet import Prophet
from datetime import datetime, timedelta

#util.startLoop()
ib=IB()

class bardata:
    def __init__(self, contract, hist, freq, freq2, lookahead, cutoff,fname='/tmp/logfile.txt'):
        self.bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=hist,
            barSizeSetting=freq,
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1,
            keepUpToDate=True)
        self.thedata = util.df(self.bars)
        self.contract = contract
        self.hist = hist
        self.freq = freq
        self.freq2 = freq2
        self.lookahead = lookahead
        self.cutoff=cutoff
        self.thedate = None
        self.outfile = open(fname, "a")
        
        
    def doprof( self):

        df = self.thedata
    
        prodf = df[['date', 'average']]
        prodf.columns = ['ds', 'y']
        prodf.y = np.log(prodf.y)
        pp = Prophet(changepoint_prior_scale=0.001)
        pp.fit(prodf)
        future = pp.make_future_dataframe(periods=self.lookahead, freq=self.freq2)
        forecast = pp.predict(future)
        #return pd.concat([prodf, forecast], axis=1)
        return forecast.tail(1).yhat.iloc[0]-prodf.tail(1).y.iloc[0]
    
    def protrader(self,amount = 1, holdtime=600 ):
        try:
            thesig = self.doprof()
            self.outfile.write(repr(thesig))
            print(thesig)
            if thesig > cutoff:
                enter = 'BUY'
                exter = 'SELL'
            elif thesig < -cutoff:
                enter = 'SELL'
                exter = 'BUY'
            else:
                return
            order = MarketOrder(enter, amount)
            ib.placeOrder(self.contract, order)
            order = MarketOrder(exter, amount)
            util.schedule(datetime.now() + timedelta(seconds = holdtime), ib.placeOrder, contract, order)
            return
        except:
            return
    
    def onBarUpdateEvent(self, bars, hasNewBar):
        self.thedata = util.df(bars)
        newdate = self.thedata.iloc[-1]['date']
        self.outfile.write(repr(newdate))
        print(newdate)
        if self.thedate is None or newdate > self.thedate:
            display(self.thedata.tail())
            self.outfile.write(repr(self.thedata.tail()))
            self.thedate = newdate
            self.protrader()
        
        
def profinit(idnum,  ipaddr='127.0.0.1', socknum=7497):
    ib.connect(ipaddr, socknum, clientId=idnum)



def doprof(contract, hist='50 D', freq='1 hour', freq2='1H', lookahead=24, include_history=True, bd=None):
    if bd is None:
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr=hist,
            barSizeSetting=freq,
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1)
        df = util.df(bars)
    else:
        df = bd.thedata
    
    prodf = df[['date', 'average']]
    prodf.columns = ['ds', 'y']
    prodf.y = np.log(prodf.y)
    pp = Prophet(changepoint_prior_scale=0.001)
    pp.fit(prodf)
    future = pp.make_future_dataframe(periods=lookahead, freq=freq2, include_history=include_history)
    forecast = pp.predict(future)
    #return pd.concat([prodf, forecast], axis=1)
    return forecast.tail(1).yhat.iloc[0]-prodf.tail(1).y.iloc[0]

def protrader(contract, cutoff, amount = 1, hist = '10000 S', freq='10 secs', freq2 = '10s', holdtime=300, lookahead=30, waittime=10,defaultwait=10, incwait=0, bd=None):
    try:
        thesig = doprof(contract, hist=hist, freq=freq, freq2=freq2, lookahead=lookahead, bd=bd)
        print(thesig)
        if thesig > cutoff:
            enter = 'BUY'
            exter = 'SELL'
        elif thesig < -cutoff:
            enter = 'SELL'
            exter = 'BUY'
        else:
            return defaultwait
        order = MarketOrder(enter, amount)
        ib.placeOrder(contract, order)
        order = MarketOrder(exter, amount)
        util.schedule(datetime.now() + timedelta(seconds = holdtime), ib.placeOrder, contract, order)
        return waittime + incwait
    except:
        return defaultwait
    
def makepredb(df, numperiods=30, freq='10s'):
    prodf = df.reset_index()[['timestamp', 'vwap']]
    prodf.columns = ['ds', 'y']
    prodf.y = np.log(prodf.y)
    pp = Prophet(changepoint_prior_scale=0.001)
    pp.fit(prodf)
    future = pp.make_future_dataframe(periods=numperiods, freq=freq)
    forecast = pp.predict(future)
    f_ind = forecast.set_index('ds')
    f_ind1= f_ind.yhat
    prodf_ind = prodf.set_index('ds')
    prodf_ind['gain']=-prodf_ind.y + prodf_ind.y.shift(periods=-numperiods, freq = freq)
    theboth = pd.concat([f_ind1, prodf_ind], axis=1)
    theboth['predgain'] = theboth.yhat - theboth.y
    return theboth
    
