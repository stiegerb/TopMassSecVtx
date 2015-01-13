#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import Plot, getRatio, setMaximums
from UserCode.TopMassSecVtx.CMS_lumi import CMS_lumi
from runPlotter import openTFile

TREENAME = 'SVLInfo'
SELECTIONS = [
	('mrankinc',  'SVLMassRank==1'),
	('mrank',     'SVLDeltaR<2.0&&SVLMassRank==1'),
	('drrankinc', 'SVLDeltaRRank==1'),
	('drrank',    'SVLDeltaR<2.0&&SVLDeltaRRank==1')
]

CONTROLVARS = [
	('SVLDeltaR' , 0  , 5   , '#Delta R(Sec.Vtx., lepton)'),
	('LPt'       , 20 , 100 , 'Lepton pt [GeV]'),
	('SVPt'      , 0  , 100 , 'Sec.Vtx. pt [GeV]'),
	('JPt'       , 30 , 200 , 'Jet pt [GeV]'),
]

# COLORS = [100, 91, 85, 78, 67, 61, 57, 51]
COLORS = [
	ROOT.kViolet-7,
	ROOT.kViolet-6,
	ROOT.kViolet+4,
	ROOT.kViolet+9,
	ROOT.kBlue,
	ROOT.kBlue-7,
	ROOT.kAzure+1,
	ROOT.kAzure+8,
]

NBINS = 100
XMAX = 200.

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

	tc.SaveAs(os.path.join(opt.outDir,"control_%s.pdf"%tag))

def makeSVLMassvsmtPlots(histos, tag, opt):
	for n,mass in enumerate(sorted(histos.keys())):
		histos[mass].SetLineColor(COLORS[n])

	for hist in histos.values():
		hist.Scale(1./hist.Integral())

	setMaximums(histos.values(), setminimum=0)

	tc = ROOT.TCanvas("massscan_%s"%tag, "massscan", 800, 800)
	tc.cd()

	tc.SetWindowSize(800 + (800 - tc.GetWw()), (800 + (800 - tc.GetWh())));
	p2 = ROOT.TPad("pad2","pad2",0,0,1,0.31);
	p2.SetTopMargin(0);
	p2.SetBottomMargin(0.3);
	p2.SetFillStyle(0);
	p2.Draw();
	p1 = ROOT.TPad("pad1","pad1",0,0.31,1,1);
	p1.SetBottomMargin(0);
	p1.Draw();
	p1.cd();

	tl = ROOT.TLegend(0.74, 0.75-0.035*max(len(histos)-3,0), .89, .89)
	tl.SetBorderSize(0)
	tl.SetFillColor(0)
	tl.SetShadowColor(0)
	tl.SetTextFont(42)
	tl.SetTextSize(0.035)

	histos.values()[0].Draw("axis")

	for mass in sorted(histos.keys()):
		tl.AddEntry(histos[mass], '%5.1f GeV'%mass, 'l')
		histos[mass].Draw("hist same")

	tl.Draw()


	p2.cd()

	ratioframe = histos[172.5].Clone('ratioframe')
	ratioframe.Reset('ICE')
	ratioframe.GetYaxis().SetRangeUser(0.50,1.50)
	ratioframe.GetYaxis().SetTitle('Ratio wrt 172.5 GeV')
	ratioframe.GetYaxis().SetNdivisions(5)
	ratioframe.GetYaxis().SetLabelSize(0.10)
	ratioframe.GetXaxis().SetLabelSize(0.10)
	ratioframe.GetYaxis().SetTitleSize(0.10)
	ratioframe.GetXaxis().SetTitleSize(0.12)
	ratioframe.GetYaxis().SetTitleOffset(0.37)
	ratioframe.GetXaxis().SetTitleOffset(1.0)
	ratioframe.Draw()

	ratios = {}
	# f = ROOT.TFile(os.path.join(opt.outDir,"histos.root"), "RECREATE")
	# f.cd()
	for mass,hist in histos.iteritems():
		ratios[mass] = getRatio(hist, histos[172.5])
		# ratios[mass].Write(ratios[mass].GetName())
	setMaximums(ratios.values())

	for ratio in ratios.values():
		ratio.Draw("hist same")

	tc.cd()
	tc.Modified()
	tc.Update()
	tc.SaveAs(os.path.join(opt.outDir,"masscan_%s.pdf"%tag))
	tc.Close()
	# f.Write()
	# f.Close()


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
		for mass, tree in masstrees.iteritems():
			for tag,sel in SELECTIONS:
				print ' ... processing %5.1f GeV %s' % (mass, sel)
				htag = ("%s_%5.1f"%(tag,mass)).replace('.','')
				histos[(tag, mass)] = getSVLHistos(tree, sel,
					                               var="SVLMass", tag=htag,
					                               titlex='m(SV,lepton) [GeV]')

		controlhistos = {} # (var) -> h_tot, h_cor, h_wro, h_unm
		for var,xmin,xmax,titlex in CONTROLVARS:
			controlhistos[var] = getSVLHistos(masstrees[172.5],"1",
				                              var=var, tag="incl",
				                              xmin=xmin, xmax=xmax,
				                              titlex=titlex)

		cachefile = open(".svlhistos.pck", 'w')
		pickle.dump(histos, cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(controlhistos, cachefile, pickle.HIGHEST_PROTOCOL)
		cachefile.close()

	else:
		cachefile = open(".svlhistos.pck", 'r')
		histos = pickle.load(cachefile)
		controlhistos = pickle.load(cachefile)
		cachefile.close()

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)


	for var,_,_,_ in CONTROLVARS:
		makeControlPlot(controlhistos[var], var, opt)

	for tag,sel in SELECTIONS:
		print tag, sel
		for mass in sorted(masstrees.keys()):
			hists = histos[(tag, mass)]
			n_tot, n_cor, n_wro, n_unm = (x.GetEntries() for x in hists)
			p_cor = 100.*(n_cor/float(n_tot))
			p_wro = 100.*(n_wro/float(n_tot))
			p_unm = 100.*(n_unm/float(n_tot))
			print ('  %5.1f GeV: %7d entries '
				   '(%2.0f%% corr, %2.0f%% wrong, %2.0f%% unmatched)' %
				   (mass, n_tot, p_cor, p_wro, p_unm))

		makeControlPlot(histos[(tag, 172.5)], tag, opt)

		makeSVLMassvsmtPlots(dict((mass, histos[(tag, mass)][0])
								   for mass in sorted(masstrees.keys())),
							 "%s_tot"%tag, opt)
		makeSVLMassvsmtPlots(dict((mass, histos[(tag, mass)][1])
								   for mass in sorted(masstrees.keys())),
							 "%s_cor"%tag, opt)
		makeSVLMassvsmtPlots(dict((mass, histos[(tag, mass)][2])
								   for mass in sorted(masstrees.keys())),
							 "%s_wro"%tag, opt)
		makeSVLMassvsmtPlots(dict((mass, histos[(tag, mass)][3])
								   for mass in sorted(masstrees.keys())),
							 "%s_unm"%tag, opt)



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
	parser.add_option('-l', '--lumi', dest='lumi', default=17123,
					  type='float',
					  help='Re-scale to integrated luminosity [pb]'
						   ' [default: %default]')
	parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
					  help='Output directory [default: %default]')
	parser.add_option('-c', '--cache', dest='cache', action="store_true",
					  help='Read from cache')
	parser.add_option("--jobs", default=0,
					  action="store", type="int", dest="jobs",
					  help=("Run N jobs in parallel."
							"[default: %default]"))
	(opt, args) = parser.parse_args()

	main(args, opt)
	exit(-1)




