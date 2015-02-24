#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot
from numpy import roots

# MASSES = [163.5, 166.5, 169.5, 171.5, 172.5, 173.5, 175.5, 178.5, 181.5]
NBINS = 100
XMIN = 5.
XMAX = 200.
FITRANGE = (20., 140.)
MASSXAXISTITLE = 'm(SV,lepton) [GeV]'

#NTRKBINS = [(2,3), (3,4), (4,5), (5,7) ,(7,1000)]
NTRKBINS = [(2,3), (3,4), (4,1000)]
COMMONWEIGHT = "Weight[1]*Weight[4]*JESWeight[0]"

TREENAME = 'SVLInfo'
SELECTIONS = [
	('inclusive', 'abs(EvCat)<200', '#geq 1 lepton'),
	('ee',        'EvCat==-121',    'ee'),
	('em',        'EvCat==-143',    'e#mu'),
	('mm',        'EvCat==-169',    '#mu#mu'),
	('e',         'abs(EvCat)==11', 'e'),
	('m',         'abs(EvCat)==13', '#mu'),
	('inclusive_mrank1', 'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&abs(EvCat)<200', '#geq 1 lepton'),
	('ee_mrank1',        'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&EvCat==-121', 'ee'),
	('em_mrank1',        'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&EvCat==-143', 'e#mu'),
	('mm_mrank1',        'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&EvCat==-169', '#mu#mu'),
	('e_mrank1',         'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&abs(EvCat)==11', 'e'),
	('m_mrank1',         'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&abs(EvCat)==13', '#mu'),
]

CONTROLVARS = [
	('SVLDeltaR' , NBINS, 0  , 5   , '#Delta R(Sec.Vtx., lepton)'),
	('SVLxy'     , NBINS, 0  , 5   , 'SV flight distance (Lxy) [cm]'),
	('LPt'       , NBINS, 20 , 100 , 'Lepton pt [GeV]'),
	('SVPt'      , NBINS, 0  , 100 , 'Sec.Vtx. pt [GeV]'),
	('JPt'       , NBINS, 30 , 200 , 'Jet pt [GeV]'),
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

def projectFromTree(hist, varname, sel, tree, option=''):
	try:
		tree.Project(hist.GetName(),varname, sel, option)
		return True
	except Exception, e:
		raise e

def getHistoFromTree(tree, sel='', var="SVLMass",
	         hname="histo",
	         nbins=NBINS, xmin=XMIN, xmax=XMAX,
	         titlex='',
	         weight=COMMONWEIGHT):
	histo = ROOT.TH1D(hname, "histo" , nbins, xmin, xmax)
	if sel=="": sel = "1"
	sel = "(%s)" % sel
	if len(weight):
		sel = "%s*(%s)" % (sel, weight)
	projectFromTree(histo, var, sel, tree)
	histo.SetLineWidth(2)
	histo.GetXaxis().SetTitle(titlex)
	histo.Sumw2()
	histo.SetDirectory(0)
	return histo

def getNTrkHistos(tree, sel='', var="SVLMass", tag='',
		          nbins=NBINS, xmin=XMIN, xmax=XMAX,
		          titlex='', combsToProject=[('tot','')]):
	hists = []
	for ntk1,ntk2 in NTRKBINS:
		title = "%d #leq N_{trk.} < %d" %(ntk1, ntk2)
		if ntk2 > 100:
			title = "%d #leq N_{trk.}" %(ntk1)


		for comb,combSel in combsToProject:
			hist = ROOT.TH1D("%s_%s_%d_%s"%(var,comb,ntk1,tag),
				             title, nbins, xmin, xmax)
			tksel = "(SVNtrk>=%d && SVNtrk<%d)"%(ntk1,ntk2)
			finalSel=sel
			if finalSel=="": finalSel = "1"
			if combSel=="" : finalSel = "(%s)"%finalSel
			else           : finalSel = "(%s && %s)"%(finalSel,combSel)
			finalSel=finalSel+"&&"+tksel
			projectFromTree(hist, var, finalSel, tree)
			hists.append(hist)

	for x in hists:
		x.SetLineWidth(2)
		x.GetXaxis().SetTitle(titlex)
		x.Sumw2()

	return hists

def getSVLHistos(tree, sel='',
				 var="SVLMass",
				 tag='', nbins=NBINS, xmin=XMIN, xmax=XMAX,
				 titlex=''):
	h_tot = getHistoFromTree(tree, sel,
		             var=var, hname="%s_tot_%s"%(var,tag),
		             nbins=nbins, xmin=xmin, xmax=xmax, titlex=titlex)
	h_cor = getHistoFromTree(tree, sel+'&&CombInfo==1',
		             var=var, hname="%s_cor_%s"%(var,tag),
		             nbins=nbins, xmin=xmin, xmax=xmax, titlex=titlex)
	h_wro = getHistoFromTree(tree, sel+'&&CombInfo==0',
		             var=var, hname="%s_wro_%s"%(var,tag),
		             nbins=nbins, xmin=xmin, xmax=xmax, titlex=titlex)
	h_unm = getHistoFromTree(tree, sel+'&&CombInfo==-1',
		             var=var, hname="%s_unm_%s"%(var,tag),
		             nbins=nbins, xmin=xmin, xmax=xmax, titlex=titlex)
	h_tot.SetLineColor(ROOT.kBlack)
	h_cor.SetLineColor(ROOT.kBlue)
	h_wro.SetLineColor(ROOT.kRed)
	h_unm.SetLineColor(ROOT.kSpring-5)
	return h_tot, h_cor, h_wro, h_unm

def getTopPtHistos(tree, sel='',
				 var="SVLMass",
				 tag='',
				 nbins=NBINS,xmin=XMIN, xmax=XMAX,
				 titlex=''):
	weight = "%s*Weight[7]" % COMMONWEIGHT
	h_tpt = getHistoFromTree(tree, sel=sel,
	                  var=var, hname="%s_toppt_%s"%(var,tag),
	                  nbins=nbins,xmin=xmin,xmax=xmax,titlex=titlex,
	                  weight=weight)
	weight = "%s*Weight[8]" % COMMONWEIGHT
	h_tup = getHistoFromTree(tree, sel=sel,
	                  var=var, hname="%s_topptup_%s"%(var,tag),
	                  nbins=nbins,xmin=xmin,xmax=xmax,titlex=titlex,
	                  weight=weight)

	h_tpt.SetLineColor(ROOT.kRed)
	h_tup.SetLineColor(ROOT.kRed-6)
	return h_tpt, h_tup

def getBfragHistos(tree, sel='',
				   var="SVLMass",
				   tag='',
				   nbins=NBINS,xmin=XMIN, xmax=XMAX,
				   titlex=''):
	weight = "%s*SVBfragWeight[0]" % COMMONWEIGHT
	h_bfrag = getHistoFromTree(tree, sel=sel,
		              var=var, hname="%s_tot_%s_bfrag"%(var,tag),
	                  nbins=nbins,xmin=xmin,xmax=xmax,titlex=titlex,
	                  weight=weight)
	weight = "%s*SVBfragWeight[1]" % COMMONWEIGHT
	h_bfhar = getHistoFromTree(tree, sel=sel,
		              var=var, hname="%s_tot_%s_bfrag_hard"%(var,tag),
	                  nbins=nbins,xmin=xmin,xmax=xmax,titlex=titlex,
	                  weight=weight)
	weight = "%s*SVBfragWeight[2]" % COMMONWEIGHT
	h_bfsof = getHistoFromTree(tree, sel=sel,
		              var=var, hname="%s_tot_%s_bfrag_soft"%(var,tag),
	                  nbins=nbins,xmin=xmin,xmax=xmax,titlex=titlex,
	                  weight=weight)

	h_bfrag.SetLineColor(ROOT.kGreen+2)
	h_bfhar.SetLineColor(ROOT.kGreen+5)
	h_bfsof.SetLineColor(ROOT.kGreen)
	return h_bfrag, h_bfhar, h_bfsof

def getJESHistos(tree, sel='',
				 var="SVLMass",
				 tag='',
				 nbins=NBINS, xmin=XMIN, xmax=XMAX,
				 titlex=''):
	weight = COMMONWEIGHT.replace('JESWeight[0]', 'JESWeight[1]')
	h_jesup = getHistoFromTree(tree, sel=sel,
		              var=var, hname="%s_tot_%s_jes_up"%(var,tag),
	                  nbins=nbins,xmin=xmin,xmax=xmax,titlex=titlex,
	                  weight=weight)
	weight = COMMONWEIGHT.replace('JESWeight[0]', 'JESWeight[2]')
	h_jesdn = getHistoFromTree(tree, sel=sel,
		              var=var, hname="%s_tot_%s_jes_dn"%(var,tag),
	                  nbins=nbins,xmin=xmin,xmax=xmax,titlex=titlex,
	                  weight=weight)

	h_jesup.SetLineColor(ROOT.kBlue+2)
	h_jesdn.SetLineColor(ROOT.kBlue-6)

	return h_jesup, h_jesdn

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

def fitChi2(chi2s, tag='', oname='chi2fit.pdf', drawfit=False):
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
	tcanv = ROOT.TCanvas("chi2fit_%s"%tag, "chi2fit", 400, 400)
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

	if not drawfit:
		tcanv.SaveAs(oname)


	# need to reverse because the indices change when removing a point
	for n in reversed(points_to_remove):
		tg.RemovePoint(n)
	tf = ROOT.TF1("fitf", "pol2", 160., 190.)
	tg.Fit(tf, "WQ")
	if drawfit:
		tf.SetLineColor(ROOT.kBlue)
		tf.SetLineWidth(3)
		tf.Draw("same")
		tcanv.SaveAs(oname)

	def getError(chi2test):
		coeff = [tf.GetParameter(2),
				 tf.GetParameter(1),
				 tf.GetParameter(0)-chi2test]
		mt1, mt2 = roots(coeff)
		return abs(mt1-mt2)


	return getError

def plotFracVsTopMass(fcor, fwro, funm, tag, subtag, oname):
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

	tlat = ROOT.TLatex()
	tlat.SetTextFont(43)
	tlat.SetNDC(1)
	tlat.SetTextAlign(33)
	if len(tag)>0:
		tlat.SetTextSize(11)
		tlat.DrawLatex(0.85, 0.85, tag)
	if len(subtag)>0:
		tlat.SetTextSize(10)
		tlat.DrawLatex(0.85, 0.78, subtag)

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

		treefiles = {} # procname -> filename
		for filename in os.listdir(args[0]):
			if not os.path.splitext(filename)[1] == '.root': continue
			procname = filename.split('_', 1)[1][:-5]
			treefiles[procname] = os.path.join(args[0],filename)

		massfiles = {} # mass -> filename
		# find mass scan files
		for filename in os.listdir(os.path.join(args[0],'mass_scan')):
			if not os.path.splitext(filename)[1] == '.root': continue
			masspos = 3 if 'MSDecays' in filename else 2
			mass = float(filename.split('_')[masspos][:3]) + 0.5
			if mass == 172.5: continue
			massfiles[mass] = os.path.join(args[0],'mass_scan',filename)

		## nominal file
		massfiles[172.5] = os.path.join(args[0],'MC8TeV_TTJets_MSDecays_172v5.root')

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
		masshistos = {}     # (tag, mass) -> h_tot, h_cor, h_wro, h_unm
		fittertkhistos = {} # (tag, mass or syst) -> h_tot, h_cor, h_wro, h_unm
		systhistos = {}     # (tag) -> h_tptw, h_tptup, h_tptdn
		massntkhistos = {}  # (tag) -> (h_ntk1, h_ntk2, h_ntk3, ..)
		ntkhistos = {}      # (tag) -> h_ntk_tot, h_ntk_cor, h_ntk_wro, h_ntk_unm
		for tag,sel,_ in SELECTIONS:
			for mass, tree in systtrees.iteritems():
				if not mass in massfiles.keys(): continue
				htag = ("%s_%5.1f"%(tag,mass)).replace('.','')
				print ' ... processing %5.1f GeV %s tag=%s' % (mass, sel,htag)
				masshistos[(tag, mass)] = getSVLHistos(tree, sel,
								       var="SVLMass", tag=htag,
								       titlex=MASSXAXISTITLE)

				fittertkhistos[(tag,mass)] = getNTrkHistos(tree,
									   sel=sel,
									   tag=htag,
									   var='SVLMass',
									   titlex=MASSXAXISTITLE,
									   combsToProject=[('tot',''),
									                   ('cor','CombInfo==1'),
									                   ('wro','CombInfo==0'),
									                   ('unm','CombInfo==-1')])

			systhistos[(tag,'ptt_tot')] = getTopPtHistos(systtrees[172.5],
											  sel=sel,
											  var="SVLMass", tag=tag,
											  titlex=MASSXAXISTITLE)

			systhistos[(tag,'ptt_cor')] = getTopPtHistos(systtrees[172.5],
											  sel=sel+'&&(CombInfo==1)',
											  var="SVLMass", tag=tag+'_cor',
											  titlex=MASSXAXISTITLE)

			systhistos[(tag,'ptt_wro')] = getTopPtHistos(systtrees[172.5],
											  sel=sel+'&&(CombInfo==0)',
											  var="SVLMass", tag=tag+'_wro',
											  titlex=MASSXAXISTITLE)

			for syst,_,_ in SYSTS:
				systhistos[(tag,syst)] = getSVLHistos(systtrees[syst],
								      sel=sel,
								      var="SVLMass", tag=tag+'_'+syst,
								      titlex=MASSXAXISTITLE)

			systhistos[(tag,'bfrag')] = getBfragHistos(systtrees[172.5],
				                        sel=sel, var='SVLMass',
				                        tag=tag+'_bfrag',
				                        titlex=MASSXAXISTITLE)

			systhistos[(tag,'jes')] = getJESHistos(systtrees[172.5],
				                        sel=sel, var='SVLMass',
				                        tag=tag+'_jes',
				                        titlex=MASSXAXISTITLE)

			massntkhistos[tag] = getNTrkHistos(systtrees[172.5],
							   sel=sel,
							   tag=tag,
							   var='SVLMass',
							   titlex=MASSXAXISTITLE)


			ntkhistos[tag] = getSVLHistos(systtrees[172.5], sel,
										  var='SVNtrk', tag="_ntk_%s"%tag,
										  nbins=8, xmin=2, xmax=10,
										  titlex='Track Multiplicity')

		controlhistos = {} # (var) -> h_tot, h_cor, h_wro, h_unm
		for var,nbins,xmin,xmax,titlex in CONTROLVARS:
			controlhistos[var] = getSVLHistos(systtrees[172.5],"1",
											  var=var, tag="incl",
											  nbins=nbins,xmin=xmin, xmax=xmax,
											  titlex=titlex)


		cachefile = open(".svlhistos.pck", 'w')
		pickle.dump(masshistos,     cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(fittertkhistos, cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(systhistos,     cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(ntkhistos,      cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(massntkhistos,  cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(controlhistos,  cachefile, pickle.HIGHEST_PROTOCOL)
		cachefile.close()

		ofi = ROOT.TFile(os.path.join(opt.outDir,'histos.root'), 'recreate')
		ofi.cd()
		for hist in [h for hists in masshistos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in fittertkhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in systhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in controlhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in massntkhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in ntkhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		ofi.Write()
		ofi.Close()

	else:
		cachefile = open(".svlhistos.pck", 'r')
		masshistos     = pickle.load(cachefile)
		fittertkhistos = pickle.load(cachefile)
		systhistos     = pickle.load(cachefile)
		ntkhistos      = pickle.load(cachefile)
		massntkhistos  = pickle.load(cachefile)
		controlhistos  = pickle.load(cachefile)
		cachefile.close()

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)


	for var,_,_,_,_ in CONTROLVARS:
		makeControlPlot(controlhistos[var], var, 'Fully Inclusive', opt)

	errorGetters = {} # tag -> function(chi2) -> error
	systematics = {} # (seltag, systname) -> error
	for tag,sel,seltag in SELECTIONS:
		print "... processing %s"%tag
		makeControlPlot(masshistos[(tag, 172.5)], tag, seltag, opt)

		ratplot = RatioPlot('ratioplot')
		ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
		ratplot.ratiorange = (0.5, 1.5)
		ratplot.reference = masshistos[(tag,172.5)][0]
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
								    "chi2_simple_fit_%s.pdf"%tag),
									drawfit=False)
		ratplot.reset()

		ratplot.reference = masshistos[(tag,172.5)][1]
		for mass in sorted(massfiles.keys()):
			legentry = 'm_{t} = %5.1f GeV' % mass
			ratplot.add(masshistos[(tag,mass)][1], legentry)
		ratplot.tag = 'Correct combinations'
		ratplot.subtag = seltag
		ratplot.show("massscan_%s_cor"%tag, opt.outDir)
		ratplot.reset()

		ratplot.reference = masshistos[(tag,172.5)][2]
		for mass in sorted(massfiles.keys()):
			legentry = 'm_{t} = %5.1f GeV' % mass
			ratplot.add(masshistos[(tag,mass)][2], legentry)
		ratplot.tag = 'Wrong combinations'
		ratplot.subtag = seltag
		ratplot.show("massscan_%s_wro"%tag, opt.outDir)
		ratplot.reset()

		ratplot.reference = masshistos[(tag,172.5)][3]
		for mass in sorted(massfiles.keys()):
			legentry = 'm_{t} = %5.1f GeV' % mass
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

		bfragplot = RatioPlot('bfragplot_%s'%tag)
		bfragplot.add(masshistos[(tag, 172.5)][0], 'Nominal (Z2*)')
		bfragplot.add(systhistos[(tag,'bfrag')][0],
								  'rb LEP weighted')
		bfragplot.add(systhistos[(tag,'bfrag')][1],
								  'rb LEP hard weighted')
		bfragplot.add(systhistos[(tag,'bfrag')][2],
								  'rb LEP soft weighted')
		bfragplot.tag = 'B fragmentation'
		bfragplot.subtag = seltag
		bfragplot.ratiotitle = 'Ratio wrt Nominal'
		bfragplot.ratiorange = (0.5, 1.5)
		bfragplot.colors = [ROOT.kBlack, ROOT.kMagenta, ROOT.kMagenta+2,
							ROOT.kMagenta-9, ROOT.kViolet+2]
		bfragplot.show("bfrag_%s"%tag, opt.outDir)
		bfragchi2s = bfragplot.getChiSquares(rangex=FITRANGE)
		bfragchi2 = max([bfragchi2s['rb LEP weighted'],
						 bfragchi2s['rb LEP hard weighted'],
						 bfragchi2s['rb LEP soft weighted']])
		systematics[(tag,'bfrag')] = (errorGetters[tag](bfragchi2), bfragchi2)
		bfragplot.reset()

		jesplot = RatioPlot('jesplot_%s'%tag)
		jesplot.add(masshistos[(tag, 172.5)][0], 'Nominal')
		jesplot.add(systhistos[(tag,'jes')][0],
								  'JES up')
		jesplot.add(systhistos[(tag,'jes')][1],
								  'JES down')
		jesplot.tag = 'Jet energy scales'
		jesplot.subtag = seltag
		jesplot.ratiotitle = 'Ratio wrt Nominal'
		jesplot.ratiorange = (0.5, 1.5)
		jesplot.colors = [ROOT.kBlack, ROOT.kBlue+2, ROOT.kBlue-6]
		jesplot.show("jes_%s"%tag, opt.outDir)
		jeschi2s = jesplot.getChiSquares(rangex=FITRANGE)
		jeschi2 = max([jeschi2s['JES up'], jeschi2s['JES down']])
		systematics[(tag,'jes')] = (errorGetters[tag](jeschi2), jeschi2)
		jesplot.reset()

		ntkmassplot = RatioPlot('ntkmassplot_%s'%tag)
		ntkmassplot.add(masshistos[(tag, 172.5)][0], 'Sum')
		for hist in massntkhistos[tag]:
			ntkmassplot.add(hist, hist.GetTitle())
		ntkmassplot.colors = [ROOT.kOrange+10, ROOT.kGreen+4, ROOT.kGreen+2,
							  ROOT.kGreen, ROOT.kGreen-7, ROOT.kGreen-8]
		ntkmassplot.ratiorange = (0,3.0)
		ntkmassplot.ratiotitle = "Ratio wrt Sum"
		ntkmassplot.tag = 'm_{t} = 172.5 GeV'
		ntkmassplot.subtag = seltag
		ntkmassplot.show("ntkscan_%s"%tag, opt.outDir)
		ntkmassplot.reset()

	ntkplot = RatioPlot('ntkplot')
	ntkplot.colors = [ROOT.kGreen+2,
					  ROOT.kBlue, ROOT.kAzure-4, ROOT.kViolet+7,
					  ROOT.kRed-4, ROOT.kOrange-3, ROOT.kPink+7]
	ntkplot.ratiorange = (0.8,1.3)
	ntkplot.titlex = 'SV Track Multiplicity'
	ntkplot.ratiotitle = "Ratio wrt Incl."
	ntkplot.tag = 'm_{t} = 172.5 GeV'

	for tag,_,_ in SELECTIONS:
		ntkplot.add(ntkhistos[tag][0], tag)
	ntkplot.reference = ntkhistos['inclusive'][0]
	ntkplot.subtag = '(All combinations)'
	ntkplot.show("ntks_tot", opt.outDir)
	ntkplot.reset()

	for tag,_,_ in SELECTIONS:
		ntkplot.add(ntkhistos[tag][1], tag)
	ntkplot.reference = ntkhistos['inclusive'][1]
	ntkplot.subtag = '(Correct combinations)'
	ntkplot.show("ntks_cor", opt.outDir)
	ntkplot.reset()

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
		plotFracVsTopMass(fcor, fwro, funm, tag, seltag, oname)

	print 112*'-'
	print 'Estimated systematics (from a crude chi2 fit)'
	print '%20s | %-15s | %-15s | %-15s | %-15s | %-15s' % (
										 'selection', 'bfrag', 'scale',
										 'toppt', 'matching', 'uecr')
	for tag,_,_ in SELECTIONS:
			sys.stdout.write("%20s | " % tag)
			for syst in ['bfrag', 'scale', 'toppt', 'matching', 'uecr']:
				err, chi2 = systematics[(tag,syst)]
				sys.stdout.write('%4.1f (%4.1f GeV)' % (chi2*1e5, err))
				# sys.stdout.write('%4.1f (%4.1f GeV)' % (chi2, err))
				sys.stdout.write(' | ')
			sys.stdout.write('\n')
	print 112*'-'


	return 0



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

	exit(main(args, opt))




