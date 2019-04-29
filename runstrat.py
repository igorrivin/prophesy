from prostrat import *
import argparse

timedict = {'1 secs':'1s', '5 secs':'5s', '10 secs':'10s', '15 secs':'15s', '30 secs':'30s', '1 min': '60s', '2 mins': '120s', '3 mins':'180 s', '5 mins': '300s', '10 mins':'600s', '15 mins': '900s', '20 mins': '1200s', '30 mins': '1800s', '1 hour': '3600s', '2 hours': '7200s', '3 hours':'3H','4 hours':'4H', '8 hours': '8H', '1 day':'1D'}

def main(args=None, infile=None, outfile=None, freq=None, portnum=None, clientid=None):
    if args is not None:
        infile = args.infile
        outfile = args.outfile
        freq = args.freq
        portnum = int(args.portnum)
        clientid = int(args.clientid)
    
    freq2 = timedict[freq]
    
    
    print('yay')
    profinit(clientid, socknum=portnum)
    
    thedf = pd.read_csv(infile, index_col=0)
    print('yay')
    symbols = list(thedf[thedf.columns[0]])
    preddict = {}
    for i in symbols:
        try:
            preddict[i] = doprof(Future(i, '201906', 'GLOBEX'), freq=freq, freq2=freq2)
        except:
            pass
    preds = pd.Series(preddict)
    predsdf = pd.DataFrame(preds, columns = ['prediction'])
    print(thedf.head())
    thedf.set_index(thedf.columns[0], inplace=True)
    newdf =pd.concat([thedf, predsdf], axis=1)
    newdf = newdf[['cpair', 'prediction']]
    print(newdf)
    newdf.to_csv(outfile)
    return 0
    
    if __name__=="__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument('infile', help="input dataframe")
        parser.add_argument('outfile', help="output")
        parser.add_argument('freq', help='sampling frequency')
        parser.add_argument('portnum', help='API port number')
        parser.add_argument('clientid', help = 'client id')
                  
                        
                        
        args = parser.parse_args()
        print(args)
        sys.exit(main(args))
    
