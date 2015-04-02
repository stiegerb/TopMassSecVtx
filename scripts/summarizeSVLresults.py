#!/usr/bin/env python
import ROOT
import os,sys
import optparse
import math

"""
steer
"""
def main():
    usage = """
    Parses the results for pseudo-experiments stored in a directory and produces a summary
    usage: %prog directory
    """

    parser = optparse.OptionParser(usage)
    (opt, args) = parser.parse_args()
    
    #parse results from file
    results={}
    fileNames=[f for f in os.listdir(args[0]) if f.endswith('root')]
    for f in fileNames :
        fIn=ROOT.TFile.Open(os.path.join(args[0],f))
        tag=os.path.splitext(f)[0]
        tag=tag.replace('_results','')
        tag=tag.replace('nominal_','')
        tag=tag.replace('v5','.5')
        for key in fIn.GetListOfKeys():
            keyName=key.GetName()
            mtop=fIn.Get(keyName+'/mtop')
            if not(keyName in results):
                results[keyName]={}
            results[keyName][tag]=(mtop[0],mtop[1])
        fIn.Close()
        

    
    #show results
    print '{0:12s}'.format(''),
    for cat in sorted(results, reverse=False):
        print '{0:12s}'.format(cat),
    print ' '
    print 80*'-'
    for expTag in sorted(results.itervalues().next(),reverse=False):
        if expTag=='172.5' : continue
        if expTag=='p11_172.5': continue
        if expTag=='bfrac_172.5': continue
        print '{0:12s}'.format(expTag),
        for cat in sorted(results, reverse=False):           
            
            expTag2diff='172.5'
            if 'p11' in expTag:     expTag2diff='p11_172.5'
            if 'powherw' in expTag: expTag2diff='powpyth_172.5'
            if 'bfrag' in expTag:   expTag2diff='bfrag_172.5'

            diff=results[cat][expTag][0]-results[cat][expTag2diff][0]
            print '{0:12s}'.format('%3.2f'%(diff)),
            #diffErr=math.sqrt( math.pow(results[cat][expTag][1],2)+pow(results[cat][expTag2diff][1],2))
            #print '%3.2f \pm %3.2f'%(diff,diffErr),            
        print ' '
    print 80*'-'
    return 0



if __name__ == "__main__":
    sys.exit(main())
