#!/usr/bin/env python
import ROOT, os, sys
from ROOT import TFile, TCanvas, THStack, TLegend, TH1D, TGraph

## Run by calling in the shell:
## ./macroTemplate.py

# Open a file
path = "/afs/cern.ch/work/j/jklocans/private/CMSSW_5_3_15/src/UserCode/llvv_fwk/lxyplots/"

################

ts_correct = []
ts_wrong = []

#min mass
ts_correctmass = []
ts_wrongmass = []

# Make a new TCanvas
c = TCanvas("canvas", "c", 500, 600)
c.Divide(2,5,0.01,0.01)


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

# Open the files -> adds all samples together
for i in range(0,6):

	rootfile1 = []

	ts_correct.append(TH1D("hs1","test stacked histograms", 50, 0., 150.))
	ts_wrong.append(TH1D("hs2","test stacked histograms", 50, 0., 150.))
	ts_correctmass.append(TH1D("hs3","test stacked histograms", 50, 0., 150.))
	ts_wrongmass.append(TH1D("hs4","test stackhsed histograms", 50, 0., 150.))


	for x in listoffiles[i]:
	#inv.m. l + sv
		rootfile1.append(TFile.Open("./../lxyplots/" + x, "READ"))

	#deltar
	histo_correct = []
	histo_wrong = []

	#min mass
	histo_correctmass = []
	histo_wrongmass = []

	for x in range(0,len(listoffiles[i])):

		histo_correct.append(rootfile1[x].Get("mlSv_emu_deltar_correct"))
		histo_wrong.append(rootfile1[x].Get("mlSv_emu_deltar_wrong"))

		#min mass
		histo_correctmass.append(rootfile1[x].Get("mlSv_emu_minmass_correct"))
		histo_wrongmass.append(rootfile1[x].Get("mlSv_emu_minmass_wrong"))

		#adding histos

		ts_correct[i].Add(histo_correct[x])
		ts_wrong[i].Add(histo_wrong[x])
		ts_correctmass[i].Add(histo_correctmass[x])
		ts_wrongmass[i].Add(histo_wrongmass[x])
	# Set colors and stuff
	# Set colors and stuff

		#normalization

	if (ts_correct[i].Integral() != 0):
		ts_correct[i].Scale(1/ts_correct[i].Integral())


	if (ts_correctmass[i].Integral() != 0):
		ts_correctmass[i].Scale(1/ts_correctmass[i].Integral())


	if (ts_wrong[i].Integral() != 0):
		ts_wrong[i].Scale(1/ts_wrong[i].Integral())


	if (ts_wrongmass[i].Integral() != 0):
		ts_wrongmass[i].Scale(1/ts_wrongmass[i].Integral())

	ts_correct[i].SetLineColor(51 + 9*i)
	ts_wrong[i].SetLineColor(51 + 9*i)
	ts_correctmass[i].SetLineColor(51 + 9*i)
	ts_wrongmass[i].SetLineColor(51 + 9*i)

	ts_correct[i].SetMarkerColor(51 + 9*i)
	ts_wrong[i].SetMarkerColor(51 + 9*i)
	ts_correctmass[i].SetMarkerColor(51 + 9*i)
	ts_wrongmass[i].SetMarkerColor(51 + 9*i)

	# Draw them

	c.cd(1)
	if i==0: 	ts_correct[i].Draw("")
	else: 	ts_correct[i].Draw("same")

	c.cd(3)
	if i==0: 		ts_wrong[i].Draw("")
	else: 		ts_wrong[i].Draw("same")


	c.cd(2)
	if i==0: 	ts_correctmass[i].Draw("")
	else: 	ts_correctmass[i].Draw("same")

	leg = TLegend(0.7,0.3,1,0.7)
	leg.SetHeader("Results after assigning lepton to closest (DeltaR <-> Minmass) sec.v.")  ##NEEDS TO BE CHANGED
	if i>=0: leg.AddEntry(ts_correctmass[0],"166v5","l",)
	if i>=1: leg.AddEntry(ts_correctmass[1],"169v5","l")
	if i>=2: leg.AddEntry(ts_correctmass[2],"172v5","l")
	if i>=3: leg.AddEntry(ts_correctmass[3],"173v5","l")
	if i>=4: leg.AddEntry(ts_correctmass[4],"175v5","l")
	if i>=5: leg.AddEntry(ts_correctmass[5],"178v5","l")
	leg.Draw();

	c.cd(4)
	if i==0: 	ts_wrongmass[i].Draw("")
	else:	ts_wrongmass[i].Draw("same")


	# titles
	ts_correct[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE")

	ts_correctmass[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE")

	ts_wrong[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE")

	ts_wrongmass[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) WRONG CHARGE")

	c.Modified()

	del histo_correct
	del histo_wrong 
	#min mass
	del histo_correctmass
	del histo_wrongmass

	del rootfile1

# this part for different plot

c2=TCanvas("c2", "mean value of inv.m. vs top mass", 500, 600) 

x = []
x.append(166.5)
x.append(169.5)
x.append(172.5)
x.append(173.5)
x.append(175.5)
x.append(178.5)

graph1 = TGraph(6)
graph2 = TGraph(6)
y = [0.]*6
z = [0.]*6
for i in range(0,6):
	y[i]=ts_correct[i].GetMean()
	z[i]=ts_correctmass[i].GetMean()
	graph1.SetPoint(i, x[i], y[i])	
	graph2.SetPoint(i, x[i], z[i])

c2.cd()
graph1.Draw("A*")
graph2.SetLineColor(2)
graph2.SetMarkerColor(2)
graph2.Draw("*")

prob=4
count=0
while(count < 6):
	ts_correct[prob].Divide(ts_correct[3])
	ts_wrong[prob].Divide(ts_wrong[3])
	ts_correctmass[prob].Divide(ts_correctmass[3])
	ts_wrongmass[prob].Divide(ts_wrongmass[3])
	prob = prob + 1
	count = count + 1
	if prob == 6: prob = 0

ts_correct[0].SetMaximum(2.5)
ts_correctmass[0].SetMaximum(2.5)
ts_wrong[0].SetMaximum(2.5)
ts_wrongmass[0].SetMaximum(2.5)

c.Update()
c.Modified()	

# Save the plot and close the files
c.SaveAs("./../plots/deltar_minmass_4plots_divided.pdf")
c2.SaveAs("./../plots/deltar_minmass_2plots_divided.pdf")

