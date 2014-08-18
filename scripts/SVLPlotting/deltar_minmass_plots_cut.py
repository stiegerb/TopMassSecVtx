#!/usr/bin/env python
import ROOT, os, sys
from ROOT import TFile, TCanvas, THStack, TLegend, TH1D, TGraph, TGraphErrors, TF1

## Run by calling in the shell:
## ./macroTemplate.py

# Open a file
path = "/afs/cern.ch/work/j/jklocans/private/CMSSW_5_3_15/src/UserCode/llvv_fwk/lxyplots/"

################

ts_correct = []
ts_wrong = []

# Make a new TCanvas
c = TCanvas("canvas", "c", 1000, 500)
c.Divide(2,1,0.01,0.01)

leg = TLegend(0.7,0.35,1,0.75)

# save all names of desired files in a list

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

	ts_correct.append(TH1D("emu_deltar_correct_cut" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrong.append(TH1D("emu_deltar_wrong_cut" + x,"test stacked histograms", 50, 0., 150.))


# Open the files -> adds all samples together
for i in range(0,6):
	ts_correct[i].Sumw2()
	ts_wrong[i].Sumw2()

	rootfile1 = []

	for x in listoffiles[i]:
	#inv.m. l + sv
		rootfile1.append(TFile.Open("./../lxyplots/" + x, "READ"))

	#deltar
	histo_correct = []
	histo_wrong = []

	for x in range(0,len(listoffiles[i])):

		histo_correct.append(rootfile1[x].Get("mlsv_emu_deltar_cut_correct"))
		histo_wrong.append(rootfile1[x].Get("mlsv_emu_deltar_cut_wrong"))
		histo_correct[x].Sumw2()
		histo_wrong[x].Sumw2()

		#adding histos

		ts_correct[i].Add(histo_correct[x])
		ts_wrong[i].Add(histo_wrong[x])

	#normalization

	ts_correct[i].Scale(1/ts_correct[i].Integral())
	ts_wrong[i].Scale(1/ts_wrong[i].Integral())

	# Set colors and stuff
	# Set colors and stuff

	ts_correct[i].SetLineColor(51 + 9*i)
	ts_wrong[i].SetLineColor(51 + 9*i)

	ts_correct[i].SetMarkerColor(51 + 9*i)
	ts_wrong[i].SetMarkerColor(51 + 9*i)


	ts_correct[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correct[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrong[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrong[i].GetYaxis().SetTitle("number of events (normalized by area)")

	# titles
	ts_correct[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE")

	ts_wrong[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE")


	# Draw them

	if i >=5:

		leg.SetHeader("Results for diff. top masses")   ##NEEDS TO BE CHANGED
		leg.AddEntry(ts_correct[0],"166v5","l",)
		leg.AddEntry(ts_correct[1],"169v5","l")
		leg.AddEntry(ts_correct[2],"172v5","l")
		leg.AddEntry(ts_correct[3],"173v5","l")
		leg.AddEntry(ts_correct[4],"175v5","l")
		leg.AddEntry(ts_correct[5],"178v5","l")
		leg.SetTextSize(0.02)

	c.cd(1)
	if i==0: 	ts_correct[i].Draw("")
	else: 	ts_correct[i].Draw("same")

	c.cd(2)
	if i==0: 		ts_wrong[i].Draw("")
	else: 		ts_wrong[i].Draw("same")

	c.Modified()
	c.Update()

	del histo_correct
	del histo_wrong 

	del rootfile1
# Save the plot and close the files
c.SaveAs("./../plots/deltar_cut_4plots.pdf")

#to save all samples together

#rootfile2 = []


#rootfile2.append((TFile("../newsamples/jevgeny_samples_total.root", "RECREATE")))
#for i in range(0,6):

c2=TCanvas("c2", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
y = [0.]*6 
yerr = [0.]*6 
graph1 = TGraphErrors(6)
x = []
x.append(166.5)
x.append(169.5)
x.append(172.5)
x.append(173.5)
x.append(175.5)
x.append(178.5)

for i in range(0,6):
	y[i]=ts_correct[i].GetMean()
	yerr[i] = ts_correct[i].GetMeanError()
	graph1.SetPoint(i, x[i], y[i])
	graph1.SetPointError(i, 0, yerr[i])


c2.cd()
graph1.Draw("AP")
graph1.GetYaxis().SetTitle("Mean value")
graph1.GetXaxis().SetTitle("Top M(GeV)")
graph1.Draw("AP")


graph1.Fit("pol1")

pol1=TF1()
pol1=graph1.GetFunction("pol1")

a0=str(round(pol1.GetParameter(0),2))
a1=str(round(pol1.GetParameter(1),2))

pol1.SetLineColor(1)
graph1.SetMarkerColor(1)
graph1.SetLineColor(1)

leg2 = TLegend(0.7,0.15,1,0.25)
leg2.SetHeader("Fits:")  ##NEEDS TO BE CHANGED
leg2.AddEntry(pol1, "deltar: y = " + a0 + " + " + a1 + "x", "ll")
leg2.Draw()
# part for relative ratios
# part for relative ratios
# part for relative ratios

c2.SaveAs("./../plots/deltar_cut_calib.pdf")
prob=3
count=0
while(count < 6):
	ts_correct[prob].Divide(ts_correct[2])
	ts_wrong[prob].Divide(ts_wrong[2])

	prob = prob + 1
	count = count + 1
	if prob == 6: prob = 0

	ts_correct[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV")
	ts_wrong[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV")


c3 = TCanvas("canvas3", "c3", 1000, 500)
c3.Divide(2,1,0.01,0.01)


for i in range(0,6):



	# Draw them

	c3.cd(1)
	if i==0: 	ts_correct[i].Draw("HIST")
	else: 	ts_correct[i].Draw("HIST:same")
	leg_ratio = TLegend(0.25,0.5,0.55,0.9)
	leg_ratio.SetHeader("Results for diff. top masses")  ##NEEDS TO BE CHANGED
	leg_ratio.AddEntry(ts_correct[0],"166v5","l")
	leg_ratio.AddEntry(ts_correct[1],"169v5","l")
	leg_ratio.AddEntry(ts_correct[2],"172v5","l")
	leg_ratio.AddEntry(ts_correct[3],"173v5","l")
	leg_ratio.AddEntry(ts_correct[4],"175v5","l")
	leg_ratio.AddEntry(ts_correct[5],"178v5","l")
	leg_ratio.SetTextSize(0.02)
	leg_ratio.Draw()

	c3.cd(2)
	if i==0: 		ts_wrong[i].Draw("HIST")
	else: 		ts_wrong[i].Draw("HIST:same")

ts_correct[0].SetMaximum(2.5)

c3.Update()
c3.Modified()

# Save the plot and close the files
c3.SaveAs("./../plots/deltar_cut_4plots_divided.pdf")
