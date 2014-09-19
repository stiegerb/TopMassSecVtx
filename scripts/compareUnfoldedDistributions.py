#!/usr/bin/env python

import ROOT
import os,sys
import optparse
import glob
import math
from CMS_lumi import CMS_lumi

COLORS=[862,800,1,922]
FILLS=[1001,3001,3004,3002]

TAGS = {
	'D0':   'D^{0} (K^{-}#pi^{+})',
	'Dpm':  'D^{#pm}(K^{-}#pi^{+}#pi^{+})',
	'JPsi': 'J/#Psi(#mu^{+}#mu^{-})'
}

"""
steer the script
"""
def main():

   #configuration
   usage = 'usage: %prog [options]'
   parser = optparse.OptionParser(usage)
   parser.add_option('-i', '--input'      ,    dest='InputDirs'       , help='csv list of directories'    , default=None,     type='string')
   parser.add_option('-t', '--title'      ,    dest='InputTitles'     , help='titles'                     , default=None,     type='string')
   parser.add_option('-d', '--dist'       ,    dest='Dist'            , help='distribution to compare'    , default='ptfrac', type='string')
   parser.add_option('-m', '--maxY'       ,    dest='MaxY'            , help='max y'                      , default=0.75,     type=float)
   parser.add_option('-b', '--base'       ,    dest='BaseName'        , help='base name for root files'   , default='UnfoldedDistributions', type='string')
   parser.add_option('--tag'       ,    dest='Tag'        , help='Add a tag label'   , default='', type='string')
   (opt, args) = parser.parse_args()

   #global ROOT configuration
   ROOT.gStyle.SetOptStat(0)
   ROOT.gStyle.SetOptTitle(0)
   ROOT.gStyle.SetPadTopMargin(0.05)
   ROOT.gStyle.SetPadBottomMargin(0.1)
   ROOT.gStyle.SetPadLeftMargin(0.15)
   ROOT.gStyle.SetPadRightMargin(0.05)

   #get graphs from files
   allGr=[]
   dataIdx=-1
   mcIdx=-1
   titles=opt.InputTitles.split(',')
   for dir in opt.InputDirs.split(','):
       files=glob.glob("%s/%s_*.root"%(dir,opt.BaseName))
       if len(files)==0:
           print "No files found:", "%s/%s_*.root"%(dir,opt.BaseName)
           continue
       inF=ROOT.TFile.Open(files[0])
       allGr.append( inF.Get('%s'%opt.Dist) )
       inF.Close()

       #format the new plot
       idx=len(allGr)-1
       name='gr%d'%idx
       title=titles[idx]
       allGr[idx].SetName(name)
       allGr[idx].SetTitle(title)
       allGr[idx].GetYaxis().SetTitleSize(0.04)
       allGr[idx].GetXaxis().SetTitleSize(0.04)
       allGr[idx].GetYaxis().SetLabelSize(0.03)
       allGr[idx].GetXaxis().SetLabelSize(0.03)

       allGr[idx].GetYaxis().SetTitleOffset(1.5);
       if 'pt_dS' in opt.Dist:
          allGr[idx].GetXaxis().SetTitle("Transverse momentum [GeV]")
          allGr[idx].GetYaxis().SetTitle("1/#sigma d#sigma/dp_{T} [GeV^{-1}]")
       if 'eta_dS' in opt.Dist:
          allGr[idx].GetXaxis().SetTitle("Pseudorapidity")
          allGr[idx].GetYaxis().SetTitle("1/#sigma d#sigma/d#eta")
       if "ptrel_" in opt.Dist:
          allGr[idx].GetXaxis().SetTitle("p_{T}^{rel} [GeV]")
          allGr[idx].GetYaxis().SetTitle("1/#sigma d#sigma/d p_{T}^{rel} [GeV^{-1}]")
       if "pfrac_" in opt.Dist:
          allGr[idx].GetXaxis().SetTitle("R_{p} = p / p^{jet}");
          allGr[idx].GetYaxis().SetTitle("1/#sigma d#sigma/d R_{p}")
       if "ptfrac_" in opt.Dist:
          allGr[idx].GetXaxis().SetTitle("R_{p_{T}} = p_{T} / p_{T}^{jet}");
          allGr[idx].GetYaxis().SetTitle("1/#sigma d#sigma/d R_{p_{T}}")
       if "pzfrac_" in opt.Dist:
          allGr[idx].GetXaxis().SetTitle("R_{p_{z}} = p_{z} / p_{z}^{jet}");
          allGr[idx].GetYaxis().SetTitle("1/#sigma d#sigma/d R_{p_{z}}")
       if "ptchfrac_" in opt.Dist:
          allGr[idx].GetXaxis().SetTitle("R_{p_{T}}^{ch} = p_{T} / #Sigma p_{T}^{ch}");
          allGr[idx].GetYaxis().SetTitle("1/#sigma d#sigma/d R_{p_{T}}^{ch}")
       if "pzchfrac_" in opt.Dist:
          allGr[idx].GetXaxis().SetTitle("R_{p_{z}}^{ch} = p_{z} / #Sigma p_{z}^{ch}");
          allGr[idx].GetYaxis().SetTitle("1/#sigma d#sigma/d R_{p_{z}}^{ch}")
       if "dr_" in opt.Dist:
          allGr[idx].GetXaxis().SetTitle("#DeltaR");
          allGr[idx].GetYaxis().SetTitle("1/#sigma d#sigma/d #DeltaR")
       if title=='Data':
          dataIdx=idx
          allGr[idx].SetFillStyle(0)
          allGr[idx].SetFillColor(0)
          allGr[idx].SetLineWidth(2)
          allGr[idx].SetMarkerColor(1)
          allGr[idx].SetMarkerStyle(20)
       else:
          mcIdx+=1
          allGr[idx].SetMarkerStyle(1)
          allGr[idx].SetLineColor(COLORS[mcIdx])
          allGr[idx].SetMarkerColor(COLORS[mcIdx])
          allGr[idx].SetFillStyle(FILLS[mcIdx])
          allGr[idx].SetFillColor(COLORS[mcIdx])

   #show plots in a canvas
   c=ROOT.TCanvas('c','c',600,600)
   drawOpt='a2'
   for i in xrange(0,len(allGr)):
       if i==dataIdx : continue
       allGr[i].Draw(drawOpt)
       allGr[i].GetYaxis().SetRangeUser(0,opt.MaxY)
       drawOpt='2'
   if dataIdx>=0 : allGr[dataIdx].Draw('p')

   #caption
   CMS_lumi(c,2,10)
   #pt=ROOT.TPaveText(0.18,0.9,0.9,0.93,'brNDC')
   #pt.SetFillStyle(0)
   #pt.SetBorderSize(0)
   #pt.SetTextAlign(12)
   #pt.SetTextFont(42)
   #pt.SetTextSize(0.03)
   #pt.AddText("CMS Preliminary, #sqrt{s}=8 TeV, 19.7 fb^{-1}")
   # pt.AddText('CMS work in progress')
   #pt.Draw()

   #tag
   if opt.Tag:
      tl=ROOT.TLatex()
      tl.SetNDC()
      tl.SetTextFont(42)
      tl.SetTextSize(0.04)
      tl.DrawLatex(0.18, 0.8, TAGS[opt.Tag])

   #build a legend
   leg=ROOT.TLegend(0.55,0.75,0.95,0.95,"","brNDC")
   leg.SetFillStyle(0)
   leg.SetBorderSize(0)
   leg.SetTextFont(42)
   leg.SetTextSize(0.025)
   #leg.SetNColumns(2)
   if dataIdx>=0 : leg.AddEntry(allGr[dataIdx],allGr[dataIdx].GetTitle(),'lp')
   for i in xrange(0, len(allGr)):
      if i==dataIdx: continue
      leg.AddEntry(allGr[i],allGr[i].GetTitle(),'f')
   leg.Draw()

   c.SaveAs('%s.pdf'%opt.Dist)
   c.SaveAs('%s.png'%opt.Dist)
   c.SaveAs('%s.C'%opt.Dist)
   #raw_input()

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())


