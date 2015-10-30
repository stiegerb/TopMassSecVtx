#! /usr/bin/env python
import os, sys, re
import os.path as osp
import ROOT
import pickle
from numpy import roots

from UserCode.TopMassSecVtx.PlotUtils import RatioPlot
from makeSVLMassHistos import NTRKBINS, COMMONWEIGHT, TREENAME
from makeSVLMassHistos import SELECTIONS, COMBINATIONS, INCSEL,EMSEL
from makeSVLSystPlots import SYSTSFROMWEIGHTS
from makeSVLDataMCPlots import resolveFilename, getHistoFromTree

BFRAGSYSTS = [s for s in SYSTSFROMWEIGHTS if 'bfrag' in s[0]]
	# ('bfrag',       'Z2* rb LEP',                'SVBfragWeight[0]',       ['tot']),
	# ('bfragup',     'Z2* rb LEP hard',           'SVBfragWeight[1]',       ['tot']),
	# ('bfragdn',     'Z2* rb LEP soft',           'SVBfragWeight[2]',       ['tot']),
	# ('bfragp11',    'P11 fragmentation',         'SVBfragWeight[3]',       ['tot']),
	# ('bfragpete',   'Z2* Peterson',              'SVBfragWeight[4]',       ['tot']),
	# ('bfraglund',   'Z2* Lund',                  'SVBfragWeight[5]',       ['tot']),

VARS = [
	('SVPtChFrac', 100, 0., 2., 'SVPtChFrac'),
	('SVMass',      60, 0., 5., 'Secondary Vertex Mass [GeV]'),
	]

def makeHistos((url, name)):
	print "... processing", url
	tree = ROOT.TFile.Open(url,'READ').Get(TREENAME)
	histos = {}
	# selection = "SVMassWeight*(SVLCombRank>0 && %s)"%INCSEL
	selection = "(SVLCombRank>0 && %s)"%INCSEL
	# selection = "(SVLCombRank>0 && %s)"%EMSEL
	for varname, nbins, xmin, xmax, titlex in VARS:
		for ntk1,ntk2 in NTRKBINS:
			tksel = "(SVNtrk>=%d && SVNtrk<%d)"%(ntk1,ntk2)
			finalsel = "%s*%s" %(selection,tksel)
			histos[(varname, ntk1)] = getHistoFromTree(
				                              tree, sel=finalsel, var=varname,
			                                  hname='%s_%s_%d'%(name, varname, ntk1),
			                                  nbins=nbins, xmin=xmin, xmax=xmax,
			                                  titlex=titlex)
	return name,histos

def makeSVMassPlots(histodict):
	ratplot = RatioPlot('SVMass')
	ratplot.normalized = True
	ratplot.ratiorange = (0.5,1.5)
	ratplot.legpos = (0.65, 0.60)
	ratplot.ratiotitle = 'Data/MC'
	ratplot.extratext = '' #Work in Progress'
	ratplot.tag = "Inclusive"
	# ratplot.tag = "e#mu channel"
	ratplot.tagpos = (0.80,0.55)
	ratplot.add(histodict[('nominal','SVMass',3)], 'N_{trk}=3 t#bar{t} MC', includeInRatio=False)
	ratplot.add(histodict[('data',   'SVMass',3)], 'N_{trk}=3 Data',        includeInRatio=True)
	ratplot.add(histodict[('nominal','SVMass',4)], 'N_{trk}=4 t#bar{t} MC', includeInRatio=False)
	ratplot.add(histodict[('data',   'SVMass',4)], 'N_{trk}=4 Data',        includeInRatio=True)
	ratplot.add(histodict[('nominal','SVMass',5)], 'N_{trk}=5 t#bar{t} MC', includeInRatio=False)
	ratplot.add(histodict[('data',   'SVMass',5)], 'N_{trk}=5 Data',        includeInRatio=True)

	ratplot.reference =     [histodict[('nominal','SVMass',3)]]
	ratplot.reference.append(histodict[('nominal','SVMass',4)])
	ratplot.reference.append(histodict[('nominal','SVMass',5)])

	ratplot.colors = [ROOT.kMagenta+1, ROOT.kMagenta+1,
	                  ROOT.kViolet+2, ROOT.kViolet+2,
	                  ROOT.kAzure+7, ROOT.kAzure+7]

	ratplot.drawoptions =  ['hist', 'PE', 'hist', 'PE', 'hist', 'PE']
	ratplot.markerstyles = [24, 24, 25, 25, 26, 26]
	ratplot.markersizes = len(ratplot.histos)*[1.4]
	ratplot.show('svmassplot',opt.outDir)
	ratplot.saveRatios('svmass_weights',opt.outDir,['SVMass_weight_3','SVMass_weight_4','SVMass_weight_5'])

def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	treefiles = {} # procname -> filename
	try:
		# Get the data files
		treefiles['data'] = []
		for fname in os.listdir(args[0]):
			if not osp.splitext(fname)[1] == '.root': continue
			isdata,procname,splitno = resolveFilename(fname)
			if not isdata: continue

			treefiles['data'].append(osp.join(args[0],fname))

		# Get the split nominal files
		treefiles['nominal'] = []
		for fname in os.listdir(osp.join(args[0],'Chunks')):
			if not osp.splitext(fname)[1] == '.root': continue
			isdata,procname,splitno = resolveFilename(fname)
			if not procname == 'TTJets_MSDecays_172v5': continue
			if not splitno: continue # file is split

			treefiles['nominal'].append(osp.join(args[0],'Chunks',fname))
		if len(treefiles['nominal']) < 20:
			print "ERROR >>> Missing files for split nominal sample?"
			return -1

	except IndexError:
		print "Please provide a valid input directory"
		exit(-1)

	if not opt.cache:

		tasks = []
		for tag,files in treefiles.iteritems():
			for n,fname in enumerate(files):
				tasks.append((fname, '%s_%d'%(tag,n)))

		frachistos = {}
		if not opt.jobs>1:
			for url, name in tasks:
				_,frachistos[name] = makeHistos((url, name))
		else:
			allhistos = []
			from multiprocessing import Pool
			p = Pool(opt.jobs)
			allhistos = p.map(makeHistos, tasks)
			p.close()
			p.join()
			for name,hists in allhistos:
				frachistos[name] = hists

		# Merge the histos
		frachistos_merged = {}
		for tag in treefiles.keys():
			for n in range(len(treefiles[tag])):
				name = '%s_%d'%(tag,n)
				for ntk,_ in NTRKBINS:
					for var in [v[0] for v in VARS]:
						hist = frachistos[name][(var, ntk)].Clone()
						if not (tag,var,ntk) in frachistos_merged:
							frachistos_merged[(tag,var,ntk)] = hist
						else:
							frachistos_merged[(tag,var,ntk)].Add(hist)

		cachefile = open(".svptfrachistos.pck", 'w')
		pickle.dump(frachistos_merged, cachefile, pickle.HIGHEST_PROTOCOL)
		print ">>> Wrote frachistos to cache (.svptfrachistos.pck)"
		cachefile.close()

	cachefile = open(".svptfrachistos.pck", 'r')
	frachistos = pickle.load(cachefile)
	print '>>> Read frachistos from cache (.svptfrachistos.pck)'
	cachefile.close()

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)

	makeSVMassPlots(frachistos)

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
	parser.add_option('-j', '--jobs', dest='jobs', action="store",
				  type='int', default=1,
				  help=('Number of jobs to run in parallel '
				  	    '[default: single]'))
	parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
					  help='Output directory [default: %default]')
	parser.add_option('-c', '--cache', dest='cache', action="store_true",
					  help='Read from cache')
	(opt, args) = parser.parse_args()


	exit(main(args, opt))




