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
       ROOT.TH1F('chfrac',  ';p_{T}(SecVtx)/|#sigma\vec{p}_{T}(ch.)};Events;', 36,0,1.5),
       ROOT.TH1F('chfracz', ';p_{z}(SecVtx)/|#sigmap_{z}(ch.)|;Events;',       36,0,1.5),
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
 
    #add files to the corresponding chain
    chains={'data':ROOT.TChain('SVLInfo'), 'mc':ROOT.TChain('SVLInfo')}
    for f in [ f for f in os.listdir(opt.inDir) if 'root' in f]:      
        key = 'data'
        if f.find('MC')==0: key='mc'
        print key,f
        chains[key].Add(os.path.join(opt.inDir,f))
                           
    #prepare to weight tag pT, if required
    weightGr={}
    for itk in xrange(NTKMIN,NTKMAX+1):        
        if opt.weightPt:
            hdata=ROOT.TH1F('hptdata','',50,0,500)
            hdata.Sumw2()
            extraCond=''
            if opt.onlyCentral : extraCond+='&&TMath::Abs(JEta)<1.1'
            if opt.vetoCentral : extraCond+='&&TMath::Abs(JEta)>0.1'
            chains['data'].Draw('LPt>>hptdata','SVNtrk==%d && SVLxySig>%f %s'%(itk,opt.minLxySig,extraCond),'norm goff')
            hmc=ROOT.TH1F('hptmc','',50,0,500)
            hmc.Sumw2()
            chains['mc'].Draw('LPt>>hptmc','(SVNtrk==%d %s)*Weight[0]*XSWeight*%f'%(itk,extraCond,LUMI),'norm goff')
            hdata.Divide(hmc)
            weightGr[itk]=ROOT.TGraphErrors(hdata)
            hdata.Delete()
            hmc.Delete()
            
    #fill the histograms
    for key in chains:
        nEntries = chains[key].GetEntries()
        print "Will loop over %s with %d entries"%(key,nEntries)
        for i in xrange(0,nEntries):
            if i%500 == 0:
                sys.stdout.write("[%3d/100]\r" % (100*i/float(nEntries)))
                sys.stdout.flush()

            #read entry
            chains[key].GetEntry(i)

            #check number of tracks
            ntk=chains[key].SVNtrk
            if ntk<NTKMIN : continue
            if ntk>NTKMAX : continue

            if opt.onlyCentral and ROOT.TMath.Abs(chains[key].JEta)>1.1: continue
            if opt.vetoCentral and ROOT.TMath.Abs(chains[key].JEta)<0.1: continue
            lxysig=chains[key].SVLxySig
            if lxysig<opt.minLxySig : continue
                
            #compute global event weight
            totalWeight=1.0
            if key=='mc':
               totalWeight=chains[key].Weight[0]*chains[key].XSWeight*LUMI
               lpt=ROOT.TMath.Min(chains[key].LPt,500)
               totalWeight *= weightGr[ntk].Eval(lpt)

            #count and fill histograms
            histoVars={}
            histoVars['svpt']    = chains[key].SVPt
            histoVars['svptrel'] = chains[key].SVPtRel
            histoVars['lxy']     = chains[key].SVLxy
            histoVars['lxysig']  = chains[key].SVLxySig
            histoVars['chfrac']  = chains[key].SVPtChFrac
            histoVars['svprojfrac'] = chains[key].SVProjFrac
            histoVars['chfracz']  = chains[key].SVPzChFrac
            histoVars['svmass']  = chains[key].SVMass
            histoVars['tagpt']   = chains[key].LPt
            histoKey='_'
            if key=='mc':
               if ROOT.TMath.Abs(chains[key].JFlav)==5   : histoKey+='b'
               elif ROOT.TMath.Abs(chains[key].JFlav)==4 : histoKey+='c'
               else                                      : histoKey+='other'
            else:
               histoKey+='data'
            for ifrag in xrange(0,7):
               fragWeight=1.0
               pfix=''
               if key=='mc' : 
                  pfix='_fw%d'%ifrag
                  if ROOT.TMath.Abs(chains[key].JFlav)==5 and ifrag>0: 
                     fragWeight = chains[key].SVBfragWeight[ifrag-1]
                     if fragWeight<0 : fragWeight=0
               if key=='data' and ifrag>0 : continue
               for var in histoVars:
                  hname=var+histoKey+'_%d%s'%(ntk,pfix)
                  histos[hname].Fill(histoVars[var],totalWeight*fragWeight)

    for key in histos:
       if not ('_b_' in key): continue
       if '_fw0' in key : continue
       normKey=key[:-1]+'0'
       print key,'->', normKey
       histos[key].Scale(histos[normKey].Integral()/histos[key].Integral())
    
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
def comparePostFitDistributions(opt):

   #read flavour normalizations from cache
   cachefile=open(opt.flavorFitUrl,'r')
   flavorFracs=pickle.load(cachefile)
   cachefile.close()
   
   #open file with templates
   fIn=ROOT.TFile(opt.wsUrl)
   
   #fit and save results 
   canvas=ROOT.TCanvas('c','c',500,1000)
   canvas.SetRightMargin(0)
   canvas.SetLeftMargin(0)
   canvas.SetTopMargin(0)
   canvas.SetBottomMargin(0)
   allLegs=[]
   pads=[]
   pads.append( ROOT.TPad('pad0','pad0',0,0.6,1.0,1.0) )
   pads[0].SetBottomMargin(0.01)
   pads.append( ROOT.TPad('pad1','pad1',0.0,0.60,1.0,0.42) )
   pads.append( ROOT.TPad('pad2','pad2',0.0,0.42,1.0,0.24) )
   pads.append( ROOT.TPad('pad3','pad3',0.0,0.24,1.0,0.00) )
   for i in xrange(1,4):
      pads[i].SetTopMargin(0.01)
      pads[i].SetBottomMargin(0.01)
   pads[-1].SetBottomMargin(0.22)
   for p in pads: p.Draw()

   for var,title in [('svmass','SecVtx mass [GeV]'),
                     ('svpt','SecVtx transverse momentum [GeV]'),
                     ('svptrel','SecVtx ch. p_{T}^{rel} [GeV]'),
                     ('chfrac','p_{T}(SecVtx) / |#sum_{ch} #vec{p}_{T}|') ,
                     ('chfracz','p_{T}(SecVtx) / |#sum_{ch} p_{z}|') ,
                     ('svprojfrac', 'R_{SPF}=1+#vec{p}(SecVtx).#vec{p}(tag)/|#vec{p}(tag)|^{2}'),
                     ('lxy', 'L_{xy} [cm]'),
                     ('lxysig', 'L_{xy} significance'),
                     ('tagpt',  'Tag transverse momentum [GeV]')]:
      for itk in xrange(NTKMIN,NTKMAX+1):
         data=fIn.Get('%s_data_%d'%(var,itk))
         data.SetMarkerStyle(20)
         data.SetLineColor(1)
         data.SetMarkerColor(1)
         data.SetTitle('data')
         if opt.rebin!=0 : data.Rebin(opt.rebin)

         dataResPull=[]
         stack=ROOT.THStack('hs','total')
         leg=ROOT.TLegend(0.8,0.5,0.95,0.25)
         leg.SetFillStyle(0)
         leg.SetBorderSize(0)
         leg.SetTextFont(42)
         leg.SetTextSize(0.03)
         for iw in xrange(0,len(flavorFracs['exp']['b'][itk])):
            dataResPull.append( data.Clone('%s_data_%d_res_%d'%(var,itk,iw)) )
            dataResPull[iw].SetDirectory(0)
            hb=None
            for flav in ['other','c','b']:
               if flavorFracs['exp'][flav][itk][iw][0]<=0 : continue
               h=fIn.Get('%s_%s_%d_fw%d'%(var,flav,itk,iw))
               h.Scale(flavorFracs['obs'][flav][itk][iw][0]/flavorFracs['exp'][flav][itk][iw][0])
               if opt.rebin!=0 : h.Rebin(opt.rebin)
               dataResPull[iw].Add(h,-1)

               if iw>0 : continue
               color = ROOT.kGray
               if flav=='c' : color=ROOT.kAzure-3
               if flav=='b' : color=ROOT.kOrange
               h.SetTitle(flav)
               h.SetFillStyle(1001)
               h.SetFillColor(color)
               h.SetLineColor(color)
               stack.Add(h,'hist')
               leg.AddEntry(h,flav,'f')

            #finalize computing pull
            for xbin in xrange(1,dataResPull[iw].GetXaxis().GetNbins()):
                mcunc=stack.GetStack().At( stack.GetStack().GetEntriesFast()-1 ).GetBinError(xbin)
                if mcunc<=0: continue
                pull=dataResPull[iw].GetBinContent(xbin)/mcunc
                pullErr=dataResPull[iw].GetBinError(xbin)/mcunc
                dataResPull[iw].SetBinContent(xbin,pull)
                dataResPull[iw].SetBinError(xbin,pullErr)



         canvas.cd()
         pads[0].cd()
         pads[0].Clear()
         if 'lxy' in var : pads[0].SetLogy(True)
         else            : pads[0].SetLogy(False)
         stack.Draw()
         stack.GetYaxis().SetTitle('Events')
         stack.GetYaxis().SetTitleOffset(1.5)
         stack.GetXaxis().SetTitle('')
         stack.GetYaxis().SetRangeUser(1,1.3*data.GetMaximum())
         stack.GetXaxis().SetTitleOffset(1.2)
         stack.GetYaxis().SetTitleSize(0.06)
         stack.GetXaxis().SetTitleSize(0.0)
         stack.GetYaxis().SetLabelSize(0.06)
         stack.GetXaxis().SetLabelSize(0.0)
         stack.GetXaxis().SetNdivisions(5)
         dataGr=convertToPoissonErrorGr(data)
         dataGr.Draw('p')
         leg.AddEntry(dataGr,'data','p')
         label=ROOT.TLatex()
         label.SetNDC()
         label.SetTextFont(42)
         label.SetTextSize(0.04)
         label.DrawLatex(0.18,0.95,'#bf{CMS} #it{simulation}  #scale[0.8]{#it{N_{tracks}=%d}}'%itk)
         label.DrawLatex(0.75,0.95,'#scale[0.8]{19.7 fb^{-1} (8 TeV)}')
         leg.Draw()

         canvas.cd()
         pullsToDraw=[{0:('Z2*',ROOT.kBlack),          4:('P11',ROOT.kMagenta)},
                      {1:('Z2* r_{b}',ROOT.kBlack),    2:('Z2* r_{b} hard',ROOT.kMagenta), 3:('Z2* r_{b} soft',ROOT.kViolet+2)},
                      {5:('Z2* peterson',ROOT.kBlack), 6:('Z2* Lund',ROOT.kMagenta) }
                      ]

         for ip in xrange(0,len(pullsToDraw)):
            pads[ip+1].cd()
            pads[ip+1].Clear()
            pads[ip+1].SetGridy(True)

            drawOpt='hist'
            allLegs.append( ROOT.TLegend(0.2,0.75,0.9,0.97) )
            for pkey in pullsToDraw[ip]:
               dataResPull[pkey].Draw(drawOpt)

               pullTitle=pullsToDraw[ip][pkey][0]
               dataResPull[pkey].SetTitle(pullTitle)
               chi2=0
               for xbin in xrange(1,dataResPull[pkey].GetXaxis().GetNbins()):
                  pullVal=dataResPull[pkey].GetBinContent(xbin)
                  chi2 += pullVal*pullVal
                  dataResPull[pkey].SetBinError(xbin,0)
               pullTitle += ' #chi^{2}/dof=%3.1f'%(chi2/dataResPull[pkey].GetXaxis().GetNbins())
               dataResPull[pkey].SetTitle(pullTitle)
               allLegs[-1].AddEntry( dataResPull[pkey], pullTitle, 'l' )
               drawOpt='histsame'
               color=pullsToDraw[ip][pkey][1]
               
               dataResPull[pkey].SetLineColor(color)
               dataResPull[pkey].SetMarkerColor(color)
               dataResPull[pkey].SetMarkerStyle(1)
               dataResPull[pkey].SetMarkerSize(0.)
               dataResPull[pkey].GetYaxis().SetTitle('Pull')
               dataResPull[pkey].GetXaxis().SetTitle('')
               dataResPull[pkey].GetYaxis().SetNdivisions(5)
               dataResPull[pkey].GetXaxis().SetNdivisions(5)
               dataResPull[pkey].GetYaxis().SetRangeUser(-5.7,6)
               if ip+1==3 :
                  dataResPull[pkey].GetXaxis().SetTitleSize(0.1)
                  dataResPull[pkey].GetXaxis().SetLabelSize(0.1)
                  dataResPull[pkey].GetXaxis().SetTitle(title)
                  dataResPull[pkey].GetYaxis().SetTitleOffset(0.7)
                  dataResPull[pkey].GetXaxis().SetTitleOffset(0.8)
                  dataResPull[pkey].GetYaxis().SetTitleSize(0.1)
                  dataResPull[pkey].GetYaxis().SetLabelSize(0.1)
               else:
                  dataResPull[pkey].GetXaxis().SetTitleSize(0)
                  dataResPull[pkey].GetXaxis().SetLabelSize(0)
                  dataResPull[pkey].GetXaxis().SetTitle('')
                  dataResPull[pkey].GetYaxis().SetTitleOffset(0.5)
                  dataResPull[pkey].GetYaxis().SetTitleSize(0.13)
                  dataResPull[pkey].GetYaxis().SetLabelSize(0.13)
            allLegs[-1].SetFillStyle(3001)
            allLegs[-1].SetFillColor(0)
            allLegs[-1].SetBorderSize(0)
            allLegs[-1].SetTextFont(42)
            allLegs[-1].SetTextSize(0.08)
            allLegs[-1].Draw()         
         canvas.Modified()
         canvas.Update()
         canvas.SaveAs('%s/%s_%d.png'%(opt.outDir,var,itk))
         canvas.SaveAs('%s/%s_%d.pdf'%(opt.outDir,var,itk))
         #raw_input('...press key to continue')
         

#        #loop over variables
#        scales={}
#            h_data  = ROOT.RooAbsData.createHistogram(data,var+'_data',ws.var(var))
#            h_data.SetMarkerStyle(20)
#            h_data.SetLineColor(1)
#            h_data.SetMarkerColor(1)
#            if opt.rebin!=0 : h_data.Rebin(opt.rebin)
#            h_b     = ROOT.RooAbsData.createHistogram(mc_b,var+'_mc_b',ws.var(var))
#            try:        
#                h_b.Scale(scales['b'])
#            except:
#                scales['b']=ws.var('n_b_%d'%itk).getVal()/h_b.Integral()
#                h_b.Scale(scales['b'])
#            h_b.SetFillStyle(1001)
#            h_b.SetFillColor(ROOT.kOrange)
#            if opt.rebin!=0 : h_b.Rebin(opt.rebin)
#            h_c     = ROOT.RooAbsData.createHistogram(mc_c,var+'_mc_c',ws.var(var))
#            try:
#                h_c.Scale(scales['c'])
#            except:
#                scales['c']=ws.var('n_c_%d'%itk).getVal()/h_c.Integral()
#                h_c.Scale(scales['c'])
#            h_c.SetFillStyle(1001)
#            h_c.SetFillColor(ROOT.kAzure-3)
#            if opt.rebin!=0 : h_c.Rebin(opt.rebin)
#            h_other = ROOT.RooAbsData.createHistogram(mc_other,var+'_mc_other',ws.var(var))
#            try:
#                h_other.Scale(scales['other'])
#            except:
#                scales['other']=ws.var('n_other_%d'%itk).getVal()/h_other.Integral()
#                h_other.Scale(scales['other'])
#            h_other.SetFillStyle(1001)
#            h_other.SetFillColor(ROOT.kGray)
#            if opt.rebin : h_other.Rebin(opt.rebin)
#            
#            
#            h_data_sub=h_data.Clone(var+'_datasub')
#            h_data_sub.Add(h_c,-1)
#            h_data_sub.Add(h_other,-1)            
#            h_data_sub.SetMarkerSize(1.0)
#
#            canvas.cd()
#            pad = ROOT.TPad('pad','pad',0.45,0.73,0.95,0.91)
#            pad.SetRightMargin(0.05)
#            pad.SetLeftMargin(0.25)
#            pad.SetTopMargin(0.008)
#            pad.SetBottomMargin(0.03)
#            pad.Clear()
#            pad.Draw()
#            pad.cd()
#            if 'lxy' in var and itk<4 : pad.SetLogy(True)
#            else : pad.SetLogy(False)
#            h_b.Draw('hist')
#            h_b.GetYaxis().SetRangeUser(1,h_b.GetMaximum()*1.3)
#            h_b.GetYaxis().SetTitle('Events-#Sigmabkg')
#            h_b.GetXaxis().SetTitle('')
#            h_b.GetYaxis().SetTitleOffset(0.5)
#            h_b.GetYaxis().SetNdivisions(5)
#            h_b.GetYaxis().SetTitleSize(0.17)
#            h_b.GetYaxis().SetLabelSize(0.17)
#            h_data_sub.Draw('e1same')
#            h_data_sub.SetMarkerSize(0.6)
#
#            canvas.cd()
#            pad2 = ROOT.TPad('pad2','pad2',0.45,0.48,0.95,0.72)
#            pad2.SetRightMargin(0.05)
#            pad2.SetLeftMargin(0.25)
#            pad2.SetTopMargin(0.008)
#            pad2.SetBottomMargin(0.4)
#            pad2.SetFillStyle(0)
#            pad2.Clear()
#            pad2.Draw()
#            pad2.cd()
#            pad2.SetGridy()
#            canvas.cd()
#            pad.Delete()
#            pad2.Delete()

"""
steer the script
"""
def main():

    #configuration
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-i', '--inDir',       dest='inDir'   ,    help='input directory',        default=None,  type='string')
    parser.add_option('-o', '--outDir',      dest='outDir'  ,    help='output directory',       default='./',  type='string')
    parser.add_option(      '--weightPt',    dest='weightPt',    help='weight pt',              default=False, action='store_true')
    parser.add_option(      '--rebin',       dest='rebin',       help='rebin',                  default=0,     type=int)
    parser.add_option(      '--onlyCentral', dest='onlyCentral', help='only central jets',      default=False, action='store_true')
    parser.add_option(      '--vetoCentral', dest='vetoCentral', help='veto very central jets', default=False, action='store_true')
    parser.add_option(      '--minLxySig'  , dest='minLxySig',   help='min. lxy sig',           default=-1,    type=float)
    parser.add_option(      '--applyLEPweight', dest='applyLEPweight', help='reweight Z2* to LEP weight', default=False, action='store_true')
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

    #create ROOT file with templates and data
    if opt.flavorFitUrl is None: 
       if opt.wsUrl is None: opt.wsUrl=buildWorkspace(opt)
       opt.flavorFitUrl = doMassFit(opt)

    #show results of the flavour fits
    comparePostFitDistributions(opt)
    showFlavorFracs(opt)

    return 0

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())



