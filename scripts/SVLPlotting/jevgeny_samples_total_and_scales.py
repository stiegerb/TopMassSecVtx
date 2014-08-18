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
ts_correctmass = []
ts_wrongmass = []

ts_correct_topweight = []
ts_wrong_topweight = []
ts_correctmass_topweight = []
ts_wrongmass_topweight = []

ts_correct_topweightup = []
ts_wrong_topweightup = []
ts_correctmass_topweightup = []
ts_wrongmass_topweightup = []

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

# save all names of desired files in a list
listofnames = []
listofnames.append("166v5")
listofnames.append("169v5")
listofnames.append("172v5")
listofnames.append("173v5")
listofnames.append("175v5")
listofnames.append("178v5")
listofnames.append("scaleup")
listofnames.append("scaledown")

listoffiles = [[] for x in xrange(0,8)]

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

	elif(file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_scaleup")):
		listoffiles[6].insert(0,file)

	elif(file.endswith(".root") and file.startswith("MC8TeV_TTJets_MSDecays_scaledown")):
		listoffiles[7].insert(0,file)



for x in range(0,6):

	ts_correct.append(TH1D("emu_deltar_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrong.append(TH1D("emu_deltar_wrong_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_correctmass.append(TH1D("emu_minmass_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrongmass.append(TH1D("emu_minmass_wrong_" + listofnames[x],"test stackhsed histograms", 50, 0., 150.))

	ts_correct_topweight.append(TH1D("emu_deltar_topweight_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrong_topweight.append(TH1D("emu_deltar_topweight_wrong_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_correctmass_topweight.append(TH1D("emu_minmass_topweight_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_topweight.append(TH1D("emu_minmass_topweight_wrong_" + listofnames[x],"test stackhsed histograms", 50, 0., 150.))

	ts_correct_topweightup.append(TH1D("emu_deltar_topweightup_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrong_topweightup.append(TH1D("emu_deltar_topweightup_wrong_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_correctmass_topweightup.append(TH1D("emu_minmass_topweightup_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_topweightup.append(TH1D("emu_minmass_topweightup_wrong_" + listofnames[x],"test stackhsed histograms", 50, 0., 150.))


	ts_correct_2ntr.append(TH1D("emu2tk_deltar_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrong_2ntr.append(TH1D("emu2tk_deltar_wrong_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_correctmass_2ntr.append(TH1D("emu2tk_minmass_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_2ntr.append(TH1D("emu2tk_minmass_wrong_" + listofnames[x],"test stackhsed histograms", 50, 0., 150.))

	ts_correct_3ntr.append(TH1D("emu3tk_deltar_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrong_3ntr.append(TH1D("emu3tk_deltar_wrong_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_correctmass_3ntr.append(TH1D("emu3tk_minmass_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_3ntr.append(TH1D("emu3tk_minmass_wrong_" + listofnames[x],"test stackhsed histograms", 50, 0., 150.))

	ts_correct_4ntr.append(TH1D("emu4tk_deltar_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrong_4ntr.append(TH1D("emu4tk_deltar_wrong_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_correctmass_4ntr.append(TH1D("emu4tk_minmass_correct_" + listofnames[x],"test stacked histograms", 50, 0., 150.))
	ts_wrongmass_4ntr.append(TH1D("emu4tk_minmass_wrong_" + listofnames[x],"test stackhsed histograms", 50, 0., 150.))

ts_correct.append(TH1D("emu_deltar_scaleup_correct_172v5","test stacked histograms", 50, 0., 150.))
ts_wrong.append(TH1D("emu_deltar_scaleup_wrong_172v5","test stacked histograms", 50, 0., 150.))
ts_correctmass.append(TH1D("emu_minmass_scaleup_correct_172v5","test stacked histograms", 50, 0., 150.))
ts_wrongmass.append(TH1D("emu_minmass_scaleup_wrong_172v5","test stackhsed histograms", 50, 0., 150.))

ts_correct.append(TH1D("emu_deltar_scaledown_correct_172v5","test stacked histograms", 50, 0., 150.))
ts_wrong.append(TH1D("emu_deltar_scaledown_wrong_172v5","test stacked histograms", 50, 0., 150.))
ts_correctmass.append(TH1D("emu_minmass_scaledown_correct_172v5","test stacked histograms", 50, 0., 150.))
ts_wrongmass.append(TH1D("emu_minmass_scaledown_wrong_172v5","test stackhsed histograms", 50, 0., 150.))



# Open the files -> adds all samples together
for i in range(0,len(listofnames)):
	ts_correct[i].Sumw2()
	ts_wrong[i].Sumw2()
	ts_correct[i].Sumw2()
	ts_wrongmass[i].Sumw2()

	if (i<6):
		ts_correct_topweight[i].Sumw2()
		ts_wrong_topweight[i].Sumw2()
		ts_correct_topweight[i].Sumw2()
		ts_wrongmass_topweight[i].Sumw2()

		ts_correct_topweightup[i].Sumw2()
		ts_wrong_topweightup[i].Sumw2()
		ts_correct_topweightup[i].Sumw2()
		ts_wrongmass_topweightup[i].Sumw2()

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


	histo_correct = []
	histo_wrong = []
	histo_correctmass = []
	histo_wrongmass = []

	histo_correct_topweight = []
	histo_wrong_topweight = []
	histo_correctmass_topweight = []
	histo_wrongmass_topweight = []

	histo_correct_topweightup = []
	histo_wrong_topweightup = []
	histo_correctmass_topweightup = []
	histo_wrongmass_topweightup = []


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

		histo_correct_topweight.append(rootfile1[x].Get("mlsv_emu_deltar_cut_correct_topweight"))
		histo_wrong_topweight.append(rootfile1[x].Get("mlsv_emu_deltar_cut_wrong_topweight"))
		histo_correctmass_topweight.append(rootfile1[x].Get("mlsv_emu_minmass_correct_topweight"))
		histo_wrongmass_topweight.append(rootfile1[x].Get("mlsv_emu_minmass_wrong_topweight"))

		histo_correct_topweightup.append(rootfile1[x].Get("mlsv_emu_deltar_cut_correct_topweight_up"))
		histo_wrong_topweightup.append(rootfile1[x].Get("mlsv_emu_deltar_cut_wrong_topweight_up"))
		histo_correctmass_topweightup.append(rootfile1[x].Get("mlsv_emu_minmass_correct_topweight_up"))
		histo_wrongmass_topweightup.append(rootfile1[x].Get("mlsv_emu_minmass_wrong_topweight_up"))


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


		histo_correct_topweight[x].Sumw2()
		histo_wrong_topweight[x].Sumw2()
		histo_correctmass_topweight[x].Sumw2()
		histo_wrongmass_topweight[x].Sumw2()

		histo_correct_topweightup[x].Sumw2()
		histo_wrong_topweightup[x].Sumw2()
		histo_correctmass_topweightup[x].Sumw2()
		histo_wrongmass_topweightup[x].Sumw2()

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

		if(i<6):
			ts_correct_topweight[i].Add(histo_correct_topweight[x])
			ts_wrong_topweight[i].Add(histo_wrong_topweight[x])
			ts_correctmass_topweight[i].Add(histo_correctmass_topweight[x])
			ts_wrongmass_topweight[i].Add(histo_wrongmass_topweight[x])

			ts_correct_topweightup[i].Add(histo_correct_topweightup[x])
			ts_wrong_topweightup[i].Add(histo_wrong_topweightup[x])
			ts_correctmass_topweightup[i].Add(histo_correctmass_topweightup[x])
			ts_wrongmass_topweightup[i].Add(histo_wrongmass_topweightup[x])


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

	del histo_correct
	del histo_wrong 
	del histo_correctmass
	del histo_wrongmass

	del histo_correct_topweight
	del histo_wrong_topweight
	del histo_correctmass_topweight
	del histo_wrongmass_topweight

	del histo_correct_topweightup
	del histo_wrong_topweightup
	del histo_correctmass_topweightup
	del histo_wrongmass_topweightup


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

	if(i<6):
		print "emu_deltar_topweight"
		print ts_correct_topweight[i].GetEntries() + ts_wrong_topweight[i].GetEntries()
		print ""

		print "emu_deltar_topweightup"
		print ts_correct_topweightup[i].GetEntries() + ts_wrong_topweightup[i].GetEntries()
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
	print "_________________________________________________"

	print "emu_minmass"
	print ts_correctmass[i].GetEntries() + ts_wrongmass[i].GetEntries()
	print ""

	if(i<6):	
		print "emu_minmass_topweight"
		print ts_correctmass_topweight[i].GetEntries() + ts_wrongmass_topweight[i].GetEntries()
		print ""

		print "emu_minmass_topweightup"
		print ts_correctmass_topweightup[i].GetEntries() + ts_wrongmass_topweightup[i].GetEntries()
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
	print "_________________________________________________"
	print "_________________________________________________"


print "emu_deltar total"
print ts_correct[0].GetEntries() + ts_wrong[0].GetEntries() + ts_correct[1].GetEntries() + ts_wrong[1].GetEntries()+ ts_correct[2].GetEntries() + ts_wrong[2].GetEntries()+ ts_correct[3].GetEntries() + ts_wrong[3].GetEntries()+ ts_correct[4].GetEntries() + ts_wrong[4].GetEntries()+ ts_correct[5].GetEntries() + ts_wrong[5].GetEntries()

#to save all samples together
rootfile2 = []
rootfile2.append((TFile("../newsamples/jevgeny_samples_total_and_scales.root", "RECREATE")))
for i in range(0,6):
	ts_correct[i].Write()
	ts_wrong[i].Write()
	ts_correctmass[i].Write()
	ts_wrongmass[i].Write()
	ts_correct_topweight[i].Write()
	ts_wrong_topweight[i].Write()
	ts_correctmass_topweight[i].Write()
	ts_wrongmass_topweight[i].Write()
	ts_correct_topweightup[i].Write()
	ts_wrong_topweightup[i].Write()
	ts_correctmass_topweightup[i].Write()
	ts_wrongmass_topweightup[i].Write()

	ts_correct_2ntr[i].Write()
	ts_wrong_2ntr[i].Write()
	ts_correctmass_2ntr[i].Write()
	ts_wrongmass_2ntr[i].Write()
	ts_correct_3ntr[i].Write()
	ts_wrong_3ntr[i].Write()
	ts_correctmass_3ntr[i].Write()
	ts_wrongmass_3ntr[i].Write()
	ts_correct_4ntr[i].Write()
	ts_wrong_4ntr[i].Write()
	ts_correctmass_4ntr[i].Write()
	ts_wrongmass_4ntr[i].Write()
	
	if(i!=2):

		ts_correct[i].SetName("emu_deltar_scaleup_correct_" + listofnames[i])
		ts_wrong[i].SetName("emu_deltar_scaleup_wrong_" + listofnames[i])
		ts_correctmass[i].SetName("emu_minmass_scaleup_correct_" + listofnames[i])
		ts_wrongmass[i].SetName("emu_minmass_scaleup_wrong_" + listofnames[i])

		ts_correct[i].Write()
		ts_wrong[i].Write()
		ts_correctmass[i].Write()
		ts_wrongmass[i].Write()

		ts_correct[i].SetName("emu_deltar_scaledown_correct_" + listofnames[i])
		ts_wrong[i].SetName("emu_deltar_scaledown_wrong_" + listofnames[i])
		ts_correctmass[i].SetName("emu_minmass_scaledown_correct_" + listofnames[i])
		ts_wrongmass[i].SetName("emu_minmass_scaledown_wrong_" + listofnames[i])

		ts_correct[i].Write()
		ts_wrong[i].Write()
		ts_correctmass[i].Write()
		ts_wrongmass[i].Write()

ts_correct[6].Write()
ts_wrong[6].Write()
ts_correctmass[6].Write()
ts_wrongmass[6].Write()

ts_correct[7].Write()
ts_wrong[7].Write()
ts_correctmass[7].Write()
ts_wrongmass[7].Write()

rootfile2[0].Close()
