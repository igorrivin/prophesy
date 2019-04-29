from prostrat import *
import argparse

def main(args):
    infile = args.infile
    outfile = args.outfile
    freq = int(args.freq)
    portnum = int(args.portnum)
    clientid = int(args.clientid)
    print('yay')
    profinit(clientid, portnum)
    
    thedf = pd.read_csv(infile, index_col=0)
    print('yay')
    symbols = list(thedf[thedf.columns[0]])
    preddict = {}
    for i in symbols:
        try:
            preddict[i] = doprof(Stock(i, 'SMART', 'USD'))
        except:
            pass
    preds = pd.Series(preddict)
    thedf.set_index(columns[0])
    newdf =pd.concat([thedf, preds], axis=1)
    newdf.columns = thedf.columns.append('prediction')
    newdf = newdf[['cpair', 'prediction']]
    newdf.to_csv(outfile)
    
    if __name__=="__main__":
        parser = argparse.ArgumentParser()
        #parser.add_argument('fname', help="history file")
        #parser.add_argument('tfile', help= "testfile")
        parser.add_argument('infile', help="input dataframe")
        parser.add_argument('outfile', help="output")
        parser.add_argument('freq', help='sampling frequency')
        parser.add_argument('portnum', help='API port number')
        parser.add_argument('clientid', help = 'client id')
                  
                        
                        
        args = parser.parse_args()
        print(args)
        sys.exit(main(args))
    