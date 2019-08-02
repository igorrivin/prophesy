from fbprophet import Prophet()

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
    
