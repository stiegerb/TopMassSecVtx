#!/usr/bin/env python
import ROOT, os, sys
from ROOT import TFile, TCanvas, THStack, TLegend, TH1D, TGraph, TGraphErrors, TF1

## Run by calling in the shell:
## ./macroTemplate.py

# Open a file
path = "/afs/cern.ch/work/j/jklocans/private/CMSSW_5_3_15/src/UserCode/llvv_fwk/lxyplots/"

################

ts_pratio_2ntr = []
ts_pratio_3ntr = []
ts_pratio_4ntr = []
ts_pratio_5ntr = []
ts_pratio_6ntr = []
ts_pratio_7ntr = []
ts_pratio_8ntr = []
ts_pratio_9ntr = []
ts_pratio_10ntr = []

ts_deltar_2ntr = []
ts_deltar_3ntr = []
ts_deltar_4ntr = []
ts_deltar_5ntr = []
ts_deltar_6ntr = []
ts_deltar_7ntr = []
ts_deltar_8ntr = []
ts_deltar_9ntr = []
ts_deltar_10ntr = []

# Make a new TCanvas
c = TCanvas("canvas", "c", 1000, 1000)
c.Divide(2,2,0.01,0.01)

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

	ts_pratio_2ntr.append(TH1D("secbhad_pratio_emu_2ntr_" + x,"ratio between |p| of secvtx and bhadron in eMu channel, " + x, 50, 0., 1.))
	ts_pratio_3ntr.append(TH1D("secbhad_pratio_emu_3ntr_" + x,"ratio between |p| of secvtx and bhadron in eMu channel, " + x, 50, 0., 1.))
	ts_pratio_4ntr.append(TH1D("secbhad_pratio_emu_4ntr_" + x,"ratio between |p| of secvtx and bhadron in eMu channel, " + x, 50, 0., 1.))
	ts_pratio_5ntr.append(TH1D("secbhad_pratio_emu_5ntr_" + x,"ratio between |p| of secvtx and bhadron in eMu channel, " + x, 50, 0., 1.))
	ts_pratio_6ntr.append(TH1D("secbhad_pratio_emu_6ntr_" + x,"ratio between |p| of secvtx and bhadron in eMu channel, " + x, 50, 0., 1.))
	ts_pratio_7ntr.append(TH1D("secbhad_pratio_emu_7ntr_" + x,"ratio between |p| of secvtx and bhadron in eMu channel, " + x, 50, 0., 1.))
	ts_pratio_8ntr.append(TH1D("secbhad_pratio_emu_8ntr_" + x,"ratio between |p| of secvtx and bhadron in eMu channel, " + x, 50, 0., 1.))
	ts_pratio_9ntr.append(TH1D("secbhad_pratio_emu_9ntr_" + x,"ratio between |p| of secvtx and bhadron in eMu channel, " + x, 50, 0., 1.))
	ts_pratio_10ntr.append(TH1D("secbhad_pratio_emu_10ntr_" + x,"ratio between |p| of secvtx and bhadron in eMu channel, " + x, 50, 0., 1.))

	ts_deltar_2ntr.append(TH1D("secbhad_deltar_emu_2ntr_" + x,"deltar between secvtx and bhadron in eMu channel, " + x, 100, 0., 0.4))
	ts_deltar_3ntr.append(TH1D("secbhad_deltar_emu_3ntr_" + x,"deltar between secvtx and bhadron in eMu channel, " + x, 100, 0., 0.4))
	ts_deltar_4ntr.append(TH1D("secbhad_deltar_emu_4ntr_" + x,"deltar between secvtx and bhadron in eMu channel, " + x, 100, 0., 0.4))
	ts_deltar_5ntr.append(TH1D("secbhad_deltar_emu_5ntr_" + x,"deltar between secvtx and bhadron in eMu channel, " + x, 100, 0., 0.4))
	ts_deltar_6ntr.append(TH1D("secbhad_deltar_emu_6ntr_" + x,"deltar between secvtx and bhadron in eMu channel, " + x, 100, 0., 0.4))
	ts_deltar_7ntr.append(TH1D("secbhad_deltar_emu_7ntr_" + x,"deltar between secvtx and bhadron in eMu channel, " + x, 100, 0., 0.4))
	ts_deltar_8ntr.append(TH1D("secbhad_deltar_emu_8ntr_" + x,"deltar between secvtx and bhadron in eMu channel, " + x, 100, 0., 0.4))
	ts_deltar_9ntr.append(TH1D("secbhad_deltar_emu_9ntr_" + x,"deltar between secvtx and bhadron in eMu channel, " + x, 100, 0., 0.4))
	ts_deltar_10ntr.append(TH1D("secbhad_deltar_emu_10ntr_" + x,"deltar between secvtx and bhadron in eMu channel, " + x, 100, 0., 0.4))


# Open the files -> adds all samples together
for i in range(0,6):
	ts_pratio_2ntr[i].Sumw2()
	ts_pratio_3ntr[i].Sumw2()
	ts_pratio_4ntr[i].Sumw2()
	ts_pratio_5ntr[i].Sumw2()
	ts_pratio_6ntr[i].Sumw2()
	ts_pratio_7ntr[i].Sumw2()
	ts_pratio_8ntr[i].Sumw2()
	ts_pratio_9ntr[i].Sumw2()
	ts_pratio_10ntr[i].Sumw2()

	ts_deltar_2ntr[i].Sumw2()
	ts_deltar_3ntr[i].Sumw2()
	ts_deltar_4ntr[i].Sumw2()
	ts_deltar_5ntr[i].Sumw2()
	ts_deltar_6ntr[i].Sumw2()
	ts_deltar_7ntr[i].Sumw2()
	ts_deltar_8ntr[i].Sumw2()
	ts_deltar_9ntr[i].Sumw2()
	ts_deltar_10ntr[i].Sumw2()

	rootfile1 = []

	for x in listoffiles[i]:
	#inv.m. l + sv
		rootfile1.append(TFile.Open("./../lxyplots/" + x, "READ"))

	histo_pratio_2ntr = []
	histo_pratio_3ntr = []
	histo_pratio_4ntr = []
	histo_pratio_5ntr = []
	histo_pratio_6ntr = []
	histo_pratio_7ntr = []
	histo_pratio_8ntr = []
	histo_pratio_9ntr = []
	histo_pratio_10ntr = []

	histo_deltar_2ntr = []
	histo_deltar_3ntr = []
	histo_deltar_4ntr = []
	histo_deltar_5ntr = []
	histo_deltar_6ntr = []
	histo_deltar_7ntr = []
	histo_deltar_8ntr = []
	histo_deltar_9ntr = []
	histo_deltar_10ntr = []


	for x in range(0,len(listoffiles[i])):

		histo_pratio_2ntr.append(rootfile1[x].Get("secbhad_pratio_emu_ntr2"))
		histo_pratio_3ntr.append(rootfile1[x].Get("secbhad_pratio_emu_ntr3"))
		histo_pratio_4ntr.append(rootfile1[x].Get("secbhad_pratio_emu_ntr4"))
		histo_pratio_5ntr.append(rootfile1[x].Get("secbhad_pratio_emu_ntr5"))
		histo_pratio_6ntr.append(rootfile1[x].Get("secbhad_pratio_emu_ntr6"))
		histo_pratio_7ntr.append(rootfile1[x].Get("secbhad_pratio_emu_ntr7"))
		histo_pratio_8ntr.append(rootfile1[x].Get("secbhad_pratio_emu_ntr8"))
		histo_pratio_9ntr.append(rootfile1[x].Get("secbhad_pratio_emu_ntr9"))
		histo_pratio_10ntr.append(rootfile1[x].Get("secbhad_pratio_emu_ntr10"))

		histo_deltar_2ntr.append(rootfile1[x].Get("secbhad_deltar_emu_ntr2"))
		histo_deltar_3ntr.append(rootfile1[x].Get("secbhad_deltar_emu_ntr3"))
		histo_deltar_4ntr.append(rootfile1[x].Get("secbhad_deltar_emu_ntr4"))
		histo_deltar_5ntr.append(rootfile1[x].Get("secbhad_deltar_emu_ntr5"))
		histo_deltar_6ntr.append(rootfile1[x].Get("secbhad_deltar_emu_ntr6"))
		histo_deltar_7ntr.append(rootfile1[x].Get("secbhad_deltar_emu_ntr7"))
		histo_deltar_8ntr.append(rootfile1[x].Get("secbhad_deltar_emu_ntr8"))
		histo_deltar_9ntr.append(rootfile1[x].Get("secbhad_deltar_emu_ntr9"))
		histo_deltar_10ntr.append(rootfile1[x].Get("secbhad_deltar_emu_ntr10"))

		histo_pratio_2ntr[x].Sumw2()
		histo_pratio_3ntr[x].Sumw2()
		histo_pratio_4ntr[x].Sumw2()
		histo_pratio_5ntr[x].Sumw2()
		histo_pratio_6ntr[x].Sumw2()
		histo_pratio_7ntr[x].Sumw2()
		histo_pratio_8ntr[x].Sumw2()
		histo_pratio_9ntr[x].Sumw2()
		histo_pratio_10ntr[x].Sumw2()

		histo_deltar_2ntr[x].Sumw2()
		histo_deltar_3ntr[x].Sumw2()
		histo_deltar_4ntr[x].Sumw2()
		histo_deltar_5ntr[x].Sumw2()
		histo_deltar_6ntr[x].Sumw2()
		histo_deltar_7ntr[x].Sumw2()
		histo_deltar_8ntr[x].Sumw2()
		histo_deltar_9ntr[x].Sumw2()
		histo_deltar_10ntr[x].Sumw2()

		#adding histos

		ts_pratio_2ntr[i].Add(histo_pratio_2ntr[x])
		ts_pratio_3ntr[i].Add(histo_pratio_3ntr[x])
		ts_pratio_4ntr[i].Add(histo_pratio_4ntr[x])
		ts_pratio_5ntr[i].Add(histo_pratio_5ntr[x])
		ts_pratio_6ntr[i].Add(histo_pratio_6ntr[x])
		ts_pratio_7ntr[i].Add(histo_pratio_7ntr[x])
		ts_pratio_8ntr[i].Add(histo_pratio_8ntr[x])
		ts_pratio_9ntr[i].Add(histo_pratio_9ntr[x])
		ts_pratio_10ntr[i].Add(histo_pratio_10ntr[x])

		ts_deltar_2ntr[i].Add(histo_deltar_2ntr[x])
		ts_deltar_3ntr[i].Add(histo_deltar_3ntr[x])
		ts_deltar_4ntr[i].Add(histo_deltar_4ntr[x])
		ts_deltar_5ntr[i].Add(histo_deltar_5ntr[x])
		ts_deltar_6ntr[i].Add(histo_deltar_6ntr[x])
		ts_deltar_7ntr[i].Add(histo_deltar_7ntr[x])
		ts_deltar_8ntr[i].Add(histo_deltar_8ntr[x])
		ts_deltar_9ntr[i].Add(histo_deltar_9ntr[x])
		ts_deltar_10ntr[i].Add(histo_deltar_10ntr[x])


	#normalization

	ts_pratio_2ntr[i].Scale(1/ts_pratio_2ntr[i].Integral())
	ts_pratio_3ntr[i].Scale(1/ts_pratio_3ntr[i].Integral())
	ts_pratio_4ntr[i].Scale(1/ts_pratio_4ntr[i].Integral())
	ts_pratio_5ntr[i].Scale(1/ts_pratio_5ntr[i].Integral())

	ts_deltar_2ntr[i].Scale(1/ts_deltar_2ntr[i].Integral())
	ts_deltar_3ntr[i].Scale(1/ts_deltar_3ntr[i].Integral())
	ts_deltar_4ntr[i].Scale(1/ts_deltar_4ntr[i].Integral())
	ts_deltar_5ntr[i].Scale(1/ts_deltar_5ntr[i].Integral())

	# Set colors and stuff
	# Set colors and stuff

	ts_pratio_2ntr[i].SetLineColor(51)
	ts_pratio_3ntr[i].SetLineColor(57)
	ts_pratio_4ntr[i].SetLineColor(63)
	ts_pratio_5ntr[i].SetLineColor(69)
	ts_pratio_6ntr[i].SetLineColor(75)
	ts_pratio_7ntr[i].SetLineColor(81)
	ts_pratio_8ntr[i].SetLineColor(87)
	ts_pratio_9ntr[i].SetLineColor(93)
	ts_pratio_10ntr[i].SetLineColor(99)


	ts_deltar_2ntr[i].SetLineColor(51)
	ts_deltar_3ntr[i].SetLineColor(57)
	ts_deltar_4ntr[i].SetLineColor(63)
	ts_deltar_5ntr[i].SetLineColor(69)
	ts_deltar_6ntr[i].SetLineColor(75)
	ts_deltar_7ntr[i].SetLineColor(81)
	ts_deltar_8ntr[i].SetLineColor(87)
	ts_deltar_9ntr[i].SetLineColor(93)
	ts_deltar_10ntr[i].SetLineColor(99)
	
	del histo_pratio_2ntr
	del histo_pratio_3ntr
	del histo_pratio_4ntr
	del histo_pratio_5ntr
	del histo_pratio_6ntr
	del histo_pratio_7ntr
	del histo_pratio_8ntr
	del histo_pratio_9ntr
	del histo_pratio_10ntr

	del histo_deltar_2ntr
	del histo_deltar_3ntr
	del histo_deltar_4ntr
	del histo_deltar_5ntr
	del histo_deltar_6ntr
	del histo_deltar_7ntr
	del histo_deltar_8ntr
	del histo_deltar_9ntr
	del histo_deltar_10ntr

	del rootfile1


graph1 = TGraphErrors(9)
graph1.SetTitle("Average ratio between p of secvtx and bhadron")
graph1.GetXaxis().SetTitle("Nr of tracks")
graph2 = TGraphErrors(9)
graph2.SetTitle("Average deltar between secvtx and bhadron")
graph2.GetXaxis().SetTitle("Nr of tracks")

x = []
x.append(2)
x.append(3)
x.append(4)
x.append(5)
x.append(6)
x.append(7)
x.append(8)
x.append(9)
x.append(10)

y = [[0 for xx in xrange(9)] for xx in xrange(6)] 
yerr = [[0 for xx in xrange(9)] for xx in xrange(6)]  

z = [[0 for xx in xrange(9)] for xx in xrange(6)] 
zerr = [[0 for xx in xrange(9)] for xx in xrange(6)] 

for i in range(0,6):
	
	y[i][0]=ts_pratio_2ntr[i].GetMean()
	z[i][0]=ts_deltar_2ntr[i].GetMean()
	yerr[i][0] = ts_pratio_2ntr[i].GetMeanError()
	zerr[i][0] = ts_deltar_2ntr[i].GetMeanError()

	y[i][1]=ts_pratio_3ntr[i].GetMean()
	z[i][1]=ts_deltar_3ntr[i].GetMean()
	yerr[i][1] = ts_pratio_3ntr[i].GetMeanError()
	zerr[i][1] = ts_deltar_3ntr[i].GetMeanError()

	y[i][2]=ts_pratio_4ntr[i].GetMean()
	z[i][2]=ts_deltar_4ntr[i].GetMean()
	yerr[i][2] = ts_pratio_4ntr[i].GetMeanError()
	zerr[i][2] = ts_deltar_4ntr[i].GetMeanError()

	y[i][3]=ts_pratio_5ntr[i].GetMean()
	z[i][3]=ts_deltar_5ntr[i].GetMean()
	yerr[i][3] = ts_pratio_5ntr[i].GetMeanError()
	zerr[i][3] = ts_deltar_5ntr[i].GetMeanError()

	y[i][4]=ts_pratio_6ntr[i].GetMean()
	z[i][4]=ts_deltar_6ntr[i].GetMean()
	yerr[i][4] = ts_pratio_6ntr[i].GetMeanError()
	zerr[i][4] = ts_deltar_6ntr[i].GetMeanError()

	y[i][5]=ts_pratio_7ntr[i].GetMean()
	z[i][5]=ts_deltar_7ntr[i].GetMean()
	yerr[i][5] = ts_pratio_7ntr[i].GetMeanError()
	zerr[i][5] = ts_deltar_7ntr[i].GetMeanError()

	y[i][6]=ts_pratio_8ntr[i].GetMean()
	z[i][6]=ts_deltar_8ntr[i].GetMean()
	yerr[i][6] = ts_pratio_8ntr[i].GetMeanError()
	zerr[i][6] = ts_deltar_8ntr[i].GetMeanError()

	y[i][7]=ts_pratio_9ntr[i].GetMean()
	z[i][7]=ts_deltar_9ntr[i].GetMean()
	yerr[i][7] = ts_pratio_9ntr[i].GetMeanError()
	zerr[i][7] = ts_deltar_9ntr[i].GetMeanError()

	y[i][8]=ts_pratio_10ntr[i].GetMean()
	z[i][8]=ts_deltar_10ntr[i].GetMean()
	yerr[i][8] = ts_pratio_10ntr[i].GetMeanError()
	zerr[i][8] = ts_deltar_10ntr[i].GetMeanError()

	for j in range(0,9):

		graph1.SetPoint(j, x[j], y[i][j])	
		graph2.SetPoint(j, x[j], z[i][j])
		graph1.SetPointError(j, 0, yerr[i][j])	
		graph2.SetPointError(j, 0, zerr[i][j])

	c.cd(1)
	ts_pratio_2ntr[i].Draw()
	ts_pratio_3ntr[i].Draw("same")
	ts_pratio_4ntr[i].Draw("same")
	ts_pratio_5ntr[i].Draw("same")
	ts_pratio_6ntr[i].Draw("same")
	ts_pratio_7ntr[i].Draw("same")
	ts_pratio_8ntr[i].Draw("same")
	ts_pratio_9ntr[i].Draw("same")
	ts_pratio_10ntr[i].Draw("same")

	c.cd(2)
	ts_deltar_2ntr[i].Draw()
	ts_deltar_3ntr[i].Draw("same")
	ts_deltar_4ntr[i].Draw("same")
	ts_deltar_5ntr[i].Draw("same")
	ts_deltar_6ntr[i].Draw("same")
	ts_deltar_7ntr[i].Draw("same")
	ts_deltar_8ntr[i].Draw("same")
	ts_deltar_9ntr[i].Draw("same")
	ts_deltar_10ntr[i].Draw("same")

	leg = TLegend(0.7,0.35,1,0.65)
	leg.AddEntry(ts_deltar_2ntr[i], "2 traks", "l")
	leg.AddEntry(ts_deltar_3ntr[i], "3 traks", "l")
	leg.AddEntry(ts_deltar_4ntr[i], "4 traks", "l")
	leg.AddEntry(ts_deltar_5ntr[i], "5 traks", "l")
	leg.AddEntry(ts_deltar_6ntr[i], "6 traks", "l")
	leg.AddEntry(ts_deltar_7ntr[i], "7 traks", "l")
	leg.AddEntry(ts_deltar_8ntr[i], "8 traks", "l")
	leg.AddEntry(ts_deltar_9ntr[i], "9 traks", "l")
	leg.AddEntry(ts_deltar_10ntr[i], "10 traks", "l")
	leg.SetTextSize(0.02)
	leg.Draw()

	c.cd(3)
	graph1.Draw("AP")
	graph1.GetXaxis().SetTitle("Nr of tracks")
	graph1.GetYaxis().SetTitle("<ratio>")

	c.cd(4)
	graph2.Draw("AP")
	graph2.GetXaxis().SetTitle("Nr of tracks")
	graph2.GetYaxis().SetTitle("<deltaR>")

	c.SaveAs("./../plots/secbhad_" + listofnames[i] + ".pdf")

## this part when we sum up all mases together

ts_pratio_2ntr_allmases = TH1D("secbhad_pratio_emu_2ntr_allmases", "ratio between |p| of secvtx and bhadron in eMu channel, ", 50, 0., 1.)
ts_pratio_3ntr_allmases = TH1D("secbhad_pratio_emu_3ntr_allmases", "ratio between |p| of secvtx and bhadron in eMu channel, ", 50, 0., 1.)
ts_pratio_4ntr_allmases = TH1D("secbhad_pratio_emu_4ntr_allmases", "ratio between |p| of secvtx and bhadron in eMu channel, ", 50, 0., 1.)
ts_pratio_5ntr_allmases = TH1D("secbhad_pratio_emu_5ntr_allmases", "ratio between |p| of secvtx and bhadron in eMu channel, ", 50, 0., 1.)
ts_pratio_6ntr_allmases = TH1D("secbhad_pratio_emu_6ntr_allmases", "ratio between |p| of secvtx and bhadron in eMu channel, ", 50, 0., 1.)
ts_pratio_7ntr_allmases = TH1D("secbhad_pratio_emu_7ntr_allmases", "ratio between |p| of secvtx and bhadron in eMu channel, ", 50, 0., 1.)
ts_pratio_8ntr_allmases = TH1D("secbhad_pratio_emu_8ntr_allmases", "ratio between |p| of secvtx and bhadron in eMu channel, ", 50, 0., 1.)
ts_pratio_9ntr_allmases = TH1D("secbhad_pratio_emu_9ntr_allmases", "ratio between |p| of secvtx and bhadron in eMu channel, ", 50, 0., 1.)
ts_pratio_10ntr_allmases = TH1D("secbhad_pratio_emu_10ntr_allmases", "ratio between |p| of secvtx and bhadron in eMu channel, ", 50, 0., 1.)

ts_pratio_2ntr_allmases.Sumw2()
ts_pratio_3ntr_allmases.Sumw2()
ts_pratio_4ntr_allmases.Sumw2()
ts_pratio_5ntr_allmases.Sumw2()
ts_pratio_6ntr_allmases.Sumw2()
ts_pratio_7ntr_allmases.Sumw2()
ts_pratio_8ntr_allmases.Sumw2()
ts_pratio_9ntr_allmases.Sumw2()
ts_pratio_10ntr_allmases.Sumw2()

for i in range(0,6):

	ts_pratio_2ntr_allmases.Add(ts_pratio_2ntr[i])
	ts_pratio_3ntr_allmases.Add(ts_pratio_3ntr[i])
	ts_pratio_4ntr_allmases.Add(ts_pratio_4ntr[i])
	ts_pratio_5ntr_allmases.Add(ts_pratio_5ntr[i])
	ts_pratio_6ntr_allmases.Add(ts_pratio_6ntr[i])
	ts_pratio_7ntr_allmases.Add(ts_pratio_7ntr[i])
	ts_pratio_8ntr_allmases.Add(ts_pratio_8ntr[i])
	ts_pratio_9ntr_allmases.Add(ts_pratio_9ntr[i])
	ts_pratio_10ntr_allmases.Add(ts_pratio_10ntr[i])

ts_pratio_2ntr_allmases.SetLineColor(51)
ts_pratio_3ntr_allmases.SetLineColor(57)
ts_pratio_4ntr_allmases.SetLineColor(63)
ts_pratio_5ntr_allmases.SetLineColor(69)
ts_pratio_6ntr_allmases.SetLineColor(75)
ts_pratio_7ntr_allmases.SetLineColor(81)
ts_pratio_8ntr_allmases.SetLineColor(87)
ts_pratio_9ntr_allmases.SetLineColor(93)
ts_pratio_10ntr_allmases.SetLineColor(99)

graph_allmases = TGraphErrors(4)
graph_allmases.SetTitle("Average ratio between p of secvtx and bhadron (all mases together)")
graph_allmases.GetXaxis().SetTitle("Nr of tracks")

yy = [0 for xx in xrange(9)] 
yyerr = [0 for xx in xrange(9)]
	
yy[0]=ts_pratio_2ntr_allmases.GetMean()
yyerr[0] = ts_pratio_2ntr_allmases.GetMeanError()
yy[1]=ts_pratio_3ntr_allmases.GetMean()
yyerr[1] = ts_pratio_3ntr_allmases.GetMeanError()
yy[2]=ts_pratio_4ntr_allmases.GetMean()
yyerr[2] = ts_pratio_4ntr_allmases.GetMeanError()
yy[3]=ts_pratio_5ntr_allmases.GetMean()
yyerr[3] = ts_pratio_5ntr_allmases.GetMeanError()
yy[4]=ts_pratio_6ntr_allmases.GetMean()
yyerr[4] = ts_pratio_6ntr_allmases.GetMeanError()
yy[5]=ts_pratio_7ntr_allmases.GetMean()
yyerr[5] = ts_pratio_7ntr_allmases.GetMeanError()
yy[6]=ts_pratio_8ntr_allmases.GetMean()
yyerr[6] = ts_pratio_8ntr_allmases.GetMeanError()
yy[7]=ts_pratio_9ntr_allmases.GetMean()
yyerr[7] = ts_pratio_9ntr_allmases.GetMeanError()
yy[8]=ts_pratio_10ntr_allmases.GetMean()
yyerr[8] = ts_pratio_10ntr_allmases.GetMeanError()

for j in range(0,9):

	graph_allmases.SetPoint(j, x[j], yy[j])	
	graph_allmases.SetPointError(j, 0, yyerr[j])	

c_allmases = TCanvas("canvas_allmases", "c_allmases", 1000, 500)
c_allmases.Divide(2,1,0.01,0.01)

c_allmases.cd(1)

ts_pratio_2ntr_allmases.Draw()
ts_pratio_3ntr_allmases.Draw("same")
ts_pratio_4ntr_allmases.Draw("same")
ts_pratio_5ntr_allmases.Draw("same")
ts_pratio_6ntr_allmases.Draw("same")
ts_pratio_7ntr_allmases.Draw("same")
ts_pratio_8ntr_allmases.Draw("same")
ts_pratio_9ntr_allmases.Draw("same")
ts_pratio_10ntr_allmases.Draw("same")

leg = TLegend(0.7,0.35,1,0.65)
leg.AddEntry(ts_pratio_2ntr_allmases, "2 traks", "l")
leg.AddEntry(ts_pratio_3ntr_allmases, "3 traks", "l")
leg.AddEntry(ts_pratio_4ntr_allmases, "4 traks", "l")
leg.AddEntry(ts_pratio_5ntr_allmases, "5 traks", "l")
leg.AddEntry(ts_pratio_6ntr_allmases, "6 traks", "l")
leg.AddEntry(ts_pratio_7ntr_allmases, "7 traks", "l")
leg.AddEntry(ts_pratio_8ntr_allmases, "8 traks", "l")
leg.AddEntry(ts_pratio_9ntr_allmases, "9 traks", "l")
leg.AddEntry(ts_pratio_10ntr_allmases, "10 traks", "l")
leg.SetTextSize(0.02)
leg.Draw()

c_allmases.cd(2)

graph_allmases.Draw("AP")
graph_allmases.GetXaxis().SetTitle("Nr of tracks")
graph_allmases.GetYaxis().SetTitle("<ratio>")


c_allmases.SaveAs("./../plots/secbhad_allmases.pdf")
