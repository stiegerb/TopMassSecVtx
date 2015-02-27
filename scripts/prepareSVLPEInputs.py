#! /usr/bin/env python
import os, sys, re
import os.path as osp
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot
from makeSVLMassHistos import NBINS, XMIN, XMAX, MASSXAXISTITLE
from makeSVLMassHistos import NTRKBINS, COMMONWEIGHT, TREENAME
from makeSVLMassHistos import SELECTIONS, COMBINATIONS
from makeSVLMassHistos import runSVLInfoTreeAnalysis, runTasks
from makeSVLDataMCPlots import resolveFilename
from makeSVLSystPlots import ALLSYSTS

LUMI = 17123

def makeSystTask(tag, sel, pname, hname_to_keys, weight='1'):
	tasks = []
	hname = "SVLMass_tot_%s_%s" % (tag, pname)
	finalsel = "%s*%s*(%s)"%(COMMONWEIGHT, weight, sel)

	tasks.append((hname, 'SVLMass', finalsel,
				  NBINS, XMIN, XMAX, MASSXAXISTITLE))
	hname_to_keys[hname] = (tag, pname)

	for ntk1,ntk2 in NTRKBINS:
		tksel = "(SVNtrk>=%d&&SVNtrk<%d)"%(ntk1,ntk2)
		finalsel = "%s*%s*(%s&&%s)"%(COMMONWEIGHT, weight, sel, tksel)
		hname = "SVLMass_tot_%s_%s_%d" % (tag, pname, ntk1)
		tasks.append((hname, 'SVLMass', finalsel,
					  NBINS, XMIN, XMAX, MASSXAXISTITLE))
		hname_to_keys[hname] = (tag, pname, ntk1)
	return tasks

def gatherHistosFromFiles(tasklist, files, dirname, hname_to_keys):
	## First extract a list of ALL histogram names from the tasklist
	hnames = [t[0] for tasks in tasklist.values() for t in tasks]

	histos = {}
	for ifilen in os.listdir(dirname):
		if not osp.splitext(ifilen)[1] == '.root': continue
		ifile = ROOT.TFile.Open(osp.join(dirname,ifilen), 'READ')

		for hname in hnames:
			keys = hname_to_keys[hname]
			pname = keys[1]

			tfilens = [osp.basename(x) for x in files[pname]]
			if not ifilen in tfilens: continue

			try:
				histo = ifile.Get(hname)
				try:
					histo.SetDirectory(0)

					## Add histograms with same names
					if not keys in histos:
						histos[keys] = histo
					else:
						histos[keys].Add(histo)
				except AttributeError: pass

			except ReferenceError:
				print hname, "not found in", ifilen
	return histos

def makeBackgroundHistos(treefiles, opt):
	hname_to_keys = {} # hname -> (tag, syst, comb)
	tasklist = {} # treefile -> tasklist

	for pname in treefiles.keys():
		if not pname in tasklist: tasklist[pname] = []
		for tag,sel,_ in SELECTIONS:
			tasks = []
			hname = "SVLMass_tot_%s_%s" % (tag, pname)
			finalsel = "%s*(%s)"%(COMMONWEIGHT, sel)

			tasks.append((hname, 'SVLMass', finalsel,
						  NBINS, XMIN, XMAX, MASSXAXISTITLE))
			hname_to_keys[hname] = (tag, pname, 'tot') ## add the 'tot'

			for ntk1,ntk2 in NTRKBINS:
				tksel = "(SVNtrk>=%d&&SVNtrk<%d)"%(ntk1,ntk2)
				finalsel = "%s*(%s&&%s)"%(COMMONWEIGHT, sel, tksel)
				hname = "SVLMass_tot_%s_%s_%d" % (tag, pname, ntk1)
				tasks.append((hname, 'SVLMass', finalsel,
							  NBINS, XMIN, XMAX, MASSXAXISTITLE))
				hname_to_keys[hname] = (tag, pname, 'tot', ntk1)

			tasklist[pname] += tasks

	if not opt.cache:
		runTasks(treefiles, tasklist, opt, 'bg_histos')

	bghistos = {} # (tag, pname, comb) -> histo
	bghistos = gatherHistosFromFiles(tasklist, treefiles,
								   osp.join(opt.outDir, 'bg_histos'),
								   hname_to_keys)

	cachefile = open(".svlbghistos.pck", 'w')
	pickle.dump(bghistos, cachefile, pickle.HIGHEST_PROTOCOL)
	cachefile.close()
	return bghistos


def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	treefiles = {} # procname -> filename
	try:
		for fname in os.listdir(args[0]):
			if not osp.splitext(fname)[1] == '.root': continue
			isdata,procname,splitno = resolveFilename(fname)
			if isdata: continue
			if procname == 'QCDPt30to80':           continue ## exclude QCD
			if procname == 'TTJets_MSDecays_172v5': continue ## have those already

			if not procname in treefiles:
				treefiles[procname] = []
			treefiles[procname].append(osp.join(args[0],fname))

	except IndexError:
		print "Please provide a valid input directory"
		exit(-1)


	bghistos = makeBackgroundHistos(treefiles, opt)

	## Add up the background histos with proper scales
	cachefile = open(".xsecweights.pck", 'r')
	xsecweights = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read xsec weights from cache (.xsecweights.pck)'

	cachefile = open(".svldyscalefactors.pck", 'r')
	dySFs = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read DY scale factors from cache (.svldyscalefactors.pck)'

	bghistos_added = {}
	for tag,_,_ in SELECTIONS:
		for ntk,_ in NTRKBINS:
			for pname in treefiles.keys():
				hname = "SVLMass_tot_%s_bg_%d"%(tag,ntk)
				hist = bghistos[tag, pname, 'tot', ntk].Clone("%s_%s" % (
															  hname, pname))

				## Apply scales
				hist.Scale(LUMI*xsecweights["MC8TeV_%s"%pname])
				if ((tag.startswith('ee') or tag.startswith('mm'))
					 and pname.startswith('DY')):
					hist.Scale(dySFs[tag[:2]])

				if not (tag, ntk) in bghistos_added:
					bghistos_added[(tag, ntk)] = hist
					bghistos_added[(tag, ntk)].SetName(hname)
				else:
					bghistos_added[(tag, ntk)].Add(hist)


	## Read syst histos:
	cachefile = open(".svlsysthistos.pck", 'r')
	systhistos = pickle.load(cachefile)
	cachefile.close()

	PEinputs = {} ## (tag, syst, ntk) -> histogram
	ofi = ROOT.TFile.Open(osp.join(opt.outDir,'pe_inputs.root'),'RECREATE')
	ofi.cd()


	for syst,_,_ in ALLSYSTS:
		odir = ofi.mkdir(syst)
		odir.cd()
		for tag,_,_ in SELECTIONS:
			for ntk,_ in NTRKBINS:
				hname = "SVLMass_%s_%s_%s" % (tag,syst,ntk)
				hfinal = systhistos[(tag,syst,'tot',ntk)].Clone(hname)
				hfinal.Scale(xsecweights['MC8TeV_TTJets_MSDecays_172v5'])
				hfinal.Scale(LUMI)
				hfinal.Add(bghistos_added[(tag,ntk)])

				hfinal.Write(hname, ROOT.TObject.kOverwrite)
	ofi.Write()
	ofi.Close()

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
	parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
					  help='Output directory [default: %default]')
	parser.add_option('-c', '--cache', dest='cache', action="store_true",
					  help='Read from cache')
	(opt, args) = parser.parse_args()

	exit(main(args, opt))




