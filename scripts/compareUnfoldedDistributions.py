#!/usr/bin/env python

import ROOT
import os,sys
import optparse
import glob
import math
from CMS_lumi import CMS_lumi
from runPlotter import openTFile
from myRootFunctions import checkKeyInFile

COLORS=[862,800,1,922]
FILLS=[1001,3001,3004,3002]

TAGS = {
	'D0':   't#bar{t} #rightarrow #mu D^{0} (K^{-}#pi^{+}) X',
	'Dpm':  't#bar{t} #rightarrow D^{#pm}(K^{-}#pi^{+}#pi^{+}) X',
	'JPsi': 't#bar{t} #rightarrow J/#Psi(#mu^{+}#mu^{-}) X'
}

INPUTS = [
   ('data'       , 'Data'                , 'Data8TeV_merged'                        , ROOT.kBlack),
   ('powpyth'    , 'Powheg+Pythia+Z2*'   , 'MC8TeV_TT_Z2star_powheg_pythia'         , ROOT.kYellow+1),
   ('powherw'    , 'Powheg+Herwig+AUET2' , 'MC8TeV_TT_AUET2_powheg_herwig'          , ROOT.kGreen+2),
   ('p11'        , 'Madgraph+Pythia+P11' , 'MC8TeV_TTJets_TuneP11'                  , ROOT.kRed+2),
   ('z2s'        , 'Madgraph+Pythia+Z2*' , 'MC8TeV_TTJets_MSDecays_172v5'           , ROOT.kBlue+3),
   ('z2srblep'   , 'MG+PY+Z2*rbLEP'      , 'MC8TeV_TTJets_MSDecays_172v5_bfrag'     , ROOT.kMagenta),
   ('z2srblepup' , 'MG+PY+Z2*rbLEP hard' , 'MC8TeV_TTJets_MSDecays_172v5_bfragup'   , ROOT.kMagenta+2),
   ('z2srblepdn' , 'MG+PY+Z2*rbLEP soft' , 'MC8TeV_TTJets_MSDecays_172v5_bfragdn'   , ROOT.kMagenta-9),
   ('p11frag'    , 'MG+PY+P11 (frag)'    , 'MC8TeV_TTJets_MSDecays_172v5_bfragp11'  , ROOT.kRed-9),
   ('z2spete'    , 'MG+PY+Z2* Peterson'  , 'MC8TeV_TTJets_MSDecays_172v5_bfragpete' , ROOT.kAzure+7),
   ('z2slund'    , 'MG+PY+Z2* Lund'      , 'MC8TeV_TTJets_MSDecays_172v5_bfraglund' , ROOT.kBlue-7),
]

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
   pullgraph = ROOT.TGraphAsymmErrors(len(pullpoints))
   pullgraph.SetName("%s_pull"%graph.GetName())
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
   parser.add_option('--pullrange' , dest='pullrange',
                     help='range of pull to plot',
                     default='-2,2', type='string')
   parser.add_option('-m', '--maxY', dest='MaxY',
                     help='max y',
                     default=0.75, type=float)
   parser.add_option('-b', '--base', dest='BaseName',
                     help='base name for root files' ,
                     default='UnfoldedDistributions', type='string')
   parser.add_option('--tag', dest='Tag', help='Add a tag label',
                     default='', type='string')
   (opt, args) = parser.parse_args()

   #global ROOT configuration
   ROOT.gStyle.SetOptStat(0)
   ROOT.gStyle.SetOptTitle(0)
   ROOT.gStyle.SetPadTopMargin(0.05)
   ROOT.gStyle.SetPadBottomMargin(0.1)
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
      allGr[tag].GetYaxis().SetTitleOffset(2.5)

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
         allGr[tag].SetMarkerSize(1.5)
      else:
         allGr[tag].SetMarkerStyle(20)
         allGr[tag].SetMarkerSize(1)
         allGr[tag].SetMarkerColor(color)
         allGr[tag].SetLineColor(color)
         allGr[tag].SetFillStyle(3002)
         allGr[tag].SetFillColor(color)

   # compute all the pulls:
   pullGr = {}
   for tag, graph in allGr.iteritems():
      pullGr[tag] = computePullFromGraphs(graph, allGr['data'])

   ##########################################
   # PLOTTING
   canvas=ROOT.TCanvas('c','c',800,1200)
   canvas.SetRightMargin(0)
   canvas.SetLeftMargin(0)
   canvas.SetTopMargin(0)
   canvas.SetBottomMargin(0)
   allLegs=[]
   pads=[]
   pads.append( ROOT.TPad('pad0', 'pad0', 0.0, 0.60, 1.0, 1.00) )
   pads.append( ROOT.TPad('pad1', 'pad1', 0.0, 0.60, 1.0, 0.42) )
   pads.append( ROOT.TPad('pad2', 'pad2', 0.0, 0.42, 1.0, 0.24) )
   pads.append( ROOT.TPad('pad3', 'pad3', 0.0, 0.24, 1.0, 0.00) )

   for i in xrange(0,4):
      pads[i].SetTopMargin(0.0)
      pads[i].SetBottomMargin(0.0)
   pads[0].SetTopMargin(0.1)
   pads[-1].SetBottomMargin(0.25)
   for p in pads: p.Draw()

   canvas.cd()
   pads[0].cd()
   pads[0].Clear()
   drawngraphs = []
   try:
      allGr['z2s'].Draw('A3')
      allGr['data'].Draw('p')
      # allGr['z2s'].GetYaxis().SetRangeUser(0,opt.MaxY)
      # allGr['data'].GetYaxis().SetRangeUser(0,opt.MaxY)
      drawngraphs.append(allGr['data'])
      drawngraphs.append(allGr['z2s'])
   except KeyError:
      print "WARNING: No data or Z2* to plot"
      pass

   # Build a legend
   leg = makeLegend('main',len(drawngraphs),y2=0.85)
   for gr in drawngraphs:
      if 'data' in gr.GetName(): leg.AddEntry(gr, gr.GetTitle(), 'p')
      else:                      leg.AddEntry(gr, gr.GetTitle(), 'f')
   leg.Draw()
   drawngraphs = []

   CMS_lumi(pads[0],2,10)

   #tag
   if opt.Tag:
      tl = ROOT.TLatex()
      tl.SetNDC()
      tl.SetTextFont(43)
      tl.SetTextSize(24)
      tl.DrawLatex(0.16, 0.92, TAGS[opt.Tag])

   ## Axis ranges
   xaxisrange = (allGr['data'].GetHistogram().GetXaxis().GetXmin(),
                 allGr['data'].GetHistogram().GetXaxis().GetXmax())
   pullrange = map(float, opt.pullrange.split(','))
   haxispulls = ROOT.TH2F("haxispulls", "haxispulls",
                          1, xaxisrange[0], xaxisrange[1],
                          1, pullrange[0], pullrange[1])

   haxispulls.GetXaxis().SetLabelFont(43)
   haxispulls.GetXaxis().SetLabelSize(18)
   haxispulls.GetYaxis().SetLabelFont(43)
   haxispulls.GetYaxis().SetLabelSize(18)
   haxispulls.GetXaxis().SetTitleFont(43)
   haxispulls.GetXaxis().SetTitleSize(24)
   haxispulls.GetXaxis().SetTitleOffset(4.0)
   haxispulls.GetYaxis().SetTitleFont(43)
   haxispulls.GetYaxis().SetTitleSize(24)
   haxispulls.GetYaxis().SetTitleOffset(2.5)
   haxispulls.GetYaxis().SetTitle("Pull")
   axistitles = AXISTITLES.get(opt.Dist,(opt.Dist,'Pull'))
   haxispulls.GetXaxis().SetTitle(axistitles[0])

   ## Draw the pull pads
   line = ROOT.TLine()
   line.SetLineColor(ROOT.kGray+2)
   line.SetLineWidth(2)
   line.SetLineStyle(2)

   def drawPulls(pulls,drawOpt='L3'):
      pad.cd()
      drawngraphs = []
      for pull in pulls:
         pullGr[pull].Draw(drawOpt)
         drawngraphs.append(allGr[pull])
      leg = makeLegend('leg',len(drawngraphs))
      for gr in drawngraphs: leg.AddEntry(gr, gr.GetTitle(), 'f')
      return leg

   for n,pad in enumerate(pads[1:]):
      pad.cd()
      pad.Clear()
      # pad.SetGridy(True)
      haxispulls.Draw("axis")
      if n==0:
         leg0 = drawPulls(['z2s','p11','p11frag'])
         leg0.Draw()
      if n==1:
         leg1 = drawPulls(['powpyth','powherw'])
         leg1.Draw()
      if n==2:
         leg2 = drawPulls(['z2srblep', 'z2srblepdn', 'z2srblepup',
                           'z2spete', 'z2slund'], drawOpt='LX')
         leg2.Draw()
      line.DrawLine(xaxisrange[0], 0., xaxisrange[1], 0.,)



   os.system('mkdir -p %s' % opt.outDir)
   # for ext in ['.pdf', '.png', '.C']:
   for ext in ['.pdf', '.png']:
      canvas.SaveAs(os.path.join(opt.outDir,'%s%s'%(opt.Dist,ext)))

   for pad in pads:
      pad.Delete()

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())


