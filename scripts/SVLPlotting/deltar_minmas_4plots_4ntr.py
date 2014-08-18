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

#min mass
ts_correctmass = []
ts_wrongmass = []

# Make a new TCanvas
c = TCanvas("canvas", "c", 1000, 1000)
c.Divide(2,2,0.01,0.01)
c11=TCanvas("c11", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c12=TCanvas("c12", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c13=TCanvas("c13", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c14=TCanvas("c14", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 

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

	ts_correct.append(TH1D("deltar_correct" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrong.append(TH1D("deltar_wrong" + x,"test stacked histograms", 50, 0., 150.))
	ts_correctmass.append(TH1D("minmass_correct" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrongmass.append(TH1D("minmass_wrong" + x,"test stackhsed histograms", 50, 0., 150.))

# Open the files -> adds all samples together
for i in range(0,6):
	ts_correct[i].Sumw2()
	ts_wrong[i].Sumw2()
	ts_correct[i].Sumw2()
	ts_wrongmass[i].Sumw2()
	rootfile1 = []

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

		histo_correct.append(rootfile1[x].Get("mlSv_emu_deltar_ntr4_correct"))
		histo_wrong.append(rootfile1[x].Get("mlSv_emu_deltar_ntr4_wrong"))

		#min mass
		histo_correctmass.append(rootfile1[x].Get("mlSv_emu_minmass_ntr4_correct"))
		histo_wrongmass.append(rootfile1[x].Get("mlSv_emu_minmass_ntr4_wrong"))

		histo_correct[x].Sumw2()
		histo_wrong[x].Sumw2()
		histo_correctmass[x].Sumw2()
		histo_wrongmass[x].Sumw2()

		#adding histos

		ts_correct[i].Add(histo_correct[x])
		ts_wrong[i].Add(histo_wrong[x])
		ts_correctmass[i].Add(histo_correctmass[x])
		ts_wrongmass[i].Add(histo_wrongmass[x])

		#normalization

	if (ts_correct[i].Integral() != 0):
		ts_correct[i].Scale(1/ts_correct[i].Integral())


	if (ts_correctmass[i].Integral() != 0):
		ts_correctmass[i].Scale(1/ts_correctmass[i].Integral())


	if (ts_wrong[i].Integral() != 0):
		ts_wrong[i].Scale(1/ts_wrong[i].Integral())


	if (ts_wrongmass[i].Integral() != 0):
		ts_wrongmass[i].Scale(1/ts_wrongmass[i].Integral())

	# Set colors and stuff
	# Set colors and stuff

	ts_correct[i].SetLineColor(51 + 9*i)
	ts_wrong[i].SetLineColor(51 + 9*i)
	ts_correctmass[i].SetLineColor(51 + 9*i)
	ts_wrongmass[i].SetLineColor(51 + 9*i)

	ts_correct[i].SetMarkerColor(51 + 9*i)
	ts_wrong[i].SetMarkerColor(51 + 9*i)
	ts_correctmass[i].SetMarkerColor(51 + 9*i)
	ts_wrongmass[i].SetMarkerColor(51 + 9*i)

	ts_correct[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correct[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrong[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrong[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_correctmass[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correctmass[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrongmass[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrongmass[i].GetYaxis().SetTitle("number of events (normalized by area)")

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

	leg = TLegend(0.7,0.35,1,0.75)
	leg.SetHeader("Results for diff. top masses")   ##NEEDS TO BE CHANGED
	if i>=0: leg.AddEntry(ts_correctmass[0],"166v5","l",)
	if i>=1: leg.AddEntry(ts_correctmass[1],"169v5","l")
	if i>=2: leg.AddEntry(ts_correctmass[2],"172v5","l")
	if i>=3: leg.AddEntry(ts_correctmass[3],"173v5","l")
	if i>=4: leg.AddEntry(ts_correctmass[4],"175v5","l")
	if i>=5: leg.AddEntry(ts_correctmass[5],"178v5","l")
	leg.SetTextSize(0.02)
	leg.Draw();

	c.cd(4)
	if i==0: 	ts_wrongmass[i].Draw("")
	else:	ts_wrongmass[i].Draw("same")

	c11.cd()
	if i==0: 	ts_correct[i].Draw("")
	else:	ts_correct[i].Draw("same")
	leg11 = TLegend(0.7,0.35,1,0.75)
	leg11.SetHeader("Results for diff. top masses")   ##NEEDS TO BE CHANGED
	if i>=0: leg11.AddEntry(ts_correct[0],"166v5","l")
	if i>=1: leg11.AddEntry(ts_correct[1],"169v5","l")
	if i>=2: leg11.AddEntry(ts_correct[2],"172v5","l")
	if i>=3: leg11.AddEntry(ts_correct[3],"173v5","l")
	if i>=4: leg11.AddEntry(ts_correct[4],"175v5","l")
	if i>=5: leg11.AddEntry(ts_correct[5],"178v5","l")
	leg.SetTextSize(0.02)
	leg.Draw();

	c12.cd()
	if i==0: 	ts_wrong[i].Draw("")
	else:	ts_wrong[i].Draw("same")
	leg12 = TLegend(0.7,0.35,1,0.75)
	leg12.SetHeader("Results for diff. top masses")   ##NEEDS TO BE CHANGED
	if i>=0: leg12.AddEntry(ts_wrong[0],"166v5","l")
	if i>=1: leg12.AddEntry(ts_wrong[1],"169v5","l")
	if i>=2: leg12.AddEntry(ts_wrong[2],"172v5","l")
	if i>=3: leg12.AddEntry(ts_wrong[3],"173v5","l")
	if i>=4: leg12.AddEntry(ts_wrong[4],"175v5","l")
	if i>=5: leg12.AddEntry(ts_wrong[5],"178v5","l")
	leg12.SetTextSize(0.02)
	leg12.Draw();

	c13.cd()
	if i==0: 	ts_correctmass[i].Draw("")
	else:	ts_correctmass[i].Draw("same")
	leg13 = TLegend(0.7,0.35,1,0.75)
	leg13.SetHeader("Results for diff. top masses")   ##NEEDS TO BE CHANGED
	if i>=0: leg13.AddEntry(ts_correctmass[0],"166v5","l")
	if i>=1: leg13.AddEntry(ts_correctmass[1],"169v5","l")
	if i>=2: leg13.AddEntry(ts_correctmass[2],"172v5","l")
	if i>=3: leg13.AddEntry(ts_correctmass[3],"173v5","l")
	if i>=4: leg13.AddEntry(ts_correctmass[4],"175v5","l")
	if i>=5: leg13.AddEntry(ts_correctmass[5],"178v5","l")
	leg13.SetTextSize(0.02)
	leg13.Draw();

	c14.cd()
	if i==0: 	ts_wrongmass[i].Draw("")
	else:	ts_wrongmass[i].Draw("same")
	leg14 = TLegend(0.7,0.3,1,0.7)
	leg14.SetHeader("Results for diff. top masses")   ##NEEDS TO BE CHANGED
	if i>=0: leg14.AddEntry(ts_wrongmass[0],"166v5","l")
	if i>=1: leg14.AddEntry(ts_wrongmass[1],"169v5","l")
	if i>=2: leg14.AddEntry(ts_wrongmass[2],"172v5","l")
	if i>=3: leg14.AddEntry(ts_wrongmass[3],"173v5","l")
	if i>=4: leg14.AddEntry(ts_wrongmass[4],"175v5","l")
	if i>=5: leg14.AddEntry(ts_wrongmass[5],"178v5","l")
	leg14.SetTextSize(0.02)
	leg14.Draw();

	# titles
	ts_correct[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE")

	ts_correctmass[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE")

	ts_wrong[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE")

	ts_wrongmass[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) WRONG CHARGE")

	c.Modified()
	c11.Modified()
	c12.Modified()
	c13.Modified()
	c14.Modified()

	del histo_correct
	del histo_wrong 
	#min mass
	del histo_correctmass
	del histo_wrongmass

	del rootfile1

# Save the plot and close the files
c.SaveAs("./../plots/deltar_minmass_4plots_4ntr.pdf")
c11.SaveAs("./../plots/deltar_correct_4ntr.pdf")
c12.SaveAs("./../plots/deltar_wrong_4ntr.pdf")
c13.SaveAs("./../plots/deltar_correctmass_4ntr.pdf")
c14.SaveAs("./../plots/deltar_wrongmass_4ntr.pdf")

rootfile2 = []

# to save all samples together
#for i in range(0,6):
#	rootfile2.append((TFile("../newsamples/" + listofnames[i] + "_total.root", "RECREATE")))
#	ts_correct[i].Write()
#	ts_wrong[i].Write()
#	ts_correctmass[i].Write()
#	ts_wrongmass[i].Write()
#	rootfile2[i].Close()


# this part for different plot

c2=TCanvas("c2", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 

x = []
x.append(166.5)
x.append(169.5)
x.append(172.5)
x.append(173.5)
x.append(175.5)
x.append(178.5)

graph1 = TGraphErrors(6)
graph2 = TGraphErrors(6)
graph1err = TGraphErrors(6)
graph2err = TGraphErrors(6)

y = [0.]*6 
z = [0.]*6
yerr = [0.]*6
zerr = [0.]*6

for i in range(0,6):
	y[i]=ts_correct[i].GetMean()
	z[i]=ts_correctmass[i].GetMean()
	yerr[i] = ts_correct[i].GetMeanError()
	zerr[i] = ts_correctmass[i].GetMeanError()
	graph1.SetPoint(i, x[i], y[i])	
	graph2.SetPoint(i, x[i], z[i])
	graph1.SetPointError(i, 0, yerr[i])	
	graph2.SetPointError(i, 0, zerr[i])

c2.cd()
graph1.Draw("AP")
graph1.GetYaxis().SetRangeUser(59.,68.)
graph1.GetYaxis().SetTitle("Mean value")
graph1.GetXaxis().SetTitle("Top M(GeV)")
graph1.Draw("AP")
graph1.SetTitle("Mean value of the histogram vs top mass")
graph2.SetLineColor(2)
graph2.SetMarkerColor(2)
graph2.Draw("P")

# fit

graph1.Fit("pol1")
graph2.Fit("pol1")

pol1=TF1()
pol1=graph1.GetFunction("pol1")
pol2=TF1()
pol2=graph2.GetFunction("pol1")

a0=str(round(pol1.GetParameter(0),2))
a1=str(round(pol1.GetParameter(1),2))
b0=str(round(pol2.GetParameter(0),2))
b1=str(round(pol2.GetParameter(1),2))

pol1.SetLineColor(1)
pol2.SetLineColor(2)

leg2 = TLegend(0.7,0.15,1,0.25)
leg2.SetHeader("Fits:")  ##NEEDS TO BE CHANGED
leg2.AddEntry(pol1, "deltar: y = " + a0 + " + " + a1 + "x", "ll")
leg2.AddEntry(pol2, "minmass: y = " + b0 + " + " + b1 + "x", "ll")
leg2.Draw()

c2.Update()
c2.Modified()

# Save the plot and close the files
c2.SaveAs("./../plots/deltar_minmass_2plots_4ntr.pdf")



# part for relative ratios
# part for relative ratios
# part for relative ratios

prob=3
count=0
while(count < 6):
	ts_correct[prob].Divide(ts_correct[2])
	ts_wrong[prob].Divide(ts_wrong[2])
	ts_correctmass[prob].Divide(ts_correctmass[2])
	ts_wrongmass[prob].Divide(ts_wrongmass[2])
	prob = prob + 1
	count = count + 1
	if prob == 6: prob = 0
	ts_correct[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV")
	ts_wrong[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV")
	ts_correctmass[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV")
	ts_wrongmass[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV")

c3 = TCanvas("canvas3", "c3", 1000, 1000)
c3.Divide(2,2,0.01,0.01)
c21=TCanvas("c21", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c22=TCanvas("c22", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c23=TCanvas("c23", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c24=TCanvas("c24", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 


for i in range(0,6):

	# Draw them

	c3.cd(1)
	if i==0: 	ts_correct[i].Draw("")
	else: 	ts_correct[i].Draw("same")

	c3.cd(3)
	if i==0: 		ts_wrong[i].Draw("HIST")
	else: 		ts_wrong[i].Draw("HIST:same")


	c3.cd(2)
	if i==0: 	ts_correctmass[i].Draw("")
	else: 	ts_correctmass[i].Draw("same")

	leg = TLegend(0.25,0.5,0.55,0.9)
	leg.SetHeader("Results for diff. top masses")  ##NEEDS TO BE CHANGED
	if i>=0: leg.AddEntry(ts_correctmass[0],"166v5","l")
	if i>=1: leg.AddEntry(ts_correctmass[1],"169v5","l")
	if i>=2: leg.AddEntry(ts_correctmass[2],"172v5","l")
	if i>=3: leg.AddEntry(ts_correctmass[3],"173v5","l")
	if i>=4: leg.AddEntry(ts_correctmass[4],"175v5","l")
	if i>=5: leg.AddEntry(ts_correctmass[5],"178v5","l")
	leg.SetTextSize(0.02)
	leg.Draw();

	c3.cd(4)
	if i==0: 	ts_wrongmass[i].Draw("HIST")
	else:	ts_wrongmass[i].Draw("HIST:same")

	c21.cd()
	if i==0: 	ts_correct[i].Draw("HIST")
	else: 	ts_correct[i].Draw("HIST:same")
	leg21 = TLegend(0.25,0.5,0.55,0.9)
	leg21.SetHeader("Results for diff. top masses")   ##NEEDS TO BE CHANGED
	if i>=0: leg21.AddEntry(ts_correct[0],"166v5","l")
	if i>=1: leg21.AddEntry(ts_correct[1],"169v5","l")
	if i>=2: leg21.AddEntry(ts_correct[2],"172v5","l")
	if i>=3: leg21.AddEntry(ts_correct[3],"173v5","l")
	if i>=4: leg21.AddEntry(ts_correct[4],"175v5","l")
	if i>=5: leg21.AddEntry(ts_correct[5],"178v5","l")
	leg21.SetTextSize(0.02)
	leg21.Draw();

	c22.cd()
	if i==0: 	ts_wrong[i].Draw("HIST")
	else: 	ts_wrong[i].Draw("HIST:same")
	leg22 = TLegend(0.25,0.5,0.55,0.9)
	leg22.SetHeader("Results for diff. top masses")   ##NEEDS TO BE CHANGED
	if i>=0: leg22.AddEntry(ts_wrong[0],"166v5","l")
	if i>=1: leg22.AddEntry(ts_wrong[1],"169v5","l")
	if i>=2: leg22.AddEntry(ts_wrong[2],"172v5","l")
	if i>=3: leg22.AddEntry(ts_wrong[3],"173v5","l")
	if i>=4: leg22.AddEntry(ts_wrong[4],"175v5","l")
	if i>=5: leg22.AddEntry(ts_wrong[5],"178v5","l")
	leg22.SetTextSize(0.02)
	leg22.Draw();

	c23.cd()
	if i==0: 	ts_correctmass[i].Draw("HIST")
	else: 	ts_correctmass[i].Draw("HIST:same")
	leg23 = TLegend(0.25,0.5,0.55,0.9)
	leg23.SetHeader("Results for diff. top masses")   ##NEEDS TO BE CHANGED
	if i>=0: leg23.AddEntry(ts_correctmass[0],"166v5","l")
	if i>=1: leg23.AddEntry(ts_correctmass[1],"169v5","l")
	if i>=2: leg23.AddEntry(ts_correctmass[2],"172v5","l")
	if i>=3: leg23.AddEntry(ts_correctmass[3],"173v5","l")
	if i>=4: leg23.AddEntry(ts_correctmass[4],"175v5","l")
	if i>=5: leg23.AddEntry(ts_correctmass[5],"178v5","l")
	leg23.SetTextSize(0.02)
	leg23.Draw();

	c24.cd()
	if i==0: 	ts_wrongmass[i].Draw("HIST")
	else: 	ts_wrongmass[i].Draw("HIST:same")
	leg24 = TLegend(0.25,0.5,0.55,0.9)
	leg24.SetHeader("Results for diff. top masses")   ##NEEDS TO BE CHANGED
	if i>=0: leg24.AddEntry(ts_wrongmass[0],"166v5","l")
	if i>=1: leg24.AddEntry(ts_wrongmass[1],"169v5","l")
	if i>=2: leg24.AddEntry(ts_wrongmass[2],"172v5","l")
	if i>=3: leg24.AddEntry(ts_wrongmass[3],"173v5","l")
	if i>=4: leg24.AddEntry(ts_wrongmass[4],"175v5","l")
	if i>=5: leg24.AddEntry(ts_wrongmass[5],"178v5","l")
	leg24.SetTextSize(0.02)
	leg24.Draw();


	# titles
	ts_correct[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE")

	ts_correctmass[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE")

	ts_wrong[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE")

	ts_wrongmass[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) WRONG CHARGE")

ts_correct[0].SetMaximum(2.5)
ts_correctmass[0].SetMaximum(2.5)
ts_wrong[0].SetMaximum(2.5)
ts_wrongmass[0].SetMaximum(2.5)

c3.Update()
c3.Modified()
c21.Update()
c21.Modified()	
c22.Update()
c22.Modified()		
c23.Update()
c23.Modified()
c24.Update()
c24.Modified()		
		
	

# Save the plot and close the files
c3.SaveAs("./../plots/deltar_minmass_4plots_divided_4ntr.pdf")
c21.SaveAs("./../plots/deltar_correct_divided_4ntr.pdf")
c22.SaveAs("./../plots/deltar_wrong_divided_4ntr.pdf")
c23.SaveAs("./../plots/deltar_correctmass_divided_4ntr.pdf")
c24.SaveAs("./../plots/deltar_wrongmass_divided_4ntr.pdf")
