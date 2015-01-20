#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot, getRatio, setMaximums
from UserCode.TopMassSecVtx.CMS_lumi import CMS_lumi
from runPlotter import openTFile

TREENAME = 'SVLInfo'
SELECTIONS = [
	('inclusive',  '',
	 'Fully inclusive'),
	('mrank1',    'SVLDeltaR<2.0&&SVLMassRank==1&&CombCat%2!=0',
	 'Minimum mass comb., only SV in hardest b-jet, #Delta R < 2.0'),
	('mrankinc',  'SVLMassRank==1',
	 'Minimum mass comb.'),
	('mrank',     'SVLDeltaR<2.0&&SVLMassRank==1',
	 'Minimum mass comb., #Delta R < 2.0'),
	('drrankinc', 'SVLDeltaRRank==1',
	 'Minimum #Delta R comb.'),
	('drrank',    'SVLDeltaR<2.0&&SVLDeltaRRank==1',
	 'Minimum #Delta R comb., #Delta R < 2.0'),
	('drrank1',    'SVLDeltaR<2.0&&SVLDeltaRRank==1&&CombCat%2!=0',
	 'Minimum #Delta R comb., only SV in hardest b-jet, #Delta R < 2.0'),
	# ('mrank12',   'SVLDeltaR<2.0&&((NCombs<=2&&SVLMassRank==1)||(NCombs==4&&SVLMassRank<3))',
	#  'Two minimum mass comb., #Delta R < 2.0'),
	# ('drrank12',  'SVLDeltaR<2.0&&((NCombs<=2&&SVLDeltaRRank==1)||(NCombs==4&&SVLDeltaRRank<3))',
	#  'Two minimum #Delta R comb., #Delta R < 2.0'),
]

CONTROLVARS = [
	('SVLDeltaR' , 0  , 5   , '#Delta R(Sec.Vtx., lepton)'),
	('LPt'       , 20 , 100 , 'Lepton pt [GeV]'),
	('SVPt'      , 0  , 100 , 'Sec.Vtx. pt [GeV]'),
	('JPt'       , 30 , 200 , 'Jet pt [GeV]'),
]

NBINS = 100
XMAX = 200.

NTRKBINS = [(2,3), (3,4), (4,5), (5,7) ,(7,1000)]

def projectFromTree(hist, varname, sel, tree, option=''):
	try:
		# tree.Draw(">>evlist", sel)
		# evlist = ROOT.gDirectory.Get("evlist")
		# tree.SetEventList(evlist)
		tree.Project(hist.GetName(),varname, sel, option)
		return True
	except Exception, e:
		raise e

def getSVLHistos(tree, sel,
	             var="SVLMass",
	             tag='', xmin=0, xmax=XMAX,
	             titlex=''):
	h_tot = ROOT.TH1D("%s_tot_%s"%(var,tag), "total"    , NBINS, xmin, xmax)
	h_cor = ROOT.TH1D("%s_cor_%s"%(var,tag), "correct"  , NBINS, xmin, xmax)
	h_wro = ROOT.TH1D("%s_wro_%s"%(var,tag), "wrong"    , NBINS, xmin, xmax)
	h_unm = ROOT.TH1D("%s_unm_%s"%(var,tag), "unmatched", NBINS, xmin, xmax)

	if sel=="": sel = "1"
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

def getNTrkHistos(tree, sel,
	             var="SVLMass",
	             tag='', xmin=0, xmax=XMAX,
	             titlex=''):
	hists = []
	for ntk1,ntk2 in NTRKBINS:
		title = "%d #leq N_{trk.} < %d" %(ntk1, ntk2)
		if ntk2 > 100:
			title = "%d #leq N_{trk.}" %(ntk1)
		hist = ROOT.TH1D("%s_%d_%s"%(var,ntk1,tag), title, NBINS, xmin, xmax)
		tksel = "(SVNtrk>=%d&&SVNtrk<%d)"%(ntk1,ntk2)
		if sel=="": sel = "1"
		projectFromTree(hist, var, sel+"&&"+tksel, tree)
		hists.append(hist)

	for x in hists:
		x.SetLineWidth(2)
		x.GetXaxis().SetTitle(titlex)
		x.Sumw2()

	return hists

def makeControlPlot(hists, tag, opt):
	h_tot, h_cor, h_wro, h_unm = hists

	for x in [h_cor, h_wro, h_unm]:
		x.Scale(1./x.Integral())

	setMaximums([h_cor, h_wro, h_unm], setminimum=0)

	tc = ROOT.TCanvas("control_%s"%tag, "Control", 800, 800)
	tc.cd()

	h_cor.SetLineColor(ROOT.kBlue-3)
	h_wro.SetLineColor(ROOT.kRed-4)
	h_unm.SetLineColor(ROOT.kOrange-3)

	tl = ROOT.TLegend(0.65, 0.75-0.035, .89, .89)
	tl.SetBorderSize(0)
	tl.SetFillColor(0)
	tl.SetShadowColor(0)
	tl.SetTextFont(42)
	tl.SetTextSize(0.035)
	# tl.AddEntry(h_tot , 'Total'     , 'l')
	tl.AddEntry(h_cor , 'Correct'   , 'l')
	tl.AddEntry(h_wro , 'Wrong'     , 'l')
	tl.AddEntry(h_unm , 'Unmatched' , 'l')

	# h_tot.Draw("hist")
	h_cor.Draw("hist")
	h_wro.Draw("hist same")
	h_unm.Draw("hist same")

	tl.Draw()
	CMS_lumi(pad=tc,iPeriod=2,iPosX=0,extraText='Simulation')

	tc.SaveAs(os.path.join(opt.outDir,"control_%s.pdf"%tag))


def main(args, opt):
	try:
		os.system('mkdir -p %s'%opt.outDir)

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

	except IndexError:
		print "Please provide a valid input directory"
		exit(-1)

	masstrees = {} # mass -> tree
	for mass in sorted(massfiles.keys()):
		file = ROOT.TFile.Open(massfiles[mass],'READ')
		tree = file.Get(TREENAME)
		masstrees[mass] = tree

	if not opt.cache:
		histos = {} # (tag, mass) -> h_tot, h_cor, h_wro, h_unm
		ntkhistos = {} # (tag) -> (h_ntk1, h_ntk2, h_ntk3, ..)
		for tag,sel,_ in SELECTIONS:
			for mass, tree in masstrees.iteritems():
				print ' ... processing %5.1f GeV %s' % (mass, sel)
				htag = ("%s_%5.1f"%(tag,mass)).replace('.','')
				histos[(tag, mass)] = getSVLHistos(tree, sel,
					                               var="SVLMass", tag=htag,
					                               titlex='m(SV,lepton) [GeV]')

			ntkhistos[tag] = getNTrkHistos(masstrees[172.5], sel=sel, tag=tag,
				                           var='SVLMass',
				                           titlex='m(SV,lepton) [GeV]')

		controlhistos = {} # (var) -> h_tot, h_cor, h_wro, h_unm
		for var,xmin,xmax,titlex in CONTROLVARS:
			controlhistos[var] = getSVLHistos(masstrees[172.5],"1",
				                              var=var, tag="incl",
				                              xmin=xmin, xmax=xmax,
				                              titlex=titlex)


		cachefile = open(".svlhistos.pck", 'w')
		pickle.dump(histos,        cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(ntkhistos,     cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(controlhistos, cachefile, pickle.HIGHEST_PROTOCOL)
		cachefile.close()

		ofi = ROOT.TFile(os.path.join(opt.outDir,'histos.root'), 'recreate')
		ofi.cd()
		for hist in [h for hists in histos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in controlhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in ntkhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		ofi.Write()
		ofi.Close()

	else:
		cachefile = open(".svlhistos.pck", 'r')
		histos        = pickle.load(cachefile)
		ntkhistos     = pickle.load(cachefile)
		controlhistos = pickle.load(cachefile)
		cachefile.close()

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)


	for var,_,_,_ in CONTROLVARS:
		makeControlPlot(controlhistos[var], var, opt)

	for tag,sel,seltag in SELECTIONS:
		makeControlPlot(histos[(tag, 172.5)], tag, opt)

		ratplot = RatioPlot('ratioplot')
		ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
		ratplot.ratiorange = (0.5, 1.5)
		for mass in sorted(masstrees.keys()):
			legentry = '%5.1f GeV' % mass
			ratplot.add(histos[(tag,mass)][0], legentry)
		ratplot.reference = histos[(tag,172.5)][0]
		ratplot.tag = 'All combinations'
		ratplot.subtag = seltag
		ratplot.show("massscan_%s_tot"%tag, opt.outDir)
		ratplot.reset()

		for mass in sorted(masstrees.keys()):
			legentry = '%5.1f GeV' % mass
			ratplot.add(histos[(tag,mass)][1], legentry)
		ratplot.reference = histos[(tag,172.5)][1]
		ratplot.tag = 'Correct combinations'
		ratplot.subtag = seltag
		ratplot.show("massscan_%s_cor"%tag, opt.outDir)
		ratplot.reset()

		for mass in sorted(masstrees.keys()):
			legentry = '%5.1f GeV' % mass
			ratplot.add(histos[(tag,mass)][2], legentry)
		ratplot.reference = histos[(tag,172.5)][2]
		ratplot.tag = 'Wrong combinations'
		ratplot.subtag = seltag
		ratplot.show("massscan_%s_wro"%tag, opt.outDir)
		ratplot.reset()

		for mass in sorted(masstrees.keys()):
			legentry = '%5.1f GeV' % mass
			ratplot.add(histos[(tag,mass)][3], legentry)
		ratplot.reference = histos[(tag,172.5)][3]
		ratplot.tag = 'Unmatched combinations'
		ratplot.subtag = seltag
		ratplot.show("massscan_%s_unm"%tag, opt.outDir)
		ratplot.reset()

		ntkplot = RatioPlot('ntkplot_%s'%tag)
		ntkplot.add(histos[(tag, 172.5)][0], 'Sum')
		for hist in ntkhistos[tag]:
			ntkplot.add(hist, hist.GetTitle())
		ntkplot.colors = [ROOT.kOrange+10, ROOT.kGreen+4, ROOT.kGreen+2,
		                  ROOT.kGreen, ROOT.kGreen-7, ROOT.kGreen-8]
		ntkplot.ratiorange = (0,3.0)
		ntkplot.ratiotitle = "Ratio wrt Sum"
		ntkplot.tag = 'm_{t} = 172.5 GeV'
		ntkplot.subtag = seltag
		ntkplot.show("ntkscan_%s"%tag, opt.outDir)
		ntkplot.reset()


	print 80*'-'
	for tag,sel,seltag in SELECTIONS:
		print tag, sel
		# for mass in sorted(masstrees.keys()):
		mass = 172.5
		hists = histos[(tag, mass)]
		n_tot, n_cor, n_wro, n_unm = (x.GetEntries() for x in hists)
		p_cor = 100.*(n_cor/float(n_tot))
		p_wro = 100.*(n_wro/float(n_tot))
		p_unm = 100.*(n_unm/float(n_tot))
		print ('  %5.1f GeV: %7d entries '
			   '(%2.0f%% corr, %2.0f%% wrong, %2.0f%% unmatched)' %
			   (mass, n_tot, p_cor, p_wro, p_unm))
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




