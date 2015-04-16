#!/usr/bin/env python
import ROOT
import os,sys,re
import optparse
import math
import pickle
from UserCode.TopMassSecVtx.rounding import *
from UserCode.TopMassSecVtx.PlotUtils import bcolors
from makeSVLMassHistos import NTRKBINS
COLORS=[ROOT.kMagenta, ROOT.kMagenta+2,ROOT.kMagenta-9, ROOT.kViolet+2,ROOT.kAzure+7, ROOT.kBlue-7,ROOT.kYellow-3]
from pprint import pprint

"""
"""
def parseEnsembles(url,selection='',rebin=4):
     ensemblesMap={}
     peInputFile = ROOT.TFile.Open(url, 'READ')
     allExperiments = [tkey.GetName() for tkey in peInputFile.GetListOfKeys()]

     for experimentTag in allExperiments:

         #check tag to be assigned
         tag=''
         tag='massscan' if 'nominal'  in experimentTag else tag
         tag='matching' if 'matching' in experimentTag else tag
         tag='scale'    if 'scale'    in experimentTag else tag
         tag='toppt'    if 'toppt'    in experimentTag else tag
         tag='bfrag'    if 'bfrag'    in experimentTag else tag
         tag='bfn'      if 'bfn'      in experimentTag else tag
         tag='p11'      if 'p11'      in experimentTag else tag
         tag='jes'      if 'jes'      in experimentTag else tag
         tag='powheg'   if 'powpyth'  in experimentTag else tag
         tag='powheg'   if 'powherw'  in experimentTag else tag
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
             grKey=grKey.replace('_',' ',99)
             grKey=experimentTag.replace(grKey,'')
         else:
             grKey=grKey.replace('v','.')

         for chsel in ['em','mm','ee','m','e','inclusive']:
             if len(selection)>0 : chsel += '_' + selection
             for ntrk in [tklow for tklow,_ in NTRKBINS]: # [2,3,4]
                 ihist   = peInputFile.Get('%s/SVLMass_%s_%s_%d'%(experimentTag,chsel,experimentTag,ntrk)).Clone()
                 refHist = peInputFile.Get('%s/SVLMass_%s_%s_%d'%(refTag,chsel,refTag,ntrk)).Clone()
                 ihist.Rebin(rebin)
                 refHist.Rebin(rebin)
                 ihist.Divide(refHist)
                 key=chsel+'_'+str(ntrk)
                 key=key.replace('inclusive','comb')
                 if not(key in ensemblesMap[tag]): ensemblesMap[tag][key]={}

                 ensemblesMap[tag][key][grKey]=ROOT.TGraphErrors(ihist)
                 ensemblesMap[tag][key][grKey].SetName('ratio_%s_%s_%d'%(chsel,experimentTag,ntrk))
                 ensemblesMap[tag][key][grKey].SetTitle(grKey)
                 color=COLORS[len(ensemblesMap[tag][key])-1]
                 if tag==refTag: color=1
                 ensemblesMap[tag][key][grKey].SetFillStyle(0)
                 ensemblesMap[tag][key][grKey].SetMarkerColor(color)
                 ensemblesMap[tag][key][grKey].SetLineColor(color)
                 ensemblesMap[tag][key][grKey].SetMarkerStyle(20)
                 ensemblesMap[tag][key][grKey].SetMarkerSize(1.0)

                 ihist.Delete()
                 refHist.Delete()

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
        selection = ''
        try:
             # either ['nominal', '172v5', 'results'] or
             #        ['nominal', '172v5', 'mrank1', 'results']
            syst, massstr, selection, _ = tag.rsplit('_', 3)
        except ValueError:
            syst, massstr, _ = tag.rsplit('_', 2)

        # Extract a XXXvX number from the tag string:
        # This is a bit superfluous, but it will catch if something went wrong
        # in the splitting above (e.g. a syst name containing a '_')
        mass = re.search(r'[\w]*([\d]{3}v[\d]{1})+[\w]*', tag).group(1)
        mass = float(mass.replace('v5','.5'))
        assert(mass == float(massstr.replace('v5','.5')))

        # print '... processing %-12s, %5.1f, %s' % (syst,mass,selection)

        useForCalib=True if 'nominal' in syst else False

        for key in fIn.GetListOfKeys():
            keyName=key.GetName()
            norm=fIn.Get(keyName+'/norm')
            mtop=fIn.Get(keyName+'/mtop')
            if selection is not '' and selection in keyName:
                keyName = keyName.replace('%s_'%selection,'')
            if not((keyName,selection) in results):
                results[(keyName,selection)] = {}
            if syst == 'nominal':
                syst = str(mass)
            results[(keyName,selection)][syst]=(mtop[0],mtop[1]/math.sqrt(norm[0]))

            # add point for calibration
            if not useForCalib: continue
            np=0
            try:
                np=calibGrMap[keyName][selection].GetN()
            except KeyError:
                if not keyName in calibGrMap:
                    calibGrMap[keyName] = {}
                calibGrMap[keyName][selection]=ROOT.TGraphErrors()
                calibGrMap[keyName][selection].SetName(keyName)
                title=keyName.replace('_',', ')
                if 'comb' in title:
                    title='combination'
                else:
                    title=title.replace('m','#mu')
                    title += ' tracks'
                calibGrMap[keyName][selection].SetTitle(title)
                calibGrMap[keyName][selection].SetMarkerStyle(20)
                calibGrMap[keyName][selection].SetMarkerSize(1.0)
                np=calibGrMap[keyName][selection].GetN()
            calibGrMap[keyName][selection].SetPoint     (np, mass, mtop[0]-mass)
            calibGrMap[keyName][selection].SetPointError(np, 0,  mtop[1]/math.sqrt(norm[0]))
        fIn.Close()

    return results, calibGrMap

"""
Shows results
"""
def show(grCollMap,outDir,outName,xaxisTitle,yaxisTitle,yrange=(-1.5,1.5),baseDrawOpt='p',doFit=False):
    if not os.path.exists(outDir):
        os.system('mkdir -p %s' % outDir)
    #save calibration to pickle
    fitParamsMap={}
    nx=3
    ny=int(len(grCollMap)/nx)
    while ny*nx<len(grCollMap) : ny+=1
    canvas=ROOT.TCanvas('c','c',nx*400,ny*250)
    canvas.Divide(nx,ny)
    ip=0
    allLegs=[]
    for key,grColl in sorted(grCollMap.items()):

        igrctr=0

        nleg=-1
        if 'comb' in key:
             nleg=len(allLegs)
             allLegs.append(ROOT.TLegend(0.2,0.2,0.9,0.8))
             allLegs[nleg].SetFillStyle(0)
             allLegs[nleg].SetTextFont(42)
             allLegs[nleg].SetTextSize(0.06)
             allLegs[nleg].SetBorderSize(0)
             allLegs[nleg].SetNColumns(2)
        for tag,gr in sorted(grColl.items()):
            gr.Sort()
            gr.SetMarkerStyle(gr.GetMarkerStyle()+igrctr)
            igrctr+=1

            if doFit:
                gr.Fit('pol1','MQ+')
                offset=gr.GetFunction('pol1').GetParameter(0)
                slope=gr.GetFunction('pol1').GetParameter(1)
                gr.GetFunction('pol1').SetLineColor(ROOT.kBlue)
                fitParamsMap[key]=(offset,slope)

            drawOpt='a'+baseDrawOpt if igrctr==1 else baseDrawOpt
            if 'comb' in key :
                if igrctr==1 :
                    p=canvas.cd(2+nx*(ny-1))
                gr.Draw(drawOpt)
                allLegs[nleg].AddEntry(gr,gr.GetTitle(),baseDrawOpt)
            else:
                if igrctr==1 :
                    ip+=1
                    p=canvas.cd(ip)
                gr.Draw(drawOpt)
            gr.GetYaxis().SetRangeUser(yrange[0],yrange[1])
            gr.GetYaxis().SetNdivisions(5)

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
            allLegs[nleg].Draw()


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

    for ext in ['png','pdf']:
        canvas.SaveAs(os.path.join(outDir,'%s.%s'%(outName,ext)))
    return fitParamsMap


"""
Prints the table of systematics
"""
def showSystematicsTable(results):
    # pprint(results)
    #show results
    selections = list(set([s for _,s in results.keys()]))
    categories = list(set([k for k,_ in results.keys()]))

    for sel in selections:
        print 140*'-'
        print bcolors.BOLD+sel+bcolors.ENDC
        print 14*' ',
        for cat in sorted(categories):
                print '{0:7s}'.format(cat),
        print ' '
        print 140*'-'
        for expTag in sorted(results.itervalues().next()):
            if expTag in ['172.5', 'p11_172.5', 'bfrag_172.5']: continue
            print '{0:12s}'.format(expTag.replace('_172.5','')),
            for cat in sorted(categories):

                expTag2diff='172.5'
                if 'p11' in expTag:     expTag2diff='p11'
                if expTag == 'p11':     expTag2diff='172.5'
                if 'powherw' in expTag: expTag2diff='powpyth'
                if 'bfrag' in expTag:   expTag2diff='bfrag'

                diff = results[(cat,sel)][expTag][0]-results[(cat,sel)][expTag2diff][0]
                diffstr = ' %6.3f'%diff
                if expTag not in ['166.5','169.5','171.5','173.5','175.5','178.5']:
                    if abs(diff) > 0.5 and abs(diff) < 1.0:
                        diffstr = "%7s"%(bcolors.YELLOW+diffstr+bcolors.ENDC)
                    if abs(diff) >= 1.0:
                        diffstr = "%7s"%(bcolors.RED+diffstr+bcolors.ENDC)
                diffErr = math.sqrt( results[(cat,sel)][expTag][1]**2+results[(cat,sel)][expTag2diff][1]**2 )
                print diffstr,
                #print '{0:12s}'.format(toLatexRounded(diff,diffErr)),
            print ' '
        print 140*'-'
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
    parser.add_option('--rebin', dest='rebin',   default=4,    type=int, help='rebin pe plots by this factor')
    parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
                      help='Output directory [default: %default]')
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
        showSystematicsTable(results=results)

    if opt.peInput:
    	for sel in ['','mrank1']:
	        ensemblesMap=parseEnsembles(url=opt.peInput, selection=sel,rebin=opt.rebin)
	        for tag,grMap in ensemblesMap.items():
	            outName = tag if sel == '' else '%s_%s'%(tag,sel)
	            show(grCollMap=ensemblesMap[tag],
	                 outDir=opt.outDir,
	                 outName=outName,
	                 yaxisTitle='Ratio to reference',
	                 xaxisTitle='m(SV,lepton) [GeV]',
	                 yrange=(0.75,1.25),
	                 baseDrawOpt='lx',
	                 doFit=False)
    return


if __name__ == "__main__":
    sys.exit(main())
