#!/usr/bin/env python
import ROOT, os, sys
from ROOT import TFile, TCanvas, THStack, TLegend, TH1D, TGraph, TGraphErrors, TF1

## Run by calling in the shell:
## ./macroTemplate.py

# Open a file
path = "/afs/cern.ch/work/j/jklocans/private/CMSSW_5_3_15/src/UserCode/llvv_fwk/lxyplots/"

################

ts_correct = []

#min mass
ts_correctmass = []

# Make a new TCanvas
c = TCanvas("canvas", "c", 1000, 500)
c1 = TCanvas("canvas1", "c", 1000, 1000)
c2 = TCanvas("canvas2", "c", 1000, 1000)
c.Divide(2,1,0.01,0.01)

# save all names of desired files in a list

listoffiles = [[] for x in xrange(0,3)]

for file in os.listdir( path ):
	if(file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_scaledown")):
		listoffiles[0].insert(0,file)
	elif(file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_172v5")):
		listoffiles[1].insert(0,file)
	elif(file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_scaleup")):       
		listoffiles[2].insert(0,file)

listofnames = []
listofnames.append("scaledown")
listofnames.append("172v5")
listofnames.append("scaleup")

for x in listofnames:

	ts_correct.append(TH1D("deltar_correct" + x,"test stacked histograms", 50, 0., 150.))
	ts_correctmass.append(TH1D("minmass_correct" + x,"test stacked histograms", 50, 0., 150.))

# Open the files -> adds all samples together
for i in range(0,len(listoffiles)):
	ts_correct[i].Sumw2()
	ts_correctmass[i].Sumw2()
	rootfile1 = []

	for x in listoffiles[i]:
	#inv.m. l + sv
		rootfile1.append(TFile.Open("./../lxyplots/" + x, "READ"))

	#deltar
	histo_correct = []

	#min mass
	histo_correctmass = []

	for x in range(0,len(listoffiles[i])):

		histo_correct.append(rootfile1[x].Get("mlsv_emu_deltar_correct"))

		#min mass
		histo_correctmass.append(rootfile1[x].Get("mlsv_emu_minmass_correct"))

		histo_correct[x].Sumw2()
		histo_correctmass[x].Sumw2()

		#adding histos

		ts_correct[i].Add(histo_correct[x])
		ts_correctmass[i].Add(histo_correctmass[x])

		#normalization

	if (ts_correct[i].Integral() != 0):
		ts_correct[i].Scale(1/ts_correct[i].Integral())


	if (ts_correctmass[i].Integral() != 0):
		ts_correctmass[i].Scale(1/ts_correctmass[i].Integral())


	# Set colors and stuff
	# Set colors and stuff

	ts_correct[i].SetLineColor(51 + 23*i)
	ts_correctmass[i].SetLineColor(51 + 23*i)

	ts_correct[i].SetMarkerColor(51 + 23*i)
	ts_correctmass[i].SetMarkerColor(51 + 23*i)

	ts_correct[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correct[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_correctmass[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correctmass[i].GetYaxis().SetTitle("number of events (normalized by area)")

	# Draw them

	c.cd(1)
	if i==0: 	ts_correct[i].Draw("")
	else: 	ts_correct[i].Draw("same")
	ts_correct[1].Draw("same")


	c.cd(2)
	if i==0: 	ts_correctmass[i].Draw("")
	else: 	ts_correctmass[i].Draw("same")
	ts_correctmass[1].Draw("same")

	leg = TLegend(0.7,0.35,1,0.75)
	leg.SetHeader("Systematics") 
	if i>=0: leg.AddEntry(ts_correctmass[0],"scaledown","l",)
	if i>=1: leg.AddEntry(ts_correctmass[1],"172v5","l")
	if i>=2: leg.AddEntry(ts_correctmass[2],"scaleup","l")

	leg.SetTextSize(0.02)
	leg.Draw();
#####
	c1.cd()
	if i==0: 	ts_correct[i].Draw("")
	else: 	ts_correct[i].Draw("same")
	ts_correct[1].Draw("same")
	leg.Draw();


	c2.cd()
	if i==0: 	ts_correctmass[i].Draw("")
	else: 	ts_correctmass[i].Draw("same")
	ts_correctmass[1].Draw("same")
	leg.Draw();




	# titles
	ts_correct[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE")

	ts_correctmass[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE")

	c.Modified()

	del histo_correct
	#min mass
	del histo_correctmass

	del rootfile1

c1.SaveAs("./../plots/compare_scales_deltar.pdf")
c2.SaveAs("./../plots/compare_scales_minmass.pdf")
c.SaveAs("./../plots/compare_scales_2plots.pdf")

# with r.t. 172v5

ts_correct[0].Divide(ts_correct[1])
ts_correct[2].Divide(ts_correct[1])
ts_correct[1].Divide(ts_correct[1])
ts_correctmass[0].Divide(ts_correctmass[1])
ts_correctmass[2].Divide(ts_correctmass[1])
ts_correctmass[1].Divide(ts_correctmass[1])

c_divided = TCanvas("canvasd_divided", "c", 1000, 500)
c_divided.Divide(2,1,0.01,0.01)
c1_divided = TCanvas("canvas1_divided", "c", 1000, 1000)
c2_divided = TCanvas("canvas2_divided", "c", 1000, 1000)

ts_correct[0].SetMaximum(2.5)
ts_correctmass[0].SetMaximum(2.5)

for i in range(0,3):
	c_divided.cd(1)
	if i==0: 	ts_correct[i].Draw("HIST")
	else: 	ts_correct[i].Draw("HIST:same")
	ts_correct[1].Draw("HIST:same")


	c_divided.cd(2)
	if i==0: 	ts_correctmass[i].Draw("HIST")
	else: 	ts_correctmass[i].Draw("HIST:same")
	ts_correctmass[1].Draw("HIST:same")

	leg = TLegend(0.35,0.55,0.65,0.9)
	leg.SetHeader("Systematics (w.r.t. 172v5)") 
	if i>=0: leg.AddEntry(ts_correctmass[0],"scaledown","l",)
	if i>=1: leg.AddEntry(ts_correctmass[1],"172v5","l")
	if i>=2: leg.AddEntry(ts_correctmass[2],"scaleup","l")

	leg.SetTextSize(0.02)
	leg.Draw();
	#####
	c1_divided.cd()
	if i==0: 	ts_correct[i].Draw("HIST")
	else: 	ts_correct[i].Draw("HIST:same")
	ts_correct[1].Draw("HIST:same")
	leg.Draw();


	c2_divided.cd()
	if i==0: 	ts_correctmass[i].Draw("HIST")
	else: 	ts_correctmass[i].Draw("HIST:same")
	ts_correctmass[1].Draw("HIST:same")
	leg.Draw();

c_divided.Modified()
c1_divided.Modified()
c2_divided.Modified()
c_divided.Update()
c1_divided.Update()
c2_divided.Update()
# Save the plot and close the files

c1_divided.SaveAs("./../plots/compare_scales_deltar_divided.pdf")
c2_divided.SaveAs("./../plots/compare_scales_minmass_divided.pdf")
c_divided.SaveAs("./../plots/compare_scales_2plots_divided.pdf")

