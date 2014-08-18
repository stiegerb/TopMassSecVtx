#!/usr/bin/env python
import ROOT, os, sys
from ROOT import TFile, TCanvas, THStack, TLegend, TH1D, TGraph, TGraphErrors, TF1

## Run by calling in the shell:
## ./macroTemplate.py

# Open a file
path = "/afs/cern.ch/work/j/jklocans/private/CMSSW_5_3_15/src/UserCode/llvv_fwk/lxyplots/"

################

ts_correctmass = []
ts_correctmass_bin1 = []
ts_correctmass_bin2 = []
ts_correctmass_bin3 = []
ts_correctmass_bin4 = []
ts_wrongmass = []
ts_wrongmass_bin1 = []
ts_wrongmass_bin2 = []
ts_wrongmass_bin3 = []
ts_wrongmass_bin4 = []

c_correct = TCanvas("c_correct", "c", 1000, 1000)
c_correct.Divide(2,3,0.01,0.01)
c_wrong = TCanvas("c_wrong", "c", 1000, 1000)
c_wrong.Divide(2,3,0.01,0.01)

listoffiles = [[] for x in xrange(0,6)]

for file in os.listdir( path ):
	if(file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_166v5")):
		listoffiles[0].insert(0,file)
	elif (file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_169v5")):
		listoffiles[1].insert(0,file)
	elif(file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_172v5")):
		listoffiles[2].insert(0,file)
	elif(file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_173v5")):       
		listoffiles[3].insert(0,file)
	elif(file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_175v5")):
		listoffiles[4].insert(0,file)
	elif(file.endswith(".root") and file.startswith("MC8TeV_TTJets_178v5")):
		listoffiles[5].insert(0,file)

listofnames = []
listofnames.append("166v5")
listofnames.append("169v5")
listofnames.append("172v5")
listofnames.append("173v5")
listofnames.append("175v5")
listofnames.append("178v5")

for x in listofnames:

	ts_correctmass.append(TH1D("minmass_correct_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrongmass.append(TH1D("minmass_wrong_" + x,"test stackhsed histograms", 50, 0., 150.))
	ts_correctmass_bin1.append(TH1D("minmass_correct_bin1_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_bin1.append(TH1D("minmass_wrong_bin1_" + x,"test stackhsed histograms", 50, 0., 150.))
	ts_correctmass_bin2.append(TH1D("minmass_correct_bin2_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_bin2.append(TH1D("minmass_wrong_bin2_" + x,"test stackhsed histograms", 50, 0., 150.))
	ts_correctmass_bin3.append(TH1D("minmass_correct_bin3_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_bin3.append(TH1D("minmass_wrong_bin3_" + x,"test stackhsed histograms", 50, 0., 150.))
	ts_correctmass_bin4.append(TH1D("minmass_correct_bin4_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_bin4.append(TH1D("minmass_wrong_bin4_" + x,"test stackhsed histograms", 50, 0., 150.))

for i in range(0,6):

	ts_correctmass[i].Sumw2()
	ts_correctmass_bin1[i].Sumw2()
	ts_correctmass_bin2[i].Sumw2()
	ts_correctmass_bin3[i].Sumw2()
	ts_correctmass_bin4[i].Sumw2()
	ts_wrongmass[i].Sumw2()
	ts_wrongmass_bin1[i].Sumw2()
	ts_wrongmass_bin2[i].Sumw2()
	ts_wrongmass_bin3[i].Sumw2()
	ts_wrongmass_bin4[i].Sumw2()

	rootfile1 = []

	for x in listoffiles[i]:
	#inv.m. l + sv
		rootfile1.append(TFile.Open("./../lxyplots/" + x, "READ"))

		histo_correctmass = []
		histo_correctmass_bin1 = []
		histo_correctmass_bin2 = []
		histo_correctmass_bin3 = []
		histo_correctmass_bin4 = []
		histo_wrongmass = []
		histo_wrongmass_bin1 = []
		histo_wrongmass_bin2 = []
		histo_wrongmass_bin3 = []
		histo_wrongmass_bin4 = []

	for x in range(0,len(listoffiles[i])):

		histo_correctmass.append(rootfile1[x].Get("mlsv_emu_minmass_correct"))
		histo_wrongmass.append(rootfile1[x].Get("mlsv_emu_minmass_wrong"))
		histo_correctmass_bin1.append(rootfile1[x].Get("mlsv_emu_minmass_correct_nvtx_1bin"))
		histo_wrongmass_bin1.append(rootfile1[x].Get("mlsv_emu_minmass_wrong_nvtx_1bin"))
		histo_correctmass_bin2.append(rootfile1[x].Get("mlsv_emu_minmass_correct_nvtx_2bin"))
		histo_wrongmass_bin2.append(rootfile1[x].Get("mlsv_emu_minmass_wrong_nvtx_2bin"))
		histo_correctmass_bin3.append(rootfile1[x].Get("mlsv_emu_minmass_correct_nvtx_3bin"))
		histo_wrongmass_bin3.append(rootfile1[x].Get("mlsv_emu_minmass_wrong_nvtx_3bin"))
		histo_correctmass_bin4.append(rootfile1[x].Get("mlsv_emu_minmass_correct_nvtx_4bin"))
		histo_wrongmass_bin4.append(rootfile1[x].Get("mlsv_emu_minmass_wrong_nvtx_4bin"))

		histo_correctmass[x].Sumw2()
		histo_wrongmass[x].Sumw2()
		histo_correctmass_bin1[x].Sumw2()
		histo_wrongmass_bin1[x].Sumw2()
		histo_correctmass_bin2[x].Sumw2()
		histo_wrongmass_bin2[x].Sumw2()
		histo_correctmass_bin3[x].Sumw2()
		histo_wrongmass_bin3[x].Sumw2()
		histo_correctmass_bin4[x].Sumw2()
		histo_wrongmass_bin4[x].Sumw2()


		ts_correctmass[i].Add(histo_correctmass[x])
		ts_wrongmass[i].Add(histo_wrongmass[x])
		ts_correctmass_bin1[i].Add(histo_correctmass_bin1[x])
		ts_wrongmass_bin1[i].Add(histo_wrongmass_bin1[x])
		ts_correctmass_bin2[i].Add(histo_correctmass_bin2[x])
		ts_wrongmass_bin2[i].Add(histo_wrongmass_bin2[x])
		ts_correctmass_bin3[i].Add(histo_correctmass_bin3[x])
		ts_wrongmass_bin3[i].Add(histo_wrongmass_bin3[x])
		ts_correctmass_bin4[i].Add(histo_correctmass_bin4[x])
		ts_wrongmass_bin4[i].Add(histo_wrongmass_bin4[x])

	ts_correctmass[i].Scale(1/ts_correctmass[i].Integral())
	ts_wrongmass[i].Scale(1/ts_wrongmass[i].Integral())
	ts_correctmass_bin1[i].Scale(1/ts_correctmass_bin1[i].Integral())
	ts_wrongmass_bin1[i].Scale(1/ts_wrongmass_bin1[i].Integral())
	ts_correctmass_bin2[i].Scale(1/ts_correctmass_bin2[i].Integral())
	ts_wrongmass_bin2[i].Scale(1/ts_wrongmass_bin2[i].Integral())
	ts_correctmass_bin3[i].Scale(1/ts_correctmass_bin3[i].Integral())
	ts_wrongmass_bin3[i].Scale(1/ts_wrongmass_bin3[i].Integral())
	ts_correctmass_bin4[i].Scale(1/ts_correctmass_bin4[i].Integral())
	ts_wrongmass_bin4[i].Scale(1/ts_wrongmass_bin4[i].Integral())

	ts_correctmass[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correctmass[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrongmass[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrongmass[i].GetYaxis().SetTitle("number of events (normalized by area)")


	del histo_correctmass
	del histo_wrongmass
	del histo_correctmass_bin1
	del histo_wrongmass_bin1
	del histo_correctmass_bin2
	del histo_wrongmass_bin2
	del histo_correctmass_bin3
	del histo_wrongmass_bin3
	del histo_correctmass_bin4
	del histo_wrongmass_bin4

leg = TLegend(0.5,0.65,0.7,0.9)
leg.SetHeader("Results for diff. nvtx")
leg.AddEntry(ts_correctmass[0],"all nvtx","l")
leg.AddEntry(ts_correctmass_bin1[0],"1-10 nvtx","l")
leg.AddEntry(ts_correctmass_bin2[0],"11-14 nvtx","l")
leg.AddEntry(ts_correctmass_bin3[0],"15-19 nvtx","l")
leg.AddEntry(ts_correctmass_bin4[0],"20+ nvtx","l")
leg.SetTextSize(0.02)

for i in range(0,6):
	
	ts_correctmass_bin1[i].Divide(ts_correctmass[i])
	ts_correctmass_bin2[i].Divide(ts_correctmass[i])
	ts_correctmass_bin3[i].Divide(ts_correctmass[i])
	ts_correctmass_bin4[i].Divide(ts_correctmass[i])
	ts_correctmass[i].Divide(ts_correctmass[i])

	ts_correctmass[i].SetLineColor(1)
	ts_wrongmass[i].SetLineColor(1)
	ts_correctmass_bin1[i].SetLineColor(52)
	ts_wrongmass_bin1[i].SetLineColor(52)
	ts_correctmass_bin2[i].SetLineColor(61)
	ts_wrongmass_bin2[i].SetLineColor(61)
	ts_correctmass_bin3[i].SetLineColor(70)
	ts_wrongmass_bin3[i].SetLineColor(70)
	ts_correctmass_bin4[i].SetLineColor(79)
	ts_wrongmass_bin4[i].SetLineColor(79)

	ts_correctmass[i].SetMaximum(2.5)
	ts_wrongmass[i].SetMaximum(2.5)

	ts_wrongmass_bin1[i].Divide(ts_wrongmass[i])
	ts_wrongmass_bin2[i].Divide(ts_wrongmass[i])
	ts_wrongmass_bin3[i].Divide(ts_wrongmass[i])
	ts_wrongmass_bin4[i].Divide(ts_wrongmass[i])
	ts_wrongmass[i].Divide(ts_wrongmass[i])

	c_correct.cd(i+1)
	ts_correctmass[i].Draw("HIST")
	ts_correctmass_bin1[i].Draw("HIST:same")
	ts_correctmass_bin2[i].Draw("HIST:same")
	ts_correctmass_bin3[i].Draw("HIST:same")
	ts_correctmass_bin4[i].Draw("HIST:same")
	ts_correctmass[i].Draw("HIST:same")
	if i==0: leg.Draw()

	c_wrong.cd(i+1)
	ts_wrongmass[i].Draw("HIST")
	ts_wrongmass_bin1[i].Draw("HIST:same")
	ts_wrongmass_bin2[i].Draw("HIST:same")
	ts_wrongmass_bin3[i].Draw("HIST:same")
	ts_wrongmass_bin4[i].Draw("HIST:same")
	ts_wrongmass[i].Draw("HIST:same")
	if i==0: leg.Draw()

	ts_correctmass[i].SetTitle("Lepton/SecVtx Mass for diff. nvtx in emu channel (take the lowest mass) CORRECT CHARGE - " + listofnames[i])
	ts_wrongmass[i].SetTitle("Lepton/SecVtx Mass for diff. nvtx in emu channel (take the lowest mass) WRONG CHARGE - " + listofnames[i])


c_correct.Modified()
c_wrong.Modified()
c_correct.Update()
c_wrong.Update()

c_correct.SaveAs("./../plots/compare_number_of_vertices_minmass_correct.pdf")
c_wrong.SaveAs("./../plots/compare_number_of_vertices_minmass_wrong.pdf")

c_correct_172 = TCanvas("c_correct_172", "c172", 2000, 1000)
c_correct_172.Divide(2,1,0.01,0.01)

c_correct_172.cd(1)

ts_correctmass[2].Draw("HIST")
ts_correctmass_bin1[2].Draw("HIST:same")
ts_correctmass_bin2[2].Draw("HIST:same")
ts_correctmass_bin3[2].Draw("HIST:same")
ts_correctmass_bin4[2].Draw("HIST:same")
ts_correctmass[2].Draw("HIST:same")
leg.Draw()

c_correct_172.cd(2)
ts_wrongmass[2].Draw("HIST")
ts_wrongmass_bin1[2].Draw("HIST:same")
ts_wrongmass_bin2[2].Draw("HIST:same")
ts_wrongmass_bin3[2].Draw("HIST:same")
ts_wrongmass_bin4[2].Draw("HIST:same")
ts_wrongmass[2].Draw("HIST:same")
leg.Draw()

c_correct_172.SaveAs("./../plots/compare_number_of_vertices_minmass_2plots.pdf")
