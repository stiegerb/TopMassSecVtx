#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot, getRatio, setMaximums
from UserCode.TopMassSecVtx.CMS_lumi import CMS_lumi
from runPlotter import openTFile
from numpy import roots

# MASSES = [163.5, 166.5, 169.5, 172.5, 173.5, 175.5, 178.5, 181.5]
TREENAME = 'SVLInfo'
SELECTIONS = [
	('inclusive',  '1',
	 'Fully inclusive'),
	('mrankinc',  'SVLMassRank==1',
	 'Minimum mass comb.'),
	('mrank',     'SVLMassRank==1&&SVLDeltaR<2.0',
	 'Minimum mass comb., #Delta R < 2.0'),
	('mrank1',    'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0',
	 'Minimum mass comb., only SV in hardest b-jet, #Delta R < 2.0'),
	('drrankinc', 'SVLDeltaRRank==1',
	 'Minimum #Delta R comb.'),
	('drrank',    'SVLDeltaRRank==1&&SVLDeltaR<2.0',
	 'Minimum #Delta R comb., #Delta R < 2.0'),
	('drrank1',   'SVLDeltaRRank==1&&SVLDeltaR<2.0&&CombCat%2!=0',
	 'Minimum #Delta R comb., only SV in hardest b-jet, #Delta R < 2.0'),
	# ('mrank12',   'SVLDeltaR<2.0&&((NCombs<=2&&SVLMassRank==1)||'
	# 	          '(NCombs==4&&SVLMassRank<3))',
	#  'Two minimum mass comb., #Delta R < 2.0'),
	# ('drrank12',  'SVLDeltaR<2.0&&((NCombs<=2&&SVLDeltaRRank==1)||'
	# 	          '(NCombs==4&&SVLDeltaRRank<3))',
	#  'Two minimum #Delta R comb., #Delta R < 2.0'),
]

CONTROLVARS = [
	('SVLDeltaR' , 0  , 5   , '#Delta R(Sec.Vtx., lepton)'),
	('SVLxy'     , 0  , 5   , 'SV flight distance (Lxy) [cm]'),
	('LPt'       , 20 , 100 , 'Lepton pt [GeV]'),
	('SVPt'      , 0  , 100 , 'Sec.Vtx. pt [GeV]'),
	('JPt'       , 30 , 200 , 'Jet pt [GeV]'),
]

SYSTS = [
	('scaleup', 'Q^{2} Scale up',
		'MC8TeV_TTJets_MSDecays_scaleup.root'),
	('scaledown', 'Q^{2} Scale down',
		'MC8TeV_TTJets_MSDecays_scaledown.root'),
	('matchingup', 'ME/PS maching Scale up',
		'MC8TeV_TTJets_MSDecays_matchingup.root'),
	('matchingdown', 'ME/PS maching Scale down',
		'MC8TeV_TTJets_MSDecays_matchingdown.root'),
	('p11', 'P11 nominal',
		'MC8TeV_TTJets_TuneP11.root'),
	('p11nocr', 'P11 no color-reconnection',
		'MC8TeV_TTJets_TuneP11noCR.root'),
	('p11tev', 'P11 Tevatron tune',
		'MC8TeV_TTJets_TuneP11TeV.root'),
	('p11mpihi', 'P11 high multi-parton interaction',
		'MC8TeV_TTJets_TuneP11mpiHi.root'),
]

NBINS = 100
XMIN = 5.
XMAX = 200.
FITRANGE = (20., 140.)

NTRKBINS = [(2,3), (3,4), (4,5), (5,7) ,(7,1000)]

def projectFromTree(hist, varname, sel, tree, option=''):
	try:
		tree.Project(hist.GetName(),varname, sel, option)
		return True
	except Exception, e:
		raise e


def getSVLHistos(tree, sel,
				 var="SVLMass",
				 tag='', nbins=NBINS, xmin=XMIN, xmax=XMAX,
				 titlex=''):
	h_tot = ROOT.TH1D("%s_tot_%s"%(var,tag), "total"    , nbins, xmin, xmax)
	h_cor = ROOT.TH1D("%s_cor_%s"%(var,tag), "correct"  , nbins, xmin, xmax)
	h_wro = ROOT.TH1D("%s_wro_%s"%(var,tag), "wrong"    , nbins, xmin, xmax)
	h_unm = ROOT.TH1D("%s_unm_%s"%(var,tag), "unmatched", nbins, xmin, xmax)

	if sel=="": sel = "1"
	sel = "(%s)"%sel
	projectFromTree(h_tot, var, sel,                  tree)
	projectFromTree(h_cor, var, sel+'&&CombInfo==1',  tree)
	projectFromTree(h_wro, var, sel+'&&CombInfo==0',  tree)
	projectFromTree(h_unm, var, sel+'&&CombInfo==-1', tree)

	h_tot.SetLineColor(ROOT.kBlack)
	h_cor.SetLineColor(ROOT.kBlue)
	h_wro.SetLineColor(ROOT.kRed)
	h_unm.SetLineColor(ROOT.kSpring-5)

	for x in [h_tot, h_cor, h_wro, h_unm]:
		x.SetLineWidth(2)
		x.GetXaxis().SetTitle(titlex)
		x.Sumw2()

	return h_tot, h_cor, h_wro, h_unm

def getTopPtHistos(tree, sel,
				 var="SVLMass",
				 tag='', xmin=XMIN, xmax=XMAX,
				 titlex=''):
	h_tpt = ROOT.TH1D("%s_toppt_%s"%(var,tag),
					  "top pt weighted"    , NBINS, xmin, xmax)
	h_tup = ROOT.TH1D("%s_topptup_%s"%(var,tag),
					  "top pt weighted up" , NBINS, xmin, xmax)

	if sel=="": sel = "1"
	sel = "(%s)"%sel
	projectFromTree(h_tpt, var, sel+"*Weight[7]", tree)
	projectFromTree(h_tup, var, sel+"*Weight[8]", tree)

	h_tpt.SetLineColor(ROOT.kRed)
	h_tup.SetLineColor(ROOT.kRed-6)

	for x in [h_tpt, h_tup]:
		x.SetLineWidth(2)
		x.GetXaxis().SetTitle(titlex)
		x.Sumw2()

	return h_tpt, h_tup

def getNTrkHistos(tree, sel,
				 var="SVLMass",
				 tag='', xmin=XMIN, xmax=XMAX,
				 titlex=''):
	hists = []
	for ntk1,ntk2 in NTRKBINS:
		title = "%d #leq N_{trk.} < %d" %(ntk1, ntk2)
		if ntk2 > 100:
			title = "%d #leq N_{trk.}" %(ntk1)
		hist = ROOT.TH1D("%s_%d_%s"%(var,ntk1,tag), title, NBINS, xmin, xmax)
		tksel = "(SVNtrk>=%d&&SVNtrk<%d)"%(ntk1,ntk2)
		if sel=="": sel = "1"
		sel = "(%s)"%sel
		projectFromTree(hist, var, sel+"&&"+tksel, tree)
		hists.append(hist)

	for x in hists:
		x.SetLineWidth(2)
		x.GetXaxis().SetTitle(titlex)
		x.Sumw2()

	return hists

def makeControlPlot(hists, tag, seltag, opt):
	h_tot, h_cor, h_wro, h_unm = hists

	h_tot.Scale(1./h_tot.Integral())

	ctrlplot = RatioPlot('ctrlplot_%s'%tag)
	ctrlplot.add(h_cor, 'Correct')
	ctrlplot.add(h_wro, 'Wrong')
	ctrlplot.add(h_unm, 'Unmatched')
	ctrlplot.reference = h_tot
	ctrlplot.tag = ''
	ctrlplot.subtag = seltag
	ctrlplot.ratiotitle = 'Ratio wrt Total'
	ctrlplot.ratiorange = (0., 3.0)
	ctrlplot.colors = [ROOT.kBlue-3, ROOT.kRed-4, ROOT.kOrange-3]
	ctrlplot.show("control_%s"%tag, opt.outDir)
	ctrlplot.reset()


def fitChi2(chi2s, tag='', oname='chi2fit.pdf'):
	"""
	This does a pol2 fit to the given values and returns a callable
	that gives the width of the fit at a given chi2 value
	"""
	tg = ROOT.TGraph(len(chi2s)-2)
	points_to_remove = []
	for n,(mt,chi2) in enumerate(chi2s):
		if mt < 166. or mt > 180.:
			points_to_remove.append(n)
		# print n, mt, chi2
		tg.SetPoint(n, mt, chi2)
	tcanv = ROOT.TCanvas("chi2fit", "chi2fit", 400, 400)
	tcanv.cd()
	tg.SetMarkerStyle(20)
	tg.GetXaxis().SetTitle("m_{t, gen.} [GeV]")
	tg.GetYaxis().SetTitle("#chi^{2}")
	tg.Draw("AP")
	if len(tag)>0:
		tlat = ROOT.TLatex()
		tlat.SetTextFont(43)
		tlat.SetNDC(1)
		tlat.SetTextAlign(33)
		tlat.SetTextSize(10)
		tlat.DrawLatex(0.85, 0.78, tag)
	tcanv.SaveAs(oname)

	# need to reverse because the indices change when removing a point
	for n in reversed(points_to_remove):
		tg.RemovePoint(n)
	tf = ROOT.TF1("fitf", "pol2", 160., 190.)
	tg.Fit(tf, "WN0")
	# tf.SetLineColor(ROOT.kBlue)
	# tf.SetLineWidth(3)
	# tf.Draw("same")

	def getError(chi2test):
		coeff = [tf.GetParameter(2),
				 tf.GetParameter(1),
				 tf.GetParameter(0)-chi2test]
		mt1, mt2 = roots(coeff)
		return abs(mt1-mt2)


	return getError


def plotFracVsTopMass(fcor, fwro, funm, tag, oname):
	tg_cor = ROOT.TGraph(len(fcor))
	tg_wro = ROOT.TGraph(len(fwro))
	tg_unm = ROOT.TGraph(len(funm))

	np = 0
	for mt in sorted(fcor.keys()):
		tg_cor.SetPoint(np, mt, fcor[mt]/100.)
		tg_wro.SetPoint(np, mt, fwro[mt]/100.)
		tg_unm.SetPoint(np, mt, funm[mt]/100.)
		np += 1

	colors = [ROOT.kBlue-3, ROOT.kRed-4, ROOT.kOrange-3]
	for graph,color in zip([tg_cor, tg_wro, tg_unm], colors):
		graph.SetLineWidth(2)
		graph.SetLineColor(color)
		graph.SetMarkerStyle(20)
		graph.SetMarkerColor(color)
		graph.SetFillColor(color)
		graph.SetFillStyle(1001)


	tcanv = ROOT.TCanvas("fracvsmt_%s"%tag, "fracvsmt", 400, 400)
	tcanv.cd()

	h_axes = ROOT.TH2D("axes", "axes", 10, 162.5, 182.5, 10, 0., 1.)
	h_axes.GetXaxis().SetTitle("m_{t, gen.} [GeV]")
	h_axes.GetYaxis().SetTitleOffset(1.2)
	h_axes.GetYaxis().SetTitle("Fraction of combinations")
	h_axes.Draw()

	if len(tag)>0:
		tlat = ROOT.TLatex()
		tlat.SetTextFont(43)
		tlat.SetNDC(1)
		tlat.SetTextAlign(33)
		tlat.SetTextSize(10)
		tlat.DrawLatex(0.85, 0.78, tag)

	tleg = ROOT.TLegend(0.12, 0.75, .50, 0.89)
	tleg.SetBorderSize(0)
	tleg.SetFillColor(0)
	tleg.SetFillStyle(0)
	tleg.SetShadowColor(0)
	tleg.SetTextFont(43)
	tleg.SetTextSize(10)

	tleg.AddEntry(tg_cor, "Correct",   'F')
	tleg.AddEntry(tg_wro, "Wrong",     'F')
	tleg.AddEntry(tg_unm, "Unmatched", 'F')

	tg_cor.Draw("PL")
	tg_wro.Draw("PL")
	tg_unm.Draw("PL")

	tleg.Draw()
	# tcanv.Modified()
	tcanv.Update()

	for ext in ['.pdf','.png']:
		tcanv.SaveAs(oname+ext)

def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	try:

		massfiles = {} # mass -> filename
		# find mass scan files
		for filename in os.listdir(os.path.join(args[0],'mass_scan')):
			if not os.path.splitext(filename)[1] == '.root': continue
			masspos = 3 if 'MSDecays' in filename else 2
			mass = float(filename.split('_')[masspos][:3]) + 0.5
			if mass == 172.5: continue
			massfiles[mass] = os.path.join(args[0],'mass_scan',filename)

		## nominal file
		massfiles[172.5] = os.path.join(args[0],
										'MC8TeV_TTJets_MSDecays_172v5.root')

		systfiles = {} # systname -> filename
		for systname, systtag, systfile in SYSTS:
			if not systfile in os.listdir(os.path.join(args[0],'syst')):
				print ("File %s not found in %s" %
							  (systfile, os.path.join(args[0]), 'syst'))
				continue
			systfiles[systname] = os.path.join(args[0],'syst',systfile)

	except IndexError:
		print "Please provide a valid input directory"
		exit(-1)

	systtrees = {} # mass/systname -> tree
	for mass in sorted(massfiles.keys()):
		tfile = ROOT.TFile.Open(massfiles[mass],'READ')
		tree = tfile.Get(TREENAME)
		systtrees[mass] = tree

	for syst,_,_ in SYSTS:
		systtrees[syst] = ROOT.TFile.Open(systfiles[syst],'READ').Get(TREENAME)


	if not opt.cache:
		masshistos = {} # (tag, mass) -> h_tot, h_cor, h_wro, h_unm
		systhistos = {} # (tag) -> h_tptw, h_tptup, h_tptdn
		massntkhistos = {} # (tag) -> (h_ntk1, h_ntk2, h_ntk3, ..)
		for tag,sel,_ in SELECTIONS:
			for mass, tree in systtrees.iteritems():
				if not mass in massfiles.keys(): continue
				print ' ... processing %5.1f GeV %s' % (mass, sel)
				htag = ("%s_%5.1f"%(tag,mass)).replace('.','')
				masshistos[(tag, mass)] = getSVLHistos(tree, sel,
												   var="SVLMass", tag=htag,
												   titlex='m(SV,lepton) [GeV]')

			systhistos[(tag,'ptt_tot')] = getTopPtHistos(systtrees[172.5],
											  sel=sel,
											  var="SVLMass", tag=tag,
											  titlex='m(SV,lepton) [GeV]')

			systhistos[(tag,'ptt_cor')] = getTopPtHistos(systtrees[172.5],
											  sel=sel+'&&(CombInfo==1)',
											  var="SVLMass", tag=tag+'_cor',
											  titlex='m(SV,lepton) [GeV]')

			systhistos[(tag,'ptt_wro')] = getTopPtHistos(systtrees[172.5],
											  sel=sel+'&&(CombInfo==0)',
											  var="SVLMass", tag=tag+'_wro',
											  titlex='m(SV,lepton) [GeV]')

			for syst,_,_ in SYSTS:
				systhistos[(tag,syst)] = getSVLHistos(systtrees[syst],
										sel=sel,
										var="SVLMass", tag=tag+'_'+syst,
										titlex='m(SV,lepton) [GeV]')

			massntkhistos[tag] = getNTrkHistos(systtrees[172.5],
										   sel=sel,
										   tag=tag,
										   var='SVLMass',
										   titlex='m(SV,lepton) [GeV]')

		controlhistos = {} # (var) -> h_tot, h_cor, h_wro, h_unm
		for var,xmin,xmax,titlex in CONTROLVARS:
			controlhistos[var] = getSVLHistos(systtrees[172.5],"1",
											  var=var, tag="incl",
											  xmin=xmin, xmax=xmax,
											  titlex=titlex)


		cachefile = open(".svlhistos.pck", 'w')
		pickle.dump(masshistos,    cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(systhistos,    cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(massntkhistos,     cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(controlhistos, cachefile, pickle.HIGHEST_PROTOCOL)
		cachefile.close()

		ofi = ROOT.TFile(os.path.join(opt.outDir,'histos.root'), 'recreate')
		ofi.cd()
		for hist in [h for hists in masshistos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in systhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in controlhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in massntkhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		ofi.Write()
		ofi.Close()

	else:
		cachefile = open(".svlhistos.pck", 'r')
		masshistos    = pickle.load(cachefile)
		systhistos    = pickle.load(cachefile)
		massntkhistos = pickle.load(cachefile)
		controlhistos = pickle.load(cachefile)
		cachefile.close()

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)


	for var,_,_,_ in CONTROLVARS:
		makeControlPlot(controlhistos[var], var, 'Fully Inclusive', opt)

	errorGetters = {} # tag -> function(chi2) -> error
	systematics = {} # (seltag, systname) -> error
	for tag,sel,seltag in SELECTIONS:
		makeControlPlot(masshistos[(tag, 172.5)], tag, seltag, opt)

		ratplot = RatioPlot('ratioplot')
		ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
		ratplot.ratiorange = (0.5, 1.5)
		ratplot.reference = masshistos[(tag,172.5)][0]
		chisquares = []
		for mass in sorted(massfiles.keys()):
			legentry = 'm_{t} = %5.1f GeV' % mass
			ratplot.add(masshistos[(tag,mass)][0], legentry)
		ratplot.tag = 'All combinations'
		ratplot.subtag = seltag
		ratplot.show("massscan_%s_tot"%tag, opt.outDir)
		chi2s = ratplot.getChiSquares(rangex=FITRANGE)

		chi2stofit = []
		for legentry in sorted(chi2s.keys()):
			chi2stofit.append((float(legentry[8:-4]), chi2s[legentry]))
		errorGetters[tag] = fitChi2(chi2stofit,
									tag=seltag,
									oname=os.path.join(opt.outDir,
													   "chi2fit_%s.pdf"%tag))
		ratplot.reset()

		ratplot.reference = masshistos[(tag,172.5)][1]
		for mass in sorted(massfiles.keys()):
			legentry = '%5.1f GeV' % mass
			ratplot.add(masshistos[(tag,mass)][1], legentry)
		ratplot.tag = 'Correct combinations'
		ratplot.subtag = seltag
		ratplot.show("massscan_%s_cor"%tag, opt.outDir)
		ratplot.reset()

		ratplot.reference = masshistos[(tag,172.5)][2]
		for mass in sorted(massfiles.keys()):
			legentry = '%5.1f GeV' % mass
			ratplot.add(masshistos[(tag,mass)][2], legentry)
		ratplot.tag = 'Wrong combinations'
		ratplot.subtag = seltag
		ratplot.show("massscan_%s_wro"%tag, opt.outDir)
		ratplot.reset()

		ratplot.reference = masshistos[(tag,172.5)][3]
		for mass in sorted(massfiles.keys()):
			legentry = '%5.1f GeV' % mass
			ratplot.add(masshistos[(tag,mass)][3], legentry)
		ratplot.tag = 'Unmatched combinations'
		ratplot.subtag = seltag
		ratplot.show("massscan_%s_unm"%tag, opt.outDir)
		ratplot.reset()

		topptplot = RatioPlot('topptplot_%s'%tag)
		topptplot.add(masshistos[(tag, 172.5)][0], 'Nominal')
		topptplot.add(systhistos[(tag,'ptt_tot')][0], 'top pt weighted')
		topptplot.add(systhistos[(tag,'ptt_tot')][1], 'top pt weight up')
		topptplot.tag = 'Top pt systematic'
		topptplot.subtag = seltag
		topptplot.ratiotitle = 'Ratio wrt Nominal'
		topptplot.ratiorange = (0.5, 1.5)
		topptplot.colors = [ROOT.kBlack, ROOT.kRed, ROOT.kRed-6]
		topptplot.show("toppt_%s"%tag, opt.outDir)
		topptchi2 = max(topptplot.getChiSquares(rangex=FITRANGE).values())
		systematics[(tag,'toppt')] = (errorGetters[tag](topptchi2), topptchi2)
		topptplot.reset()

		topptplot.add(masshistos[(tag, 172.5)][1], 'Nominal')
		topptplot.reference = masshistos[(tag, 172.5)][1]
		topptplot.add(systhistos[(tag,'ptt_cor')][0], 'top pt weighted')
		topptplot.add(systhistos[(tag,'ptt_cor')][1], 'top pt weight up')
		topptplot.tag = 'Top pt systematic (correct comb.)'
		topptplot.subtag = seltag
		topptplot.ratiotitle = 'Ratio wrt Nominal'
		topptplot.ratiorange = (0.5, 1.5)
		topptplot.colors = [ROOT.kBlack, ROOT.kRed, ROOT.kRed-6]
		topptplot.show("toppt_cor_%s"%tag, opt.outDir)
		topptplot.reset()

		topptplot.add(masshistos[(tag, 172.5)][2], 'Nominal')
		topptplot.reference = masshistos[(tag, 172.5)][2]
		topptplot.add(systhistos[(tag,'ptt_wro')][0], 'top pt weighted')
		topptplot.add(systhistos[(tag,'ptt_wro')][1], 'top pt weight up')
		topptplot.tag = 'Top pt systematic (wrong comb.)'
		topptplot.subtag = seltag
		topptplot.ratiotitle = 'Ratio wrt Nominal'
		topptplot.ratiorange = (0.5, 1.5)
		topptplot.colors = [ROOT.kBlack, ROOT.kRed, ROOT.kRed-6]
		topptplot.show("toppt_wro_%s"%tag, opt.outDir)
		topptplot.reset()

		scaleplot = RatioPlot('scaleplot_%s'%tag)
		scaleplot.add(masshistos[(tag, 172.5)][0], 'Nominal')
		scaleplot.add(systhistos[(tag,'scaleup')][0],   'Q^{2} Scale up')
		scaleplot.add(systhistos[(tag,'scaledown')][0], 'Q^{2} Scale down')
		scaleplot.tag = 'Q^{2} Scale systematic'
		scaleplot.subtag = seltag
		scaleplot.ratiotitle = 'Ratio wrt Nominal'
		scaleplot.ratiorange = (0.5, 1.5)
		scaleplot.colors = [ROOT.kBlack, ROOT.kGreen+1, ROOT.kRed+1]
		scaleplot.show("scale_%s"%tag, opt.outDir)
		scalechi2 = max(scaleplot.getChiSquares(rangex=FITRANGE).values())
		systematics[(tag,'scale')] = (errorGetters[tag](scalechi2),
																 scalechi2)
		scaleplot.reset()

		matchplot = RatioPlot('matchplot_%s'%tag)
		matchplot.add(masshistos[(tag, 172.5)][0], 'Nominal')
		matchplot.add(systhistos[(tag,'matchingup')][0],
								  'Matching up')
		matchplot.add(systhistos[(tag,'matchingdown')][0],
								  'Matching down')
		matchplot.tag = 'ME/PS matching scale systematic'
		matchplot.subtag = seltag
		matchplot.ratiotitle = 'Ratio wrt Nominal'
		matchplot.ratiorange = (0.5, 1.5)
		matchplot.colors = [ROOT.kBlack, ROOT.kGreen+1, ROOT.kRed+1]
		matchplot.show("matching_%s"%tag, opt.outDir)
		matchchi2 = max(matchplot.getChiSquares(rangex=FITRANGE).values())
		systematics[(tag,'matching')] = (errorGetters[tag](matchchi2),
																 matchchi2)
		matchplot.reset()

		matchplot.reference = masshistos[(tag, 172.5)][1]
		matchplot.add(masshistos[(tag, 172.5)][1], 'Correct')
		matchplot.add(systhistos[(tag,'matchingup')][1],
								  'Matching up')
		matchplot.add(systhistos[(tag,'matchingdown')][1],
								  'Matching down')
		matchplot.tag = 'ME/PS matching scale systematic'
		matchplot.subtag = seltag+', correct comb.'
		matchplot.ratiotitle = 'Ratio wrt Nominal'
		matchplot.ratiorange = (0.5, 1.5)
		matchplot.colors = [ROOT.kBlack, ROOT.kGreen+1, ROOT.kRed+1]
		matchplot.show("matching_cor_%s"%tag, opt.outDir)
		matchplot.reset()

		matchplot.reference = masshistos[(tag, 172.5)][2]
		matchplot.add(masshistos[(tag, 172.5)][2], 'Wrong')
		matchplot.add(systhistos[(tag,'matchingup')][2],
								  'Matching up')
		matchplot.add(systhistos[(tag,'matchingdown')][2],
								  'Matching down')
		matchplot.tag = 'ME/PS matching scale systematic'
		matchplot.subtag = seltag+', wrong comb.'
		matchplot.ratiotitle = 'Ratio wrt Nominal'
		matchplot.ratiorange = (0.5, 1.5)
		matchplot.colors = [ROOT.kBlack, ROOT.kGreen+1, ROOT.kRed+1]
		matchplot.show("matching_wro_%s"%tag, opt.outDir)
		matchplot.reset()

		uecrplot = RatioPlot('uecrplot_%s'%tag)
		uecrplot.add(masshistos[(tag, 172.5)][0], 'Nominal (Z2*)')
		uecrplot.add(systhistos[(tag,'p11')][0],
								  'P11 Nominal')
		uecrplot.add(systhistos[(tag,'p11tev')][0],
								  'P11 Tevatron tune')
		uecrplot.add(systhistos[(tag,'p11mpihi')][0],
								  'P11 MPI High')
		uecrplot.add(systhistos[(tag,'p11nocr')][0],
								  'P11 No CR')
		uecrplot.tag = 'Underlying event / Color reconnection'
		uecrplot.subtag = seltag
		uecrplot.ratiotitle = 'Ratio wrt P11'
		uecrplot.ratiorange = (0.5, 1.5)
		uecrplot.reference = systhistos[(tag,'p11')][0]
		uecrplot.colors = [ROOT.kBlack, ROOT.kMagenta, ROOT.kMagenta+2,
							ROOT.kMagenta-9, ROOT.kViolet+2]
		uecrplot.show("uecr_%s"%tag, opt.outDir)
		uecrchi2s = uecrplot.getChiSquares(rangex=FITRANGE)
		uecrchi2 = max([uecrchi2s['P11 Nominal'],
						uecrchi2s['P11 Tevatron tune'],
						uecrchi2s['P11 MPI High'],
						uecrchi2s['P11 No CR']])
		systematics[(tag,'uecr')] = (errorGetters[tag](uecrchi2), uecrchi2)
		uecrplot.reset()


		ntkplot = RatioPlot('ntkplot_%s'%tag)
		ntkplot.add(masshistos[(tag, 172.5)][0], 'Sum')
		for hist in massntkhistos[tag]:
			ntkplot.add(hist, hist.GetTitle())
		ntkplot.colors = [ROOT.kOrange+10, ROOT.kGreen+4, ROOT.kGreen+2,
						  ROOT.kGreen, ROOT.kGreen-7, ROOT.kGreen-8]
		ntkplot.ratiorange = (0,3.0)
		ntkplot.ratiotitle = "Ratio wrt Sum"
		ntkplot.tag = 'm_{t} = 172.5 GeV'
		ntkplot.subtag = seltag
		ntkplot.show("ntkscan_%s"%tag, opt.outDir)
		ntkplot.reset()

	print 94*'-'
	print 'Estimated systematics (from a crude chi2 fit)'
	print '%20s | %-15s | %-15s | %-15s | %-15s' % (
										 'selection', 'scale', 'toppt',
										 'matching', 'uecr')
	for tag,_,_ in SELECTIONS:
			sys.stdout.write("%20s | " % tag)
			for syst in ['scale', 'toppt', 'matching', 'uecr']:
				err, chi2 = systematics[(tag,syst)]
				sys.stdout.write('%4.1f (%4.1f GeV)' % (chi2, err))
				sys.stdout.write(' | ')
			sys.stdout.write('\n')
	print 94*'-'

	for tag,sel,seltag in SELECTIONS:
		print 70*'-'
		print '%-10s: %s' % (tag, sel)
		fcor, fwro, funm = {}, {}, {}
		for mass in sorted(massfiles.keys()):
		# mass = 172.5
			hists = masshistos[(tag, mass)]
			n_tot, n_cor, n_wro, n_unm = (x.GetEntries() for x in hists)
			fcor[mass] = 100.*(n_cor/float(n_tot))
			fwro[mass] = 100.*(n_wro/float(n_tot))
			funm[mass] = 100.*(n_unm/float(n_tot))
			print ('  %5.1f GeV: %7d entries \t'
				   '(%4.1f%% corr, %4.1f%% wrong, %4.1f%% unmatched)' %
				   (mass, n_tot, fcor[mass], fwro[mass], funm[mass]))

		oname = os.path.join(opt.outDir, 'fracvsmt_%s'%tag)
		plotFracVsTopMass(fcor, fwro, funm, tag, oname)

	print 80*'-'

	exit(0)



if __name__ == "__main__":
	import sys
	tmpargv  = sys.argv[:]     # [:] for a copy, not reference
	sys.argv = []
	from ROOT import gROOT, gStyle
	sys.argv = tmpargv
	from optparse import OptionParser
	usage = """
	usage: %prog [options] input_directory
	"""
	parser = OptionParser(usage=usage)
	parser.add_option('-v', '--verbose', dest='verbose', action="store",
					  type='int', default=1,
					  help='Verbose mode [default: %default (semi-quiet)]')
	parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
					  help='Output directory [default: %default]')
	parser.add_option('-c', '--cache', dest='cache', action="store_true",
					  help='Read from cache')
	(opt, args) = parser.parse_args()

	main(args, opt)
	exit(-1)




