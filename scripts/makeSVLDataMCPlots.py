#! /usr/bin/env python
import os, sys
import ROOT
from copy import deepcopy
from runPlotter import runPlotter, addPlotterOptions
from UserCode.TopMassSecVtx.PlotUtils import setTDRStyle

from makeSVLMassHistos import SELECTIONS, TREENAME, NBINS
from makeSVLMassHistos import XMIN, XMAX, MASSXAXISTITLE
from makeSVLMassHistos import COMMONWEIGHT, LUMI

DATAMCPLOTS = [
	('SVLDeltaR'   , NBINS, 0  , 5 , '#Delta R(Sec.Vtx., lepton)'),
	('SVNtrk'      , 8,     2  , 10, 'SV Track Multiplicity'),
	('LPt'         , NBINS, 20 , 200, 'Lepton pt [GeV]'),
	('JPt'         , NBINS, 30 , 200, 'Jet pt [GeV]'),
	('SVLMass'     , NBINS, XMIN, XMAX, MASSXAXISTITLE),
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


def writeDataMCHistos(tree, processName, outputFile):
	print " processing %-30s %7d entries ..." % (processName, tree.GetEntries())
	outputFile.cd()
	for tag,sel,_ in SELECTIONS:
		for var,nbins,xmin,xmax,titlex in DATAMCPLOTS:
			hist = getHistoFromTree(tree, sel=sel, var=var,
				              hname="%s_%s_%s"%(var,tag,processName),
			                  nbins=nbins,xmin=xmin,xmax=xmax,titlex=titlex)
			hist.Write(hist.GetName())

			#MC truth
			if 'SVNtrk' in var:
				for b,addSel in [('Bpm',   'abs(BHadId)==521'),
						 ('B0',    'abs(BHadId)==511'),
						 ('Bs',    'abs(BHadId)==531'),
						 ('Others','abs(BHadId)!=521 && abs(BHadId)!=511 && abs(BHadId)!=531 && BHadId!=0'),
						 ('Fakes', 'BHadId==0')]:
					hist=getHistoFromTree(tree, sel=sel, var=var,
							      hname="%s_%s_%s_%s"%(var,tag,processName,b),
							      nbins=nbins,xmin=xmin,xmax=xmax,titlex=titlex)
					hist.Write(hist.GetName())

def resolveFilename(fname):
	if not os.path.splitext(fname)[1] == '.root': return None
	import re
	matchres = re.match(
	       r'(Data8TeV|MC8TeV)_([\w]+?)(?:_([0-9]{1,2}))?\.root', fname)

	if not matchres:
		print 'resolveFilename::file does not match template: %s' % fname
		return None

	# print fname, matchres.groups()
	isdata = (matchres.group(1) == 'Data8TeV')
	procname = matchres.group(2)
	splitno = matchres.group(3)
	return isdata, procname, splitno

def main(args, options):
	os.system('mkdir -p %s'%options.outDir)
	try:

		treefiles = {} # procname -> [filename1, filename2, ...]
		for filename in os.listdir(args[0]):
			if not os.path.splitext(filename)[1] == '.root': continue

			isdata, pname, splitno = resolveFilename(filename)

			if not pname in treefiles: treefiles[pname] = []
			treefiles[pname].append(os.path.join(args[0],filename))

	except IndexError:
		print "Please provide a valid input directory"
		return -1

	outputFileName = os.path.join(options.outDir, 'datamc_histos.root')
	if not options.cached:
		ofi = ROOT.TFile(outputFileName, 'recreate')
		for proc,filename in treefiles.iteritems():
			tree = ROOT.TFile.Open(filename[0],'READ').Get(TREENAME)
			writeDataMCHistos(tree, proc, ofi)

		ofi.Write()
		ofi.Close()


	# print 80*'='
	# print ' Producing charm peak control plots from histograms'
	# charmoptions = deepcopy(options)
	# charmoptions.filter = 'JPsi,D0,Dpm,DMDs,Ds2010' ## charm plots
	# charmoptions.excludeProcesses = 'QCD'
	# charmoptions.cutUnderOverFlow = True
	# runPlotter(args[0], charmoptions)

	print 80*'='
	print ' Producing DY control plots for scale factors'
	dycontroldir = os.path.join(options.outDir, 'dy_control')
	os.system('mkdir -p %s'% dycontroldir)
	dyoptions = deepcopy(options)
	dyoptions.outDir = dycontroldir
	dyoptions.filter = 'DY'
	runPlotter(args[0], dyoptions)

	scaleFactors = {}
	from extractDYScaleFactor import prepareDYScaleFactors
	scaleFactors = prepareDYScaleFactors(os.path.join(dycontroldir,
		                                              'plotter.root'),
		                                 plotfile=outputFileName,
		                                 inputdir=args[0],
		                                 options=options)

	print 80*'='
	print ' Producing unscaled MET plots for comparison'
	dyoptions.filter = 'MET_ee,MET_mm'
	runPlotter(args[0], dyoptions)

	print 80*'='
	print ' Producing (DY-scaled) control plots from histograms'
	options.filter = '!,JPsi,D0,Dpm,DMDs,DMDsmD0,Mjj' ## not the charm plots
	runPlotter(args[0], options, scaleFactors=scaleFactors)

	print 80*'='
	print ' Producing plots from SVLInfo trees'
	runPlotter(outputFileName, options, scaleFactors=scaleFactors)


	options.filter = 'Mjj,LJNtk' ## not the charm plots
	options.excludeProcesses = 'QCD'
	options.cutUnderOverFlow = True
	options.normToData = True
	options.ratioRange = '0.7,1.7'
	runPlotter(args[0], options, scaleFactors=scaleFactors)

	return 0


def addDataMCPlotOptions(parser):
	parser.add_option('--cached', dest='cached', action="store_true",
	                  help='Read the histos from the previous run')

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
	addDataMCPlotOptions(parser)
	(opt, args) = parser.parse_args()
	opt.lumi = LUMI

	setTDRStyle()
	gROOT.SetBatch(True)
	gStyle.SetOptTitle(0)
	gStyle.SetOptStat(0)


	exit(main(args, opt))




