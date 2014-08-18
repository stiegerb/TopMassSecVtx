#!/usr/bin/env python
import ROOT, os, sys
from ROOT import TFile, TCanvas, THStack, TLegend, TH1D, TGraph, TGraphErrors, TF1

## Run by calling in the shell:
## ./macroTemplate.py

# Open a file
path = "/afs/cern.ch/work/j/jklocans/private/CMSSW_5_3_15/src/UserCode/llvv_fwk/lxyplots/"

################

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

ts_correct = []
ts_wrong = []
ts_correctmass = []
ts_wrongmass = []

ts_correct_2ntr = []
ts_wrong_2ntr = []
ts_correctmass_2ntr = []
ts_wrongmass_2ntr = []

ts_correct_3ntr = []
ts_wrong_3ntr = []
ts_correctmass_3ntr = []
ts_wrongmass_3ntr = []

ts_correct_4ntr = []
ts_wrong_4ntr = []
ts_correctmass_4ntr = []
ts_wrongmass_4ntr = []


# Make a new TCanvas
c = TCanvas("canvas", "c", 1000, 1000)
c.Divide(2,2,0.01,0.01)
c11=TCanvas("c11", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c12=TCanvas("c12", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c13=TCanvas("c13", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c14=TCanvas("c14", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 

c_2ntr = TCanvas("canvas_2ntr", "c", 1000, 1000)
c_2ntr.Divide(2,2,0.01,0.01)
c11_2ntr=TCanvas("c11_2ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c12_2ntr=TCanvas("c12_2ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c13_2ntr=TCanvas("c13_2ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c14_2ntr=TCanvas("c14_2ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 

c_3ntr = TCanvas("canvas_3ntr", "c", 1000, 1000)
c_3ntr.Divide(2,2,0.01,0.01)
c11_3ntr=TCanvas("c11_3ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c12_3ntr=TCanvas("c12_3ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c13_3ntr=TCanvas("c13_3ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c14_3ntr=TCanvas("c14_3ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 

c_4ntr = TCanvas("canvas_4ntr", "c", 1000, 1000)
c_4ntr.Divide(2,2,0.01,0.01)
c11_4ntr=TCanvas("c11_4ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c12_4ntr=TCanvas("c12_4ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c13_4ntr=TCanvas("c13_4ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c14_4ntr=TCanvas("c14_4ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 

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

	ts_correct.append(TH1D("emu_deltar_correct_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrong.append(TH1D("emu_deltar_wrong_" + x,"test stacked histograms", 50, 0., 150.))
	ts_correctmass.append(TH1D("emu_minmass_correct_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrongmass.append(TH1D("emu_minmass_wrong_" + x,"test stackhsed histograms", 50, 0., 150.))

	ts_correct_2ntr.append(TH1D("emu2tk_deltar_correct_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrong_2ntr.append(TH1D("emu2tk_deltar_wrong_" + x,"test stacked histograms", 50, 0., 150.))
	ts_correctmass_2ntr.append(TH1D("emu2tk_minmass_correct_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_2ntr.append(TH1D("emu2tk_minmass_wrong_" + x,"test stackhsed histograms", 50, 0., 150.))

	ts_correct_3ntr.append(TH1D("emu3tk_deltar_correct_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrong_3ntr.append(TH1D("emu3tk_deltar_wrong_" + x,"test stacked histograms", 50, 0., 150.))
	ts_correctmass_3ntr.append(TH1D("emu3tk_minmass_correct_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_3ntr.append(TH1D("emu3tk_minmass_wrong_" + x,"test stackhsed histograms", 50, 0., 150.))

	ts_correct_4ntr.append(TH1D("emu4tk_deltar_correct_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrong_4ntr.append(TH1D("emu4tk_deltar_wrong_" + x,"test stacked histograms", 50, 0., 150.))
	ts_correctmass_4ntr.append(TH1D("emu4tk_minmass_correct_" + x,"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_4ntr.append(TH1D("emu4tk_minmass_wrong_" + x,"test stackhsed histograms", 50, 0., 150.))




# Open the files -> adds all samples together
for i in range(0,6):
	ts_correct[i].Sumw2()
	ts_wrong[i].Sumw2()
	ts_correct[i].Sumw2()
	ts_wrongmass[i].Sumw2()

	ts_correct_2ntr[i].Sumw2()
	ts_wrong_2ntr[i].Sumw2()
	ts_correct_2ntr[i].Sumw2()
	ts_wrongmass_2ntr[i].Sumw2()

	ts_correct_3ntr[i].Sumw2()
	ts_wrong_3ntr[i].Sumw2()
	ts_correct_3ntr[i].Sumw2()
	ts_wrongmass_3ntr[i].Sumw2()

	ts_correct_4ntr[i].Sumw2()
	ts_wrong_4ntr[i].Sumw2()
	ts_correct_4ntr[i].Sumw2()
	ts_wrongmass_4ntr[i].Sumw2()

	rootfile1 = []

	for x in listoffiles[i]:
	#inv.m. l + sv
		rootfile1.append(TFile.Open("./../lxyplots/" + x, "READ"))

	#deltar
	histo_correct = []
	histo_wrong = []
	histo_correctmass = []
	histo_wrongmass = []

	histo_correct_2ntr = []
	histo_wrong_2ntr = []
	histo_correctmass_2ntr = []
	histo_wrongmass_2ntr = []

	histo_correct_3ntr = []
	histo_wrong_3ntr = []
	histo_correctmass_3ntr = []
	histo_wrongmass_3ntr = []

	histo_correct_4ntr = []
	histo_wrong_4ntr = []
	histo_correctmass_4ntr = []
	histo_wrongmass_4ntr = []

	for x in range(0,len(listoffiles[i])):

		histo_correct.append(rootfile1[x].Get("mlsv_emu_deltar_cut_correct"))
		histo_wrong.append(rootfile1[x].Get("mlsv_emu_deltar_cut_wrong"))
		histo_correctmass.append(rootfile1[x].Get("mlsv_emu_minmass_correct"))
		histo_wrongmass.append(rootfile1[x].Get("mlsv_emu_minmass_wrong"))

		histo_correct_2ntr.append(rootfile1[x].Get("mlsv_emu_deltar_cut_ntr2_correct"))
		histo_wrong_2ntr.append(rootfile1[x].Get("mlsv_emu_deltar_cut_ntr2_wrong"))
		histo_correctmass_2ntr.append(rootfile1[x].Get("mlsv_emu_minmass_ntr2_correct"))
		histo_wrongmass_2ntr.append(rootfile1[x].Get("mlsv_emu_minmass_ntr2_wrong"))

		histo_correct_3ntr.append(rootfile1[x].Get("mlsv_emu_deltar_cut_ntr3_correct"))
		histo_wrong_3ntr.append(rootfile1[x].Get("mlsv_emu_deltar_cut_ntr3_wrong"))
		histo_correctmass_3ntr.append(rootfile1[x].Get("mlsv_emu_minmass_ntr3_correct"))
		histo_wrongmass_3ntr.append(rootfile1[x].Get("mlsv_emu_minmass_ntr3_wrong"))

		histo_correct_4ntr.append(rootfile1[x].Get("mlsv_emu_deltar_cut_ntr4_correct"))
		histo_wrong_4ntr.append(rootfile1[x].Get("mlsv_emu_deltar_cut_ntr4_wrong"))
		histo_correctmass_4ntr.append(rootfile1[x].Get("mlsv_emu_minmass_ntr4_correct"))
		histo_wrongmass_4ntr.append(rootfile1[x].Get("mlsv_emu_minmass_ntr4_wrong"))

		histo_correct[x].Sumw2()
		histo_wrong[x].Sumw2()
		histo_correctmass[x].Sumw2()
		histo_wrongmass[x].Sumw2()

		histo_correct_2ntr[x].Sumw2()
		histo_wrong_2ntr[x].Sumw2()
		histo_correctmass_2ntr[x].Sumw2()
		histo_wrongmass_2ntr[x].Sumw2()

		histo_correct_3ntr[x].Sumw2()
		histo_wrong_3ntr[x].Sumw2()
		histo_correctmass_3ntr[x].Sumw2()
		histo_wrongmass_3ntr[x].Sumw2()

		histo_correct_4ntr[x].Sumw2()
		histo_wrong_4ntr[x].Sumw2()
		histo_correctmass_4ntr[x].Sumw2()
		histo_wrongmass_4ntr[x].Sumw2()

		#adding histos

		ts_correct[i].Add(histo_correct[x])
		ts_wrong[i].Add(histo_wrong[x])
		ts_correctmass[i].Add(histo_correctmass[x])
		ts_wrongmass[i].Add(histo_wrongmass[x])


		ts_correct_2ntr[i].Add(histo_correct_2ntr[x])
		ts_wrong_2ntr[i].Add(histo_wrong_2ntr[x])
		ts_correctmass_2ntr[i].Add(histo_correctmass_2ntr[x])
		ts_wrongmass_2ntr[i].Add(histo_wrongmass_2ntr[x])

		ts_correct_3ntr[i].Add(histo_correct_3ntr[x])
		ts_wrong_3ntr[i].Add(histo_wrong_3ntr[x])
		ts_correctmass_3ntr[i].Add(histo_correctmass_3ntr[x])
		ts_wrongmass_3ntr[i].Add(histo_wrongmass_3ntr[x])

		ts_correct_4ntr[i].Add(histo_correct_4ntr[x])
		ts_wrong_4ntr[i].Add(histo_wrong_4ntr[x])
		ts_correctmass_4ntr[i].Add(histo_correctmass_4ntr[x])
		ts_wrongmass_4ntr[i].Add(histo_wrongmass_4ntr[x])

	#normalization

	ts_correct[i].Scale(1/ts_correct[i].Integral())
	ts_correctmass[i].Scale(1/ts_correctmass[i].Integral())
	ts_wrong[i].Scale(1/ts_wrong[i].Integral())
	ts_wrongmass[i].Scale(1/ts_wrongmass[i].Integral())

	ts_correct_2ntr[i].Scale(1/ts_correct_2ntr[i].Integral())
	ts_correctmass_2ntr[i].Scale(1/ts_correctmass_2ntr[i].Integral())
	ts_wrong_2ntr[i].Scale(1/ts_wrong_2ntr[i].Integral())
	ts_wrongmass_2ntr[i].Scale(1/ts_wrongmass_2ntr[i].Integral())

	ts_correct_3ntr[i].Scale(1/ts_correct_3ntr[i].Integral())
	ts_correctmass_3ntr[i].Scale(1/ts_correctmass_3ntr[i].Integral())
	ts_wrong_3ntr[i].Scale(1/ts_wrong_3ntr[i].Integral())
	ts_wrongmass_3ntr[i].Scale(1/ts_wrongmass_3ntr[i].Integral())

	ts_correct_4ntr[i].Scale(1/ts_correct_4ntr[i].Integral())
	ts_correctmass_4ntr[i].Scale(1/ts_correctmass_4ntr[i].Integral())
	ts_wrong_4ntr[i].Scale(1/ts_wrong_4ntr[i].Integral())
	ts_wrongmass_4ntr[i].Scale(1/ts_wrongmass_4ntr[i].Integral())

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

	ts_correct_2ntr[i].SetLineColor(51 + 9*i)
	ts_wrong_2ntr[i].SetLineColor(51 + 9*i)
	ts_correctmass_2ntr[i].SetLineColor(51 + 9*i)
	ts_wrongmass_2ntr[i].SetLineColor(51 + 9*i)

	ts_correct_2ntr[i].SetMarkerColor(51 + 9*i)
	ts_wrong_2ntr[i].SetMarkerColor(51 + 9*i)
	ts_correctmass_2ntr[i].SetMarkerColor(51 + 9*i)
	ts_wrongmass_2ntr[i].SetMarkerColor(51 + 9*i)

	ts_correct_3ntr[i].SetLineColor(51 + 9*i)
	ts_wrong_3ntr[i].SetLineColor(51 + 9*i)
	ts_correctmass_3ntr[i].SetLineColor(51 + 9*i)
	ts_wrongmass_3ntr[i].SetLineColor(51 + 9*i)

	ts_correct_3ntr[i].SetMarkerColor(51 + 9*i)
	ts_wrong_3ntr[i].SetMarkerColor(51 + 9*i)
	ts_correctmass_3ntr[i].SetMarkerColor(51 + 9*i)
	ts_wrongmass_3ntr[i].SetMarkerColor(51 + 9*i)

	ts_correct_4ntr[i].SetLineColor(51 + 9*i)
	ts_wrong_4ntr[i].SetLineColor(51 + 9*i)
	ts_correctmass_4ntr[i].SetLineColor(51 + 9*i)
	ts_wrongmass_4ntr[i].SetLineColor(51 + 9*i)

	ts_correct_4ntr[i].SetMarkerColor(51 + 9*i)
	ts_wrong_4ntr[i].SetMarkerColor(51 + 9*i)
	ts_correctmass_4ntr[i].SetMarkerColor(51 + 9*i)
	ts_wrongmass_4ntr[i].SetMarkerColor(51 + 9*i)

	ts_correct[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correct[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrong[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrong[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_correctmass[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correctmass[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrongmass[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrongmass[i].GetYaxis().SetTitle("number of events (normalized by area)")

	ts_correct_2ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correct_2ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrong_2ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrong_2ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_correctmass_2ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correctmass_2ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrongmass_2ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrongmass_2ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")

	ts_correct_3ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correct_3ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrong_3ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrong_3ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_correctmass_3ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correctmass_3ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrongmass_3ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrongmass_3ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")

	ts_correct_4ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correct_4ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrong_4ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrong_4ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_correctmass_4ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_correctmass_4ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")
	ts_wrongmass_4ntr[i].GetXaxis().SetTitle("inv.M(GeV)")
	ts_wrongmass_4ntr[i].GetYaxis().SetTitle("number of events (normalized by area)")

	# Draw them

	ts_correct[i].SetTitleSize(3)
	ts_correct[i].GetXaxis().SetLabelSize(0.05)
	ts_correct[i].GetYaxis().SetLabelSize(0.05)
	ts_correct[i].GetXaxis().SetTitleSize(0.07)
	ts_correct[i].GetYaxis().SetTitleSize(0.07)
	ts_correct[i].GetXaxis().SetTitleOffset(1.5)
	ts_correct[i].GetYaxis().SetTitleOffset(1.5)

	ts_wrong[i].SetTitleSize(3)
	ts_wrong[i].GetXaxis().SetLabelSize(0.05)
	ts_wrong[i].GetYaxis().SetLabelSize(0.05)
	ts_wrong[i].GetXaxis().SetTitleSize(0.07)
	ts_wrong[i].GetYaxis().SetTitleSize(0.07)
	ts_wrong[i].GetXaxis().SetTitleOffset(1.5)
	ts_wrong[i].GetYaxis().SetTitleOffset(1.5)

	ts_correctmass[i].SetTitleSize(3)
	ts_correctmass[i].GetXaxis().SetLabelSize(0.05)
	ts_correctmass[i].GetYaxis().SetLabelSize(0.05)
	ts_correctmass[i].GetXaxis().SetTitleSize(0.07)
	ts_correctmass[i].GetYaxis().SetTitleSize(0.07)
	ts_correctmass[i].GetXaxis().SetTitleOffset(1.5)
	ts_correctmass[i].GetYaxis().SetTitleOffset(1.5)


	ts_wrongmass[i].SetTitleSize(3)
	ts_wrongmass[i].GetXaxis().SetLabelSize(0.05)
	ts_wrongmass[i].GetYaxis().SetLabelSize(0.05)
	ts_wrongmass[i].GetXaxis().SetTitleSize(0.07)
	ts_wrongmass[i].GetYaxis().SetTitleSize(0.07)
	ts_wrongmass[i].GetXaxis().SetTitleOffset(1.5)
	ts_wrongmass[i].GetYaxis().SetTitleOffset(1.5)


	if i >=5:

		leg.SetHeader("Top mass")   ##NEEDS TO BE CHANGED
		leg.AddEntry(ts_correctmass[0],"166v5","l",)
		leg.AddEntry(ts_correctmass[1],"169v5","l")
		leg.AddEntry(ts_correctmass[2],"172v5","l")
		leg.AddEntry(ts_correctmass[3],"173v5","l")
		leg.AddEntry(ts_correctmass[4],"175v5","l")
		leg.AddEntry(ts_correctmass[5],"178v5","l")
		leg.SetTextSize(0.04)

	c.cd(1)
	if i==0: 	ts_correct[i].Draw("")
	else: 	ts_correct[i].Draw("same")

	c.cd(3)
	if i==0: 		ts_wrong[i].Draw("")
	else: 		ts_wrong[i].Draw("same")


	c.cd(2)
	if i==0: 	ts_correctmass[i].Draw("")
	else: 	ts_correctmass[i].Draw("same")
	leg.Draw()

	c.cd(4)
	if i==0: 	ts_wrongmass[i].Draw("")
	else:	ts_wrongmass[i].Draw("same")

	c11.cd()
	if i==0: 	ts_correct[i].Draw("")
	else:	ts_correct[i].Draw("same")
	leg.Draw()

	c12.cd()
	if i==0: 	ts_wrong[i].Draw("")
	else:	ts_wrong[i].Draw("same")
	leg.Draw()

	c13.cd()
	if i==0: 	ts_correctmass[i].Draw("")
	else:	ts_correctmass[i].Draw("same")
	leg.Draw()

	c14.cd()
	if i==0: 	ts_wrongmass[i].Draw("")
	else:	ts_wrongmass[i].Draw("same")
	leg.Draw()


	#2 trcks

	c_2ntr.cd(1)
	if i==0: 	ts_correct_2ntr[i].Draw("")
	else: 	ts_correct_2ntr[i].Draw("same")

	c_2ntr.cd(3)
	if i==0: 		ts_wrong_2ntr[i].Draw("")
	else: 		ts_wrong_2ntr[i].Draw("same")


	c_2ntr.cd(2)
	if i==0: 	ts_correctmass_2ntr[i].Draw("")
	else: 	ts_correctmass_2ntr[i].Draw("same")
	leg.Draw()

	c_2ntr.cd(4)
	if i==0: 	ts_wrongmass_2ntr[i].Draw("")
	else:	ts_wrongmass_2ntr[i].Draw("same")

	c11_2ntr.cd()
	if i==0: 	ts_correct_2ntr[i].Draw("")
	else:	ts_correct_2ntr[i].Draw("same")
	leg.Draw()

	c12_2ntr.cd()
	if i==0: 	ts_wrong_2ntr[i].Draw("")
	else:	ts_wrong_2ntr[i].Draw("same")
	leg.Draw()

	c13_2ntr.cd()
	if i==0: 	ts_correctmass_2ntr[i].Draw("")
	else:	ts_correctmass_2ntr[i].Draw("same")
	leg.Draw()

	c14_2ntr.cd()
	if i==0: 	ts_wrongmass_2ntr[i].Draw("")
	else:	ts_wrongmass_2ntr[i].Draw("same")
	leg.Draw()

	# 3 tracks

	c_3ntr.cd(1)
	if i==0: 	ts_correct_3ntr[i].Draw("")
	else: 	ts_correct_3ntr[i].Draw("same")

	c_3ntr.cd(3)
	if i==0: 		ts_wrong_3ntr[i].Draw("")
	else: 		ts_wrong_3ntr[i].Draw("same")


	c_3ntr.cd(2)
	if i==0: 	ts_correctmass_3ntr[i].Draw("")
	else: 	ts_correctmass_3ntr[i].Draw("same")
	leg.Draw()

	c_3ntr.cd(4)
	if i==0: 	ts_wrongmass_3ntr[i].Draw("")
	else:	ts_wrongmass_3ntr[i].Draw("same")

	c11_3ntr.cd()
	if i==0: 	ts_correct_3ntr[i].Draw("")
	else:	ts_correct_3ntr[i].Draw("same")
	leg.Draw()

	c12_3ntr.cd()
	if i==0: 	ts_wrong_3ntr[i].Draw("")
	else:	ts_wrong_3ntr[i].Draw("same")
	leg.Draw()

	c13_3ntr.cd()
	if i==0: 	ts_correctmass_3ntr[i].Draw("")
	else:	ts_correctmass_3ntr[i].Draw("same")
	leg.Draw()

	c14_3ntr.cd()
	if i==0: 	ts_wrongmass_3ntr[i].Draw("")
	else:	ts_wrongmass_3ntr[i].Draw("same")
	leg.Draw()

	# 4 and more tracks

	#2 trcks

	c_4ntr.cd(1)
	if i==0: 	ts_correct_4ntr[i].Draw("")
	else: 	ts_correct_4ntr[i].Draw("same")

	c_4ntr.cd(3)
	if i==0: 		ts_wrong_4ntr[i].Draw("")
	else: 		ts_wrong_4ntr[i].Draw("same")


	c_4ntr.cd(2)
	if i==0: 	ts_correctmass_4ntr[i].Draw("")
	else: 	ts_correctmass_4ntr[i].Draw("same")
	leg.Draw()

	c_4ntr.cd(4)
	if i==0: 	ts_wrongmass_4ntr[i].Draw("")
	else:	ts_wrongmass_4ntr[i].Draw("same")

	c11_4ntr.cd()
	if i==0: 	ts_correct_4ntr[i].Draw("")
	else:	ts_correct_4ntr[i].Draw("same")
	leg.Draw()

	c12_4ntr.cd()
	if i==0: 	ts_wrong_4ntr[i].Draw("")
	else:	ts_wrong_4ntr[i].Draw("same")
	leg.Draw()

	c13_4ntr.cd()
	if i==0: 	ts_correctmass_4ntr[i].Draw("")
	else:	ts_correctmass_4ntr[i].Draw("same")
	leg.Draw()

	c14_4ntr.cd()
	if i==0: 	ts_wrongmass_4ntr[i].Draw("")
	else:	ts_wrongmass_4ntr[i].Draw("same")
	leg.Draw()

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
	c.Update()
	c11.Update()
	c12.Update()
	c13.Update()
	c14.Update()

	ts_correct_2ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE (2 tracks)")

	ts_correctmass_2ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE (2 tracks)")

	ts_wrong_2ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE (2 tracks)")

	ts_wrongmass_2ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) WRONG CHARGE (2 tracks)")

	c_2ntr.Modified()
	c11_2ntr.Modified()
	c12_2ntr.Modified()
	c13_2ntr.Modified()
	c14_2ntr.Modified()
	c_2ntr.Update()
	c11_2ntr.Update()
	c12_2ntr.Update()
	c13_2ntr.Update()
	c14_2ntr.Update()

	ts_correct_3ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE (3 tracks)")

	ts_correctmass_3ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE (3 tracks)")

	ts_wrong_3ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE (3 tracks)")

	ts_wrongmass_3ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) WRONG CHARGE (3 tracks)")

	c_3ntr.Modified()
	c11_3ntr.Modified()
	c12_3ntr.Modified()
	c13_3ntr.Modified()
	c14_3ntr.Modified()
	c_3ntr.Update()
	c11_3ntr.Update()
	c12_3ntr.Update()
	c13_3ntr.Update()
	c14_3ntr.Update()

	ts_correct_4ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE (4 and more tracks)")

	ts_correctmass_4ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE (4 and more tracks)")

	ts_wrong_4ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE (4 and more tracks)")

	ts_wrongmass_4ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) WRONG CHARGE (4 and more tracks)")

	c_4ntr.Modified()
	c11_4ntr.Modified()
	c12_4ntr.Modified()
	c13_4ntr.Modified()
	c14_4ntr.Modified()
	c_4ntr.Update()
	c11_4ntr.Update()
	c12_4ntr.Update()
	c13_4ntr.Update()
	c14_4ntr.Update()

	c.Modified()
	c11.Modified()
	c12.Modified()
	c13.Modified()
	c14.Modified()
	c.Update()
	c11.Update()
	c12.Update()
	c13.Update()
	c14.Update()

	del histo_correct
	del histo_wrong 
	del histo_correctmass
	del histo_wrongmass

	del histo_correct_2ntr
	del histo_wrong_2ntr
	del histo_correctmass_2ntr
	del histo_wrongmass_2ntr

	del histo_correct_3ntr
	del histo_wrong_3ntr
	del histo_correctmass_3ntr
	del histo_wrongmass_3ntr

	del histo_correct_4ntr
	del histo_wrong_4ntr
	del histo_correctmass_4ntr
	del histo_wrongmass_4ntr

	del rootfile1

	print listofnames[i]
	print "emu_deltar"
	print ts_correct[i].GetEntries() + ts_wrong[i].GetEntries()
	print ""

	print "emu2tk_deltar"
	print ts_correct_2ntr[i].GetEntries() + ts_wrong_2ntr[i].GetEntries()
	print ""

	print "emu3tk_deltar"
	print ts_correct_3ntr[i].GetEntries() + ts_wrong_3ntr[i].GetEntries()
	print ""

	print "emu4tk_deltar"
	print ts_correct_4ntr[i].GetEntries() + ts_wrong_4ntr[i].GetEntries()
	print ""
	print ""

	print "emu_minmass"
	print ts_correctmass[i].GetEntries() + ts_wrongmass[i].GetEntries()
	print ""

	print "emu2tk_minmass"
	print ts_correctmass_2ntr[i].GetEntries() + ts_wrongmass_2ntr[i].GetEntries()
	print ""

	print "emu3tk_minmass"
	print ts_correctmass_3ntr[i].GetEntries() + ts_wrongmass_3ntr[i].GetEntries()
	print ""

	print "emu4tk_minmass"
	print ts_correctmass_4ntr[i].GetEntries() + ts_wrongmass_4ntr[i].GetEntries()
	print ""








# Save the plot and close the files
c.SaveAs("./../plots/deltar_minmass_4plots.pdf")
c11.SaveAs("./../plots/deltar_correct.pdf")
c12.SaveAs("./../plots/deltar_wrong.pdf")
c13.SaveAs("./../plots/deltar_correctmass.pdf")
c14.SaveAs("./../plots/deltar_wrongmass.pdf")

c_2ntr.SaveAs("./../plots/deltar_minmass_4plots_2ntr.pdf")
c11_2ntr.SaveAs("./../plots/deltar_correct_2ntr.pdf")
c12_2ntr.SaveAs("./../plots/deltar_wrong_2ntr.pdf")
c13_2ntr.SaveAs("./../plots/deltar_correctmass_2ntr.pdf")
c14_2ntr.SaveAs("./../plots/deltar_wrongmass_2ntr.pdf")

c_3ntr.SaveAs("./../plots/deltar_minmass_4plots_3ntr.pdf")
c11_3ntr.SaveAs("./../plots/deltar_correct_3ntr.pdf")
c12_3ntr.SaveAs("./../plots/deltar_wrong_3ntr.pdf")
c13_3ntr.SaveAs("./../plots/deltar_correctmass_3ntr.pdf")
c14_3ntr.SaveAs("./../plots/deltar_wrongmass_3ntr.pdf")

c_4ntr.SaveAs("./../plots/deltar_minmass_4plots_4ntr.pdf")
c11_4ntr.SaveAs("./../plots/deltar_correct_4ntr.pdf")
c12_4ntr.SaveAs("./../plots/deltar_wrong_4ntr.pdf")
c13_4ntr.SaveAs("./../plots/deltar_correctmass_4ntr.pdf")
c14_4ntr.SaveAs("./../plots/deltar_wrongmass_4ntr.pdf")

#to save all samples together

#rootfile2 = []
#rootfile2.append((TFile("../newsamples/jevgeny_samples_total.root", "RECREATE")))
#for i in range(0,6):
#	ts_correct[i].Write()
#	ts_wrong[i].Write()
#	ts_correctmass[i].Write()
#	ts_wrongmass[i].Write()
#	ts_correct_2ntr[i].Write()
#	ts_wrong_2ntr[i].Write()
#	ts_correctmass_2ntr[i].Write()
#	ts_wrongmass_2ntr[i].Write()
#	ts_correct_3ntr[i].Write()
#	ts_wrong_3ntr[i].Write()
#	ts_correctmass_3ntr[i].Write()
#	ts_wrongmass_3ntr[i].Write()
#	ts_correct_4ntr[i].Write()
#	ts_wrong_4ntr[i].Write()
#	ts_correctmass_4ntr[i].Write()
#	ts_wrongmass_4ntr[i].Write()

#rootfile2[0].Close()

# this part for different plot

c2=TCanvas("c2", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c2_2ntr=TCanvas("c2_2ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c2_3ntr=TCanvas("c2_3ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c2_4ntr=TCanvas("c2_4ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 

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

graph1_2ntr = TGraphErrors(6)
graph2_2ntr = TGraphErrors(6)
graph1err_2ntr = TGraphErrors(6)
graph2err_2ntr = TGraphErrors(6)

graph1_3ntr = TGraphErrors(6)
graph2_3ntr = TGraphErrors(6)
graph1err_3ntr = TGraphErrors(6)
graph2err_3ntr = TGraphErrors(6)

graph1_4ntr = TGraphErrors(6)
graph2_4ntr = TGraphErrors(6)
graph1err_4ntr = TGraphErrors(6)
graph2err_4ntr = TGraphErrors(6)

y = [0.]*6 
z = [0.]*6
yerr = [0.]*6
zerr = [0.]*6

y_2ntr = [0.]*6 
z_2ntr = [0.]*6
yerr_2ntr = [0.]*6
zerr_2ntr = [0.]*6

y_3ntr = [0.]*6 
z_3ntr = [0.]*6
yerr_3ntr = [0.]*6
zerr_3ntr = [0.]*6

y_4ntr = [0.]*6 
z_4ntr = [0.]*6
yerr_4ntr = [0.]*6
zerr_4ntr = [0.]*6

for i in range(0,6):
	y[i]=ts_correct[i].GetMean()
	z[i]=ts_correctmass[i].GetMean()
	yerr[i] = ts_correct[i].GetMeanError()
	zerr[i] = ts_correctmass[i].GetMeanError()
	graph1.SetPoint(i, x[i], y[i])	
	graph2.SetPoint(i, x[i], z[i])
	graph1.SetPointError(i, 0, yerr[i])	
	graph2.SetPointError(i, 0, zerr[i])

	y_2ntr[i]=ts_correct_2ntr[i].GetMean()
	z_2ntr[i]=ts_correctmass_2ntr[i].GetMean()
	yerr_2ntr[i] = ts_correct_2ntr[i].GetMeanError()
	zerr_2ntr[i] = ts_correctmass_2ntr[i].GetMeanError()
	graph1_2ntr.SetPoint(i, x[i], y_2ntr[i])	
	graph2_2ntr.SetPoint(i, x[i], z_2ntr[i])
	graph1_2ntr.SetPointError(i, 0, yerr_2ntr[i])	
	graph2_2ntr.SetPointError(i, 0, zerr_2ntr[i])

	y_3ntr[i]=ts_correct_3ntr[i].GetMean()
	z_3ntr[i]=ts_correctmass_3ntr[i].GetMean()
	yerr_3ntr[i] = ts_correct_3ntr[i].GetMeanError()
	zerr_3ntr[i] = ts_correctmass_3ntr[i].GetMeanError()
	graph1_3ntr.SetPoint(i, x[i], y_3ntr[i])	
	graph2_3ntr.SetPoint(i, x[i], z_3ntr[i])
	graph1_3ntr.SetPointError(i, 0, yerr_3ntr[i])	
	graph2_3ntr.SetPointError(i, 0, zerr_3ntr[i])

	y_4ntr[i]=ts_correct_4ntr[i].GetMean()
	z_4ntr[i]=ts_correctmass_4ntr[i].GetMean()
	yerr_4ntr[i] = ts_correct_4ntr[i].GetMeanError()
	zerr_4ntr[i] = ts_correctmass_4ntr[i].GetMeanError()
	graph1_4ntr.SetPoint(i, x[i], y_4ntr[i])	
	graph2_4ntr.SetPoint(i, x[i], z_4ntr[i])
	graph1_4ntr.SetPointError(i, 0, yerr_4ntr[i])	
	graph2_4ntr.SetPointError(i, 0, zerr_4ntr[i])

c2.cd()
graph1.Draw("AP")
graph1.GetYaxis().SetRangeUser(52.,62.)
graph1.GetYaxis().SetTitle("Mean value")
graph1.GetXaxis().SetTitle("Top M(GeV)")
graph1.Draw("AP")
graph1.SetTitle("Mean value of the inv.mass vs top mass")
graph2.SetLineColor(2)
graph2.SetMarkerColor(2)
graph2.Draw("P")

c2_2ntr.cd()
graph1_2ntr.Draw("AP")
graph1_2ntr.GetYaxis().SetRangeUser(43.,53.)
graph1_2ntr.GetYaxis().SetTitle("Mean value")
graph1_2ntr.GetXaxis().SetTitle("Top M(GeV)")
graph1_2ntr.Draw("AP")
graph1_2ntr.SetTitle("Mean value of the inv.mass vs top mass")
graph2_2ntr.SetLineColor(2)
graph2_2ntr.SetMarkerColor(2)
graph2_2ntr.Draw("P")

c2_3ntr.cd()
graph1_3ntr.Draw("AP")
graph1_3ntr.GetYaxis().SetRangeUser(51.,61.)
graph1_3ntr.GetYaxis().SetTitle("Mean value")
graph1_3ntr.GetXaxis().SetTitle("Top M(GeV)")
graph1_3ntr.Draw("AP")
graph1_3ntr.SetTitle("Mean value of the inv.mass vs top mass")
graph2_3ntr.SetLineColor(2)
graph2_3ntr.SetMarkerColor(2)
graph2_3ntr.Draw("P")

c2_4ntr.cd()
graph1_4ntr.Draw("AP")
graph1_4ntr.GetYaxis().SetRangeUser(59.,69.)
graph1_4ntr.GetYaxis().SetTitle("Mean value")
graph1_4ntr.GetXaxis().SetTitle("Top M(GeV)")
graph1_4ntr.Draw("AP")
graph1_4ntr.SetTitle("Mean value of the inv.mass vs top mass")
graph2_4ntr.SetLineColor(2)
graph2_4ntr.SetMarkerColor(2)
graph2_4ntr.Draw("P")

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

c2.cd()
leg2 = TLegend(0.7,0.15,1,0.25)
leg2.SetHeader("Fits:")  ##NEEDS TO BE CHANGED
leg2.AddEntry(pol1, "deltar: y = " + a0 + " + " + a1 + "x", "ll")
leg2.AddEntry(pol2, "minmass: y = " + b0 + " + " + b1 + "x", "ll")
leg2.Draw()

graph1_2ntr.Fit("pol1")
graph2_2ntr.Fit("pol1")

pol1_2ntr=TF1()
pol1_2ntr=graph1_2ntr.GetFunction("pol1")
pol2_2ntr=TF1()
pol2_2ntr=graph2_2ntr.GetFunction("pol1")

a0_2ntr=str(round(pol1_2ntr.GetParameter(0),2))
a1_2ntr=str(round(pol1_2ntr.GetParameter(1),2))
b0_2ntr=str(round(pol2_2ntr.GetParameter(0),2))
b1_2ntr=str(round(pol2_2ntr.GetParameter(1),2))

c2_2ntr.cd()
leg22 = TLegend(0.7,0.15,1,0.25)
leg22.SetHeader("Fits:")  ##NEEDS TO BE CHANGED
leg22.AddEntry(pol1_2ntr, "deltar: y = " + a0_2ntr + " + " + a1_2ntr + "x", "ll")
leg22.AddEntry(pol2_2ntr, "minmass: y = " + b0_2ntr + " + " + b1_2ntr + "x", "ll")
leg22.Draw()

graph1_3ntr.Fit("pol1")
graph2_3ntr.Fit("pol1")

pol1_3ntr=TF1()
pol1_3ntr=graph1_3ntr.GetFunction("pol1")
pol2_3ntr=TF1()
pol2_3ntr=graph2_3ntr.GetFunction("pol1")

a0_3ntr=str(round(pol1_3ntr.GetParameter(0),2))
a1_3ntr=str(round(pol1_3ntr.GetParameter(1),2))
b0_3ntr=str(round(pol2_3ntr.GetParameter(0),2))
b1_3ntr=str(round(pol2_3ntr.GetParameter(1),2))

c2_3ntr.cd()
leg23 = TLegend(0.7,0.15,1,0.25)
leg23.SetHeader("Fits:")  ##NEEDS TO BE CHANGED
leg23.AddEntry(pol1_3ntr, "deltar: y = " + a0_3ntr + " + " + a1_3ntr + "x", "ll")
leg23.AddEntry(pol2_3ntr, "minmass: y = " + b0_3ntr + " + " + b1_3ntr + "x", "ll")
leg23.Draw()

graph1_4ntr.Fit("pol1")
graph2_4ntr.Fit("pol1")

pol1_4ntr=TF1()
pol1_4ntr=graph1_4ntr.GetFunction("pol1")
pol2_4ntr=TF1()
pol2_4ntr=graph2_4ntr.GetFunction("pol1")

a0_4ntr=str(round(pol1_4ntr.GetParameter(0),2))
a1_4ntr=str(round(pol1_4ntr.GetParameter(1),2))
b0_4ntr=str(round(pol2_4ntr.GetParameter(0),2))
b1_4ntr=str(round(pol2_4ntr.GetParameter(1),2))

c2_4ntr.cd()
leg24 = TLegend(0.7,0.15,1,0.25)
leg24.SetHeader("Fits:")  ##NEEDS TO BE CHANGED
leg24.AddEntry(pol1_4ntr, "deltar: y = " + a0_4ntr + " + " + a1_4ntr + "x", "ll")
leg24.AddEntry(pol2_4ntr, "minmass: y = " + b0_4ntr + " + " + b1_4ntr + "x", "ll")
leg24.Draw()

pol1.SetLineColor(1)
pol2.SetLineColor(15)
pol1_2ntr.SetLineColor(2)
pol2_2ntr.SetLineColor(46)
pol1_3ntr.SetLineColor(3)
pol2_3ntr.SetLineColor(8)
pol1_4ntr.SetLineColor(4)
pol2_4ntr.SetLineColor(38)

graph1err.SetLineColor(1)
graph2err.SetLineColor(15)
graph1err_2ntr.SetLineColor(2)
graph2err_2ntr.SetLineColor(46)
graph1err_3ntr.SetLineColor(3)
graph2err_3ntr.SetLineColor(8)
graph1err_4ntr.SetLineColor(4)
graph2err_4ntr.SetLineColor(38)

graph1.SetMarkerColor(1)
graph2.SetMarkerColor(15)
graph1_2ntr.SetMarkerColor(2)
graph2_2ntr.SetMarkerColor(46)
graph1_3ntr.SetMarkerColor(3)
graph2_3ntr.SetMarkerColor(8)
graph1_4ntr.SetMarkerColor(4)
graph2_4ntr.SetMarkerColor(38)

graph1.SetLineColor(1)
graph2.SetLineColor(15)
graph1_2ntr.SetLineColor(2)
graph2_2ntr.SetLineColor(46)
graph1_3ntr.SetLineColor(3)
graph2_3ntr.SetLineColor(8)
graph1_4ntr.SetLineColor(4)
graph2_4ntr.SetLineColor(38)

graph1err.SetMarkerColor(1)
graph2err.SetMarkerColor(15)
graph1err_2ntr.SetMarkerColor(2)
graph2err_2ntr.SetMarkerColor(46)
graph1err_3ntr.SetMarkerColor(3)
graph2err_3ntr.SetMarkerColor(8)
graph1err_4ntr.SetMarkerColor(4)
graph2err_4ntr.SetMarkerColor(38)



# Save the plot and close the files
c2.SaveAs("./../plots/deltar_minmass_2plots.pdf")
c2_2ntr.SaveAs("./../plots/deltar_minmass_2plots_2ntr.pdf")
c2_3ntr.SaveAs("./../plots/deltar_minmass_2plots_3ntr.pdf")
c2_4ntr.SaveAs("./../plots/deltar_minmass_2plots_4ntr.pdf")

c_all_fits=TCanvas("c_all_fits", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c_all_fits.cd()

graph1_2ntr.Draw("AP")
graph1_2ntr.GetYaxis().SetRangeUser(38.,68.)
graph1_2ntr.Draw("AP")
graph2_2ntr.Draw("P")
graph1_3ntr.Draw("P")
graph2_3ntr.Draw("P")
graph1_4ntr.Draw("P")
graph2_4ntr.Draw("P")
graph1.Draw("P")
graph2.Draw("P")

c2.Update()
c2.Modified()
c2_2ntr.Update()
c2_2ntr.Modified()
c2_3ntr.Update()
c2_3ntr.Modified()
c2_4ntr.Update()
c2_4ntr.Modified()

leg_all = TLegend(0.55,0.1,1.0,0.35)
leg_all.SetHeader("Fits for diff. numb. of tr. (bright - deltar/faint - minmass)")   ##NEEDS TO BE CHANGED
leg_all.AddEntry(pol1, "All tracks, deltar: y = " + a0 + " + " + a1 + "x", "l")
leg_all.AddEntry(pol2, "All tracks, minmass: y = " + b0 + " + " + b1 + "x", "l")
leg_all.AddEntry(pol1_2ntr,"2 tracks, deltar: y = " + a0_2ntr + " + " + a1_2ntr + "x", "l")
leg_all.AddEntry(pol2_2ntr,"2 tracks, minmass: y = " + b0_2ntr + " + " + b1_2ntr + "x", "l")
leg_all.AddEntry(pol1_3ntr,"3 tracks, deltar: y = " + a0_3ntr + " + " + a1_3ntr + "x", "l")
leg_all.AddEntry(pol2_3ntr,"3 tracks, minmass: y = " + b0_3ntr + " + " + b1_3ntr + "x", "l")
leg_all.AddEntry(pol1_4ntr,"4 and more tracks, deltar: y = " + a0_4ntr + " + " + a1_4ntr + "x", "l")
leg_all.AddEntry(pol2_4ntr,"4 and more tracks, minmass: y = " + b0_4ntr + " + " + b1_4ntr + "x", "l")
leg_all.SetTextSize(0.015)
leg_all.Draw();

#save all fits together
c_all_fits.SaveAs("./../plots/deltar_minmass_2plots_allfits.pdf")

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

	ts_correct_2ntr[prob].Divide(ts_correct_2ntr[2])
	ts_wrong_2ntr[prob].Divide(ts_wrong_2ntr[2])
	ts_correctmass_2ntr[prob].Divide(ts_correctmass_2ntr[2])
	ts_wrongmass_2ntr[prob].Divide(ts_wrongmass_2ntr[2])

	ts_correct_3ntr[prob].Divide(ts_correct_3ntr[2])
	ts_wrong_3ntr[prob].Divide(ts_wrong_3ntr[2])
	ts_correctmass_3ntr[prob].Divide(ts_correctmass_3ntr[2])
	ts_wrongmass_3ntr[prob].Divide(ts_wrongmass_3ntr[2])

	ts_correct_4ntr[prob].Divide(ts_correct_4ntr[2])
	ts_wrong_4ntr[prob].Divide(ts_wrong_4ntr[2])
	ts_correctmass_4ntr[prob].Divide(ts_correctmass_4ntr[2])
	ts_wrongmass_4ntr[prob].Divide(ts_wrongmass_4ntr[2])

	prob = prob + 1
	count = count + 1
	if prob == 6: prob = 0

	ts_correct[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV")
	ts_wrong[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV")
	ts_correctmass[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV")
	ts_wrongmass[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV")

	ts_correct_2ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 2 tracks")
	ts_wrong_2ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 2 tracks")
	ts_correctmass_2ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 2 tracks")
	ts_wrongmass_2ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 2 tracks")

	ts_correct_3ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 3 tracks")
	ts_wrong_3ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 3 tracks")
	ts_correctmass_3ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 3 tracks")
	ts_wrongmass_3ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 3 tracks")

	ts_correct_4ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 4 and more tracks")
	ts_wrong_4ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 4 and more tracks")
	ts_correctmass_4ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 4 and more tracks")
	ts_wrongmass_4ntr[prob].GetYaxis().SetTitle("number of events (normalized by area) relative to M=172.5GeV, 4 and more tracks")


c3 = TCanvas("canvas3", "c3", 1000, 1000)
c3.Divide(2,2,0.01,0.01)
c21=TCanvas("c21", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c22=TCanvas("c22", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c23=TCanvas("c23", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c24=TCanvas("c24", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 

c3_2ntr = TCanvas("canvas3_2ntr", "c3", 1000, 1000)
c3_2ntr.Divide(2,2,0.01,0.01)
c21_2ntr=TCanvas("c21_2ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c22_2ntr=TCanvas("c22_2ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c23_2ntr=TCanvas("c23_2ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c24_2ntr=TCanvas("c24_2ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 

c3_3ntr = TCanvas("canvas3_3ntr", "c3", 1000, 1000)
c3_3ntr.Divide(2,2,0.01,0.01)
c21_3ntr=TCanvas("c21_3ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c22_3ntr=TCanvas("c22_3ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c23_3ntr=TCanvas("c23_3ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c24_3ntr=TCanvas("c24_3ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 

c3_4ntr = TCanvas("canvas3_4ntr", "c3", 1000, 1000)
c3_4ntr.Divide(2,2,0.01,0.01)
c21_4ntr=TCanvas("c21_4ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c22_4ntr=TCanvas("c22_4ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c23_4ntr=TCanvas("c23_4ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 
c24_4ntr=TCanvas("c24_4ntr", "mean value of inv.m. vs top mass", 100, 100, 500, 500) 


for i in range(0,6):


	leg_ratio = TLegend(0.25,0.5,0.55,0.9)
	leg_ratio.SetHeader("Top mass")  ##NEEDS TO BE CHANGED
	leg_ratio.AddEntry(ts_correctmass[0],"166v5","l")
	leg_ratio.AddEntry(ts_correctmass[1],"169v5","l")
	leg_ratio.AddEntry(ts_correctmass[2],"172v5","l")
	leg_ratio.AddEntry(ts_correctmass[3],"173v5","l")
	leg_ratio.AddEntry(ts_correctmass[4],"175v5","l")
	leg_ratio.AddEntry(ts_correctmass[5],"178v5","l")
	leg_ratio.SetTextSize(0.04)
	leg_ratio.Draw
	# Draw them

	c3.cd(1)
	if i==0: 	ts_correct[i].Draw("HIST")
	else: 	ts_correct[i].Draw("HIST:same")

	c3.cd(3)
	if i==0: 		ts_wrong[i].Draw("HIST")
	else: 		ts_wrong[i].Draw("HIST:same")


	c3.cd(2)
	if i==0: 	ts_correctmass[i].Draw("HIST")
	else: 	ts_correctmass[i].Draw("HIST:same")
	leg_ratio.Draw();

	c3.cd(4)
	if i==0: 	ts_wrongmass[i].Draw("HIST")
	else:	ts_wrongmass[i].Draw("HIST:same")

	c21.cd()
	if i==0: 	ts_correct[i].Draw("HIST")
	else: 	ts_correct[i].Draw("HIST:same")
	leg_ratio.Draw();

	c22.cd()
	if i==0: 	ts_wrong[i].Draw("HIST")
	else: 	ts_wrong[i].Draw("HIST:same")
	leg_ratio.Draw();

	c23.cd()
	if i==0: 	ts_correctmass[i].Draw("HIST")
	else: 	ts_correctmass[i].Draw("HIST:same")
	leg_ratio.Draw();

	c24.cd()
	if i==0: 	ts_wrongmass[i].Draw("HIST")
	else: 	ts_wrongmass[i].Draw("HIST:same")
	leg_ratio.Draw();

	# 2 tracks

	c3_2ntr.cd(1)
	if i==0: 	ts_correct_2ntr[i].Draw("HIST")
	else: 	ts_correct_2ntr[i].Draw("HIST:same")

	c3_2ntr.cd(3)
	if i==0: 		ts_wrong_2ntr[i].Draw("HIST")
	else: 		ts_wrong_2ntr[i].Draw("HIST:same")


	c3_2ntr.cd(2)
	if i==0: 	ts_correctmass_2ntr[i].Draw("HIST")
	else: 	ts_correctmass_2ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c3_2ntr.cd(4)
	if i==0: 	ts_wrongmass_2ntr[i].Draw("HIST")
	else:	ts_wrongmass_2ntr[i].Draw("HIST:same")

	c21_2ntr.cd()
	if i==0: 	ts_correct_2ntr[i].Draw("HIST")
	else: 	ts_correct_2ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c22_2ntr.cd()
	if i==0: 	ts_wrong_2ntr[i].Draw("HIST")
	else: 	ts_wrong_2ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c23_2ntr.cd()
	if i==0: 	ts_correctmass_2ntr[i].Draw("HIST")
	else: 	ts_correctmass_2ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c24_2ntr.cd()
	if i==0: 	ts_wrongmass_2ntr[i].Draw("HIST")
	else: 	ts_wrongmass_2ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	# 3 tracks

	c3_3ntr.cd(1)
	if i==0: 	ts_correct_3ntr[i].Draw("HIST")
	else: 	ts_correct_3ntr[i].Draw("HIST:same")

	c3_3ntr.cd(3)
	if i==0: 		ts_wrong_3ntr[i].Draw("HIST")
	else: 		ts_wrong_3ntr[i].Draw("HIST:same")


	c3_3ntr.cd(2)
	if i==0: 	ts_correctmass_3ntr[i].Draw("HIST")
	else: 	ts_correctmass_3ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c3_3ntr.cd(4)
	if i==0: 	ts_wrongmass_3ntr[i].Draw("HIST")
	else:	ts_wrongmass_3ntr[i].Draw("HIST:same")

	c21_3ntr.cd()
	if i==0: 	ts_correct_3ntr[i].Draw("HIST")
	else: 	ts_correct_3ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c22_3ntr.cd()
	if i==0: 	ts_wrong_3ntr[i].Draw("HIST")
	else: 	ts_wrong_3ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c23_3ntr.cd()
	if i==0: 	ts_correctmass_3ntr[i].Draw("HIST")
	else: 	ts_correctmass_3ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c24_3ntr.cd()
	if i==0: 	ts_wrongmass_3ntr[i].Draw("HIST")
	else: 	ts_wrongmass_3ntr[i].Draw("HIST:same")
	leg_ratio.Draw();


	# 4 and more tracks

	c3_4ntr.cd(1)
	if i==0: 	ts_correct_4ntr[i].Draw("HIST")
	else: 	ts_correct_4ntr[i].Draw("HIST:same")

	c3_4ntr.cd(3)
	if i==0: 		ts_wrong_4ntr[i].Draw("HIST")
	else: 		ts_wrong_4ntr[i].Draw("HIST:same")


	c3_4ntr.cd(2)
	if i==0: 	ts_correctmass_4ntr[i].Draw("HIST")
	else: 	ts_correctmass_4ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c3_4ntr.cd(4)
	if i==0: 	ts_wrongmass_4ntr[i].Draw("HIST")
	else:	ts_wrongmass_4ntr[i].Draw("HIST:same")

	c21_4ntr.cd()
	if i==0: 	ts_correct_4ntr[i].Draw("HIST")
	else: 	ts_correct_4ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c22_4ntr.cd()
	if i==0: 	ts_wrong_4ntr[i].Draw("HIST")
	else: 	ts_wrong_4ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c23_4ntr.cd()
	if i==0: 	ts_correctmass_4ntr[i].Draw("HIST")
	else: 	ts_correctmass_4ntr[i].Draw("HIST:same")
	leg_ratio.Draw();

	c24_4ntr.cd()
	if i==0: 	ts_wrongmass_4ntr[i].Draw("HIST")
	else: 	ts_wrongmass_4ntr[i].Draw("HIST:same")
	leg_ratio.Draw();


	# titles
	ts_correct[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE")
	ts_correctmass[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE")
	ts_wrong[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE")
	ts_wrongmass[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) WRONG CHARGE")


	ts_correct_2ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE (2 tracks)")
	ts_correctmass_2ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE (2 tracks)")
	ts_wrong_2ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE (2 tracks)")
	ts_wrongmass_2ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) WRONG CHARGE (2 tracks)")

	ts_correct_3ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE (3 tracks)")
	ts_correctmass_3ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE (3 tracks)")
	ts_wrong_3ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE (3 tracks)")
	ts_wrongmass_3ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) WRONG CHARGE (3 tracks)")

	ts_correct_4ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) CORRECT CHARGE (4 and more tracks)")
	ts_correctmass_4ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) CORRECT CHARGE (4 and more tracks)")
	ts_wrong_4ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (deltaR) WRONG CHARGE (4 and more tracks)")
	ts_wrongmass_4ntr[i].SetTitle("Lepton/SecVtx Mass in emu channel (take the lowest mass) WRONG CHARGE (4 and more tracks)")

ts_correct[0].SetMaximum(2.5)
ts_correctmass[0].SetMaximum(2.5)
ts_wrong[0].SetMaximum(2.5)
ts_wrongmass[0].SetMaximum(2.5)

ts_correct_2ntr[0].SetMaximum(3)
ts_correctmass_2ntr[0].SetMaximum(3)
ts_wrong_2ntr[0].SetMaximum(3)
ts_wrongmass_2ntr[0].SetMaximum(3)

ts_correct_3ntr[0].SetMaximum(3)
ts_correctmass_3ntr[0].SetMaximum(3)
ts_wrong_3ntr[0].SetMaximum(3)
ts_wrongmass_3ntr[0].SetMaximum(3)


ts_correct_4ntr[0].SetMaximum(3)
ts_correctmass_4ntr[0].SetMaximum(3)
ts_wrong_4ntr[0].SetMaximum(3)
ts_wrongmass_4ntr[0].SetMaximum(3)


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

c3_2ntr.Update()
c3_2ntr.Modified()
c21_2ntr.Update()
c21_2ntr.Modified()	
c22_2ntr.Update()
c22_2ntr.Modified()		
c23_2ntr.Update()
c23_2ntr.Modified()
c24_2ntr.Update()
c24_2ntr.Modified()

c3_3ntr.Update()
c3_3ntr.Modified()
c21_3ntr.Update()
c21_3ntr.Modified()	
c22_3ntr.Update()
c22_3ntr.Modified()		
c23_3ntr.Update()
c23_3ntr.Modified()
c24_3ntr.Update()
c24_3ntr.Modified()

c3_4ntr.Update()
c3_4ntr.Modified()
c21_4ntr.Update()
c21_4ntr.Modified()	
c22_4ntr.Update()
c22_4ntr.Modified()		
c23_4ntr.Update()
c23_4ntr.Modified()
c24_4ntr.Update()
c24_4ntr.Modified()		
		
	

# Save the plot and close the files
c3.SaveAs("./../plots/deltar_minmass_4plots_divided.pdf")
c21.SaveAs("./../plots/deltar_correct_divided.pdf")
c22.SaveAs("./../plots/deltar_wrong_divided.pdf")
c23.SaveAs("./../plots/deltar_correctmass_divided.pdf")
c24.SaveAs("./../plots/deltar_wrongmass_divided.pdf")

c3_2ntr.SaveAs("./../plots/deltar_minmass_4plots_divided_2ntr.pdf")
c21_2ntr.SaveAs("./../plots/deltar_correct_divided_2ntr.pdf")
c22_2ntr.SaveAs("./../plots/deltar_wrong_divided_2ntr.pdf")
c23_2ntr.SaveAs("./../plots/deltar_correctmass_divided_2ntr.pdf")
c24_2ntr.SaveAs("./../plots/deltar_wrongmass_divided_2ntr.pdf")

c3_3ntr.SaveAs("./../plots/deltar_minmass_4plots_divided_3ntr.pdf")
c21_3ntr.SaveAs("./../plots/deltar_correct_divided_3ntr.pdf")
c22_3ntr.SaveAs("./../plots/deltar_wrong_divided_3ntr.pdf")
c23_3ntr.SaveAs("./../plots/deltar_correctmass_divided_3ntr.pdf")
c24_3ntr.SaveAs("./../plots/deltar_wrongmass_divided_3ntr.pdf")

c3_4ntr.SaveAs("./../plots/deltar_minmass_4plots_divided_4ntr.pdf")
c21_4ntr.SaveAs("./../plots/deltar_correct_divided_4ntr.pdf")
c22_4ntr.SaveAs("./../plots/deltar_wrong_divided_4ntr.pdf")
c23_4ntr.SaveAs("./../plots/deltar_correctmass_divided_4ntr.pdf")
c24_4ntr.SaveAs("./../plots/deltar_wrongmass_divided_4ntr.pdf")
