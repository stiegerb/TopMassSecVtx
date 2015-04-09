#!/usr/bin/env python

import ROOT
import os,sys
import optparse
import math
import pickle
from array import array

from UserCode.TopMassSecVtx.PlotUtils import *
from UserCode.TopMassSecVtx.CMS_lumi import *

NTKMIN, NTKMAX   = 2, 8
MASSMIN,MASSMAX  = 0.0, 6.0
MASSBINS         = 50

"""
"""
def showFlavorFit(url):

   #read histo map from cache
   cachefile=open(url,'r')
   flavorfracs=pickle.load(cachefile)
   cachefile.close()

   outDir=os.path.dirname(url)

   totalBnorm={}

   #iterate
   canvas=ROOT.TCanvas('c','c',500,500)
   for key in flavorfracs:

      totalBnorm[key]=flavorfracs[key]['b'].Clone(key+'_norm_b')
      totalBnorm[key].Scale(1./totalBnorm[key].Integral())
      totalBnorm[key].SetDirectory(0)

      #normalize for each vertex category
      for xbin in xrange(1,totalBnorm[key].GetXaxis().GetNbins()+1):
         totalBnorm[key].GetXaxis().SetBinLabel(xbin,'%d'%totalBnorm[key].GetXaxis().GetBinLowEdge(xbin))

         totalVtx=0
         for flavor in flavorfracs[key]:
            totalVtx+=flavorfracs[key][flavor].GetBinContent(xbin)
            flavorfracs[key][flavor].GetXaxis().SetBinLabel(xbin,'%d'%flavorfracs[key][flavor].GetXaxis().GetBinLowEdge(xbin))
         if totalVtx==0 : continue
         for flavor in flavorfracs[key]:
            flavorfracs[key][flavor].SetBinContent(xbin,
                                                   flavorfracs[key][flavor].GetBinContent(xbin)/totalVtx)
            flavorfracs[key][flavor].SetBinError(xbin,
                                                 flavorfracs[key][flavor].GetBinError(xbin)/totalVtx)

      #show normalized fractions
      canvas.Clear()
      stack=ROOT.THStack(key,key)
      leg=ROOT.TLegend(0.8,0.5,0.95,0.25)
      leg.SetFillStyle(0)
      leg.SetBorderSize(0)
      leg.SetTextFont(42)
      leg.SetTextSize(0.03)
      for flavor in flavorfracs[key]:
         color=ROOT.kGray
         if flavor=='c' : color=ROOT.kAzure-3
         if flavor=='b' : color=ROOT.kOrange
         flavorfracs[key][flavor].SetFillColor(color)
         flavorfracs[key][flavor].SetLineColor(color)
         flavorfracs[key][flavor].SetFillStyle(1001)
         flavorfracs[key][flavor].GetYaxis().SetRangeUser(0,1)
         stack.Add(flavorfracs[key][flavor],'hist')
         leg.AddEntry(flavorfracs[key][flavor],flavor,"f")
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

      canvas.SaveAs('%s/%s_flavor.png'%(outDir,key))
      canvas.SaveAs('%s/%s_flavor.pdf'%(outDir,key))            

   canvas.Clear()
   totalBnorm['obs'].Divide(totalBnorm['exp'])
   totalBnorm['obs'].Draw()
   totalBnorm['obs'].GetYaxis().SetTitle('observed/expected')
   totalBnorm['obs'].GetXaxis().SetTitle('SecVtx track multiplicity')
   totalBnorm['obs'].GetYaxis().SetRangeUser(0.5,1.25)
   totalBnorm['obs'].Fit('pol1','MRQ+','',4,NTKMAX)
   canvas.SetGridy(True)
   label=ROOT.TLatex()
   label.SetNDC()
   label.SetTextFont(42)
   label.SetTextSize(0.04)
   label.DrawLatex(0.18,0.95,'#bf{CMS} #it{simulation}')
   label.DrawLatex(0.75,0.95,'#scale[0.8]{19.7 fb^{-1} (8 TeV)}')
   canvas.SaveAs('%s/bobs_over_bexp.png'%outDir)   
   canvas.SaveAs('%s/bobs_over_bexp.pdf'%outDir)   
   totalBnorm['obs'].SaveAs('%s/bobs_over_bexp.root'%outDir)   

   

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

    #add files to the corresponding chain
    chains={'data':ROOT.TChain('SVLInfo'), 'mc':ROOT.TChain('SVLInfo')}
    for f in [ f for f in os.listdir(opt.inDir) if 'root' in f]:      
        key = 'data'
        if f.find('MC')==0: key='mc'
        chains[key].Add(os.path.join(opt.inDir,f))
                            
    #init the workspace
    ws=ROOT.RooWorkspace("w")

    #create the datasets
    variables=ROOT.RooArgSet()
    variables.add( ws.factory("pt[0,0,100.]") )
    variables.add( ws.factory("flav[0,0,99999.]") )
    variables.add( ws.factory("tagpt[0,0,200.]") )
    variables.add( ws.factory("probeeta[0,0,2.5]") )
    variables.add( ws.factory("mass[2,%f,%f]"%(MASSMIN,MASSMAX)))
    variables.add( ws.factory("chfrac[0,0,2]") )
    variables.add( ws.factory("lxy[0,0,15.]") )
    variables.add( ws.factory("lxysig[0,0,100.]") )
    variables.add( ws.factory("ntk[2,%d,%d]"%(NTKMIN,NTKMAX)) )
    variables.add( ws.factory("wgt[0,0,9999999.]") )
    datasets={
        'data':ROOT.RooDataSet("data","data",variables,"wgt"),
        'mc':ROOT.RooDataSet("mc","mc",variables,"wgt")
        }
    norm={'data':[],'mc':[]}
    templates={'b':[],'c':[],'other':[]}
    weightGr=[]
    for itk in xrange(NTKMIN,NTKMAX+1):
        norm['data'].append(0.0)
        norm['mc'].append(0.0)
        for key in templates:
            templates[key].append(ROOT.TH1F('%s_%d_template'%(key,itk),'',MASSBINS,MASSMIN,MASSMAX))
        if opt.weightPt:
            #binPt = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,250,500]
            #hdata=ROOT.TH1F('hptdata','',len(binPt)-1,array('d',binPt))
            hdata=ROOT.TH1F('hptdata','',100,0,500)
            hdata.Sumw2()
            extraCond=''
            if opt.onlyCentral : extraCond+='&&TMath::Abs(JEta)<1.1'
            if opt.vetoCentral : extraCond+='&&TMath::Abs(JEta)>0.1'
            chains['data'].Draw('LPt>>hptdata','SVNtrk==%d && SVLxySig>%f %s'%(itk,opt.minLxySig,extraCond),'norm goff')
            #hmc=ROOT.TH1F('hptmc','',len(binPt)-1,array('d',binPt))
            hmc=ROOT.TH1F('hptmc','',100,0,500)
            hmc.Sumw2()
            chains['mc'].Draw('LPt>>hptmc','(SVNtrk==%d %s)*Weight[0]*XSWeight'%(itk,extraCond),'norm goff')
            hdata.Divide(hmc)
            weightGr.append( ROOT.TGraphErrors(hdata) )
            hdata.Delete()
            hmc.Delete()

            
    #fill the datasets
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
                
            #renormalize to range
            lpt=ROOT.TMath.Min(chains[key].LPt,500)
            mass=ROOT.TMath.Max( MASSMIN, ROOT.TMath.Min(chains[key].SVMass,MASSMAX) )
            
                      
            #check weight
            totalWeight=chains[key].Weight[0]*chains[key].XSWeight
            if totalWeight<0 or math.isnan(totalWeight) :
                print 'Caught unphysical weight ',totalWeight
                continue
            if key=='data' : totalWeight=1.0
            elif len(weightGr)>ntk-NTKMIN:
                totalWeight *= weightGr[ntk-NTKMIN].Eval(lpt)
            
            #fill variables
            norm[key][ntk-2]+=totalWeight
            ws.var('pt').setVal(chains[key].SVPt)
            ws.var('lxy').setVal(chains[key].SVLxy)
            ws.var('lxysig').setVal(lxysig)
            ws.var('mass').setVal(mass)
            ws.var('ntk').setVal(ntk)
            ws.var('tagpt').setVal(lpt)
            ws.var('probeeta').setVal(ROOT.TMath.Abs(chains[key].JEta))
            ws.var('flav').setVal(ROOT.TMath.Abs(chains[key].JFlav))
            ws.var('chfrac').setVal(chains[key].SVPtChFrac)
            ws.var('wgt').setVal(totalWeight)
            argset = ROOT.RooArgSet()
            for var in ['pt','flav','mass','chfrac','lxy','lxysig','tagpt','probeeta','ntk','wgt']: argset.add(ws.var(var))
            datasets[key].add(argset, ws.var("wgt").getVal())

            #fill binned templates
            if key=='mc':
                templateKey='other'
                if ROOT.TMath.Abs( ws.var('flav').getVal() ) == 5 : templateKey='b'
                if ROOT.TMath.Abs( ws.var('flav').getVal() ) == 4 : templateKey='c'
                templates[templateKey][ntk-2].Fill(mass,totalWeight)

        #import new dataset
        print 'Dataset is filled with %f selected entries'%(datasets[key].sumEntries())
        getattr(ws,'import')(datasets[key])
        
    #check templates for entries with 0 and create PDFs
    massvariables=ROOT.RooArgSet()
    massvariables.add( ws.var('mass') )
    for itk in xrange(0,len(templates['b'])):
        ntk=NTKMIN+itk
        mcScaleFactor=norm['data'][itk]/norm['mc'][itk]
        print 'For %d tracks residual scale factor for MC is %f'%(ntk,mcScaleFactor)
        for key in templates:
            for xbin in xrange(1,templates[key][itk].GetXaxis().GetNbins()):
                binContent=templates[key][itk].GetBinContent(xbin)
                if binContent>0: continue
                templates[key][itk].SetBinContent(xbin,1.0e-3)
            templates[key][itk].Scale(mcScaleFactor)
            catKey='%s_%d'%(key,ntk)
            getattr(ws,'import')( ROOT.RooDataHist('%s_shapehist'%catKey,'%s_shapehist'%catKey,
                                                ROOT.RooArgList(massvariables), templates[key][itk]) )
            getattr(ws,'import')( ROOT.RooHistPdf('%s_shape'%catKey,     '%s_shapehist'%catKey,
                                            massvariables, ws.data('%s_shapehist'%catKey) ) )
            
            nexp=templates[key][itk].Integral()
            ws.factory('n_%s[%f,%f,%f]'%(catKey,nexp,0.,5*nexp))
                        
        ws.factory("SUM::model_%d( n_b_%d*b_%d_shape, n_c_%d*c_%d_shape, n_other_%d*other_%d_shape )"%(ntk,ntk,ntk,ntk,ntk,ntk,ntk))
        
    #save workspace
    wsUrl=os.path.join(opt.outDir,"SecVtxWorkspace.root")
    ws.writeToFile(wsUrl)
    fOut=ROOT.TFile.Open(wsUrl,'UPDATE')
    for key in templates: 
        for h in templates[key]:
            h.Write()
    fOut.Close()
    return wsUrl


"""
"""
def doMassFit(opt):

    #read workspace from file
    fIn=ROOT.TFile.Open(opt.wsUrl)
    ws=fIn.Get('w')
    fIn.Close()
                
    flavorFracs={'exp':{},'obs':{}}
    for key in flavorFracs:
       for flav in ['b','c','other']:
          flavorFracs[key][flav]=ROOT.TH1F(flav+'_'+key,';Track multiplicity; Vertices',NTKMAX-NTKMIN+1,NTKMIN,NTKMAX+1)
          flavorFracs[key][flav].SetDirectory(0)
          flavorFracs[key][flav].Sumw2()
          
    #fit and save results
    canvas=ROOT.TCanvas('c','c',500,500)
    ws.var('mass').setBins(MASSBINS)
    for itk in xrange(NTKMIN,NTKMAX+1):

        data=ws.data('data').reduce('ntk==%d'%itk)
        mc_b=ws.data('mc').reduce('ntk==%d && flav==5'%itk)
        mc_c=ws.data('mc').reduce('ntk==%d && flav==4'%itk)
        mc_other=ws.data('mc').reduce('ntk==%d && flav!=5 && flav!=4'%itk)

        for flavor in ['b','c','other']:
           flavorFracs['exp'][flavor]    .SetBinContent(itk-NTKMIN+1,ws.var('n_%s_%d'%(flavor,itk)).getVal())

        model=ws.pdf('model_%d'%itk)
        model.fitTo(data,ROOT.RooFit.Extended())        

        for flavor in ['b','c','other']:
           flavorFracs['obs'][flavor]    .SetBinContent(itk-NTKMIN+1,ws.var('n_%s_%d'%(flavor,itk)).getVal())
           flavorFracs['obs'][flavor]    .SetBinError(itk-NTKMIN+1,ws.var('n_%s_%d'%(flavor,itk)).getError())
                
        #loop over variables
        scales={}
        for var,title in [('mass','SecVtx mass [GeV]'),
                          ('pt','SecVtx transverse momentum [GeV]'),
                          ('tagpt','Tag transverse momentum [GeV]'),
                          ('probeeta','Probe jet pseudo-rapidity'),
                          ('chfrac','p_{T}(SecVtx) / #sum_{ch} p_{T}') ,
                          ('lxy', 'L_{xy} [cm]'),
                          ('lxysig', 'L_{xy} significance')]:
            h_data  = ROOT.RooAbsData.createHistogram(data,var+'_data',ws.var(var))
            h_data.SetMarkerStyle(20)
            h_data.SetLineColor(1)
            h_data.SetMarkerColor(1)
            if opt.rebin!=0 : h_data.Rebin(opt.rebin)
            h_b     = ROOT.RooAbsData.createHistogram(mc_b,var+'_mc_b',ws.var(var))
            try:        
                h_b.Scale(scales['b'])
            except:
                scales['b']=ws.var('n_b_%d'%itk).getVal()/h_b.Integral()
                h_b.Scale(scales['b'])
            h_b.SetFillStyle(1001)
            h_b.SetFillColor(ROOT.kOrange)
            if opt.rebin!=0 : h_b.Rebin(opt.rebin)
            h_c     = ROOT.RooAbsData.createHistogram(mc_c,var+'_mc_c',ws.var(var))
            try:
                h_c.Scale(scales['c'])
            except:
                scales['c']=ws.var('n_c_%d'%itk).getVal()/h_c.Integral()
                h_c.Scale(scales['c'])
            h_c.SetFillStyle(1001)
            h_c.SetFillColor(ROOT.kAzure-3)
            if opt.rebin!=0 : h_c.Rebin(opt.rebin)
            h_other = ROOT.RooAbsData.createHistogram(mc_other,var+'_mc_other',ws.var(var))
            try:
                h_other.Scale(scales['other'])
            except:
                scales['other']=ws.var('n_other_%d'%itk).getVal()/h_other.Integral()
                h_other.Scale(scales['other'])
            h_other.SetFillStyle(1001)
            h_other.SetFillColor(ROOT.kGray)
            if opt.rebin : h_other.Rebin(opt.rebin)
            
            stack=ROOT.THStack('hs','total')
            stack.Add(h_b,'hist')
            stack.Add(h_c,'hist')
            stack.Add(h_other,'hist')
            stack.Draw()
            stack.GetYaxis().SetTitle('Events')
            stack.GetYaxis().SetTitleOffset(1.5)
            stack.GetXaxis().SetTitle(title)
            stack.GetXaxis().SetTitleOffset(1.2)
            stack.GetYaxis().SetTitleSize(0.04)
            stack.GetXaxis().SetTitleSize(0.04)
            stack.GetYaxis().SetLabelSize(0.035)
            stack.GetXaxis().SetLabelSize(0.035)

            h_data.Draw('same')
            if 'lxy' in var and itk<4 : canvas.SetLogy(True)
            else : canvas.SetLogy(False)
            
            h_data_sub=h_data.Clone(var+'_datasub')
            h_data_sub.Add(h_c,-1)
            h_data_sub.Add(h_other,-1)            
            h_data_sub.SetMarkerSize(1.0)

            canvas.cd()
            pad = ROOT.TPad('pad','pad',0.45,0.73,0.95,0.91)
            pad.SetRightMargin(0.05)
            pad.SetLeftMargin(0.25)
            pad.SetTopMargin(0.008)
            pad.SetBottomMargin(0.03)
            pad.Clear()
            pad.Draw()
            pad.cd()
            if 'lxy' in var and itk<4 : pad.SetLogy(True)
            else : pad.SetLogy(False)
            h_b.Draw('hist')
            h_b.GetYaxis().SetRangeUser(1,h_b.GetMaximum()*1.3)
            h_b.GetYaxis().SetTitle('Events-#Sigmabkg')
            h_b.GetXaxis().SetTitle('')
            h_b.GetYaxis().SetTitleOffset(0.5)
            h_b.GetYaxis().SetNdivisions(5)
            h_b.GetYaxis().SetTitleSize(0.17)
            h_b.GetYaxis().SetLabelSize(0.17)
            h_data_sub.Draw('e1same')
            h_data_sub.SetMarkerSize(0.6)

            canvas.cd()
            pad2 = ROOT.TPad('pad2','pad2',0.45,0.48,0.95,0.72)
            pad2.SetRightMargin(0.05)
            pad2.SetLeftMargin(0.25)
            pad2.SetTopMargin(0.008)
            pad2.SetBottomMargin(0.4)
            pad2.SetFillStyle(0)
            pad2.Clear()
            pad2.Draw()
            pad2.cd()
            h_res=h_data_sub.Clone(var+'_datares')
            h_res.Add(h_b,-1)
            for xbin in xrange(1,h_res.GetXaxis().GetNbins()):
                mcunc=stack.GetStack().At( stack.GetStack().GetEntriesFast()-1 ).GetBinError(xbin)
                if mcunc<=0: continue
                pull=h_res.GetBinContent(xbin)/mcunc
                pullErr=h_res.GetBinError(xbin)/mcunc
                h_res.SetBinContent(xbin,pull)
                h_res.SetBinError(xbin,pullErr)
            h_res.Draw()
            h_res.GetYaxis().SetTitle('Pull')
            h_res.GetXaxis().SetTitle('')
            h_res.GetYaxis().SetTitleOffset(0.7)
            h_res.GetYaxis().SetNdivisions(5)
            h_res.GetXaxis().SetNdivisions(5)
            h_res.GetYaxis().SetTitleSize(0.13)
            h_res.GetYaxis().SetLabelSize(0.13)
            h_res.GetXaxis().SetTitleSize(0.13)
            h_res.GetXaxis().SetLabelSize(0.13)
            h_res.SetMarkerSize(0.6)
            h_res.GetYaxis().SetRangeUser(-5.7,6)
            pad2.SetGridy()
            canvas.cd()
            label=ROOT.TLatex()
            label.SetNDC()
            label.SetTextFont(42)
            label.SetTextSize(0.04)
            label.DrawLatex(0.18,0.95,'#bf{CMS} #it{simulation}  #scale[0.8]{#it{N_{tracks}=%d}}'%itk)
            label.DrawLatex(0.75,0.95,'#scale[0.8]{19.7 fb^{-1} (8 TeV)}')

            leg=ROOT.TLegend(0.8,0.5,0.95,0.25)
            leg.SetFillStyle(0)
            leg.SetBorderSize(0)
            leg.SetTextFont(42)
            leg.SetTextSize(0.03)
            leg.AddEntry(h_data, "data","p")
            leg.AddEntry(h_b,"b","f")
            leg.AddEntry(h_c,"c","f")
            leg.AddEntry(h_other,"other","f")
            leg.Draw()
            canvas.Modified()
            canvas.Update()
            canvas.SaveAs('%s/%s_%d.png'%(opt.outDir,var,itk))
            canvas.SaveAs('%s/%s_%d.pdf'%(opt.outDir,var,itk))
            #raw_input('...press key to continue')
            pad.Delete()
            pad2.Delete()


    #dump fits to file
    flavorFitUrl='%s/.flavorfits.pck'%opt.outDir
    cachefile = open(flavorFitUrl,'w')
    pickle.dump( flavorFracs, cachefile, pickle.HIGHEST_PROTOCOL)
    cachefile.close()

    return flavorFitUrl

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

    if opt.flavorFitUrl is None:
       if opt.wsUrl is None: opt.wsUrl=buildWorkspace(opt)
       opt.flavorFitUrl = doMassFit(opt)
    showFlavorFit(url=opt.flavorFitUrl)
    return

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())



