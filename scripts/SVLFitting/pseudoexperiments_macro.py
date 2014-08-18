#!/usr/bin/env python
import ROOT, os, sys, math
from ROOT import TFile, TCanvas, THStack, TLegend, TH1D, TGraph, TGraphErrors, TF1, TLine, TStyle

## Run by calling in the shell:
## ./macroTemplate.py

###############

# Make a new TCanvas


listofnames = []
listofnames.append("166v5")
listofnames.append("169v5")
listofnames.append("172v5")
listofnames.append("173v5")
listofnames.append("175v5")
listofnames.append("178v5")

ROOT.gStyle.SetOptStat(1111)

listofalgorithms = []
listofalgorithms.append("emu_deltar")
listofalgorithms.append("emu_minmass")


x = []
x.append(166.5)
x.append(169.5)
x.append(172.5)
x.append(173.5)
x.append(175.5)
x.append(178.5)


line1 = TLine(165.,0,180.5,0)
line2 = TLine(165.,1,180.5,1)

# error correction

coef_deltar=math.sqrt(1000*66290/653850)
coef_minmass=math.sqrt(18750*1000/184545)

for xi in xrange(0,len(listofalgorithms)):

	rootfile1 = TFile.Open("./mBl_Workspace_" + listofalgorithms[xi] + "_pe.root", "READ")
	rootfile1_t = TFile.Open("./mBl_Workspace_" + listofalgorithms[xi] + "_topweight_pe.root", "READ")
	rootfile1_tup = TFile.Open("./mBl_Workspace_" + listofalgorithms[xi] + "_topweightup_pe.root", "READ")

	y=[]
	yerr=[]
	z=[]
	zerr=[]

	y_t=[]
	yerr_t=[]
	z_t=[]
	zerr_t=[]

	y_tup=[]
	yerr_tup=[]
	z_tup=[]
	zerr_tup=[]

	graph1 = TGraphErrors(6)
	graph2 = TGraphErrors(6)
	graph1.SetTitle("Measured m(t) vs. true m(t)")
	graph2.SetTitle("Measured RMS (pull) vs. expected RMS (pull)")
	
	graph1_t = TGraphErrors(6)
	graph2_t = TGraphErrors(6)
	graph1_tup = TGraphErrors(6)
	graph2_tup = TGraphErrors(6)

	graph2_scaleup = TGraphErrors(1)
	graph1_scaleup = TGraphErrors(1)

	graph2_scaledown = TGraphErrors(1)
	graph1_scaledown = TGraphErrors(1)


	for i in range(0,len(listofnames)):

		histo = []
		histo.append(rootfile1.Get("m" + listofnames[i] + "_biasH"))
		histo.append(rootfile1.Get("m" + listofnames[i] + "_statuncH"))
		histo.append(rootfile1.Get("m" + listofnames[i] + "_pullH"))
		
		y.append(histo[0].GetMean())
		if (listofalgorithms[xi]=="emu_deltar"): yerr.append(histo[0].GetMeanError()*coef_deltar)
		elif(listofalgorithms[xi]=="emu_minmass"): yerr.append(histo[0].GetMeanError()*coef_minmass)

		z.append((histo[2].GetRMS()))
		if (listofalgorithms[xi]=="emu_deltar"): zerr.append(histo[2].GetRMSError())
		elif(listofalgorithms[xi]=="emu_minmass"): zerr.append(histo[2].GetRMSError())

		graph1.SetPoint(i+1, x[i], y[i])	
		graph2.SetPoint(i+1, x[i], z[i])
		graph1.SetPointError(i+1, 0, yerr[i])	
		graph2.SetPointError(i+1, 0, zerr[i])

#
		histo_t = []
		histo_t.append(rootfile1_t.Get("m" + listofnames[i] + "_biasH"))
		histo_t.append(rootfile1_t.Get("m" + listofnames[i] + "_statuncH"))
		histo_t.append(rootfile1_t.Get("m" + listofnames[i] + "_pullH"))
		
		y_t.append(histo_t[0].GetMean())
		if (listofalgorithms[xi]=="emu_deltar"): yerr_t.append(histo_t[0].GetMeanError()*coef_deltar)
		elif(listofalgorithms[xi]=="emu_minmass"): yerr_t.append(histo_t[0].GetMeanError()*coef_minmass)

		z_t.append((histo_t[2].GetRMS()))
		if (listofalgorithms[xi]=="emu_deltar"): zerr_t.append(histo_t[2].GetRMSError())
		elif(listofalgorithms[xi]=="emu_minmass"): zerr_t.append(histo_t[2].GetRMSError())

		graph1_t.SetPoint(i+1, x[i], y_t[i])	
		graph2_t.SetPoint(i+1, x[i], z_t[i])
		graph1_t.SetPointError(i+1, 0, yerr_t[i])	
		graph2_t.SetPointError(i+1, 0, zerr_t[i])

#

		histo_tup = []
		histo_tup.append(rootfile1_tup.Get("m" + listofnames[i] + "_biasH"))
		histo_tup.append(rootfile1_tup.Get("m" + listofnames[i] + "_statuncH"))
		histo_tup.append(rootfile1_tup.Get("m" + listofnames[i] + "_pullH"))
		
		y_tup.append(histo_tup[0].GetMean())
		if (listofalgorithms[xi]=="emu_deltar"): yerr_tup.append(histo_tup[0].GetMeanError()*coef_deltar)
		elif(listofalgorithms[xi]=="emu_minmass"): yerr_tup.append(histo_tup[0].GetMeanError()*coef_minmass)

		z_tup.append((histo_tup[2].GetRMS()))
		if (listofalgorithms[xi]=="emu_deltar"): zerr_tup.append(histo_tup[2].GetRMSError())
		elif(listofalgorithms[xi]=="emu_minmass"): zerr_tup.append(histo_tup[2].GetRMSError())

		graph1_tup.SetPoint(i+1, x[i], y_tup[i])	
		graph2_tup.SetPoint(i+1, x[i], z_tup[i])
		graph1_tup.SetPointError(i+1, 0, yerr_tup[i])	
		graph2_tup.SetPointError(i+1, 0, zerr_tup[i])

		if(listofnames[i]=="172v5" and listofalgorithms[xi]=="emu_deltar"):

			rootfile2 = TFile.Open("./mBl_Workspace_" + listofalgorithms[xi] + "_scaleup_pe.root", "READ")
			histo_up = []
			histo_up.append(rootfile2.Get("m" + listofnames[i] + "_biasH"))
			histo_up.append(rootfile2.Get("m" + listofnames[i] + "_statuncH"))
			histo_up.append(rootfile2.Get("m" + listofnames[i] + "_pullH"))

			graph1_scaleup.SetPoint(0, x[i], histo_up[0].GetMean())	
			graph2_scaleup.SetPoint(0, x[i], histo_up[2].GetRMS())

			graph1_scaleup.SetPointError(0, 0, histo_up[0].GetMeanError()*coef_deltar)	
			graph2_scaleup.SetPointError(0, 0, histo_up[2].GetRMSError())

			del rootfile2

			rootfile2 = TFile.Open("./mBl_Workspace_" + listofalgorithms[xi] + "_scaledown_pe.root", "READ")
			histo_down = []
			histo_down.append(rootfile2.Get("m" + listofnames[i] + "_biasH"))
			histo_down.append(rootfile2.Get("m" + listofnames[i] + "_statuncH"))
			histo_down.append(rootfile2.Get("m" + listofnames[i] + "_pullH"))

			graph1_scaledown.SetPoint(1, x[i], histo_down[0].GetMean())	
			graph2_scaledown.SetPoint(1, x[i], histo_down[2].GetRMS())
			graph1_scaledown.SetPointError(1, 0, histo_down[0].GetMeanError()*coef_deltar)	
			graph2_scaledown.SetPointError(1, 0, histo_down[2].GetRMSError())

			del rootfile2


		if(listofnames[i]=="172v5" and listofalgorithms[xi]=="emu_minmass"):

			rootfile2 = TFile.Open("./mBl_Workspace_" + listofalgorithms[xi] + "_scaleup_pe.root", "READ")
			histo_up2 = []
			histo_up2.append(rootfile2.Get("m" + listofnames[i] + "_biasH"))
			histo_up2.append(rootfile2.Get("m" + listofnames[i] + "_statuncH"))
			histo_up2.append(rootfile2.Get("m" + listofnames[i] + "_pullH"))

			graph1_scaleup.SetPoint(0, x[i], histo_up2[0].GetMean())	
			graph2_scaleup.SetPoint(0, x[i], histo_up2[2].GetRMS())
			graph1_scaleup.SetPointError(0, 0, histo_up2[0].GetMeanError()*coef_minmass)	
			graph2_scaleup.SetPointError(0, 0, histo_up2[2].GetRMSError())

			del rootfile2

			rootfile2 = TFile.Open("./mBl_Workspace_" + listofalgorithms[xi] + "_scaledown_pe.root", "READ")
			histo_down2 = []
			histo_down2.append(rootfile2.Get("m" + listofnames[i] + "_biasH"))
			histo_down2.append(rootfile2.Get("m" + listofnames[i] + "_statuncH"))
			histo_down2.append(rootfile2.Get("m" + listofnames[i] + "_pullH"))

			graph1_scaledown.SetPoint(1, x[i], histo_down2[0].GetMean())	
			graph2_scaledown.SetPoint(1, x[i], histo_down2[2].GetRMS())
			graph1_scaledown.SetPointError(1, 0, histo_down2[0].GetMeanError()*coef_minmass)	
			graph2_scaledown.SetPointError(1, 0, histo_down2[2].GetRMSError())

			del rootfile2

		c=TCanvas("bias", "c1", 1000, 1000)
		c.Divide(2,2,0.01,0.01)
		c_mt1=TCanvas("mt1", "cmt1", 1000, 1000)
		c_pull1=TCanvas("pull1", "cpull1", 1000, 1000)

		c.cd(1)
		histo[0].Draw("")

		c.cd(2)
		histo[1].Draw("")

		c.cd(3)
		histo[2].Draw("")
		c.SaveAs("./plots/" + listofalgorithms[xi] + "_m" + listofnames[i] + "_pseudoexp.pdf")

		c_mt1.cd()
		histo[0].Draw("")
		histo[0].SetLabelSize(0.07, "XY")
		histo[0].GetXaxis().SetTitleOffset(3.)
		histo[0].GetYaxis().SetTitleOffset(3.)
		c_mt1.SaveAs("./plots/" + listofalgorithms[xi] + "_m" + listofnames[i] + "_pseudoexp_mt.pdf")

		c_pull1.cd()
		histo[2].Draw("")
		histo[2].SetLabelSize(0.07, "XY")
		histo[2].GetXaxis().SetTitleOffset(3.)
		histo[2].GetYaxis().SetTitleOffset(3.)
		c_pull1.SaveAs("./plots/" + listofalgorithms[xi] + "_m" + listofnames[i] + "_pseudoexp_pull.pdf")
	
		c.Delete()
		c.Close()
		del histo
		del histo_t
		del histo_tup
		del c
		del c_mt1
		del c_pull1

	c2=TCanvas("total", "c2", 2000, 1000)
	c2.Divide(2,1,0.01,0.01)


	# fit

	graph1.Fit("pol1")
	graph2.Fit("pol1")
	graph1_t.Fit("pol1")
	graph2_t.Fit("pol1")
	graph1_tup.Fit("pol1")
	graph2_tup.Fit("pol1")

	line1.SetLineStyle(7)
	line2.SetLineStyle(7)

	pol1=graph1.GetFunction("pol1")
	pol2=graph2.GetFunction("pol1")
	pol1.SetLineColor(4)
	pol2.SetLineColor(4)
	pol1.SetLineStyle(2)
	pol2.SetLineStyle(2)

	graph1_scaledown.SetLineColor(6)
	graph2_scaledown.SetLineColor(6)
	graph1_scaledown.SetMarkerColor(6)
	graph2_scaledown.SetMarkerColor(6)
	graph1_scaledown.SetMarkerStyle(21)
	graph2_scaledown.SetMarkerStyle(21)
	graph1_scaledown.SetMarkerSize(1.0)
	graph2_scaledown.SetMarkerSize(1.0)
	graph1_scaleup.SetLineColor(2)
	graph2_scaleup.SetLineColor(2)
	graph1_scaleup.SetMarkerColor(2)
	graph2_scaleup.SetMarkerColor(2)
	graph1_scaleup.SetMarkerStyle(21)
	graph2_scaleup.SetMarkerStyle(21)
	graph2_scaleup.SetMarkerSize(1.0)
	graph2_scaleup.SetMarkerSize(1.0)
	graph1_scaledown.SetLineWidth(1)
	graph2_scaledown.SetLineWidth(1)
	graph1_scaleup.SetLineWidth(1)
	graph2_scaleup.SetLineWidth(1)

	graph1.SetLineColor(4)
	graph2.SetLineColor(4)
	graph1.SetMarkerColor(4)
	graph2.SetMarkerColor(4)
	graph1.SetMarkerStyle(21)
	graph2.SetMarkerStyle(21)
	graph1.SetMarkerSize(1.0)
	graph2.SetMarkerSize(1.0)
	graph1.SetLineWidth(1)
	graph2.SetLineWidth(1)

	pol1_t=graph1_t.GetFunction("pol1")
	pol2_t=graph2_t.GetFunction("pol1")
	pol1_t.SetLineColor(3)
	pol2_t.SetLineColor(3)
	pol1_t.SetLineStyle(2)
	pol2_t.SetLineStyle(2)

	graph1_t.SetLineColor(3)
	graph2_t.SetLineColor(3)
	graph1_t.SetMarkerColor(3)
	graph2_t.SetMarkerColor(3)
	graph1_t.SetMarkerStyle(21)
	graph2_t.SetMarkerStyle(21)
	graph1_t.SetMarkerSize(1.0)
	graph2_t.SetMarkerSize(1.0)
	graph1_t.SetLineWidth(1)
	graph2_t.SetLineWidth(1)

	pol1_tup=graph1_tup.GetFunction("pol1")
	pol2_tup=graph2_tup.GetFunction("pol1")
	pol1_tup.SetLineColor(28)
	pol2_tup.SetLineColor(28)
	pol1_tup.SetLineStyle(2)
	pol2_tup.SetLineStyle(2)

	graph1_tup.SetLineColor(28)
	graph2_tup.SetLineColor(28)
	graph1_tup.SetMarkerColor(28)
	graph2_tup.SetMarkerColor(28)
	graph1_tup.SetMarkerSize(1.0)
	graph2_tup.SetMarkerSize(1.0)
	graph1_tup.SetMarkerStyle(21)
	graph2_tup.SetMarkerStyle(21)
	graph1_tup.SetLineWidth(1)
	graph2_tup.SetLineWidth(1)


	a0=str(round(pol1.GetParameter(0),2))
	a1=str(round(pol1.GetParameter(1),2))
	b0=str(round(pol2.GetParameter(0),2))
	b1=str(round(pol2.GetParameter(1),2))

	a0_t=str(round(pol1_t.GetParameter(0),2))
	a1_t=str(round(pol1_t.GetParameter(1),2))
	b0_t=str(round(pol2_t.GetParameter(0),2))
	b1_t=str(round(pol2_t.GetParameter(1),2))

	a0_tup=str(round(pol1_tup.GetParameter(0),2))
	a1_tup=str(round(pol1_tup.GetParameter(1),2))
	b0_tup=str(round(pol2_tup.GetParameter(0),2))
	b1_tup=str(round(pol2_tup.GetParameter(1),2))

	c2.cd(1)
#	graph1.GetYaxis().SetTitle("m(t)-m(true)")
#	graph1.GetXaxis().SetTitle("m(true)")
	graph1.Draw("AP")
	graph1.GetXaxis().SetRangeUser(165.5,179.5)
	graph1.GetYaxis().SetRangeUser(-1.,1.)
	graph1.Draw("AP")
	line1.Draw("same")
	graph1_tup.Draw("P")
	graph1_t.Draw("P")
	graph1_scaleup.Draw("P")
	graph1_scaledown.Draw("P")
	graph1.Draw("P")


	leg = TLegend(0.15,0.15,0.4,0.35) 
	leg.AddEntry(pol1,"incl.only pu weight: y = " + a0 + " + " + a1 + "x", "ll")
	leg.AddEntry(pol1_t,"incl.topweight: y = " + a0_t + " + " + a1_t + "x", "ll")
	leg.AddEntry(pol1_tup,"incl.topweight up: y = " + a0_tup + " + " + a1_tup + "x", "ll")
	leg.AddEntry(graph1_scaleup, "scaleup", "ll")
	leg.AddEntry(graph1_scaledown, "scaledown", "ll")
	leg.SetTextSize(0.025)
 	leg.SetBorderSize(0)
	leg.SetFillStyle(0)
	leg.Draw()

	c2.cd(2)
#	graph2.GetYaxis().SetTitle("RMS(pull)")
#	graph2.GetXaxis().SetTitle("m(true)")
	graph2.Draw("AP")
	graph2.GetXaxis().SetRangeUser(165.5,179.5)
	graph2.GetYaxis().SetRangeUser(0.5,1.5)
	graph2.Draw("AP")
	line2.Draw("same")
	graph2_tup.Draw("P")
	graph2_t.Draw("P")
	graph2_scaleup.Draw("P")
	graph2_scaledown.Draw("P")
	graph2.Draw("P")



	leg2 = TLegend(0.45,0.7,0.6,0.9)
	leg2.AddEntry(pol2, "incl.only pu weight: y = " + b0 + " + " + b1 + "x", "ll")
	leg2.AddEntry(pol2_t, "incl.topweight: y = " + b0_t + " + " + b1_t + "x", "ll")
	leg2.AddEntry(pol2_tup, "incl.topweight up: = " + b0_tup + " + " + b1_tup + "x", "ll")
	leg2.AddEntry(graph2_scaleup, "scaleup", "ll")
	leg2.AddEntry(graph2_scaledown, "scaledown", "ll")
	leg2.SetTextSize(0.025)
 	leg2.SetBorderSize(0)
	leg2.SetFillStyle(0)
	leg2.Draw()

# plotting meas. mt separately

	c_mt =TCanvas("mt", "mt", 1000, 1000)
	c_mt.cd()
#	graph1.GetYaxis().SetTitle("m(t)-m(true)")
#	graph1.GetXaxis().SetTitle("m(true)")
	graph1.Draw("AP")
	graph1.GetXaxis().SetRangeUser(165.5,179.5)
	graph1.GetYaxis().SetRangeUser(-1.,1.)
	graph1.Draw("AP")
	line1.Draw("same")
	graph1_tup.Draw("P")
	graph1_t.Draw("P")
	graph1_scaleup.Draw("P")
	graph1_scaledown.Draw("P")
	graph1.Draw("P")


	leg_mt = TLegend(0.15,0.15,0.4,0.35) 
	leg_mt.AddEntry(pol1,"incl.only pu weight: y = " + a0 + " + " + a1 + "x", "ll")
	leg_mt.AddEntry(pol1_t,"incl.topweight: y = " + a0_t + " + " + a1_t + "x", "ll")
	leg_mt.AddEntry(pol1_tup,"incl.topweight up: y = " + a0_tup + " + " + a1_tup + "x", "ll")
	leg_mt.AddEntry(graph1_scaleup, "scaleup", "ll")
	leg_mt.AddEntry(graph1_scaledown, "scaledown", "ll")
	leg_mt.SetTextSize(0.025)
 	leg_mt.SetBorderSize(0)
	leg_mt.SetFillStyle(0)
	leg_mt.Draw()

# plotting Pull separately

	c_pull =TCanvas("pull", "pull", 1000, 1000)
	c_pull.cd()
#	graph2.GetYaxis().SetTitle("RMS(pull)")
#	graph2.GetXaxis().SetTitle("m(true)")
	graph2.Draw("AP")
	graph2.GetXaxis().SetRangeUser(165.5,179.5)
	graph2.GetYaxis().SetRangeUser(0.5,1.5)
	graph2.Draw("AP")
	line2.Draw("same")
	graph2_tup.Draw("P")
	graph2_t.Draw("P")
	graph2_scaleup.Draw("P")
	graph2_scaledown.Draw("P")
	graph2.Draw("P")



	leg2_mt = TLegend(0.5,0.7,0.75,0.9)
	leg2_mt.AddEntry(pol2, "incl.only pu weight: y = " + b0 + " + " + b1 + "x", "ll")
	leg2_mt.AddEntry(pol2_t, "incl.topweight: y = " + b0_t + " + " + b1_t + "x", "ll")
	leg2_mt.AddEntry(pol2_tup, "incl.topweight up: = " + b0_tup + " + " + b1_tup + "x", "ll")
	leg2_mt.AddEntry(graph2_scaleup, "scaleup", "ll")
	leg2_mt.AddEntry(graph2_scaledown, "scaledown", "ll")
	leg2_mt.SetTextSize(0.025)
 	leg2_mt.SetBorderSize(0)
	leg2_mt.SetFillStyle(0)
	leg2_mt.Draw()

	c2.SaveAs("./plots/" + listofalgorithms[xi] + "_allmases_pseudoexp.pdf")
	c_mt.SaveAs("./plots/" + listofalgorithms[xi] + "_allmases_pseudoexp_mt.pdf")
	c_pull.SaveAs("./plots/" + listofalgorithms[xi] + "_allmases_pseudoexp_pull.pdf")
	rootfile1.Close()

	del rootfile1
	del z
	del y
	
