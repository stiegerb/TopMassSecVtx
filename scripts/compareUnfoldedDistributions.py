#!/usr/bin/env python

import ROOT
import os,sys
import optparse
import glob
import math
from CMS_lumi import CMS_lumi
from runPlotter import openTFile,checkKeyInFile

COLORS=[862,800,1,922]
FILLS=[1001,3001,3004,3002]

TAGS = {
	'D0':   't#bar{t} #rightarrow #mu D^{0} (K^{-}#pi^{+}) X',
	'Dpm':  't#bar{t} #rightarrow D^{#pm}(K^{-}#pi^{+}#pi^{+}) X',
        'JPsi': 't#bar{t} #rightarrow J/#Psi(#mu^{+}#mu^{-}) X',
	'Dsm':  't#bar{t} #rightarrow D*^{#pm}(D^{0}(K^{-}#pi^{+})#pi^{+}) X',
        }

INPUTS = [
   ('data'       , 'Data'                , 'Data8TeV_merged'                        , ROOT.kBlack),
   ('z2srblep'   , 'Z2*LEP r_{b}'      ,   'MC8TeV_TTJets_MSDecays_172v5_bfrag'     , ROOT.kBlack),
   ('z2srblepup' , 'Z2*LEP r_{b}+' ,       'MC8TeV_TTJets_MSDecays_172v5_bfragup'   , ROOT.kMagenta),
   ('z2srblepdn' , 'Z2*LEP r_{b}-' ,       'MC8TeV_TTJets_MSDecays_172v5_bfragdn'   , ROOT.kMagenta+2),
   ('z2s'        , 'Z2*' ,                 'MC8TeV_TTJets_MSDecays_172v5'           , ROOT.kRed+1),
   ('z2spete'    , 'Z2* Peterson'  ,       'MC8TeV_TTJets_MSDecays_172v5_bfragpete' , ROOT.kViolet+2),
   ('z2slund'    , 'Z2* Lund'      ,       'MC8TeV_TTJets_MSDecays_172v5_bfraglund' , ROOT.kAzure+7),
   #('powpyth'    , 'Powheg+Pythia+Z2*'   , 'MC8TeV_TT_Z2star_powheg_pythia'         , ROOT.kAzure+7),
   ('powherw'    , 'Herwig AUET2' ,        'MC8TeV_TT_AUET2_powheg_herwig'          , ROOT.kGreen+2),
   #('p11'        , 'P11' ,                 'MC8TeV_TTJets_TuneP11'           , ROOT.kYellow+1),
   #  ('p11frag'    , 'P11'    ,      'MC8TeV_TTJets_MSDecays_172v5_bfragp11'  , ROOT.kRed-9),
   ]

def computeFirstMoments(graph):
   mu0, mu1, mu2 = 0,0,0
   x, y = ROOT.Double(0), ROOT.Double(0)
   for i in xrange(0,graph.GetN()):
      graph.GetPoint( i,x,y )
      ey=graph.GetErrorY(i)
      mu0 += y
      mu1 += x*y
      mu2 += x*x*y

   mu1=mu1/mu0
   mu2=mu2/mu0

   emu1=0
   for i in xrange(0,graph.GetN()):
      emu1 += ROOT.TMath.Power(ey*(x*mu0-mu1)/mu0,2)
   emu1 = ROOT.TMath.Sqrt(emu1)
   return mu0,mu1,emu1,mu2


AXISTITLES = {
  'norm_pt_dS'           :
        ("Transverse momentum [GeV]",
         "1/#sigma d#sigma/dp_{T} [GeV^{-1}]"),
  'norm_eta_dS'          :
        ("Pseudorapidity",
         "1/#sigma d#sigma/d#eta"),
  'norm_ptrel_signal'    :
        ("p_{T}^{rel} [GeV]",
         "1/#sigma d#sigma/d p_{T}^{rel} [GeV^{-1}]"),
  'norm_pfrac_signal'    :
        ("R_{p} = p / p^{jet}",
        "1/#sigma d#sigma/d R_{p}"),
  'norm_ptfrac_signal'   :
        ("R_{p_{T}} = p_{T} / p_{T}^{jet}",
         "1/#sigma d#sigma/d R_{p_{T}}"),
  'norm_pzfrac_signal'   :
        ("R_{p_{z}} = p_{z} / p_{z}^{jet}",
         "1/#sigma d#sigma/d R_{p_{z}}"),
  'norm_ptchfrac_signal' :
        ("R_{p_{T}}^{ch} = p_{T} / #Sigma p_{T}^{ch}",
         "1/#sigma d#sigma/d R_{p_{T}}^{ch}"),
  'norm_pzchfrac_signal' :
        ("R_{p_{z}}^{ch} = p_{z} / #Sigma p_{z}^{ch}",
         "1/#sigma d#sigma/d R_{p_{z}}^{ch}"),
  'norm_dr_signal'       :
        ("#DeltaR",
         "1/#sigma d#sigma/d #DeltaR"),
}

def makeLegend(name,nentries,x1=0.70,y1=0.65,x2=0.90,y2=0.95):
   leg=ROOT.TLegend(x1,y2-nentries*0.07,x2,y2,"","brNDC")
   leg.SetFillStyle(0)
   leg.SetBorderSize(0)
   leg.SetTextFont(43)
   leg.SetTextSize(14)
   leg.SetName(name)
   return leg

def computePullFromGraphs(graph, reference):
   if not graph.GetN() == reference.GetN():
      print "divideGraphWithErrors::ERROR: Non-matching graphs"
      return None

   pullpoints = []
   for point in range(graph.GetN()):
      gx,gy = ROOT.Double(0), ROOT.Double(0)
      graph.GetPoint(point, gx, gy)
      refx,refy = ROOT.Double(0), ROOT.Double(0)
      reference.GetPoint(point, refx, refy)

      ## Check if the points are consistent, warn if not
      if abs(refx-gx)/abs(gx) > 0.1:
         print "divideGraphWithErrors::WARNING: diverging x values"


      ## Compute pulls
      err = max(abs(graph.GetErrorYhigh(point)),
                abs(graph.GetErrorYlow(point)))
      try:
         pull      = (refy-gy)/err
         pullErrUp = graph.GetErrorYhigh(point)/err
         pullErrDn = graph.GetErrorYlow(point)/err
      except ZeroDivisionError:
         # pullpoints.append((gx, 0., 0., 0.))
         continue

      pullpoints.append((gx, pull, pullErrUp, pullErrDn))

   ## Create the pull graph
   #pullgraph = ROOT.TGraphAsymmErrors(len(pullpoints))
   #pullgraph.SetName("%s_pull"%graph.GetName())
   pullgraph = graph.Clone("%s_pull"%graph.GetName())
   pullgraph.Set(0)
   for n,(x,val,up,dn) in enumerate(pullpoints):
      pullgraph.SetPoint(n, x, val)
      pullgraph.SetPointError(n, 0.,0., dn, up)

   ## Pass all the styles
   for attr in ['LineColor', 'LineWidth', 'LineStyle',
                'MarkerColor', 'MarkerStyle', 'MarkerSize',
                'FillColor', 'FillStyle']:
      getattr(pullgraph, "Set%s"%attr)(getattr(graph, "Get%s"%attr)())
   pullgraph.GetXaxis().SetTitle(graph.GetXaxis().GetTitle())

   return pullgraph

"""
steer the script
"""
def main():
   global INPUTS
   global TAGS
   #configuration
   usage = 'usage: %prog [options]'
   parser = optparse.OptionParser(usage)
   parser.add_option('-i', '--input' , dest='input',
                     help='input directory',
                     default=None, type='string')
   # parser.add_option('-t', '--title', dest='InputTitles',
   #                   help='titles',
   #                   default=None, type='string')
   parser.add_option('-o', '--outDir' , dest='outDir',
                     help='destination for output plots',
                     default='charmplots', type='string')
   parser.add_option('-d', '--dist' , dest='Dist',
                     help='distribution to compare',
                     default='ptfrac', type='string')
   parser.add_option('--showMean' , dest='showMean',
                     help='show mean instead of pull',
                     default=False, action='store_true')
   parser.add_option('-m', '--maxY', dest='MaxY',
                     help='max y',
                     default=0.75, type=float)
   parser.add_option('-b', '--base', dest='BaseName',
                     help='base name for root files' ,
                     default='UnfoldedDistributions', type='string')
   parser.add_option('--tag', dest='Tag', help='Add a tag label',
                     default='', type='string')
   parser.add_option('-z', dest='z', help='use Z control region inputs',
                     default=False, action='store_true')
   (opt, args) = parser.parse_args()

   if opt.z:
      print 'Using Z control region inputs'
      INPUTS = [
         ('data'       , 'Data'          , 'Data8TeV_DoubleLepton_merged_filt23' , ROOT.kBlack),
         ('z2s'        , 'Z2*' ,           'MC8TeV_DY_merged_filt23'             , ROOT.kBlue+3),
         ('z2srblep'   , 'Z2*LEP rb'     , 'MC8TeV_DY_merged_filt23_bfrag'       , ROOT.kMagenta),
         ('z2srblepup' , 'Z2*LEP rb+' ,    'MC8TeV_DY_merged_filt23_bfragup'     , ROOT.kMagenta+2),
         ('z2srblepdn' , 'Z2*LEP rb-' ,    'MC8TeV_DY_merged_filt23_bfragdn'     , ROOT.kMagenta-9),
         ('p11frag'    , 'P11'    ,        'MC8TeV_DY_merged_filt23_bfragp11'    , ROOT.kRed-9),
         ('z2spete'    , 'Z2* Peterson'  , 'MC8TeV_DY_merged_filt23_bfragpete'   , ROOT.kAzure+7),
         ('z2slund'    , 'Z2* Lund'      , 'MC8TeV_DY_merged_filt23_bfraglund'   , ROOT.kBlue-7)
         ]
      TAGS = {
         'D0':   'Z/#gamma^{*}(ll) #mu D^{0} (K^{-}#pi^{+}) + X',
         'Dpm':  'Z/#gamma^{*}(ll) D^{#pm}(K^{-}#pi^{+}#pi^{+}) + X',
         'JPsi': 'Z/#gamma^{*}(ll) J/#Psi(#mu^{+}#mu^{-}) + X',
         'Dsm':  'Z/#gamma^{*}(ll) D*^{#pm}(D^{0}(K^{-}#pi^{+})#pi^{+}) X',
         }

   #global ROOT configuration
   ROOT.gStyle.SetOptStat(0)
   ROOT.gStyle.SetOptTitle(0)
   ROOT.gStyle.SetPadTopMargin(0.05)
   ROOT.gStyle.SetPadBottomMargin(0.12)
   ROOT.gStyle.SetPadLeftMargin(0.15)
   ROOT.gStyle.SetPadRightMargin(0.05)

   print "Will store plots in", opt.outDir

   #get graphs from files
   allGr={}

   for tag,title,dirname,color in INPUTS:
      inputdir = os.path.join(opt.input,dirname)
      if 'diff' in opt.BaseName:
         inputdir = os.path.join(inputdir, 'diff')
      files = glob.glob("%s/%s_*.root"%(inputdir,opt.BaseName))
      if not files:
         print "No files found:", "%s/%s_*.root"%(inputdir,opt.BaseName)
         continue
      assert(len(files) == 1)
      inF=openTFile(files[0])
      checkKeyInFile('%s'%opt.Dist, inF, doraise=True)
      allGr[tag] = inF.Get('%s'%opt.Dist)
      inF.Close()

      #format the new plot
      allGr[tag].SetName('gr%s'%tag)
      allGr[tag].SetTitle(title)
      allGr[tag].GetYaxis().SetTitleFont(43)
      allGr[tag].GetYaxis().SetLabelFont(43)
      allGr[tag].GetYaxis().SetTitleSize(24)
      allGr[tag].GetXaxis().SetTitleSize(24)
      allGr[tag].GetXaxis().SetTitleFont(43)
      allGr[tag].GetXaxis().SetLabelFont(43)
      allGr[tag].GetXaxis().SetLabelSize(18)
      allGr[tag].GetYaxis().SetLabelSize(18)
      allGr[tag].GetXaxis().SetTitleOffset(0.9)
      allGr[tag].GetYaxis().SetTitleOffset(1.1)

      axistitles = AXISTITLES.get(opt.Dist,(opt.Dist,'Normalized'))
      allGr[tag].GetXaxis().SetTitle(axistitles[0])
      allGr[tag].GetYaxis().SetTitle(axistitles[1])

      if tag == 'data':
         allGr[tag].SetFillStyle(0)
         allGr[tag].SetFillColor(0)
         allGr[tag].SetLineColor(ROOT.kBlack)
         allGr[tag].SetLineWidth(2)
         allGr[tag].SetMarkerColor(ROOT.kBlack)
         allGr[tag].SetMarkerStyle(20)
         allGr[tag].SetMarkerSize(0.8)
      else:
         allGr[tag].SetMarkerStyle(20)
         allGr[tag].SetMarkerSize(0.8)
         allGr[tag].SetMarkerColor(color)
         allGr[tag].SetLineColor(color)
         allGr[tag].SetFillStyle(3002)
         allGr[tag].SetFillColor(color)

   # compute all the pulls or means:
   compGrs={}
   itagCtr=0
   for tag,_,_,_ in INPUTS:
      graph=allGr[tag]
      if opt.showMean:
         mu0, avg, avgErr, mu2 = computeFirstMoments(graph)
         rms = ROOT.TMath.Sqrt(mu2-avg*avg)
         if tag=='data' : continue
         compGrs[tag]=graph.Clone('compgr%s'%tag)
         compGrs[tag].Set(0)
         compGrs[tag].SetPoint(0,avg,len(compGrs))
         compGrs[tag].SetPointError(0,avgErr,avgErr,0.5,0.5)
         itagCtr+=1
      else:
         compGrs[tag]=computePullFromGraphs(graph, allGr['data'])

   ##########################################
   # PLOTTING
   canvas=ROOT.TCanvas('c','c',500,500)
   canvas.cd()
   try:
      allGr['z2srblep'].Draw('A3')
      allGr['z2srblep'].GetYaxis().SetRangeUser(0,opt.MaxY)
      allGr['data'].Draw('p')
   except KeyError:
      print "WARNING: No data or Z2*LEP rb to plot"
      pass

   CMS_lumi(canvas,2,10)
   if opt.Tag:
      tl = ROOT.TLatex()
      tl.SetNDC()
      tl.SetTextFont(43)
      tl.SetTextSize(18)
      tl.SetTextAlign(32)
      tl.DrawLatex(0.93, 0.92, TAGS[opt.Tag])

   insetPad = ROOT.TPad('inset','inset',0.55,0.55,0.95,0.85)
   if 'chfrac' in opt.Dist : insetPad = ROOT.TPad('inset','inset',0.15,0.55,0.55,0.85)
   insetPad.SetTopMargin(0.05)
   insetPad.SetLeftMargin(0.1)
   insetPad.SetRightMargin(0.4)
   insetPad.SetBottomMargin(0.2)
   insetPad.SetFillStyle(0)
   insetPad.Draw()
   insetPad.cd()
   insetPad.Clear()
   frame,dataRef=ROOT.TGraph(),None
   if opt.showMean:
      mu0, avg, avgErr, mu2 = computeFirstMoments(allGr['data'])
      rms = ROOT.TMath.Sqrt(mu2-avg*avg)
      frame.SetTitle('frame')
      frame.SetMarkerStyle(1)
      frame.SetLineColor(1)
      frame.SetPoint(0,avg-rms*0.3,-0.5)
      frame.SetPoint(1,avg-rms*0.3,len(INPUTS)+0.5)            
      frame.SetPoint(2,avg+rms*0.3,len(INPUTS)+0.5)
      frame.SetPoint(3,avg+rms*0.3,-0.5)
      frame.SetPoint(4,avg-rms*0.3,-0.5)

      dataRef=ROOT.TGraph()
      dataRef.SetTitle('dataref')
      dataRef.SetPoint(0,avg-avgErr,-0.5)
      dataRef.SetPoint(1,avg-avgErr,len(INPUTS)+0.5)
      dataRef.SetPoint(2,avg+avgErr,len(INPUTS)+0.5)
      dataRef.SetPoint(3,avg+avgErr,-0.5)
      dataRef.SetPoint(4,avg-avgErr,-0.5)

   else:
      frame.SetTitle('frame')
      frame.SetMarkerStyle(1)
      frame.SetLineColor(1)
      frame.SetPoint(0,allGr['data'].GetHistogram().GetXaxis().GetXmin(),-5.1)
      frame.SetPoint(1,allGr['data'].GetHistogram().GetXaxis().GetXmin(),5.1)
      frame.SetPoint(2,allGr['data'].GetHistogram().GetXaxis().GetXmax(),5.1)
      frame.SetPoint(3,allGr['data'].GetHistogram().GetXaxis().GetXmax(),-5.1)
      frame.SetPoint(4,allGr['data'].GetHistogram().GetXaxis().GetXmin(),-5.1)      
      
   frame.Draw('ap')
   frameXtitle,frameYtitle='','Pull'
   frame.GetYaxis().SetNdivisions(5)
   frame.GetXaxis().SetNdivisions(5)
   if opt.showMean :
      frameXtitle,frameYtitle='Average',''
      frame.GetYaxis().SetNdivisions(0)
   frame.GetYaxis().SetTitle(frameYtitle)
   frame.GetXaxis().SetTitle(frameXtitle)
   frame.GetXaxis().SetTitleSize(0.08)
   frame.GetXaxis().SetLabelSize(0.08)
   frame.GetYaxis().SetTitleOffset(0.5)
   frame.GetXaxis().SetTitleOffset(1.0)
   frame.GetYaxis().SetTitleSize(0.08)
   frame.GetYaxis().SetLabelSize(0.08)

   #inset legend
   inleg=ROOT.TLegend(0.62,0.3,0.95,0.9)
   inleg.SetBorderSize(0)
   inleg.SetFillColor(0)
   inleg.SetTextFont(42)
   inleg.SetTextSize(0.07)         
   if dataRef : 
      dataRef.Draw('l')
      inleg.AddEntry(dataRef,'data','l')
   for tag,_,_,_ in INPUTS:
      if tag=='data' : continue
      if opt.showMean:
         compGrs[tag].Draw('p')
         inleg.AddEntry(compGrs[tag],compGrs[tag].GetTitle(),'p')
      else:
         compGrs[tag].Draw('3')
         inleg.AddEntry(compGrs[tag],compGrs[tag].GetTitle(),'l')
   inleg.Draw()


   postfix='_mean' if opt.showMean else ''
   os.system('mkdir -p %s' % opt.outDir)
   for ext in ['.pdf', '.png', '.C']:
   #for ext in ['.pdf', '.png']:
      canvas.SaveAs(os.path.join(opt.outDir,'%s%s%s'%(opt.Dist,postfix,ext)))

   insetPad.Delete()

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())


