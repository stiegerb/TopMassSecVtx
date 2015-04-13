#!/usr/bin/env python
import ROOT
import os,sys
import optparse
import math
import pickle
from UserCode.TopMassSecVtx.rounding import *
from makeSVLMassHistos import NTRKBINS

"""
"""
def parseEnsembles(url,selection=''):
     ensemblesMap={}
     peInputFile = ROOT.TFile.Open(url, 'READ')
     allExperiments = [tkey.GetName() for tkey in peInputFile.GetListOfKeys()]
     
     for experimentTag in allExperiments:

         #check tag to be assigned
         tag=''
         tag='massscan' if 'nominal' in experimentTag else tag
         tag='matching' if 'matching' in experimentTag else tag
         tag='scale'    if 'scale' in experimentTag else tag
         tag='toppt'    if 'toppt' in experimentTag else tag       
         tag='bfrag'    if 'bfrag' in experimentTag else tag
         tag='bfn'      if 'bfn' in experimentTag else tag
         tag='p11'      if 'p11' in experimentTag else tag
         tag='jes'      if 'jes' in experimentTag else tag
         tag='powheg'   if 'pow' in experimentTag else tag
         if len(tag)==0 : 
             continue
         if not (tag in ensemblesMap) : ensemblesMap[tag]={}

         #reference tag
         refTag=''
         refTag='nominal_172v5' if 'massscan' in tag else refTag
         refTag='nominal_172v5' if 'matching' in tag else refTag
         refTag='nominal_172v5' if 'scale' in tag else refTag
         refTag='nominal_172v5' if 'toppt' in tag else refTag
         refTag='nominal_172v5' if 'jes' in tag else refTag
         #refTag='bfrag_172v5'   if 'bfrag' in tag else refTag
         refTag='nominal_172v5'   if 'bfrag' in tag else refTag
         refTag='nominal_172v5' if 'bfn' in tag else refTag
         refTag='p11_172v5'     if 'p11' in tag else refTag
         refTag='nominal_172v5' if 'powheg' in tag else refTag
         if len(refTag)==0 : continue

         #parse mtop
         grKey=experimentTag.rsplit('_', 1)[1]
         if not 'massscan' in tag:
             grKey=grKey.replace('_',' ')
             grKey=experimentTag.replace(grKey,'')
         else:
             grKey=grKey.replace('v','.')
     

         for chsel in ['em','mm','ee','m','e']:
             if len(selection)>0 : chsel += '_' + selection
             for ntrk in [tklow for tklow,_ in NTRKBINS]: # [2,3,4]                 
                 ihist   = peInputFile.Get('%s/SVLMass_%s_%s_%d'%(experimentTag,chsel,experimentTag,ntrk))
                 refHist = peInputFile.Get('%s/SVLMass_%s_%s_%d'%(refTag,chsel,refTag,ntrk))
                 ratio=ihist.Clone('ratio')
                 ratio.Divide(refHist)
                 
                 key=chsel+'_'+str(ntrk)
                 if not(key in ensemblesMap[tag]): ensemblesMap[tag][key]={}

                 ensemblesMap[tag][key][grKey]=ROOT.TGraphErrors(ratio)
                 ensemblesMap[tag][key][grKey].SetName('ratio_%s_%s_%d'%(chsel,experimentTag,ntrk))
                 ensemblesMap[tag][key][grKey].SetTitle(grKey)
                 ensemblesMap[tag][key][grKey].SetMarkerStyle(20)
                 ensemblesMap[tag][key][grKey].SetMarkerSize(1.0)
                 ratio.Delete()

     return ensemblesMap

"""
Loops over the results in a directory and build the map
"""
def parsePEResultsFromFile(url):

    results, calibGrMap = {}, {}
    fileNames=[f for f in os.listdir(url) if f.endswith('root')]
    for f in fileNames :
        fIn=ROOT.TFile.Open(os.path.join(url,f))
        tag=os.path.splitext(f)[0]
        useForCalib=False
        if 'nominal' in tag : useForCalib=True
        tag=tag.replace('_results','')
        tag=tag.replace('nominal_','')
        tag=tag.replace('v5','.5')
        for key in fIn.GetListOfKeys():
            keyName=key.GetName()
            norm=fIn.Get(keyName+'/norm')
            mtop=fIn.Get(keyName+'/mtop')
            if not(keyName in results) : results[keyName]={}
            results[keyName][tag]=(mtop[0],mtop[1]/math.sqrt(norm[0]))

            #add point for calibration
            #FIXME: parse selection type: inc, mrank1,...
            if not useForCalib: continue
            np=0
            try:
                np=calibGrMap[keyName][''].GetN()
            except:
                if not keyName in calibGrMap : calibGrMap[keyName]={}
                calibGrMap[keyName]['']=ROOT.TGraphErrors()
                calibGrMap[keyName][''].SetName(keyName)
                title=keyName.replace('_',', ')
                if 'comb' in title:
                    title='combination'
                else:
                    title=title.replace('m','#mu')
                    title += ' tracks'
                calibGrMap[keyName][''].SetTitle(title)
                calibGrMap[keyName][''].SetMarkerStyle(20)
                calibGrMap[keyName][''].SetMarkerSize(1.0)
                np=calibGrMap[keyName][''].GetN()
            calibGrMap[keyName][''].SetPoint     (np, float(tag), mtop[0]-float(tag))
            calibGrMap[keyName][''].SetPointError(np, 0,          mtop[1]/math.sqrt(norm[0]))
        fIn.Close()

    return results, calibGrMap

"""
Shows results
"""
def show(grCollMap,outDir,outName,xaxisTitle,yaxisTitle,yrange=(-1.5,1.5),doFit=False):

    #save calibration to pickle
    fitParamsMap={}
    nx=3
    ny=int(len(grCollMap)/nx)
    while ny*nx<len(grCollMap) : ny+=1
    canvas=ROOT.TCanvas('c','c',nx*400,ny*250)
    canvas.Divide(nx,ny)
    ip=0
    for key,grColl in sorted(grCollMap.items()):

        igrctr=0
        leg=None
        if ip==0:
            leg=ROOT.TLegend(0.2,0.8,0.95,0.9)
            leg.SetFillStyle(0)
            leg.SetTextFont(42)
            leg.SetTextSize(0.04)
            leg.SetBorderSize(0)
            leg.SetNColumns(len(grColl))
        for tag,gr in sorted(grColl.items()):
            gr.Sort()
            gr.SetMarkerStyle(gr.GetMarkerStyle()+igrctr)
            igrctr+=1
            drawOpt='ap' if igrctr==1 else 'p'
            if doFit:
                gr.Fit('pol1','MQ+')
                offset=gr.GetFunction('pol1').GetParameter(0)
                slope=gr.GetFunction('pol1').GetParameter(1)
                gr.GetFunction('pol1').SetLineColor(ROOT.kBlue)
                fitParamsMap[key]=(offset,slope)
        
            if 'comb' in key : 
                if igrctr==1 :
                    p=canvas.cd(2+nx*(ny-1))
                gr.Draw(drawOpt)
            else:
                if igrctr==1 :
                    ip+=1
                    p=canvas.cd(ip)
                gr.Draw(drawOpt)
                
            drawOpt='p'
            if leg : leg.AddEntry(gr,gr.GetTitle(),'p')
            gr.GetYaxis().SetRangeUser(yrange[0],yrange[1])
            gr.GetYaxis().SetNdivisions(5)
            
        if leg :
            leg.Draw()
            #ROOT.SetOwnership(leg,p)
        p.SetGridy()
        label=ROOT.TLatex()
        label.SetNDC()
        label.SetTextFont(42)
        label.SetTextSize(0.08)
        title=key
        if 'comb' in title:
            title='combination'
        else:
            title=title.replace('m','#mu')
            title=title.replace('_',', ')
            title += ' tracks'
        label.DrawLatex(0.2,0.8,'#it{'+title+'}')
        if 'comb' in key:
            p.SetLeftMargin(0.03)
            p.SetRightMargin(0.03)
            gr.GetYaxis().SetRangeUser(-1.5,1.5)
            gr.GetYaxis().SetTitle(yaxisTitle)
            gr.GetYaxis().SetNdivisions(5)
            gr.GetYaxis().SetTitleOffset(0.8)
            gr.GetYaxis().SetTitleSize(0.1)
            gr.GetYaxis().SetLabelSize(0.08)
            gr.GetXaxis().SetTitle(xaxisTitle)
            gr.GetXaxis().SetTitleOffset(0.8)
            gr.GetXaxis().SetTitleSize(0.1)
            gr.GetXaxis().SetLabelSize(0.08)
            p=canvas.cd(1+nx*(ny-1))
            label.DrawLatex(0.2,0.8,'#bf{CMS} #it{simulation}')
            continue

        if (ip-1)%nx==0:
            p.SetLeftMargin(0.15)
            p.SetRightMargin(0.03)
            gr.GetYaxis().SetTitle(yaxisTitle)
            gr.GetYaxis().SetTitleOffset(0.8)
            gr.GetYaxis().SetTitleSize(0.1)
            gr.GetYaxis().SetLabelSize(0.08)
        else:
            p.SetLeftMargin(0.03)
            p.SetRightMargin(0.03)
            gr.GetYaxis().SetLabelSize(0)
            gr.GetYaxis().SetTitleSize(0)

        if ip>=len(grCollMap)-nx:
            p.SetTopMargin(0.03)
            p.SetBottomMargin(0.03)
            gr.GetXaxis().SetTitle(xaxisTitle)
            gr.GetXaxis().SetTitleOffset(0.8)
            gr.GetXaxis().SetTitleSize(0.1)            
            gr.GetXaxis().SetLabelSize(0.08)
        else:
            p.SetTopMargin(0.03)
            p.SetBottomMargin(0.03)
            gr.GetXaxis().SetTitleSize(0)
            gr.GetXaxis().SetLabelSize(0)

    for ext in ['png','pdf'] : canvas.SaveAs('%s/%s.%s'%(outDir,outName,ext))
    return fitParamsMap


"""
Prints the table of systematics
"""
def showSystematicsTable(results):
    #show results
    print '{0:12s}'.format(''),
    for cat in sorted(results, reverse=False) : print '{0:12s}'.format(cat),
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
            diffErr=math.sqrt( results[cat][expTag][1]**2+results[cat][expTag2diff][1]**2 )
            print '{0:12s}'.format('%3.3f'%diff),
            #print '{0:12s}'.format(toLatexRounded(diff,diffErr)),
        print ' '
    print 80*'-'
    return 0


"""
steer
"""
def main():
    usage = """
    Parses the results for pseudo-experiments stored in a directory and produces a summary
    usage: %prog directory
    """

    parser = optparse.OptionParser(usage)
    parser.add_option('--pe',    dest='peInput', default=None, help='compare ensembles for pseudo-experiments')
    parser.add_option('--calib', dest='calib',   default=None, help='show calibration')
    (opt, args) = parser.parse_args()

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gROOT.SetBatch(True)
    
    #parse calibration results from directory
    if opt.calib:
        results,calibGrMap = parsePEResultsFromFile(url=opt.calib)
        calibMap = show(grCollMap=calibGrMap,                        
                        outDir=opt.calib,
                        outName='svlcalib',
                        yaxisTitle='#Deltam_{t} [GeV]',
                        xaxisTitle='Generated m_{t} [GeV]',
                        doFit=True)
        calibFile=os.path.join(opt.calib,'.svlcalib.pck')
        cachefile = open(calibFile, 'w')
        pickle.dump(calibMap, cachefile, pickle.HIGHEST_PROTOCOL)
        cachefile.close()
        print 'Wrote %s with calibration constants'%calibFile
        #showSystematicsTable(results=results)

    if opt.peInput:
        ensemblesMap=parseEnsembles(url=opt.peInput)
        for tag,grMap in ensemblesMap.items():
            show(grCollMap=ensemblesMap[tag],                        
                 outDir='svlfits',
                 outName=tag,
                 yaxisTitle='m(SV,lepton) [GeV]',
                 xaxisTitle='Ratio to reference',
                 yrange=(0.5,2),
                 doFit=False)
    return


if __name__ == "__main__":
    sys.exit(main())
