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
      mu0 += y
      mu1 += x*y
      mu2 += x*x*y

   mu1=mu1/mu0
   mu2=mu2/mu0

   emu1=0
   for i in xrange(0,graph.GetN()):
      ey=graph.GetErrorY(i)
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
         ('data'       , 'Data'          ,    'Data8TeV_merged_filt23' , ROOT.kBlack),
         ('z2srblep'   , 'Z2*LEP r_{b}'     , 'MC8TeV_DY_merged_filt23_bfrag'       , ROOT.kBlack),
         ('z2srblepup' , 'Z2*LEP r_{b}+' ,    'MC8TeV_DY_merged_filt23_bfragup'     , ROOT.kMagenta),
         ('z2srblepdn' , 'Z2*LEP r_{b}-' ,    'MC8TeV_DY_merged_filt23_bfragdn'     , ROOT.kMagenta+2),
         ('z2s'        , 'Z2*' ,              'MC8TeV_DY_merged_filt23'             , ROOT.kRed+1),
         ('z2spete'    , 'Z2* Peterson'  ,    'MC8TeV_DY_merged_filt23_bfragpete'   , ROOT.kAzure+7),
         ('z2slund'    , 'Z2* Lund'      ,    'MC8TeV_DY_merged_filt23_bfraglund'   , ROOT.kBlue-7),
         #('p11frag'    , 'P11'    ,        'MC8TeV_DY_merged_filt23_bfragp11'    , ROOT.kRed-9),
         ]
      TAGS = {
         'D0':   'Z/#gamma^{*}(ll) #mu D^{0} (K^{-}#pi^{+}) + X',
         'Dpm':  'Z/#gamma^{*}(ll) D^{#pm}(K^{-}#pi^{+}#pi^{+}) + X',
         'JPsi': 'Z/#gamma^{*}(ll) J/#Psi(#mu^{+}#mu^{-}) + X',
         'Dsm':  'Z/#gamma^{*}(ll) D*^{#pm}(D^{0}(K^{-}#pi^{+})#pi^{+}) X',
         }

   #fragmentation variations to compare
   fragToUse=[('Z2*LEP r_{b}', ['z2srblep','z2srblepup','z2srblepdn'], ROOT.kBlack),
              ('Z2*',          ['z2s',     'z2s',       'z2s'],        ROOT.kRed+1),
              ('Z2* peterson', ['z2spete', 'z2spete',   'z2spete'],    ROOT.kViolet+2),
              ('Z2* Lund',     ['z2slund', 'z2slund',   'z2slund'],    ROOT.kAzure+7)
              ]
   if not opt.z:
      fragToUse.append( ('Herwig AUET6', ['powherw', 'powherw', 'powherw'], ROOT.kMagenta+2) )
   nominalFragWgt=fragToUse[0][0]


   #global ROOT configuration
   ROOT.gStyle.SetOptStat(0)
   ROOT.gStyle.SetOptTitle(0)

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
   for wtitle,iwList,wcolor in fragToUse:  

      compGrs[wtitle]=[0,0,0,0]
      for itag in xrange(0,len(iwList)):
         tag=iwList[itag]
         mu0, avg, avgErr, mu2 = computeFirstMoments(allGr[tag])
         rms = ROOT.TMath.Sqrt(mu2-avg*avg)
         if itag==0:
            compGrs[wtitle][0]=avg
            compGrs[wtitle][1]=avgErr
         else:
            compGrs[wtitle][1+itag]=avg-compGrs[wtitle][0]
   print compGrs

      
   ##########################################
   # PLOTTING
   canvas=ROOT.TCanvas('c','c',500,500)
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
   p1.cd()
   p1.Clear()
   try:
      allGr['z2srblep'].Draw('A3')
      allGr['z2srblep'].GetYaxis().SetRangeUser(0,opt.MaxY)
      allGr['z2srblep'].GetYaxis().SetTitleOffset(1.25)
      axistitles = AXISTITLES.get(opt.Dist,(opt.Dist,'Normalized'))
      allGr['z2srblep'].GetXaxis().SetTitle(axistitles[0])
      allGr['z2srblep'].GetYaxis().SetTitle(axistitles[1])
      allGr['z2srblep'].GetXaxis().SetTitleOffset(1.0)
      allGr['z2srblep'].GetYaxis().SetTitleOffset(1.2)
      allGr['z2srblep'].GetYaxis().SetTitleSize(0.04)
      allGr['z2srblep'].GetXaxis().SetTitleSize(0.04)
      allGr['z2srblep'].GetYaxis().SetLabelSize(0.035)
      allGr['z2srblep'].GetXaxis().SetLabelSize(0.035)
      allGr['z2srblep'].GetXaxis().SetNdivisions(10)
      allGr['z2srblep'].GetYaxis().SetNdivisions(5)
      allGr['data'].Draw('p')
   except KeyError:
      print "WARNING: No data or Z2*LEP rb to plot"
      pass

   label=ROOT.TLatex()
   label.SetNDC()
   label.SetTextFont(42)
   label.SetTextSize(0.05)
   label.SetTextAlign(32)
   label.DrawLatex(0.25,0.92,'#bf{CMS}')         
   if opt.Tag:
      label.DrawLatex(0.92,0.86,'#scale[0.8]{#it{%s}}'%TAGS[opt.Tag])
   label.DrawLatex(0.92,0.92,'#scale[0.8]{19.7 fb^{-1} (8 TeV)}')

   p2.cd()
   p2.Clear()
   frame,dataRef=ROOT.TGraph(),None
   mu0, avg, avgErr, mu2 = computeFirstMoments(allGr['data'])
   rms = ROOT.TMath.Sqrt(mu2-avg*avg)
   frame.SetTitle('frame')
   frame.SetMarkerStyle(1)
   frame.SetLineColor(1)
   frame.SetPoint(0,0,avg-0.5*rms)
   frame.SetPoint(1,len(fragToUse),avg-0.5*rms)
   frame.SetPoint(2,len(fragToUse),avg+0.5*rms)
   frame.SetPoint(3,0,avg+0.5*rms)
   frame.SetPoint(4,0,avg-0.5*rms)

   dataRef=ROOT.TGraph()
   dataRef.SetTitle('dataref')
   dataRef.SetFillStyle(3001)
   dataRef.SetFillColor(ROOT.kGray)
   dataRef.SetLineColor(ROOT.kGray)
   dataRef.SetLineWidth(2)
   dataRef.SetPoint(0,0,avg-avgErr)
   dataRef.SetPoint(1,len(fragToUse)+1.0,avg-avgErr)
   dataRef.SetPoint(2,len(fragToUse)+1.0,avg+avgErr)
   dataRef.SetPoint(3,0,avg+avgErr)
   dataRef.SetPoint(4,0,avg-avgErr)
   print avg,avgErr
      
   frame.Draw('ap')   
   frame.GetXaxis().SetNdivisions(0)
   frame.GetYaxis().SetNdivisions(5)
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
      dataRef.Draw('lf')
   grCtr=0
   statGrs,totalGrs={},{}
   for wtitle,iwList,wcolor in fragToUse:        
      tag=iwList[0]

      totalGrs[wtitle]=ROOT.TGraphAsymmErrors()
      totalGrs[wtitle].SetMarkerColor(wcolor)
      totalGrs[wtitle].SetLineColor(wcolor)
      totalGrs[wtitle].SetLineWidth(2)
      totalGrs[wtitle].SetMarkerStyle(20+grCtr)
      totalGrs[wtitle].SetPoint(0,grCtr+1,compGrs[wtitle][0])
 
      diff1=ROOT.TMath.Min(compGrs[wtitle][2],compGrs[wtitle][2])
      diff2=ROOT.TMath.Max(compGrs[wtitle][2],compGrs[wtitle][3])      
      statunc=compGrs[wtitle][1]      
      if diff1*diff2<0:
         totalGrs[wtitle].SetPointError(0,0,0,
                                        ROOT.TMath.Sqrt(statunc**2+diff1**2),
                                        ROOT.TMath.Sqrt(statunc**2+diff2**2))
      else:
         maxDiff=ROOT.TMath.Max(ROOT.TMath.Abs(diff1),ROOT.TMath.Abs(diff2))
         totalGrs[wtitle].SetPointError(0,0,0,
                                        ROOT.TMath.Sqrt(statunc**2+maxDiff**2),
                                        ROOT.TMath.Sqrt(statunc**2+maxDiff**2))
      
      statGrs[wtitle]=ROOT.TGraphAsymmErrors()
      statGrs[wtitle].SetMarkerColor(wcolor)
      statGrs[wtitle].SetLineColor(wcolor)
      statGrs[wtitle].SetLineWidth(1)
      statGrs[wtitle].SetMarkerStyle(20+grCtr)
      statGrs[wtitle].SetPoint(0,grCtr+1,compGrs[wtitle][0])
      statGrs[wtitle].SetPointError(0,0,0,statunc,statunc)
      
      if wtitle==nominalFragWgt : 
         totalGrs[wtitle].SetMarkerSize(0.5)
         statGrs[wtitle].SetMarkerSize(0.5)
         totalGrs[wtitle].Draw('p')          
         statGrs[wtitle].Draw('p')          
      else:
         statGrs[wtitle].Draw('pX')          
      xlabel=0.09+0.68*float(grCtr+1)/float(len(fragToUse))
      fraglabel.DrawLatex(xlabel,0.8,'#it{%s}'%wtitle)
      grCtr+=1
      
   os.system('mkdir -p %s' % opt.outDir)
   for ext in ['.pdf', '.png', '.C']:
      canvas.SaveAs(os.path.join(opt.outDir,'%s%s'%(opt.Dist,ext)))
   p1.Delete()
   p2.Delete()

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())


