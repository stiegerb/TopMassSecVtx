#!/usr/bin/env python
import ROOT, os, sys
from ROOT import TFile, TCanvas, THStack, TLegend, TH1D, TGraph, TGraphErrors, TF1

## Run by calling in the shell:
## ./macroTemplate.py

# Open a file
path = "/afs/cern.ch/work/j/jklocans/private/CMSSW_5_3_15/src/UserCode/llvv_fwk/lxyplots/"

################

ts_correct = []
ts_correct_topweight = []
ts_correct_topweight_up = []
ts_correct_topweight_down = []

#min mass
ts_correctmass = []
ts_correctmass_topweight = []
ts_correctmass_topweight_up = []
ts_correctmass_topweight_down = []

# Make a new TCanvas
c1 = TCanvas("canvas1", "c", 1000, 500)
c1_divided = TCanvas("canvas1_divided", "c", 1000, 500)

c1.Divide(2,1,0.01,0.01)
c1_divided.Divide(2,1,0.01,0.01)

# save all names of desired files in a list

listoffiles = [[] for x in xrange(0,1)]

for file in os.listdir( path ):
	if(file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_172v5")):
		listoffiles[0].insert(0,file)


# Open the files -> adds all samples together
listofnames = []
listofnames.append("172v5")

for x in listofnames:

	ts_correct.append(TH1D("deltar_correct" + x,"inv.m. of lepton and secvtx (deltar, correct charge) for diff. topweights", 50, 0., 150.))
	ts_correctmass.append(TH1D("minmass_correct" + x,"inv.m. of lepton and secvtx (minmass correct charge) for diff. topweights", 50, 0., 150.))


	ts_correct_topweight.append(TH1D("deltar_correct_topweight" + x,"inv.m. of lepton and secvtx (deltar, correct charge) for diff. topweights", 50, 0., 150.))
	ts_correctmass_topweight.append(TH1D("minmass_correct_topweight" + x,"inv.m. of lepton and secvtx (minmass correct charge) for diff. topweights", 50, 0., 150.))

	ts_correct_topweight_up.append(TH1D("deltar_correct_topweight_up" + x,"inv.m. of lepton and secvtx (deltar, correct charge) for diff. topweights", 50, 0., 150.))
	ts_correctmass_topweight_up.append(TH1D("minmass_correct_topweight_up" + x,"inv.m. of lepton and secvtx (minmass correct charge) for diff. topweights", 50, 0., 150.))

	ts_correct_topweight_down.append(TH1D("deltar_correct_topweight_down" + x,"inv.m. of lepton and secvtx (deltar, correct charge) for diff. topweights", 50, 0., 150.))
	ts_correctmass_topweight_down.append(TH1D("minmass_correct_topweight_down" + x,"inv.m. of lepton and secvtx (minmass correct charge) for diff. topweights", 50, 0., 150.))

print len(listofnames)
for i in range(0,len(listoffiles)):
	ts_correct[i].Sumw2()
	ts_correctmass[i].Sumw2()
	ts_correct_topweight[i].Sumw2()
	ts_correctmass_topweight[i].Sumw2()
	ts_correct_topweight_up[i].Sumw2()
	ts_correctmass_topweight_up[i].Sumw2()
	ts_correct_topweight_down[i].Sumw2()
	ts_correctmass_topweight_down[i].Sumw2()

	rootfile1 = []

	for x in listoffiles[i]:
	#inv.m. l + sv
		rootfile1.append(TFile.Open("./../lxyplots/" + x, "READ"))

	#deltar
	histo_correct = []
	histo_correct_topweight = []
	histo_correct_topweight_up = []
	histo_correct_topweight_down = []

	#min mass
	histo_correctmass = []
	histo_correctmass_topweight = []
	histo_correctmass_topweight_up = []
	histo_correctmass_topweight_down = []

	for x in range(0,len(listoffiles[i])):

		histo_correct.append(rootfile1[x].Get("mlsv_emu_deltar_correct"))
		histo_correct_topweight.append(rootfile1[x].Get("mlsv_emu_deltar_correct_topweight"))
		histo_correct_topweight_down.append(rootfile1[x].Get("mlsv_emu_deltar_correct_topweight_down"))
		histo_correct_topweight_up.append(rootfile1[x].Get("mlsv_emu_deltar_correct_topweight_up"))

		#min mass
		histo_correctmass.append(rootfile1[x].Get("mlsv_emu_minmass_correct"))
		histo_correctmass_topweight.append(rootfile1[x].Get("mlsv_emu_minmass_correct_topweight"))
		histo_correctmass_topweight_down.append(rootfile1[x].Get("mlsv_emu_minmass_correct_topweight_down"))
		histo_correctmass_topweight_up.append(rootfile1[x].Get("mlsv_emu_minmass_correct_topweight_up"))


		histo_correct[x].Sumw2()
		histo_correctmass[x].Sumw2()

		histo_correct_topweight[x].Sumw2()
		histo_correct_topweight_down[x].Sumw2()
		histo_correct_topweight_up[x].Sumw2()

		histo_correctmass_topweight[x].Sumw2()
		histo_correctmass_topweight_down[x].Sumw2()
		histo_correctmass_topweight_up[x].Sumw2()


		#adding histos

		ts_correct[i].Add(histo_correct[x])
		ts_correctmass[i].Add(histo_correctmass[x])

		ts_correct_topweight[i].Add(histo_correct_topweight[x])
		ts_correctmass_topweight[i].Add(histo_correctmass_topweight[x])

		ts_correct_topweight_down[i].Add(histo_correct_topweight_down[x])
		ts_correctmass_topweight_down[i].Add(histo_correctmass_topweight_down[x])

		ts_correct_topweight_up[i].Add(histo_correct_topweight_up[x])
		ts_correctmass_topweight_up[i].Add(histo_correctmass_topweight_up[x])

		#normalization

	if (ts_correct[i].Integral() != 0):
		ts_correct[i].Scale(1/ts_correct[i].Integral())

	if (ts_correctmass[i].Integral() != 0):
		ts_correctmass[i].Scale(1/ts_correctmass[i].Integral())


	if (ts_correct_topweight[i].Integral() != 0):
		ts_correct_topweight[i].Scale(1/ts_correct_topweight[i].Integral())

	if (ts_correctmass_topweight[i].Integral() != 0):
		ts_correctmass_topweight[i].Scale(1/ts_correctmass_topweight[i].Integral())


	if (ts_correct_topweight_up[i].Integral() != 0):
		ts_correct_topweight_up[i].Scale(1/ts_correct_topweight_up[i].Integral())

	if (ts_correctmass_topweight_up[i].Integral() != 0):
		ts_correctmass_topweight_up[i].Scale(1/ts_correctmass_topweight_up[i].Integral())


	if (ts_correct_topweight_down[i].Integral() != 0):
		ts_correct_topweight_down[i].Scale(1/ts_correct_topweight_down[i].Integral())

	if (ts_correctmass_topweight_down[i].Integral() != 0):
		ts_correctmass_topweight_down[i].Scale(1/ts_correctmass_topweight_down[i].Integral())


	# Set colors and stuff
	# Set colors and stuff

	ts_correct[i].SetLineColor(1)
	ts_correctmass[i].SetLineColor(1)

	ts_correctmass_topweight[i].SetLineColor(1)
	ts_correct_topweight[i].SetLineColor(1)

	ts_correctmass_topweight_up[i].SetLineColor(2)
	ts_correct_topweight_up[i].SetLineColor(2)

	ts_correctmass_topweight_down[i].SetLineColor(4)
	ts_correct_topweight_down[i].SetLineColor(4)

	ts_correct[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correct[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_correctmass[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correctmass[i].GetYaxis().SetTitle("number of events (normalized by area)")

	# Draw them


	c1.cd(1)
	if i==0: 	
		ts_correct_topweight[i].Draw("")
		ts_correct_topweight_up[i].Draw("same")
		ts_correct_topweight_down[i].Draw("same")
	else: 	
		ts_correct_topweight[i].Draw("same")
		ts_correct_topweight_up[i].Draw("same")
		ts_correct_topweight_down[i].Draw("same")

	ts_correct_topweight[0].Draw("same")

	c1.cd(2)
	if i==0: 	
		ts_correctmass_topweight[i].Draw("")
		ts_correctmass_topweight_down[i].Draw("same")
		ts_correctmass_topweight_up[i].Draw("same")
	else: 	
		ts_correctmass_topweight[i].Draw("same")
		ts_correctmass_topweight_down[i].Draw("same")
		ts_correctmass_topweight_up[i].Draw("same")

	leg = TLegend(0.7,0.35,1,0.75)
	leg.SetHeader("Systematics") 
	leg.AddEntry(ts_correct_topweight[0],"top weight","l",)
	leg.AddEntry(ts_correct_topweight_up[0],"top up weight","l")
	leg.AddEntry(ts_correct_topweight_down[0],"top down weight","l")

	leg.SetTextSize(0.02)
	leg.Draw();

	# titles
	ts_correct[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE")

	ts_correctmass[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE")

	del histo_correct
	del histo_correctmass
	del histo_correct_topweight
	del histo_correctmass_topweight
	del histo_correct_topweight_down
	del histo_correctmass_topweight_down
	del histo_correct_topweight_up
	del histo_correctmass_topweight_up
	del rootfile1

c1.Modified()
c1.Update()

# Save the plot and close the files
c1.SaveAs("./../plots/compare_scales_topweight_up_2plots.pdf")


for i in range(0,len(listoffiles)):
	
	ts_correct_topweight_up[i].Divide(ts_correct_topweight[i])
	ts_correct_topweight_down[i].Divide(ts_correct_topweight[i])
	ts_correct_topweight[i].Divide(ts_correct_topweight[i])

	ts_correctmass_topweight_up[i].Divide(ts_correctmass_topweight[i])
	ts_correctmass_topweight_down[i].Divide(ts_correctmass_topweight[i])
	ts_correctmass_topweight[i].Divide(ts_correctmass_topweight[i])

	c1_divided.cd(1)
	if i==0: 		
		ts_correct_topweight[i].Draw("HIST")
		ts_correct_topweight_down[i].Draw("HIST:same")
		ts_correct_topweight_up[i].Draw("HIST:same")
	else: 	
		ts_correct_topweight[i].Draw("HIST:same")
		ts_correct_topweight_down[i].Draw("HIST:same")
		ts_correct_topweight_up[i].Draw("HIST:same")

	ts_correct_topweight[i].Draw("HIST:same")

	c1_divided.cd(2)
	if i==0: 	
		ts_correctmass_topweight[i].Draw("HIST")
		ts_correctmass_topweight_down[i].Draw("HIST:same")
		ts_correctmass_topweight_up[i].Draw("HIST:same")
	else: 	
		ts_correctmass_topweight[i].Draw("HIST:same")
		ts_correctmass_topweight_down[i].Draw("HIST:same")
		ts_correctmass_topweight_up[i].Draw("HIST:same")

	leg = TLegend(0.45,0.75,0.7,0.9)
	leg.SetHeader("Systematics") 
	leg.AddEntry(ts_correct_topweight[0],"top weight","l",)
	leg.AddEntry(ts_correct_topweight_up[0],"top up weight","l")
	leg.AddEntry(ts_correct_topweight_down[0],"top down weight","l")

	leg.SetTextSize(0.02)
	leg.Draw();

ts_correct_topweight[i].SetMaximum(1.5)
ts_correctmass_topweight[i].SetMaximum(1.5)

ts_correct_topweight[i].SetMinimum(0.5)
ts_correctmass_topweight[i].SetMinimum(0.5)


c1_divided.Modified()
c1_divided.Update()

c1_divided.SaveAs("./../plots/compare_scales_topweight_up_2plots_divided.pdf")
