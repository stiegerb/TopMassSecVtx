#!/usr/bin/env python
import ROOT
import os,sys,re
import optparse
import math
import pickle

from UserCode.TopMassSecVtx.rounding import toLatexRounded
from UserCode.TopMassSecVtx.PlotUtils import bcolors,getContours
from makeSVLMassHistos import NTRKBINS
COLORS=[ROOT.kMagenta, ROOT.kMagenta+2,ROOT.kMagenta-9, ROOT.kViolet+2,ROOT.kAzure+7, ROOT.kBlue-7,ROOT.kYellow-3]
from pprint import pprint

CATTOLABEL = {
  'comb_0'   : 'Combined',
  'comb_3'   : '=3 trks',
  'comb_4'   : '=4 trks',
  'comb_5'   : '=5 trks',
  'combe_0'  : 'e+jets',
  'combee_0' : 'ee',
  'combem_0' : 'emu',
  'combm_0'  : 'mu+jets',
  'combmm_0' : 'mumu',
}

"""
"""
def parsePEInputs(url,selection='',rebin=4):
     ensemblesMap={}
     peInputFile = ROOT.TFile.Open(url, 'READ')
     allExperiments = [tkey.GetName() for tkey in peInputFile.GetListOfKeys()]

     for experimentTag in allExperiments:

         #check tag to be assigned
         tag=''
         tag='les'      if 'les'      in experimentTag else tag
         tag='lepsel'   if 'lepsel'   in experimentTag else tag
         tag='umet'     if 'umet'     in experimentTag else tag
         tag='pu'       if 'pu'       in experimentTag else tag
         tag='massscan' if 'nominal'  in experimentTag else tag
         tag='matching' if 'matching' in experimentTag else tag
         tag='scale'    if 'scale'    in experimentTag else tag
         tag='toppt'    if 'toppt'    in experimentTag else tag
         tag='bfrag'    if 'bfrag'    in experimentTag else tag
         tag='bfn'      if 'bfn'      in experimentTag else tag
         tag='p11'      if 'p11'      in experimentTag else tag
         tag='jes'      if 'jes'      in experimentTag else tag
         tag='powheg'   if 'powpyth'  in experimentTag else tag
         #tag='powheg'   if 'powherw'  in experimentTag else tag
         if len(tag)==0 :
             continue
         if not (tag in ensemblesMap) : ensemblesMap[tag]={}

         #reference tag
         refTag=''
         refTag='nominal_172v5' if 'lepsel'   in tag else refTag
         refTag='nominal_172v5' if 'les'      in tag else refTag
         refTag='nominal_172v5' if 'pu'       in tag else refTag
         refTag='nominal_172v5' if 'umet'     in tag else refTag
         refTag='nominal_172v5' if 'massscan' in tag else refTag
         refTag='nominal_172v5' if 'matching' in tag else refTag
         refTag='nominal_172v5' if 'scale'    in tag else refTag
         refTag='nominal_172v5' if 'toppt'    in tag else refTag
         refTag='nominal_172v5' if 'jes'      in tag else refTag
         refTag='nominal_172v5' if 'bfrag'    in tag else refTag
         refTag='nominal_172v5' if 'bfn'      in tag else refTag
         refTag='p11_172v5'     if 'p11'      in tag else refTag
         refTag='nominal_172v5' if 'powheg'   in tag else refTag
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
Analyze final results for a given category
"""
def analyzePEresults(key,fIn,outDir,doPlots=True,syst=''):

     PEsummary={}

     #show results
     canvas = ROOT.TCanvas('c_%s_%s'%(key,syst),'c',1500,500)
     canvas.Divide(3,1)

     #bias
     canvas.cd(1)
     mtopFitH=fIn.Get('%s/mtopfit_%s'%(key,key))
     mtopFitH.Draw()
     mtopFitH.Fit('gaus','LMQ+')
     try:
          gaus=mtopFitH.GetFunction('gaus')
          PEsummary['bias']=(gaus.GetParameter(1),gaus.GetParError(1))
     except:
          pass
     label=ROOT.TLatex()
     label.SetNDC()
     label.SetTextFont(42)
     label.SetTextSize(0.04)
     label.DrawLatex(0.1,0.92,'#bf{CMS} #it{simulation}')
     if 'bias' in PEsummary : label.DrawLatex(0.15,0.80,'<m_{t}>=%3.3f#pm%3.3f'%(PEsummary['bias'][0],PEsummary['bias'][1]))
     channelTitle=key.replace('_',', ')
     label.DrawLatex(0.15,0.84,channelTitle)

     #stat unc
     #canvas.cd(2)
     mtopFitStatH=fIn.Get('%s/mtopfit_statunc_%s'%(key,key))
     #mtopFitStatH.Draw('hist')
     #mtopFitStatH.SetFillStyle(1001)
     #mtopFitStatH.SetFillColor(ROOT.kGray)
     #label.DrawLatex(0.15,0.80,
     #                '<#sigma_{stat}>=%3.3f #sigma(#sigma_{stat})=%3.3f'
     #                %(mtopFitStatH.GetMean(),mtopFitStatH.GetRMS()))
     PEsummary['stat']=(mtopFitStatH.GetMean(),mtopFitStatH.GetMeanError())

     #pull
     canvas.cd(2)
     mtopFitPullH=fIn.Get('%s/mtopfit_pull_%s'%(key,key))
     mtopFitPullH.Rebin(4)
     mtopFitPullH.Draw()
     mtopFitPullH.Fit('gaus','LMQ+')
     try:
          gaus=mtopFitPullH.GetFunction('gaus')
          PEsummary['pull']=(gaus.GetParameter(1),gaus.GetParameter(2))
          label.DrawLatex(0.15,0.80,'<pull>=%3.3f  #sigma(pull)=%3.3f'%(gaus.GetParameter(1),gaus.GetParameter(2)))
     except:
          pass

     #correlation with signal strength
     canvas.cd(3)
     fitCorrH=fIn.Get('%s/muvsmtop_%s'%(key,key))
     fitCorrH.Draw('contz')
     #cont=getContours(fitCorrH)
     #drawOpt='ac'
     #for gr in cont:
     #     gr.Draw(drawOpt)
     #     drawOpt='c'
     #     gr.GetXaxis().SetTitle(fitCorrH.GetXaxis().GetTitle())
     #     gr.GetYaxis().SetTitle(fitCorrH.GetYaxis().GetTitle())
     label.DrawLatex(0.15,0.80,'#rho(m_{t},#mu)=%3.3f'%fitCorrH.GetCorrelationFactor())

     #all done, save
     canvas.cd()
     canvas.Modified()
     canvas.Update()

     if doPlots:
           pename=os.path.splitext(os.path.basename(fIn.GetName()))[0]
           for ext in ['png','pdf']:
                  canvas.SaveAs('%s/plots/%s_%s.%s'%(outDir,key,pename,ext))

     ## Return results
     return PEsummary


"""
Loops over the results in a directory and builds a map of PE results
"""
def parsePEResultsFromFile(url,verbose=False):

    results, calibGrMap = {}, {}
    fileNames=[f for f in os.listdir(url) if f.endswith('results.root')]
    for f in fileNames:
        fIn=ROOT.TFile.Open(os.path.join(url,f))

        tag=os.path.splitext(f)[0]
        selection = ''
        try:
            syst, massstr, selection, _ = tag.rsplit('_', 3)
        except ValueError:
            syst, massstr, _ = tag.rsplit('_', 2)

        # Extract a XXXvX number from the tag string:
        # This is a bit superfluous, but it will catch if something went wrong
        # in the splitting above (e.g. a syst name containing a '_')
        mass = re.search(r'[\w]*([\d]{3}v[\d]{1})+[\w]*', tag).group(1)
        mass = float(mass.replace('v5','.5'))
        assert(mass == float(massstr.replace('v5','.5')))

        if verbose:
              print '%sSyst: %s, %5.1f GeV, %s%s' % (bcolors.BOLD,
                                                     syst, mass, selection,
                                                     bcolors.ENDC)


        useForCalib=True if 'nominal' in syst else False
        for key in fIn.GetListOfKeys():
             if verbose:
                  print '  %-18s  ' % key.GetName(),

             keyName=key.GetName()
             PEsummary=analyzePEresults(key=keyName,fIn=fIn,outDir=url,doPlots=True,syst=syst)
             if not 'bias' in PEsummary : continue

             bias, biasErr = PEsummary['bias']
             if verbose:
                  print '%6.3f +- %5.3f' % (bias, biasErr)


             #save results
             if selection is not '' and selection in keyName:
                  keyName = keyName.replace('%s_'%selection,'')
             if not((keyName,selection) in results):
                  results[(keyName,selection)] = {}

             if syst == 'nominal': syst = str(mass)

             # add point for systematics
             # if not useForCalib or mass==172.5:
             results[(keyName,selection)][syst] = (mass+bias,biasErr)
             if not useForCalib:
                  continue

             # otherwise use it for calibration
             np=0
             try:
                  np=calibGrMap[keyName][selection].GetN()
             except KeyError:
                  if not keyName in calibGrMap:
                        calibGrMap[keyName] = {}
                  calibGrMap[keyName][selection] = ROOT.TGraphErrors()
                  calibGrMap[keyName][selection].SetName(keyName)
                  calibGrMap[keyName][selection].SetTitle(selection)
                  calibGrMap[keyName][selection].SetMarkerStyle(20)
                  calibGrMap[keyName][selection].SetMarkerSize(1.0)
                  np = calibGrMap[keyName][selection].GetN()

             #require less than 1 GeV in unc.
             if biasErr<1:
                  calibGrMap[keyName][selection].SetPoint     (np, mass, mass+bias)
                  calibGrMap[keyName][selection].SetPointError(np, 0, biasErr)
        fIn.Close()

    return results, calibGrMap

"""
Shows results
"""
def show(grCollMap,outDir,outName,xaxisTitle,yaxisTitle,
         y_range=(160,190),x_range=(160,190),
         baseDrawOpt='p',doFit=False, verbose=False):

     #prepare output
     if not os.path.exists(outDir): os.system('mkdir -p %s' % outDir)

     #fit results
     fitParamsMap={}

     #prepare results
     nx=3
     ny=int(len(grCollMap)/nx)
     while ny*nx<len(grCollMap) : ny+=1

     canvas = ROOT.TCanvas('c','c',nx*400,ny*250)
     canvas.Divide(nx,ny)
     ip=0
     allLegs = []
     line=ROOT.TLine(x_range[0],y_range[0],x_range[1],y_range[1])
     line.SetLineStyle(2)
     line.SetLineColor(ROOT.kGray)
     for key,grColl in sorted(grCollMap.items()):

          ip+=1
          if ip==1:
               nleg=len(allLegs)
               allLegs.append(ROOT.TLegend(0.2,0.5,0.6,0.8))
               allLegs[nleg].SetFillStyle(0)
               allLegs[nleg].SetTextFont(42)
               allLegs[nleg].SetTextSize(0.06)
               allLegs[nleg].SetBorderSize(0)

          yTitleOffset, yLabelSize = 0, 0
          if 'comb_0' in key:
               padCtr=1
               ip-=1
               yTitleOffset, yLabelSize=0.8,0.07
          else:
               padCtr=ip+1
          p = canvas.cd(padCtr)

          # if (padCtr-1)%nx==0:
          p.SetLeftMargin(0.15)
          p.SetRightMargin(0.03)
          yTitleOffset, yLabelSize=0.8,0.07
          # else:
          #      p.SetLeftMargin(0.03)
          #      p.SetRightMargin(0.03)
          #      yTitleOffset, yLabelSize=0.,0.0

          p.SetTopMargin(0.03)
          p.SetBottomMargin(0.15)
          p.SetGridy()
          p.SetGridx()

          #draw graphs on pads
          igrctr=0
          color=[ROOT.kBlack, ROOT.kMagenta, ROOT.kMagenta+2,ROOT.kMagenta-9,ROOT.kViolet+2,ROOT.kAzure+7, ROOT.kBlue-7,ROOT.kYellow-3]
          for tag,gr in sorted(grColl.items()):
               gr.Sort()
               gr.SetMarkerStyle(20+igrctr)
               gr.SetMarkerColor(color[igrctr])
               gr.SetLineColor(color[igrctr])
               if doFit:
                    gr.Fit('pol1','MQ+','same')
                    offset=gr.GetFunction('pol1').GetParameter(0)
                    slope=gr.GetFunction('pol1').GetParameter(1)
                    gr.GetFunction('pol1').SetLineColor(ROOT.kBlue)

                    if verbose:
                         try: keyname = CATTOLABEL[key]
                         except KeyError: keyname = key
                         print ('%-20s (%5.3f, %6.3f GeV) (slope, offset at central point)' %
                                   (keyname,
                                    slope, (offset+slope*172.5)-172.5))
                    #add to map
                    title=gr.GetTitle()
                    if not (title in fitParamsMap): fitParamsMap[title]={}
                    # Inverted x and y, so have to invert fit parameters
                    fitParamsMap[title][key]=(-1.0*offset/slope,1.0/slope)
                    # fitParamsMap[title][key]=(offset,slope)

               igrctr+=1
               drawOpt='a'+baseDrawOpt if igrctr==1 else baseDrawOpt
               if ip==1 : allLegs[nleg].AddEntry(gr,gr.GetTitle(),baseDrawOpt)
               gr.Draw(drawOpt)

               gr.GetYaxis().SetRangeUser(y_range[0],y_range[1])
               gr.GetXaxis().SetRangeUser(x_range[0],x_range[1])
               gr.GetYaxis().SetNdivisions(5)
               gr.GetXaxis().SetTitle(xaxisTitle)
               gr.GetYaxis().SetTitle(yaxisTitle)
               gr.GetYaxis().SetTitleOffset(yTitleOffset)
               gr.GetYaxis().SetTitleSize(yLabelSize)
               gr.GetYaxis().SetLabelSize(yLabelSize)
               gr.GetXaxis().SetTitleSize(0.07)
               gr.GetXaxis().SetLabelSize(0.07)

          if doFit: line.Draw('same')

          #label this pad
          label=ROOT.TLatex()
          label.SetNDC()
          label.SetTextFont(42)
          label.SetTextSize(0.08)
          title=key
          title=title.replace('_',', ')
          if 'comb' in title:
               title=title.replace('comb','combination ')
               title=title.replace('0','')
          else:
               title=title.replace('m','#mu')
               title += ' tracks'
          label.DrawLatex(0.2,0.8,'#it{'+title+'}')

     #independentently of 'comb_0' being found, draw legend in first pad
     canvas.cd(1)
     allLegs[nleg].Draw()
     label.DrawLatex(0.2,0.9,'#bf{CMS} #it{simulation}')
     canvas.cd()

     #all done
     canvas.Modified()
     canvas.Update()
     for ext in ['png','pdf']:
          canvas.SaveAs(os.path.join(outDir,'%s.%s'%(outName,ext)))
     return fitParamsMap


"""
Prints the table of systematics
"""
def showSystematicsTable(results,filterCats):
    #show results
    selections = list(set([s for _,s in results.keys()]))
    categories = list(set([k for k,_ in results.keys()]))

    # pprint(results)
    # return 0
    for sel in selections:
        print 140*'-'
        print bcolors.BOLD+sel+bcolors.ENDC
        print 20*' ','&',
        for cat in sorted(categories):
             if not cat in filterCats: continue
             print '{0:^20s}'.format(CATTOLABEL[cat]),'&',
        print '\\\\'
        print 140*'-'
        for expTag in sorted(results.itervalues().next()):
             # if expTag in ['nominal', '172.5', 'p11_172.5', 'bfrag_172.5']: continue
             if expTag == 'powherw': continue
             print '{0:20s}'.format(expTag.replace('_172.5','')),'&',
             for cat in sorted(categories):

                  if not cat in filterCats: continue

                  expTag2diff='172.5'
                  if 'p11' in expTag:     expTag2diff='p11'
                  if expTag == 'p11':     expTag2diff='172.5'
                  if 'bfrag' in expTag:   expTag2diff='bfrag'
                  if expTag == 'bfrag':   expTag2diff='172.5'

                  diff = results[(cat,sel)][expTag][0]-results[(cat,sel)][expTag2diff][0]
                  diffErr = math.sqrt( results[(cat,sel)][expTag][1]**2+results[(cat,sel)][expTag2diff][1]**2 )
                  # diffstr='{0:20s}'.format(toLatexRounded(diff,diffErr))
                  diffstr = '$ %6.3f \\pm %5.3f $' % (diff, diffErr)
                  if expTag not in ['166.5','169.5','171.5','173.5','175.5','178.5']:
                       if abs(diff) > 0.5 and abs(diff) < 1.0:
                            diffstr = "%7s"%(bcolors.YELLOW+diffstr+bcolors.ENDC)
                       if abs(diff) >= 1.0:
                            diffstr = "%7s"%(bcolors.RED+diffstr+bcolors.ENDC)
                  print diffstr,'&',
             print '\\\\'
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
    parser.add_option('--syst',  dest='syst',    default=None, help='show systematics table')
    parser.add_option('--rebin', dest='rebin',   default=4,    type=int, help='rebin pe plots by this factor')
    (opt, args) = parser.parse_args()

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gROOT.SetBatch(True)

    #parse calibration results from directory
    if opt.calib:
        results,calibGrMap = parsePEResultsFromFile(url=opt.calib)
        calibMap = show(grCollMap=calibGrMap,
                        outDir=opt.calib+'/plots',
                        outName='svlcalib',
                        xaxisTitle='m_{t}^{gen} [GeV]',
                        x_range=(165,180),
                        yaxisTitle='<m_{t}^{fit}> [GeV]',
                        y_range=(165,180),
                        doFit=True,
                        verbose=True)
        calibFile=os.path.join(opt.calib,'.svlcalib.pck')
        cachefile = open(calibFile, 'w')
        pickle.dump(calibMap, cachefile, pickle.HIGHEST_PROTOCOL)
        pickle.dump(results,  cachefile, pickle.HIGHEST_PROTOCOL)
        cachefile.close()
        print 'Wrote %s with calibration constants and results'%calibFile

    #show systematics table
    if opt.syst:
         cachefile = open(opt.syst, 'r')
         calibMap  = pickle.load(cachefile)
         results   = pickle.load(cachefile)
         cachefile.close()

         showSystematicsTable(results=results,
                              filterCats=['comb_0','combe_0','combee_0','combem_0','combm_0','combmm_0'])
         showSystematicsTable(results=results,
                              filterCats=['comb_0','comb_3','comb_4','comb_5'])
         #showSystematicsTable(results=results,
         #                     filterCats=['e_3','e_4','e_5','m_3','m_4','m_5'])
         #showSystematicsTable(results=results,
         #                     filterCats=['ee_3','ee_4','ee_5','em_3','em_4','em_5','mm_3','mm_4','mm_5'])

    #compare inputs for pseudo-experiments
    if opt.peInput:
         outDir=os.path.dirname(opt.peInput)+'/pe_plots'
         for sel in ['','mrank1','optmrank']:
              ensemblesMap=parsePEInputs(url=opt.peInput, selection=sel,rebin=opt.rebin)
              for tag,grMap in ensemblesMap.items():
                   outName = tag if sel == '' else '%s_%s'%(tag,sel)
                   show(grCollMap=ensemblesMap[tag],
                        outDir=outDir,
                        outName=outName,
                        yaxisTitle='Ratio to reference',
                        xaxisTitle='m(SV,lepton) [GeV]',
                        y_range=(0.75,1.25),
                        x_range=(0,200),
                        baseDrawOpt='lx',
                        doFit=False)
    return


if __name__ == "__main__":
    sys.exit(main())
