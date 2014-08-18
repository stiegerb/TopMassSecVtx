#!/usr/bin/env python
import ROOT, os, sys
from ROOT import TFile, TCanvas, THStack, TLegend, TH1D, TGraph, TGraphErrors, TF1

## Run by calling in the shell:
## ./macroTemplate.py

# Open a file
path = "/afs/cern.ch/work/j/jklocans/private/CMSSW_5_3_15/src/UserCode/llvv_fwk/lxyplots/"

################

ts_data = TH1D("Reconstructed number of tracks in data samples", "Reconstructed number of tracks in data samples", 15, 0., 15.)
ts_mc = TH1D("Number of tracks in MC samples (signal + background)", "Number of tracks in MC samples (signal + background)", 15, 0., 15.)
ts_ttbar = TH1D("Number of tracks in ttbar samples", "Number of tracks in ttbar samples", 15, 0., 15.)
ts_data.SetLineColor(1)
ts_mc.SetLineColor(4)
ts_mc.SetFillColor(4)
ts_ttbar.SetLineColor(4)
ts_ttbar.SetFillColor(4)
ts_data.Sumw2()
ts_mc.Sumw2()
ts_ttbar.Sumw2()

listoffiles_data = []
listoffiles_mc = []
listoffiles_ttbar = []

for file in os.listdir( path ):
	if(file.endswith(".root") and file.startswith("Data8TeV")):
		listoffiles_data.insert(0,file)
	if (file.endswith(".root") and file.startswith("MC8TeV")):
		listoffiles_mc.insert(0,file)
	if (file.endswith(".root") and file.startswith("MC8TeV_TTJets")):
		listoffiles_ttbar.insert(0,file)


rootfile_data = []
rootfile_mc = []
rootfile_ttbar = []

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptStat(0)

for x in listoffiles_data:
	rootfile_data.append(TFile.Open("./../lxyplots/" + x, "READ"))

for x in range(0,len(listoffiles_data)):

	histo = rootfile_data[x].Get("svntk")		
	histo.Sumw2()
	ts_data.Add(histo)
	del histo

for x in listoffiles_mc:
	rootfile_mc.append(TFile.Open("./../lxyplots/" + x, "READ"))

for x in range(0,len(listoffiles_mc)):

	histo = rootfile_mc[x].Get("svntk")		
	histo.Sumw2()
	ts_mc.Add(histo)
	del histo

for x in listoffiles_ttbar:
	rootfile_ttbar.append(TFile.Open("./../lxyplots/" + x, "READ"))

for x in range(0,len(listoffiles_ttbar)):

	histo = rootfile_ttbar[x].Get("svntk")		
	histo.Sumw2()
	ts_ttbar.Add(histo)
	del histo

ts_data.Scale(1/ts_data.Integral())
ts_mc.Scale(1/ts_mc.Integral())
ts_ttbar.Scale(1/ts_ttbar.Integral())

ts_data.SetMarkerStyle(21)

c = TCanvas("canvas", "c", 1000, 1000)
c2 = TCanvas("canvas2", "c2", 1000, 1000)
c.cd()

ts_data.Draw("P")
ts_mc.Draw("HIST:same")
ts_data.Draw("P:same")

leg = TLegend(0.65,0.65,0.85,0.85) 
leg.AddEntry(ts_mc,"Monte Carlo", "ll")
leg.AddEntry(ts_data,"Data", "ll")
leg.SetTextSize(0.02)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
leg.Draw()

c2.cd()

ts_data.Draw("P")
ts_ttbar.Draw("HIST:same")
ts_data.Draw("P:same")

leg.Draw()

c.SaveAs("./../plots/svntk_data_and_mc.pdf")
c2.SaveAs("./../plots/svntk_data_and_ttbar.pdf")
