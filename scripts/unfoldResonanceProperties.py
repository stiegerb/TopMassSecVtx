#!/usr/bin/env python

import ROOT
import os,sys
import optparse

VARIABLES = ["mass", "pt", "eta", "ptfrac", "pzfrac", "ptrel", "pfrac", "ptchfrac", "pzchfrac", "dr", "wgt"]
XAXIS = {
	"D0":   "m(K^{+}#pi^{-}) [GeV]",
	"Dpm":  "m(K^{+}#pi^{-}#pi^{-}) [GeV]",
	"JPsi": "m(#mu^{+}#mu^{-}) [GeV]"
}

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
      # dx=gr.GetErrorXhigh(ip)-gr.GetErrorXlow(ip)
      totalY+=y
      # totalY+=y*dx

   # totalY = gr.Integral()

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
builds a canvas with the unfolded distributions and saves the distributions to a file (if given)
"""
def showUnfolded(sigData,bkgData,var=None,outD='unfolded',outF=None,postfixForOutputs=''):

   if var is None: return
   name=var.GetName()

   #create canvas
   c=ROOT.TCanvas(name,name,500,500)
   c.cd()
   frame = var.frame()
   bkgData.plotOn(frame,
                  ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),
                  ROOT.RooFit.Name(name+'_bckg'),
                  ROOT.RooFit.MarkerColor(419),
                  ROOT.RooFit.MarkerStyle(24),
                  ROOT.RooFit.LineWidth(2),
                  ROOT.RooFit.LineColor(419) )
   sigData.plotOn(frame,
                  ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),
                  ROOT.RooFit.Name(name+'_signal'),
                  ROOT.RooFit.MarkerColor(1),
                  ROOT.RooFit.MarkerStyle(20),
                  ROOT.RooFit.LineWidth(2),
                  ROOT.RooFit.LineColor(1) )
   frame.Draw()
   frame.GetYaxis().SetTitle('Candidates')
   frame.GetYaxis().SetTitleOffset(1.5)
   frame.GetXaxis().SetTitle(var.GetTitle())
   frame.GetXaxis().SetTitleOffset(1.0)

   #show a legend
   leg=ROOT.TLegend(0.6,0.75,0.9,0.9,"","brNDC")
   leg.SetFillStyle(0)
   leg.SetBorderSize(0)
   leg.SetTextFont(42)
   leg.SetTextSize(0.035)
   leg.AddEntry(name+"_signal", "Signal","p")
   leg.AddEntry(name+"_bckg","Background","p")
   leg.Draw()

   #save plot
   c.SaveAs(os.path.join(outD,name+"_unfolded%s.pdf"%postfixForOutputs))

   #save also distributions if output file is given
   if outF is None: return
   outF.cd()

   #get unfolded distributions
   signalGr=c.GetPrimitive(name+'_signal')
   signalGr.Clone().Write()

   bkgGr=c.GetPrimitive(name+'_bckg')
   bkgGr.Clone().Write()

   #prepare normalized distributions as well
   for gr in [signalGr,bkgGr]:
      norm_gr=normalizeDistribution(gr)
      norm_gr.Write()


"""
do the mass fit and display the result
"""
def doTheMassFit(ws,data=None,
                 CandTypes=None,
                 showResult=False,
                 outD='unfolded',
                 postfixForOutputs=''):

   #fit the mass spectrum
   ws.pdf('model').fitTo(data,ROOT.RooFit.Extended())

   if not showResult: return

   #get the main parameters of the fit
   nsig     = ws.var("nsig").getVal()
   nsigErr  = ws.var("nsig").getError()
   nbkg     = ws.var("nbkg").getVal()
   nbkgErr  = ws.var("nbkg").getError()
   mass     = ws.var("sig_mu").getVal()
   massErr  = ws.var("sig_mu").getError()
   try:
      width    = ws.var("sig_sigma").getVal()
      widthErr = ws.var("sig_sigma").getError()
   except:
      width    = ws.var("sig_Gauss1_sigma").getVal()
      widthErr = ws.var("sig_Gauss1_sigma").getError()


   #show result of the fit
   cfit=ROOT.TCanvas("cfit","cfit",500,500)
   cfit.cd()
   frame=ws.var("mass").frame()#ROOT.RooFit.Bins(50))
   data.plotOn(frame,ROOT.RooFit.DrawOption("p"),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.Name("data"))
   ws.pdf("model").plotOn(frame,
			  ROOT.RooFit.Components('bkg_model'),
                          ROOT.RooFit.LineColor(1),
                          ROOT.RooFit.LineWidth(2),
			  ROOT.RooFit.FillStyle(1001),
                          ROOT.RooFit.FillColor(920),
			  ROOT.RooFit.DrawOption("LF"),
                          ROOT.RooFit.MoveToBack(),
			  ROOT.RooFit.Name("bkg"))
   ws.pdf("model").plotOn(frame, ROOT.RooFit.FillStyle(0), ROOT.RooFit.MoveToBack(), ROOT.RooFit.Name("total"))
   frame.Draw()
   frame.GetYaxis().SetRangeUser(frame.GetMinimum(),1.4*frame.GetMaximum())
   frame.GetYaxis().SetTitle("Candidates")
   frame.GetYaxis().SetTitleOffset(1.6)
   if '411' in str(CandTypes):
	   frame.GetXaxis().SetTitle(XAXIS['Dpm'])
   if '421' in str(CandTypes):
	   frame.GetXaxis().SetTitle(XAXIS['D0'])
   if '443' in str(CandTypes):
	   frame.GetXaxis().SetTitle(XAXIS['JPsi'])
   frame.GetXaxis().SetTitleOffset(1.0)
   cfit.Modified()
   cfit.Update()

   #build a legend
   leg=ROOT.TLegend(0.7,0.8,0.9,0.95,"","brNDC")
   leg.SetFillStyle(0)
   leg.SetBorderSize(0)
   leg.SetTextFont(42)
   leg.SetTextSize(0.03)
   leg.AddEntry("data",  "Data",       "p")
   leg.AddEntry("bkg",   "Background", "f")
   leg.AddEntry("total", "Signal",     "f")
   leg.Draw()

   #display fit results on the canvas
   pt=ROOT.TPaveText(0.16,0.95,0.5,0.75,"brNDC")
   pt.SetFillStyle(0)
   pt.SetBorderSize(0)
   pt.SetTextFont(42)
   pt.SetTextAlign(12)
   pt.SetTextSize(0.03)
   pt.AddText("CMS work in progress")
   pt.AddText("m=%3.4f #pm %3.4f"%(mass,massErr))
   pt.AddText("#sigma=%3.4f #pm %3.4f"%(width,widthErr))
   pt.AddText("N_{signal}=%3.0f #pm %3.0f"%(nsig,nsigErr))
   pt.AddText("N_{bkg}=%3.0f #pm %3.0f"%(nbkg,nbkgErr))
   pt.Draw()

   #save to file
   outF='cfit%s'%postfixForOutputs
   cfit.SaveAs(os.path.join(outD,outF+'.pdf'))


"""
generates the RooFit workspace with the data and the fitting model
"""
def generateWorkspace(CandTypes,inputUrl,outputDir,postfixForOutputs):
   import math

   #init the workspace
   ws=ROOT.RooWorkspace("w")

   #create the data set
   variables=ROOT.RooArgSet()
   if '421' in str(CandTypes): ## D0 #note: str([1,2,3]) = '[1,2,3]'
      variables.add( ws.factory("mass[1.85,1.70,2.0]") )
   elif '411' in str(CandTypes): ## D+
      variables.add( ws.factory("mass[1.87,1.75,1.98]") )
   elif '443' in str(CandTypes): ## J/Psi
      variables.add( ws.factory("mass[3.1,2.50,3.40]") )

   variables.add( ws.factory("pt[0,0,100]") )
   variables.add( ws.factory("eta[0,0,2.5]") )
   variables.add( ws.factory("ptfrac[0,0,1.1]") )
   variables.add( ws.factory("pzfrac[0,0,1.1]") )
   variables.add( ws.factory("ptrel[0,0,4.0]") )
   variables.add( ws.factory("pfrac[0,0,1.1]") )
   variables.add( ws.factory("ptchfrac[0,0,1.1]") )
   variables.add( ws.factory("pzchfrac[0,0,1.1]") )
   variables.add( ws.factory("dr[0,0,0.3]") )
   variables.add( ws.factory("wgt[0,0,9999999.]") )
   data=ROOT.RooDataSet("data","data",variables,"wgt")

   #fill the dataset
   chain=ROOT.TChain("CharmInfo")
   for f in inputUrl: chain.AddFile(f)
   nEntries = chain.GetEntries()
   print "Will loop over", nEntries, "entries."
   for i in xrange(0,nEntries):
      if i%500 == 0:
         sys.stdout.write("[%3d/100]\r" % (100*i/float(nEntries)))
         sys.stdout.flush()

      chain.GetEntry(i)

      #filter on candidate type and mass range
      if not (chain.CandType in CandTypes) : continue
      if (chain.CandMass > ws.var("mass").getMax() or
          chain.CandMass < ws.var("mass").getMin()): continue

      #compute the variables and add to the dataset
      ws.var("mass").setVal(chain.CandMass)
      ws.var("pt").setVal(chain.CandPt)
      ws.var("eta").setVal(abs(chain.CandEta))
      ws.var("ptfrac").setVal(chain.CandPt/chain.JetPt)
      ws.var("pzfrac").setVal(chain.CandPz/chain.JetPz)
      ws.var("ptrel").setVal(chain.CandPtRel)
      ws.var("pfrac").setVal(chain.CandPt*math.cosh(chain.CandEta)/(chain.JetPt*math.cosh(chain.JetEta)))
      ws.var("ptchfrac").setVal(chain.CandPt/chain.SumPtCharged)
      ws.var("pzchfrac").setVal(chain.CandPz/chain.SumPzCharged)
      ws.var("dr").setVal(chain.CandDeltaR)
      ws.var("wgt").setVal(1.0)
      argset = ROOT.RooArgSet()
      for var in VARIABLES:
         argset.add(ws.var(var))
      argset.add(ws.var("wgt"))

      data.add(argset, ws.var("wgt").getVal())

   print "[  done ]"

   #import dataset to workspace
   getattr(ws,'import')(data)

   #now create a fitting model for the mass spectrum
   getattr(ws,'import')( ROOT.RooRealVar("nsig","Signal candidates",     0., 0., data.sumEntries()*2) )
   getattr(ws,'import')( ROOT.RooRealVar("nbkg","Background candidates", 0., 0., data.sumEntries()*2) )

   #specialization by candidate type may be needed
   ## D+-
   if '411' in str(CandTypes):
      ws.factory("RooGaussian::sig_model(mass,sig_mu[1.87,1.86,1.88],sig_sigma[0.01,0.001,0.05])")
      #ws.factory("RooCBShape::sig_model(mass,sig_mu[1.87,1.86,1.88],sig_sigma[0.001,0,0.025],sig_alpha[1,0.5,2],sig_n[5,0,10])")
      ws.factory("RooExponential::bkg_model(mass,bkg_lambda[-0.5,-4,0])")
   ## D0
   elif '421' in str(CandTypes):
      ws.factory("RooCBShape::sig_model(mass,sig_mu[1.87,1.86,1.88],sig_sigma[0.001,0,0.025],sig_alpha[1,0.5,2],sig_n[5,0,10])")
      ws.factory("RooExponential::bkg_model(mass,bkg_lambda[-0.5,-4,0])")
   ## J/Psi
   elif '443' in str(CandTypes):
      # ws.factory("RooCBShape::sig_CB(mass,sig_mu[3.1,3.05,3.15],sig_CB_sigma[0.07,0.01,0.5],sig_CB_alpha[1,0.5,2],sig_CB_n[5,0,10])")
      # ws.factory("RooGaussian::sig_Gauss(mass,sig_mu,sig_Gauss_sigma[0.1,0,0.2])")
      # getattr(ws,'import')( ROOT.RooRealVar("frac_CB","CB Fraction", 1., 0.9, 1.) )
      # sig_model=ROOT.RooAddPdf("sig_model","signal model",
      #                           ws.pdf("sig_CB"), ws.pdf("sig_Gauss"),
      #                           ws.var("frac_CB") )
      ws.factory("RooGaussian::sig_Gauss1(mass,sig_mu[3.1,3.05,3.15],sig_Gauss1_sigma[0.03,0.01,0.05])")
      ws.factory("RooGaussian::sig_Gauss2(mass,sig_mu,               sig_Gauss2_sigma[0.1,0.04,0.2])")
      getattr(ws,'import')( ROOT.RooRealVar("frac_Gauss1","Gauss1 Fraction", 1., 0.8, 1.) )
      sig_model=ROOT.RooAddPdf("sig_model","signal model",
                                ws.pdf("sig_Gauss1"), ws.pdf("sig_Gauss2"),
                                ws.var("frac_Gauss1") )
      getattr(ws,'import')( sig_model )

      ws.factory("RooExponential::bkg_model(mass,bkg_lambda[-1,-2,0])")

   #an expected pdf of signal+background
   model=ROOT.RooAddPdf("model","signal+background model",
                        ROOT.RooArgList( ws.pdf("sig_model"), ws.pdf("bkg_model") ),
                        ROOT.RooArgList( ws.var("nsig"),      ws.var("nbkg") )
                        )
   getattr(ws,'import')(model)

   #do the fit
   doTheMassFit(ws=ws,data=ws.data('data'),
               CandTypes=CandTypes,
               showResult=True,
               outD=outputDir,
               postfixForOutputs=postfixForOutputs)

   #fix all parameters except the yields in the model
   allVars=ws.allVars()
   varIter = allVars.createIterator()
   var=varIter.Next()
   while var :
      varName=var.GetName()
      if varName.find('sig_')==0 or varName.find('bkg_')==0 :
         ws.var(varName).setConstant()
         print varName,
      var=varIter.Next()
   print ' were set constant after fitting'

   #save workspace
   wsUrl=os.path.join(outputDir,"CharmInfo_workspace%s.root"%postfixForOutputs)
   ws.writeToFile(wsUrl)

   #all done here
   return wsUrl


"""
"""
def runDifferentialMeasurement(ws,vname,ranges,outF):
   outdir = os.path.dirname(outF.GetName())
   #unfix all parameters except the yields in the model
   allVars=ws.allVars()
   varIter = allVars.createIterator()
   var=varIter.Next()
   while var :
      varName=var.GetName()
      if varName.find('sig_')==0 or varName.find('bkg_')==0 :
         ws.var(varName).setConstant(False)
         print varName,
      var=varIter.Next()
   print ' were unfrozen for fitting the differential cross sections'


   dsigma={"S"      : ROOT.TGraphAsymmErrors(),
           "SoverB" : ROOT.TGraphAsymmErrors(),
           "mass"   : ROOT.TGraphAsymmErrors(),
           "width"  : ROOT.TGraphAsymmErrors() }
   for x in dsigma: dsigma[x].SetName('%s_d%s'%(vname,x))


   for ir in xrange(0,len(ranges)-1):
      vmin=ranges[ir]
      vmax=ranges[ir+1]
      cut='%s>=%f && %s<%f'%(vname,vmin,vname,vmax)
      print cut
      redData=ws.data("data").reduce(cut)
      if redData.numEntries<10 : continue

      avgVar, sigmaVar = redData.mean( ws.var( vname ) ), redData.sigma( ws.var( vname ) )

      doTheMassFit(ws=ws,data=redData,
                   showResult=True,
                   outD=outdir,
                   postfixForOutputs='%s_%3.1f_%3.1f'%(vname,vmin,vmax))
      nsig     = ws.var("nsig").getVal()
      nsigErr  = ws.var("nsig").getError()
      nbkg     = ws.var("nbkg").getVal()
      nbkgErr  = ws.var("nbkg").getError()
      mass     = ws.var("sig_mu").getVal()
      massErr  = ws.var("sig_mu").getError()
      try:
         width    = ws.var("sig_sigma").getVal()
         widthErr = ws.var("sig_sigma").getError()
      except:
         width    = ws.var("sig_Gauss1_sigma").getVal()
         widthErr = ws.var("sig_Gauss1_sigma").getError()

      np=dsigma["S"].GetN()
      binWidth=vmax-vmin
      binErrLo=avgVar-vmin
      binErrHi=vmax-avgVar
      dsigma["S"].SetPoint(np,avgVar,nsig/binWidth)
      dsigma["S"].SetPointError(np,binErrLo,binErrHi,nsigErr/binWidth,nsigErr/binWidth)

      if nbkg>0:
         soverb=(nsig/nbkg)
         soverb_err=(ROOT.TMath.Sqrt(ROOT.TMath.Power(nsigErr*nbkg,2)+ROOT.TMath.Power(nsig*nbkgErr,2))/ROOT.TMath.Power(nbkg,2))
         dsigma["SoverB"].SetPoint(np,avgVar,soverb)
         dsigma["SoverB"].SetPointError(np,binErrLo,binErrHi,soverb_err,soverb_err)

      dsigma["mass"].SetPoint(np,avgVar,mass)
      dsigma["mass"].SetPointError(np,binErrLo,binErrHi,massErr,massErr)
      dsigma["width"].SetPoint(np,avgVar,width)
      dsigma["width"].SetPointError(np,binErrLo,binErrHi,widthErr,widthErr)

   #differential measurements canvas
   cdiff=ROOT.TCanvas("cdiff","cdiff",500,500)
   for ds in dsigma:
      cdiff.cd()
      cdiff.Clear()
      ytitle="1/#sigma d#sigma/d%s"%vname
      if ds=="SoverB" : ytitle="S/B"
      if ds=="mass" : ytitle="M"
      if ds=="sigma" : ytitle="#sigma"
      xtitle = "Transverse momentum [GeV]"
      if vname=="eta": xtitle="Pseudo-rapidity"
      dsigma[ds].Draw("ap")
      dsigma[ds].SetMarkerStyle(20)
      dsigma[ds].GetXaxis().SetTitle( xtitle )
      dsigma[ds].GetYaxis().SetTitle( ytitle )
      cdiff.SaveAs(os.path.join(outdir,'diff_%s_%s.pdf'%(vname,ds)))

      #write to file
      outF.cd()
      dsigma[ds].Write()
      if ds=='S' : normalizeDistribution(dsigma[ds]).Write()


"""
steer the script
"""
def main():

   #global ROOT configuration
   ROOT.gStyle.SetOptStat(0)
   ROOT.gStyle.SetOptTitle(0)
   ROOT.RooMsgService.instance().setSilentMode(True)
   ROOT.gStyle.SetOptStat(0)
   ROOT.gStyle.SetOptFit(0)
   ROOT.gStyle.SetOptTitle(0)
   ROOT.gStyle.SetPadTopMargin(0.05)
   ROOT.gStyle.SetPadBottomMargin(0.1)
   ROOT.gStyle.SetPadLeftMargin(0.15)
   ROOT.gStyle.SetPadRightMargin(0.05)

   ROOT.gROOT.SetBatch(True)

   #configuration
   usage = 'usage: %prog [options]'
   parser = optparse.OptionParser(usage)
   parser.add_option('-c', '--cands',  dest='CandTypes', help='csv list of candidates', default='421', type='string')
   parser.add_option('-i', '--input',  dest='inputUrl' , help='csv list of files'     , default=None, type='string')
   parser.add_option('-w', '--ws',     dest='wsUrl'    , help='ws url'                , default=None, type='string')
   parser.add_option('-o', '--output', dest='output'   , help='Where to put the output', default=None, type='string')
   (opt, args) = parser.parse_args()

   #
   # differential xsec measurement: pT, eta
   #
   if opt.wsUrl:
      if not opt.output:
         opt.output = os.path.join(os.path.dirname(opt.wsUrl).strip('.root'),'diff')
      if not os.path.exists(opt.output):
         os.system('mkdir -p %s' % opt.output)

      print "Will store output in", opt.output
      wsUrl=opt.wsUrl
      wsF=ROOT.TFile.Open(wsUrl)
      ws=wsF.Get("w")
      wsF.Close()

      outUrl=os.path.join(opt.output, os.path.basename(wsUrl).replace('workspace','diff'))
      outF=ROOT.TFile(outUrl,'RECREATE')
      varRanges={"pt":[10,20,30,50,75],
                 "eta":[0,0.45,0.9,1.1,1.5,2.5]}
      for vname in varRanges:
         runDifferentialMeasurement(ws,vname,varRanges[vname],outF)
      outF.Close()

   #
   #generate workspace and run sPlot
   #
   else:
      if not opt.output:
         opt.output = os.path.join('unfolded',os.path.basename(opt.inputUrl).strip('.root'))
      else:
         opt.output = os.path.join(opt.output,os.path.basename(opt.inputUrl).strip('.root'))

      if not opt.output.endswith('/'): opt.output += '/'
      if not os.path.exists(opt.output):
         os.system('mkdir -p %s' % opt.output)

      print "Will store all output in", opt.output

      #turn csvs to arrays
      CandTypes = None
      if len(opt.CandTypes)>0:
         CandTypes=[int(val) for val in opt.CandTypes.split(',')]
      postfixForOutputs=''
      for c in CandTypes: postfixForOutputs +='_%d'%c

      inputUrl = None
      if not (opt.inputUrl is None):
         if len(opt.inputUrl)>0:
            inputUrl=opt.inputUrl.split(',')

      #get the workspace
      wsUrl=generateWorkspace(CandTypes=CandTypes,
                              inputUrl=inputUrl,
                              outputDir=opt.output,
                              postfixForOutputs=postfixForOutputs)
      print "Retrieving workspace from ",wsUrl
      wsF=ROOT.TFile.Open(wsUrl)
      ws=wsF.Get("w")
      wsF.Close()

      #use the SPlot class to add SWeights to our data set
      sData = ROOT.RooStats.SPlot("sData","An SPlot from mass",
                                  ws.data('data'),ws.pdf('model'),
                                  ROOT.RooArgList(ws.var('nsig'),ws.var('nbkg'))
         )
      getattr(ws,'import')(ws.data('data'), ROOT.RooFit.Rename("dataWithSWeights"))
      data = ws.data("dataWithSWeights")

      #the weighted data for signal and background species
      sigData = ROOT.RooDataSet(data.GetName(),data.GetTitle(),data,data.get(),'','nsig_sw')
      bkgData = ROOT.RooDataSet(data.GetName(),data.GetTitle(),data,data.get(),'','nbkg_sw')

      #show the unfolded distributions and save then to a file
      outFurl=os.path.join(opt.output,'UnfoldedDistributions%s.root'%postfixForOutputs)
      outF=ROOT.TFile.Open(outFurl,'RECREATE')
      varsToUnfold=[
         ['ptrel',    'p_{T,rel} [GeV]',           10],
         ['pfrac',    'p / p^{Jet} [GeV]',         10],
         ['ptfrac',   'p_{T} / p_{T}^{jet}',       10],
         ['pzfrac',   'p_{z} / p_{z}^{jet}',       10],
         ['ptchfrac', 'p_{T} / #Sigma_{ch} p_{T}', 10],
         ['pzchfrac', 'p_{z} / #Sigma_{ch} p_{z}', 10],
         ['dr',       '#DeltaR to jet',            10]
         ]
      for var,varTitle,nBins in varsToUnfold:
         ws.var(var).SetTitle(varTitle)
         ws.var(var).setBins(nBins)
         showUnfolded(sigData=sigData,
                      bkgData=bkgData,
                      var=ws.var(var),
                      outD=opt.output,
                      outF=outF,
                      postfixForOutputs=postfixForOutputs)
      outF.Close()
      print 'Unfolded distributions can be found @ ',outFurl

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())



