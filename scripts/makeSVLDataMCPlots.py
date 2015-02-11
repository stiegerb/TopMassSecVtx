#! /usr/bin/env python
import os, sys
import ROOT
from runPlotter import runPlotter, addPlotterOptions

from makeSVLControlPlots import SELECTIONS, TREENAME, NBINS
from makeSVLControlPlots import getHistoFromTree

MASSXAXISTITLE = 'm(SV,lepton) [GeV]'

DATAMCPLOTS = [
	('SVLDeltaR' , NBINS, 0  , 5 , '#Delta R(Sec.Vtx., lepton)'),
	('SVNtrk'    , 8,     2  , 10, 'SV Track Multiplicity'),
	('LPt'       , NBINS, 20 , 200, 'Lepton pt [GeV]'),
	('JPt'       , NBINS, 30 , 200, 'Jet pt [GeV]'),
	# ('SVLMass'   , NBINS, XMIN, XMAX, MASSXAXISTITLE),
]

def writeDataMCHistos(tree, processName, outputFile):
	print " processing %s, %d entries ..." % (processName, tree.GetEntries())
	outputFile.cd()
	for tag,sel,_ in SELECTIONS:
		for var,nbins,xmin,xmax,titlex in DATAMCPLOTS:
			hist = getHistoFromTree(tree, sel=sel, var=var,
				              hname="%s_%s_%s"%(var,tag,processName),
			                  nbins=nbins,xmin=xmin,xmax=xmax,titlex=titlex)
			hist.Write(hist.GetName())

def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	try:

		treefiles = {} # procname -> filename
		for filename in os.listdir(args[0]):
			if not os.path.splitext(filename)[1] == '.root': continue
			procname = filename.split('_', 1)[1][:-5]
			treefiles[procname] = os.path.join(args[0],filename)

	except IndexError:
		print "Please provide a valid input directory"
		return -1

	outputFileName = os.path.join(opt.outDir, 'datamc_histos.root')
	ofi = ROOT.TFile(outputFileName, 'recreate')
	for proc,filename in treefiles.iteritems():
		tree = ROOT.TFile.Open(filename,'READ').Get(TREENAME)
		writeDataMCHistos(tree, proc, ofi)

	ofi.Write()
	ofi.Close()

	runPlotter(args[0], opt)
	runPlotter(outputFileName, opt)
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
	addPlotterOptions(parser)
	# parser.add_option('-v', '--verbose', dest='verbose', action="store",
	# 				  type='int', default=1,
	# 				  help='Verbose mode [default: %default (semi-quiet)]')
	# parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
	# 				  help='Output directory [default: %default]')
	(opt, args) = parser.parse_args()

	exit(main(args, opt))




