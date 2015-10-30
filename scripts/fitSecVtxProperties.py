#!/usr/bin/env python

import ROOT
import os,sys
import optparse
import math
import pickle
from array import array

from UserCode.TopMassSecVtx.PlotUtils import *
from UserCode.TopMassSecVtx.CMS_lumi import *
from makeSVLMassHistos import LUMI

NTKMIN, NTKMAX   = 2, 6
MASSMIN,MASSMAX  = 0.0, 6.0

"""
"""
def showFlavorFracs(opt):

   #read flavour normalizations from cache
   cachefile=open(opt.flavorFitUrl,'r')
   flavorNorm=pickle.load(cachefile)
   cachefile.close()

   flavorfracs={}
   for flav in flavorNorm['obs']:
      flavorfracs[flav]=ROOT.TH1F(flav+'_obs',';SecVtx track multiplicity;Events',NTKMAX-NTKMIN+1,NTKMIN,NTKMAX+1)
      flavorfracs[flav].SetDirectory(0)
      flavorfracs[flav].Sumw2()
      for itk in flavorNorm['obs'][flav]:
         ibin=flavorfracs[flav].GetXaxis().FindBin(itk)
         flavorfracs[flav].SetBinContent(ibin,flavorNorm['obs'][flav][itk][0][0])
         flavorfracs[flav].SetBinError(ibin,flavorNorm['obs'][flav][itk][0][1])

   #iterate
   canvas=ROOT.TCanvas('c','c',500,500)

   
   #normalize for each vertex category
   for xbin in xrange(1,flavorfracs['b'].GetXaxis().GetNbins()+1):
      totalVtx=0
      for flavor in flavorfracs:
         totalVtx+=flavorfracs[flavor].GetBinContent(xbin)
         flavorfracs[flavor].GetXaxis().SetBinLabel(xbin,'%d'%flavorfracs[flavor].GetXaxis().GetBinLowEdge(xbin))
      if totalVtx==0 : continue
      for flavor in flavorfracs:
         flavorfracs[flavor].SetBinContent(xbin,
                                                flavorfracs[flavor].GetBinContent(xbin)/totalVtx)
         flavorfracs[flavor].SetBinError(xbin,
                                              flavorfracs[flavor].GetBinError(xbin)/totalVtx)

   #show normalized fractions
   canvas.Clear()
   stack=ROOT.THStack('flavorfracs','flavorfracs')
   leg=ROOT.TLegend(0.8,0.5,0.95,0.25)
   leg.SetFillStyle(0)
   leg.SetBorderSize(0)
   leg.SetTextFont(42)
   leg.SetTextSize(0.03)
   for flavor in flavorfracs:
      color=ROOT.kGray
      if flavor=='c' : color=ROOT.kAzure-3
      if flavor=='b' : color=ROOT.kOrange
      flavorfracs[flavor].SetFillColor(color)
      flavorfracs[flavor].SetLineColor(1)
      flavorfracs[flavor].SetFillStyle(1001)
      flavorfracs[flavor].GetYaxis().SetRangeUser(0,1)
      stack.Add(flavorfracs[flavor],'hist')
      leg.AddEntry(flavorfracs[flavor],flavor,"f")
   stack.Draw()
   stack.GetYaxis().SetRangeUser(0,1)
   stack.GetYaxis().SetTitle('Fraction')
   stack.GetXaxis().SetNdivisions(5)
   stack.GetXaxis().SetLabelSize(0.06)
   stack.GetXaxis().SetTitle('SecVtx track multiplicity')
   label=ROOT.TLatex()
   label.SetNDC()
   label.SetTextFont(42)
   label.SetTextSize(0.04)
   label.DrawLatex(0.18,0.95,'#bf{CMS} #it{simulation}')
   label.DrawLatex(0.75,0.95,'#scale[0.8]{19.7 fb^{-1} (8 TeV)}')
   leg.Draw()

   canvas.SaveAs('%s/flavorfrac.png'%(opt.outDir))
   canvas.SaveAs('%s/flavorfrac.pdf'%(opt.outDir))            
   canvas.SaveAs('%s/flavorfrac.C'%(opt.outDir))            

   

"""
returns a normalized distribution
"""
def normalizeDistribution(gr) :
   norm_gr=gr.Clone('norm_'+gr.GetName())
   x, y = ROOT.Double(0), ROOT.Double(0)

   #find the integral first
   totalY=0
   for ip in xrange(0,gr.GetN()):
      gr.GetPoint(ip,x,y)
      totalY+=y

   #normalize
   for ip in xrange(0,gr.GetN()):
      gr.GetPoint(ip,x,y)
      try:
         norm_gr.SetPoint(ip,x,y/totalY)
         norm_gr.SetPointError(ip,gr.GetErrorXlow(ip),
                                  gr.GetErrorXhigh(ip),
                                  gr.GetErrorYlow(ip)/totalY,
                                  gr.GetErrorYhigh(ip)/totalY)
      except ZeroDivisionError:
         print "totalY is zero!"
         norm_gr.SetPoint(ip,x,0.0)
         norm_gr.SetPointError(ip,gr.GetErrorXlow(ip),
                                  gr.GetErrorXhigh(ip),
                                  0.0,
                                  0.0)


   return norm_gr


"""
generates the RooFit workspace with the data and the fitting model
"""
def buildWorkspace(opt):

   #prepare histograms for re-composition, after the fit
    baseHistos=[
       ROOT.TH1F('chfrac',  ';p_{T}(SecVtx)/|#Sigma#vec{p}_{T}(ch.)};Events;', 36,0,1.5),
       ROOT.TH1F('chfracz', ';p_{z}(SecVtx)/|#Sigmap_{z}(ch.)|;Events;',       36,0,1.5),
       ROOT.TH1F('svprojfrac', ';R_{SPF}=1+#vec{p}(SecVtx).#vec{p}(tag)/|#vec{p}(tag)|^{2};Events;', 36,0,2),
       ROOT.TH1F('lxy',     ';L_{xy} [cm];Events;',                      36,0,15),
       ROOT.TH1F('lxysig',  ';L_{xy} significance;Events;',              36,0,100),
       ROOT.TH1F('svpt',    ';SecVtx transverse momentum [GeV];Events;', 36,0,100),       
       ROOT.TH1F('svptrel', ';SecVtx ch. p_{T}^{rel} [GeV];Events;',     36,0,4),
       ROOT.TH1F('svmass',  ';SecVtx mass [GeV];Events;',                64,MASSMIN,MASSMAX),
       ROOT.TH1F('tagpt',   ';Tag transverse momentum [GeV];Events;',    36,0,200)
       ]
    histos={}
    for key in ['data','b','c','other']:
       for fweight in xrange(0,7):
          for itk in xrange(NTKMIN,NTKMAX+1):
             for h in baseHistos:
                if key=='data' and fweight>0 : continue                
                hkey='%s_%s_%d'%(h.GetName(),key,itk)
                if key!='data' : hkey += '_fw%d'%fweight
                histos[hkey]=h.Clone(hkey)
                histos[hkey].Sumw2()
                histos[hkey].SetDirectory(0)
                if key!='data':
                   for pf in ['scaleup','scaledown']:
                      histos[hkey+'_'+pf]=h.Clone(hkey+'_'+pf)
                      histos[hkey+'_'+pf].Sumw2()
                      histos[hkey+'_'+pf].SetDirectory(0)
                      
    #add files to the corresponding chain
    chains={'data'       : ROOT.TChain('SVLInfo'), 
            'mc'         : ROOT.TChain('SVLInfo')}
    if opt.doScales:
       chains['mcscaleup']=ROOT.TChain('SVLInfo')
       chains['mcscaledown']=ROOT.TChain('SVLInfo')
    for f in [ f for f in os.listdir(opt.inDir) if 'root' in f]:      
        pathToF=os.path.join(opt.inDir,f)
        if 'DY' in f and 'scale' in f : continue
        if f.find('MC')==0: 
           print pathToF,'mc'
           chains['mc'].Add(pathToF)
           pathToF_up, pathToF_dn = pathToF, pathToF
           if ('DY1' in f or 'DY2' in f or 'DY3' in f) and opt.doScales :
              pathToF_up=pathToF_up.replace('50toInf','50toInf_scaleup')
              pathToF_dn=pathToF_up.replace('scaleup','scaledown')
           if opt.doScales:   
              chains['mcscaleup'].Add(pathToF_up)
              chains['mcscaledown'].Add(pathToF_dn)
        else:
           print pathToF,'data'
           chains['data'].Add(pathToF)

                           
    #prepare to weight tag pT, if required
    ptWeightGr={}
    for itk in xrange(NTKMIN,NTKMAX+1):        
        if opt.weightPt:
            hdata=ROOT.TH1F('hptdata','',50,0,250)
            hdata.Sumw2()
            extraCond=''
            if opt.onlyCentral : extraCond+='&&TMath::Abs(JEta)<1.1'
            if opt.vetoCentral : extraCond+='&&TMath::Abs(JEta)>0.1'
            chains['data'].Draw('LPt>>hptdata','SVNtrk==%d && SVLxySig>%f %s'%(itk,opt.minLxySig,extraCond),'norm goff')
            hmc=ROOT.TH1F('hptmc','',50,0,250)
            hmc.Sumw2()
            for key in ['mc','mcscaleup','mcscaledown']:
               try:
                  hmc.Reset('ICE')
                  chains[key].Draw('LPt>>hptmc','(SVNtrk==%d %s)*Weight[0]*XSWeight*%f'%(itk,extraCond,LUMI),'norm goff')
                  hmc.Divide(hdata)
                  if not (key in ptWeightGr): ptWeightGr[key]={}
                  ptWeightGr[key][itk]=ROOT.TGraphErrors(hmc)
               except:
                  continue
            hdata.Delete()
            hmc.Delete()
            
    EvCatToFilter = [int(x) for x in opt.filter.split(',')]

    #fill the histograms
    for key in chains:
       
        chain_pfix=''
        if 'scaledown' in key: chain_pfix='_scaledown'
        if 'scaleup'   in key: chain_pfix='_scaleup'

        nEntries = chains[key].GetEntries()
        print "Will loop over %s with %d entries"%(key,nEntries)
        for i in xrange(0,nEntries):
            if i%500 == 0:
                sys.stdout.write("[%3d/100]\r" % (100*i/float(nEntries)))
                sys.stdout.flush()

            #read entry
            chains[key].GetEntry(i)

            #filter event category if required
            if len(EvCatToFilter)>0 and not chains[key].EvCat in EvCatToFilter : continue

            #Check number of tracks
            ntk=chains[key].SVNtrk
            if ntk<NTKMIN : continue
            if ntk>NTKMAX : continue

            if opt.onlyCentral and ROOT.TMath.Abs(chains[key].JEta)>1.1: continue
            if opt.vetoCentral and ROOT.TMath.Abs(chains[key].JEta)<0.1: continue
            lxysig=chains[key].SVLxySig
            if lxysig<opt.minLxySig : continue
                
            if chains[key].SVLMassRank!=1 or chains[key].CombCat%2==0 : continue

            #compute global event weight
            totalWeight=1.0
            if 'mc' in key:
               totalWeight=chains[key].Weight[0]*chains[key].XSWeight*LUMI
               lpt=ROOT.TMath.Min(chains[key].LPt,250)
               if key in ptWeightGr:
                  ptWeightInv=ptWeightGr[key][ntk].Eval(lpt)
                  if ptWeightInv>0.01 : totalWeight /= ptWeightInv 

            #count and fill histograms
            histoVars={}
            histoVars['svpt']       = chains[key].SVPt
            histoVars['svptrel']    = chains[key].SVPtRel
            histoVars['lxy']        = chains[key].SVLxy
            histoVars['lxysig']     = chains[key].SVLxySig
            histoVars['chfrac']     = chains[key].SVPtChFrac
            histoVars['svprojfrac'] = chains[key].SVProjFrac
            histoVars['chfracz']    = chains[key].SVPzChFrac
            histoVars['svmass']     = chains[key].SVMass
            histoVars['tagpt']      = chains[key].LPt
            histoKey='_'
            if 'mc' in  key:
               if ROOT.TMath.Abs(chains[key].JFlav)==5   : histoKey+='b'
               elif ROOT.TMath.Abs(chains[key].JFlav)==4 : histoKey+='c'
               else                                      : histoKey+='other'
            else:
               histoKey+='data'
            for ifrag in xrange(0,7):
               fragWeight=1.0
               pfix=''
               if 'mc' in key:
                  pfix='_fw%d%s'%(ifrag,chain_pfix)
                  if ROOT.TMath.Abs(chains[key].JFlav)==5 and ifrag>0: 
                     fragWeight = chains[key].SVBfragWeight[ifrag-1]
                     if fragWeight<0 : fragWeight=0
               if key=='data' and ifrag>0 : continue
               for var in histoVars:
                  hname=var+histoKey+'_%d%s'%(ntk,pfix)
                  histos[hname].Fill(histoVars[var],totalWeight*fragWeight)

    for key in histos:
       normKey=None
       if 'scale' in key:
          normKey='_'.join(key.split('_')[:-1])[:-1]+'0'
       else:
          if not ('_b_' in key): continue
          if '_fw0' in key : continue
          normKey=key[:-1]+'0'
       if histos[key].Integral()==0 : continue
       print key,'->', normKey
       #histos[key].Scale(histos[normKey].Integral()/histos[key].Integral())
    
    #save histograms
    wsUrl=os.path.join(opt.outDir,"SecVtxWorkspace.root")
    fOut=ROOT.TFile.Open(wsUrl,'RECREATE')
    for key in histos:
            histos[key].Write()
    fOut.Close()
    return wsUrl
        


"""
"""
def doMassFit(opt):

   #for the normalization of the different flavours
   flavorFracs={'exp':{},'obs':{}}
   for key in flavorFracs:
      for flav in ['b','c','other']:
         flavorFracs[key][flav]={}
         for itk in xrange(NTKMIN,NTKMAX+1) :
            flavorFracs[key][flav][itk]=[]
                  
   #open file with templates and data
   fIn=ROOT.TFile.Open(opt.wsUrl)

   #initiate a workspace for the fits to the SecVtxMass
   ws=ROOT.RooWorkspace("w")
   ws.factory('mass[2,%f,%f]'%(MASSMIN,MASSMAX))
   obsSet=ROOT.RooArgSet(ws.var('mass'))
   data2mcScaleFactors={}
   for itk in xrange(NTKMIN,NTKMAX+1):

      #observed data
      dataH = fIn.Get('svmass_data_%d'%itk)
      nobs=dataH.Integral(0,-1)
      getattr(ws,'import')( ROOT.RooDataHist('data_%d'%itk,'data_%d'%itk,
                                             ROOT.RooArgList(obsSet),
                                             dataH) )
      nexp=0
      for flav in ['b','c','other']:
         key='svmass_%s_%d_fw0'%(flav,itk)
         nexp += fIn.Get(key).Integral(0,-1)      
      data2mcScaleFactors[itk]=nobs/nexp

      #loop over fragmentation weights
      for iw in xrange(0,7):
         sumExp=''
         for flav in ['b','c','other']:
            key='svmass_%s_%d_fw%d'%(flav,itk,iw)
            template=fIn.Get(key)
            getattr(ws,'import')( ROOT.RooDataHist('hist_%s'%key,'hist_%s'%key,
                                                   ROOT.RooArgList(obsSet),
                                                   template) )
            getattr(ws,'import')( ROOT.RooHistPdf('pdf_%s'%key,'pdf_%s'%key,
                                                  obsSet,
                                                  ws.data('hist_%s'%key)) )
            nexpUnc =  ROOT.Double(0.0)
            nexp    =  template.IntegralAndError(0,-1,nexpUnc)
            flavorFracs['exp'][flav][itk].append( (nexp,float(nexpUnc)) )
            ws.factory('nobs_%s[%f,%f,%f]'%(key,nexp,0,5*nexp))
            sumExp += 'nobs_%s*pdf_%s,'%(key,key)

         #pdf to fit the data
         sumExp=sumExp[:-1]
         ws.factory("SUM::model_%d_fw%d(%s)"%(itk,iw,sumExp))
         #ws.pdf('model_%d_fw%d'%(itk,iw)).fitTo(ws.data('data_%d'%itk),ROOT.RooFit.Extended())        
         #ws.pdf('model_%d_fw%d'%(itk,iw)).fitTo(ws.data('data_%d'%itk))
         for flav in ['b','c','other']:
            key='svmass_%s_%d_fw%d'%(flav,itk,iw)
            flavorFracs['obs'][flav][itk].append( (data2mcScaleFactors[itk]*ws.var('nobs_%s'%key).getVal(),
                                                   data2mcScaleFactors[itk]*ws.var('nobs_%s'%key).getError()) )

   #dump fits to file 
   flavorFitUrl='%s/.flavorfits.pck'%opt.outDir
   cachefile = open(flavorFitUrl,'w')
   pickle.dump( flavorFracs, cachefile, pickle.HIGHEST_PROTOCOL)
   pickle.dump( data2mcScaleFactors, cachefile, pickle.HIGHEST_PROTOCOL)
   cachefile.close()
   return flavorFitUrl

"""
"""
def compareDistributions(opt):

   #fragmentation variations to compare
   fragToUse=[('Z2*LEP r_{b}', [1,2,3], ROOT.kBlack),
              ('Z2*',          [0,0,0], ROOT.kRed+1),
              ('Z2* peterson', [5,5,5], ROOT.kViolet+2),
              ('Z2* Lund',     [6,6,6], ROOT.kAzure+7)]
   nominalFragWgt=fragToUse[0][1][0]

   #read flavour normalizations from cache
   cachefile=open(opt.flavorFitUrl,'r')
   flavorFracs=pickle.load(cachefile)
   cachefile.close()
   
   #open file with templates
   fIn=ROOT.TFile(opt.wsUrl)
   
   #prepare canvas
   canvas=ROOT.TCanvas('c','c',600,600)
   canvas.SetRightMargin(0)
   canvas.SetLeftMargin(0.)
   canvas.SetTopMargin(0)
   canvas.SetBottomMargin(0.)
   canvas.cd()
   p1 = ROOT.TPad('p1','p1',0.0,0.85,1.0,0.0)
   p1.SetLeftMargin(0.12)
   p1.SetBottomMargin(0.12)
   p1.SetRightMargin(0.05)
   p1.SetTopMargin(0.01)
   p1.Draw()
   canvas.cd()
   p2 = ROOT.TPad('p2','p2',0.0,0.85,1.0,1.0)
   p2.SetLeftMargin(0.12)
   p2.SetBottomMargin(0.01)
   p2.SetRightMargin(0.05)
   p2.SetTopMargin(0.05)
   p2.Draw()
   

   #loop over variables
   for var,title in [('svmass','SecVtx mass [GeV]'),
                     ('svpt','SecVtx transverse momentum [GeV]'),
                     ('svptrel','SecVtx ch. p_{T}^{rel} [GeV]'),
                     ('chfrac','p_{T}(SecVtx) / |#sum_{ch} #vec{p}_{T}|') ,
                     ('chfracz','p_{T}(SecVtx) / |#sum_{ch} p_{z}|') ,
                     ('svprojfrac', 'R_{SPF}=1+#vec{p}(SecVtx).#vec{p}(tag)/|#vec{p}(tag)|^{2}'),
                     ('lxy', 'L_{xy} [cm]'),
                     ('lxysig', 'L_{xy} significance'),
                     ('tagpt',  'Tag transverse momentum [GeV]')
                     ]:

      #loop over track multiplicity
      for itk in xrange(NTKMIN,NTKMAX+1):
         
         fIn.cd()
         
         #data distribution
         data=fIn.Get('%s_data_%d'%(var,itk))
         data.SetDirectory(0)
         data.SetMarkerStyle(20)
         data.SetLineColor(1)
         data.SetMarkerColor(1)
         data.SetTitle('data')
         if opt.rebin!=0 : data.Rebin(opt.rebin)
         dataGr=convertToPoissonErrorGr(data)

         #legend
         p1.cd()
         p1.Clear()
         leg=ROOT.TLegend(0.72,0.6,0.95,0.85)
         if 'svprojfrac' in var : leg=ROOT.TLegend(0.15,0.8,0.49,0.95)
         leg.SetFillStyle(0)
         leg.SetBorderSize(0)
         leg.SetTextFont(42)
         leg.SetTextSize(0.04)
         leg.AddEntry(dataGr,'data','p')
         #leg.SetNColumns(2)

         #build the different total predictions
         stacks={}
         for frag,iwList,color in fragToUse:
            for iw in iwList:
               if iw in stacks: continue
               stacks[iw]=ROOT.THStack('hs%d'%iw,'total%d'%iw)
               for flav in ['other','c','b']:

                  #format histogram
                  h=fIn.Get('%s_%s_%d_fw%d'%(var,flav,itk,iw))
                  if h.Integral()==0 : continue
                  data2mcScaleFactor=flavorFracs['obs'][flav][itk][iw][0]/flavorFracs['exp'][flav][itk][iw][0]
                  h.Scale(data2mcScaleFactor)
                  h.SetDirectory(0)
                  if opt.rebin!=0 : h.Rebin(opt.rebin)
                  color = ROOT.kGray
                  if flav=='c' : color=ROOT.kAzure-3
                  if flav=='b' : color=ROOT.kOrange
                  h.SetTitle(flav)
                  h.SetFillStyle(1001)
                  h.SetFillColor(color)
                  h.SetLineColor(color)
                  if iw==nominalFragWgt : leg.AddEntry(h,flav,'f')
                  stacks[iw].Add(h,'hist')

         #show main prediction
         stacks[nominalFragWgt].Draw()
         stacks[nominalFragWgt].GetYaxis().SetTitle('Events')
         stacks[nominalFragWgt].GetXaxis().SetTitle(title)
         stacks[nominalFragWgt].GetYaxis().SetTitleOffset(1.25)
         stacks[nominalFragWgt].GetYaxis().SetRangeUser(1,1.5*data.GetMaximum())
         stacks[nominalFragWgt].GetXaxis().SetTitleOffset(0.9)
         stacks[nominalFragWgt].GetYaxis().SetTitleSize(0.04)
         stacks[nominalFragWgt].GetXaxis().SetTitleSize(0.04)
         stacks[nominalFragWgt].GetYaxis().SetLabelSize(0.04)
         stacks[nominalFragWgt].GetXaxis().SetLabelSize(0.04)
         stacks[nominalFragWgt].GetXaxis().SetNdivisions(5)
         stacks[nominalFragWgt].GetYaxis().SetNdivisions(5)
         if 'lxy' in var : 
            canvas.SetLogy(True)
            stacks[nominalFragWgt].GetYaxis().SetRangeUser(0.5,stacks[nominalFragWgt].GetYaxis().GetXmax())
         else            : canvas.SetLogy(False)
         dataGr.Draw('p')
         leg.Draw()
         label=ROOT.TLatex()
         label.SetNDC()
         label.SetTextFont(42)
         label.SetTextSize(0.05)
         label.DrawLatex(0.15,0.92,'#bf{CMS}')
         label.DrawLatex(0.72,0.86,'#scale[0.8]{#it{%d tracks}}'%itk)
         label.DrawLatex(0.72,0.92,'#scale[0.8]{19.7 fb^{-1} (8 TeV)}')


         #comparisons
         p2.cd()
         p2.Clear()        
         compGrs={}
         for wtitle,iwList,wcolor in fragToUse:
            nomw=iwList[0]
            compGrs[nomw]=ROOT.TGraphAsymmErrors()
            compGrs[nomw].SetName('compgr%d'%nomw)
            compGrs[nomw].SetTitle(wtitle)
            compGrs[nomw].SetLineColor(wcolor)
            compGrs[nomw].SetFillColor(wcolor)
            compGrs[nomw].SetLineWidth(2)
            compGrs[nomw].SetMarkerColor(wcolor)
            compGrs[nomw].SetFillStyle(3001)
            compGrs[nomw].SetMarkerStyle(20+nomw)
                        
            avgs=[]
            for iw in iwList:
               totalH=stacks[iw].GetStack().At(stacks[iw].GetStack().GetEntriesFast()-1)
               avgs.append( totalH.GetMean() )

            compGrs[nomw].SetPoint(0,len(compGrs),avgs[0])
            diff1=ROOT.TMath.Min(avgs[1]-avgs[0],avgs[2]-avgs[0])
            diff2=ROOT.TMath.Max(avgs[1]-avgs[0],avgs[2]-avgs[0])
            print wtitle,iwList,diff1,diff2
            if diff1*diff2<0:
               compGrs[nomw].SetPointError(0,0,0,ROOT.TMath.Abs(diff1),ROOT.TMath.Abs(diff2))
            else:
               maxDiff=ROOT.TMath.Max(ROOT.TMath.Abs(diff1),ROOT.TMath.Abs(diff2))
               compGrs[nomw].SetPointError(0,0,0,maxDiff,maxDiff)


         frame,dataRef=ROOT.TGraph(),None
         avg,avgErr,rms=data.GetMean(),data.GetMeanError(),data.GetRMS()

         frame.SetTitle('frame')
         frame.SetMarkerStyle(1)
         frame.SetMarkerColor(0)
         frame.SetLineColor(0)
         frame.SetPoint(0,0,avg-rms*0.05)
         frame.SetPoint(1,len(compGrs)+0.5,avg-rms*0.12)
         frame.SetPoint(2,len(compGrs)+0.5,avg+rms*0.12)
         if itk>5 :
            frame.SetPoint(1,len(compGrs)+0.5,avg-rms*0.25)
            frame.SetPoint(2,len(compGrs)+0.5,avg+rms*0.25)
         frame.SetPoint(3,0,avg+rms*0.05)
         frame.SetPoint(4,0,avg-rms*0.05)

         dataRef=ROOT.TGraph()
         dataRef.SetTitle('dataref')
         dataRef.SetFillStyle(3001)
         dataRef.SetFillColor(ROOT.kGray)
         dataRef.SetPoint(0,0,avg-avgErr)
         dataRef.SetPoint(1,len(compGrs)+1.0,avg-avgErr)
         dataRef.SetPoint(2,len(compGrs)+1.0,avg+avgErr)
         dataRef.SetPoint(3,0.0,avg+avgErr)
         dataRef.SetPoint(4,0.0,avg-avgErr)

         frame.Draw('ap')
         frame.GetYaxis().SetNdivisions(4)
         frameXtitle,frameYtitle='','Average'
         frame.GetXaxis().SetNdivisions(0)
         frame.GetYaxis().SetTitle(frameYtitle)
         frame.GetXaxis().SetTitle(frameXtitle)
         frame.GetXaxis().SetTitleSize(0.0)
         frame.GetXaxis().SetLabelSize(0.0)
         frame.GetYaxis().SetTitleOffset(0.25)
         frame.GetXaxis().SetTitleOffset(1.8)
         frame.GetYaxis().SetTitleSize(0.2)
         frame.GetYaxis().SetLabelSize(0.2)

         #inset legend
         fraglabel=ROOT.TLatex()
         fraglabel.SetNDC()
         fraglabel.SetTextFont(42)
         fraglabel.SetTextSize(0.15)        
         #fraglabel.SetTextAlign(12)
         if dataRef : 
            dataRef.Draw('f')    
         grCtr=0
         for wtitle,iwList,wcolor in fragToUse:        
            compGrs[iwList[0]].Draw('p')            
            xlabel=0.09+0.68*float(grCtr+1)/float(len(fragToUse))
            fraglabel.DrawLatex(xlabel,0.8,'#it{%s}'%wtitle)
            grCtr+=1

         postfix='_mean'
         canvas.cd()
         canvas.Modified()
         canvas.Update()
         canvas.SaveAs('%s/%s_%d%s.C'%(opt.outDir,var,itk,postfix))
         canvas.SaveAs('%s/%s_%d%s.png'%(opt.outDir,var,itk,postfix))
         canvas.SaveAs('%s/%s_%d%s.pdf'%(opt.outDir,var,itk,postfix))

"""
steer the script
"""
def main():

    #configuration
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-i', '--inDir',       dest='inDir'   ,    help='input directory',        default=None,  type='string')
    parser.add_option('-o', '--outDir',      dest='outDir'  ,    help='output directory',       default='./',  type='string')
    parser.add_option(      '--filter',      dest='filter',      help='ev cat to filter',       default='',    type='string')
    parser.add_option(      '--weightPt',    dest='weightPt',    help='weight pt',              default=False, action='store_true')
    parser.add_option(      '--doScales',    dest='doScales',    help='show QCD scales',        default=False, action='store_true')
    parser.add_option(      '--rebin',       dest='rebin',       help='rebin',                  default=0,     type=int)
    parser.add_option(      '--onlyCentral', dest='onlyCentral', help='only central jets',      default=False, action='store_true')
    parser.add_option(      '--vetoCentral', dest='vetoCentral', help='veto very central jets', default=False, action='store_true')
    parser.add_option(      '--minLxySig'  , dest='minLxySig',   help='min. lxy sig',           default=-1,    type=float)   
    parser.add_option('-w', '--ws',          dest='wsUrl'   ,    help='ws url',                 default=None,  type='string')
    parser.add_option('-s', '--show',        dest='flavorFitUrl', help='flavor fit url',        default=None,  type='string')
    parser.add_option('-m', '--max',        dest='maxTracks', help='max tracks',        default=None,  type=int)

    (opt, args) = parser.parse_args()

    if opt.outDir!='./' : os.system('mkdir -p %s'%opt.outDir)
     
    if not (opt.maxTracks is None) :
       global NTKMAX
       NTKMAX=opt.maxTracks

    #global ROOT configuration
    setTDRStyle()
    ROOT.gStyle.SetOptFit(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.RooMsgService.instance().setSilentMode(True)
    ROOT.gROOT.SetBatch(True)    
    ROOT.gROOT.SetBatch(False)    

    #create ROOT file with templates and data
    if opt.flavorFitUrl is None: 
       if opt.wsUrl is None: opt.wsUrl=buildWorkspace(opt)
       opt.flavorFitUrl = doMassFit(opt)

    #show results of the flavour fits
    compareDistributions(opt)
    showFlavorFracs(opt)

    return 0

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())



