import sys
from prostrat import *
import argparse
from joblib import Parallel, delayed
from datetime import datetime
import re

def htmldisp(df, outfile):
    pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>

    html_string = '''
    <html>
    <head><title>Signals for Currency Pairs</title></head>
    <link rel="stylesheet" type="text/css" href="df_style.css"/>
    <body>
    {table}
    </body>
    </html>.
    '''

    # OUTPUT AN HTML FILE
    with open(outfile, 'w') as f:
        f.write(html_string.format(table=df.to_html(classes='mystyle')))
    
class looper(object):
    def __init__(self, hist, freq, freq2, lookahead, include_history):
        self.hist = hist
        self.freq = freq
        self.freq2 = freq2
        self.lookahead = lookahead 
        self.include_history = include_history
    def __call__(self, s):
        return (s, theloop(s, self.hist, self.freq, self.freq2, self.lookahead, self.include_history))
    
timedict = {'1 secs':'1s', '5 secs':'5s', '10 secs':'10s', '15 secs':'15s', '30 secs':'30s', '1 min': '1min', '2 mins': '120s', '3 mins':'180 s', '5 mins': '300s', '10 mins':'600s', '15 mins': '900s', '20 mins': '1200s', '30 mins': '1800s', '1 hour': '3600s', '2 hours': '7200s', '3 hours':'3H','4 hours':'4H', '8 hours': '8H', '1 day':'1D'}

def theloop(fname, hist, freq, freq2, lookahead, include_history):
        try:
            res = doprof(Future(fname, '201906', 'GLOBEX'), hist=hist,  freq=freq, freq2=freq2, lookahead=lookahead, include_history=include_history)
        except:
            res = None
        return res

def main(args=None, infile=None, outfile=None, freq=None, portnum=None, clientid=None):
    if args is not None:
        infile = args.infile
        outfile = args.outfile
        freq = args.freq
        lookahead=int(args.lookahead)
        portnum = int(args.portnum)
        clientid = int(args.clientid)
        hist = args.hist
    
    freq2 = timedict[freq]
    
    
    print('yay')
    profinit(clientid, socknum=portnum)
    
    thedf = pd.read_csv(infile, index_col=0)
    print('yay')
    symbols = list(thedf[thedf.columns[0]])
    preddict = dict([(i, theloop(i, hist, freq, freq2, lookahead, args.hflag)) for i in symbols])
    #loopster = looper(hist, freq, freq2, lookahead, args.hflag)
    #preddict = dict(Parallel(n_jobs=2)(delayed(loopster)(i) for i in symbols))
    #preddict = {}
    #for i in symbols:
    #    try:
    #        preddict[i] = doprof(Future(i, '201906', 'GLOBEX'), hist=hist,  freq=freq, freq2=freq2, lookahead=lookahead, include_history=args.hflag)
    #    except:
    #        pass
    preds = pd.Series(preddict)
    predsdf = pd.DataFrame(preds, columns = ['prediction'])
    thedf.set_index(thedf.columns[0], inplace=True)
    newdf =pd.concat([thedf, predsdf], axis=1)
    newdf = newdf[['cpair', 'prediction']]
    newdf.dropna(inplace=True)
    newdf.sort_values('prediction', inplace=True)
    newdf.prediction = 10000 * newdf.prediction #convert to basis points
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y %H:%M:%S")
    newdf['timestamp']=date_time
    print(newdf.head())
    p = re.compile('html$')
    if p.search(outfile) is not None:
        htmldisp(newdf, outfile)
    else:
        newdf.to_csv(outfile, float_format = '%10.2f')
    return 0
    
if __name__=="__main__":
    print("spaz")
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help="input dataframe")
    parser.add_argument('outfile', help="output")
    parser.add_argument('hist', help='how much history')
    parser.add_argument('freq', help='sampling frequency')
    parser.add_argument('lookahead', help='lookahead')
    parser.add_argument('portnum', help='API port number')
    parser.add_argument('clientid', help = 'client id')
    parser.add_argument('--keep', const=False, default=True, dest='hflag', nargs='?')
    args = parser.parse_args()
    print(args)
    sys.exit(main(args))
    
