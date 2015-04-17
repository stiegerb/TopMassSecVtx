#! /usr/bin/env python
import os, sys, re
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot, setTDRStyle
from makeSVLDataMCPlots import getHistoFromTree, resolveFilename
from makeSVLMassHistos import COMBINATIONS
from makeSVLMassHistos import TREENAME,LUMIWEIGHT
from pprint import pprint

MLBAXISTITLE = 'm_{lb} [GeV] (gen. level)'
MLBSELECTIONS = [
	('cor', '(CombInfo==1)*'+LUMIWEIGHT),
	('wro', '(CombInfo==0)*'+LUMIWEIGHT),
]

def makeControlPlot(systhistos, syst, tag, seltag, opt):
	hists = tuple([systhistos[(tag, syst, c)] for c,_ in COMBINATIONS])
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
	ctrlplot.show("control_%s_%s"%(syst,tag), opt.outDir)
	ctrlplot.reset()


def main(args, opt):
	trees = {}
	for filename in os.listdir(args[0]):
		if not os.path.splitext(filename)[1] == '.root': continue
		isdata, pname, splitno = resolveFilename(filename)
		treefile = os.path.join(args[0], filename)
		tfile = ROOT.TFile.Open(treefile,'READ')
		trees[pname] = tfile.Get(TREENAME)


	try:
		cachefile = open('genmlbhists.pck', 'r')
		hists = pickle.load(cachefile)
		print '>>> Read syst histos from cache (.svlsysthistos.pck)'
		cachefile.close()
	except IOError:
		hists = {}

		for tag,sel in MLBSELECTIONS:
			for pname in trees.keys():
				print '... processing', pname, tag
				hists[(pname,tag)] = getHistoFromTree(trees[pname],
				                                sel=sel,
				                                var='GenMlb',
			                                    hname="GenMlb_%s_%s"%(pname,tag),
		                                        nbins=100,xmin=0,xmax=200,
		                                        titlex=MLBAXISTITLE)

		cachefile = open('genmlbhists.pck', 'w')
		pickle.dump(hists, cachefile, pickle.HIGHEST_PROTOCOL)
		print '>>> Dumped histos to cachefile (genmlbhists.pck)'
		cachefile.close()


	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)


	for tag,_ in MLBSELECTIONS:
		plot = RatioPlot('genmlb')
		plot.normalized = False
		plot.add(hists[('TTJets_MSDecays_172v5', tag)],     'Nominal')
		plot.add(hists[('TTJets_MSDecays_scaleup', tag)],   'Q^{2} scale up')
		plot.add(hists[('TTJets_MSDecays_scaledown', tag)], 'Q^{2} scale down')
		plot.tag = "Generator level m_{lb} shape"
		if tag == 'cor':
			plot.subtag = "Correct combinations"
		else:
			plot.subtag = "Wrong combinations"
		plot.ratiotitle = 'Ratio wrt nominal'
		plot.titlex = MLBAXISTITLE
		plot.tagpos    = (0.22, 0.85)
		plot.subtagpos = (0.22, 0.78)
		plot.legpos = (0.20, 0.55)
		plot.ratiorange = (0.85, 1.15)
		plot.colors = [ROOT.kBlue-3, ROOT.kRed-4, ROOT.kOrange-3]
		plot.show("genmlb_scale_%s"%tag, opt.outDir)

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
	parser.add_option('-j', '--jobs', dest='jobs', action="store",
				  type='int', default=1,
				  help=('Number of jobs to run in parallel '
				  	    '[default: single]'))
	parser.add_option('-v', '--verbose', dest='verbose', action="store",
					  type='int', default=1,
					  help='Verbose mode [default: %default (semi-quiet)]')
	parser.add_option('-f', '--filter', dest='filter', default='',
					  help='Run only these tasks (comma separated list)')
	parser.add_option('-o', '--outDir', dest='outDir', default='genmlb',
					  help='Output directory [default: %default]')
	parser.add_option('-c', '--cache', dest='cache', action="store_true",
					  help='Read from cache')
	(opt, args) = parser.parse_args()

	setTDRStyle()
	exit(main(args, opt))




