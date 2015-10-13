#! /usr/bin/env python
import os, sys, re
import os.path as osp
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot
from makeSVLMassHistos import NBINS, XMIN, XMAX, MASSXAXISTITLE
from makeSVLMassHistos import NTRKBINS, COMMONWEIGHT, TREENAME, LUMI
from makeSVLMassHistos import SELECTIONS, CHANMASSTOPROCNAME
from makeSVLMassHistos import runSVLInfoTreeAnalysis, runTasks
from makeSVLDataMCPlots import resolveFilename
from makeSVLSystPlots import ALLSYSTS, SYSTTOPROCNAME

TWXSECS = {
## see: https://docs.google.com/spreadsheets/d/1msX8xQ-Or0ML4D0nCCeWWSQth0O-OgcYZTZ-Bm7AGmA/
	166.5 : 25.85,
	169.5 : 24.65,
	171.5 : 23.85,
	173.5 : 23.05,
	175.5 : 22.25,
	178.5 : 21.05,
}

QCDTEMPLATESTOADD = {
#	'inclusive'          : ('',       ['e', 'm']),
#	'inclusive_mrank1'   : ('_mrank1',['e', 'm']),
#	'inclusive_mrank1dr' : ('_mrank1dr',['e', 'm']),
#	'inclusive_drrank1dr': ('_drrank1dr',['e', 'm']),
	'inclusive_optmrank' : ('_optmrank',['e', 'm']),
#	'e'                  : ('',       ['e']),
#	'm'                  : ('',       ['m']),
#	'e_mrank1'           : ('_mrank1',['e']),
#	'm_mrank1'           : ('_mrank1',['m']),
#	'e_mrank1dr'         : ('_mrank1dr',['e']),
#	'm_mrank1dr'         : ('_mrank1dr',['m']),
#	'e_drrank1dr'        : ('_drrank1dr',['e']),
#	'm_drrank1dr'        : ('_drrank1dr',['m']),
	'e_optmrank'         : ('_optmrank',['e']),
	'm_optmrank'         : ('_optmrank',['m']),
}

SYSTSTOBERENORMALIZED = [
## Renormalize these variations to the nominal one
## (to account for non-normalized event weights)
	'toppt',
	'topptup',
	'bhadcomp',
	'bfrag',
	'bfragup',
	'bfragdn',
	'bfragp11',
	'bfragpete',
	'bfraglund',
	'mgmcfmnloproddec',
	'powpythmcfmnloproddec'
]

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
		runTasks(treefiles, tasklist, opt, 'bg_histos', interactive=False)

	bghistos = {} # (tag, pname, comb) -> histo
	bghistos = gatherHistosFromFiles(tasklist, treefiles,
								   osp.join(opt.outDir, 'bg_histos'),
								   hname_to_keys)

	cachefile = open(".svlbghistos.pck", 'w')
	pickle.dump(bghistos, cachefile, pickle.HIGHEST_PROTOCOL)
	cachefile.close()
	return bghistos

def makeDataHistos(treefiles, opt):
	hname_to_keys = {} # hname -> (tag, syst, comb)
	tasklist = {} # treefile -> tasklist

	for pname in treefiles.keys():
		if not pname in tasklist: tasklist[pname] = []
		for tag,sel,_ in SELECTIONS:
			tasks = []
			hname = "SVLMass_tot_%s_%s" % (tag, pname)
			finalsel = "(%s)"%(sel)

			tasks.append((hname, 'SVLMass', finalsel,
						  NBINS, XMIN, XMAX, MASSXAXISTITLE))
			hname_to_keys[hname] = (tag, pname, 'tot') ## add the 'tot'

			for ntk1,ntk2 in NTRKBINS:
				tksel = "(SVNtrk>=%d&&SVNtrk<%d)"%(ntk1,ntk2)
				finalsel = "(%s&&%s)"%(sel, tksel)
				hname = "SVLMass_tot_%s_%s_%d" % (tag, pname, ntk1)
				tasks.append((hname, 'SVLMass', finalsel,
							  NBINS, XMIN, XMAX, MASSXAXISTITLE))
				hname_to_keys[hname] = (tag, pname, 'tot', ntk1)

			tasklist[pname] += tasks

	if not opt.cache:
		runTasks(treefiles, tasklist, opt, 'data_histos', interactive=False)

	datahistos = {} # (tag, pname, comb) -> histo
	datahistos = gatherHistosFromFiles(tasklist, treefiles,
								   osp.join(opt.outDir, 'data_histos'),
								   hname_to_keys)

	cachefile = open(".svldatahistos.pck", 'w')
	pickle.dump(datahistos, cachefile, pickle.HIGHEST_PROTOCOL)
	cachefile.close()
	return datahistos

def sumDataHistos(processes, datahistos):
	datahistos_added = {}
	for tag,_,_ in SELECTIONS:
		for ntk,_ in NTRKBINS:
			for pname in processes:
				hname = "SVLMass_tot_%s_data_%d"%(tag,ntk)
				hist = datahistos[tag, pname, 'tot', ntk].Clone("%s_%s" % (
															  hname, pname))
				## Save in dictionary
				if not (tag, ntk) in datahistos_added:
					datahistos_added[(tag, ntk)] = hist
					datahistos_added[(tag, ntk)].SetName(hname)
				else:
					datahistos_added[(tag, ntk)].Add(hist)
	return datahistos_added


def sumBGHistos(processes, bghistos, xsecweights, ntkWeights, dySFs,
	            qcdTemplates, opt, dyScale=None, qcdScale=None):
	bghistos_added = {}
 	# Save the total expected integral for the overall normalization:
 	bg_normalization = {}
	for tag,_,_ in SELECTIONS:
		if opt.verbose>2: print ' selection:',tag
		for ntk,_ in NTRKBINS:
			if opt.verbose>2: print '  ntrks:',ntk
			for pname in processes:
				if opt.verbose>3: print '   process:',pname

				hname = "SVLMass_tot_%s_bg_%d"%(tag,ntk)
				hist = bghistos[tag, pname, 'tot', ntk].Clone("%s_%s" % (
															  hname, pname))

				## Apply scale factors
				hist.Scale(LUMI*xsecweights["MC8TeV_%s"%pname])
				if ((tag.startswith('ee') or tag.startswith('mm'))
					 and pname.startswith('DY')):
					hist.Scale(dySFs[tag[:2]])

				## Scaling for background systematics
				if dyScale and pname.startswith('DY'):
					if opt.verbose>2: print '    scaling DY by',dyScale
					hist.Scale(dyScale)

				## Save normalization (even when skipped)
				if not (tag, ntk) in bg_normalization:
					bg_normalization[(tag, ntk)] = 0
				bg_normalization[(tag, ntk)] += hist.Integral()

				## Skip events with an average event weight above 2 (low statistics)
				if hist.GetEntries() == 0: continue
				if ( (hist.Integral()/hist.GetEntries() > 2) and
					hist.GetEntries() < 10 ):
					if opt.verbose>3:
						print ('\033[91m      skipping %s (%d entries, '
							   'int/entr=%5.2f)\033[0m' %
							          (pname, hist.GetEntries(),
							           hist.Integral()/hist.GetEntries()))
					continue

				## Save in dictionary
				if not (tag, ntk) in bghistos_added:
					bghistos_added[(tag, ntk)] = hist
					bghistos_added[(tag, ntk)].SetName(hname)
				else:
					bghistos_added[(tag, ntk)].Add(hist)

			## Scale the MC only histograms to the total expected integral
			## (to account for the skipped processes)
			bghistos_added[(tag,ntk)].Scale(bg_normalization[(tag,ntk)]/
				                        bghistos_added[(tag,ntk)].Integral())

			## Add QCD templates from MET fit:
			if tag in QCDTEMPLATESTOADD:
				sel,cats = QCDTEMPLATESTOADD[tag]
				for cat in cats:
					if opt.verbose>2:
						print '  adding qcd templates from',sel,ntk,cat

					qcdhist = qcdTemplates[(sel,ntk,cat)]

					## Scaling for background systematics
					if qcdScale:
						if opt.verbose>2:
							print '    scaling qcd by',qcdScale
						qcdhist.Scale(qcdScale)

					bghistos_added[(tag, ntk)].Add(qcdhist)

			## Scale by SV track multiplicity weights:
			bghistos_added[(tag, ntk)].Scale(ntkWeights['inclusive'][ntk])

	return bghistos_added


def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	mcfiles = {}   # procname -> filename
	datafiles = {} # procname -> filename
	try:
		for fname in os.listdir(args[0]):
			if not osp.splitext(fname)[1] == '.root': continue
			isdata,procname,splitno = resolveFilename(fname)
			if isdata:
				if not procname in datafiles:
					datafiles[procname] = []
				datafiles[procname].append(osp.join(args[0],fname))
			else:
				if 'QCD' in procname:                   continue ## exclude QCD
				if procname == 'TTJets_MSDecays_172v5': continue ## have those already
				if 'SingleT' in procname:               continue ## have those already

				if not procname in mcfiles:
					mcfiles[procname] = []
				mcfiles[procname].append(osp.join(args[0],fname))

	except IndexError:
		print "Please provide a valid input directory"
		exit(-1)


	## Produce (or read) the histogram data
	bghistos = makeBackgroundHistos(mcfiles, opt)

	cachefile = open(".xsecweights.pck", 'r')
	xsecweights = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read xsec weights from cache (.xsecweights.pck)'

	cachefile = open(".svldyscalefactors.pck", 'r')
	dySFs = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read DY scale factors from cache (.svldyscalefactors.pck)'

	cachefile = open(".svlqcdtemplates.pck", 'r')
	qcdTemplates = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read QCD templates from cache (.svlqcdtemplates.pck)'

	## Read SV Track multiplicity weights:
	from extractNtrkWeights import extractNTrkWeights
	ntkWeights = extractNTrkWeights()

	## Now add them up with proper scales
	mcprocesses = [k for k in mcfiles.keys() if not 'Data8TeV' in k]
	bghistos_added = sumBGHistos(processes=mcprocesses,
		                         bghistos=bghistos,
		                         xsecweights=xsecweights,
		                         ntkWeights=ntkWeights,
		                         dySFs=dySFs,
		                         qcdTemplates=qcdTemplates,
		                         opt=opt)

	bghistos_added_dyup = sumBGHistos(processes=mcprocesses,
		                         bghistos=bghistos,
		                         xsecweights=xsecweights,
		                         ntkWeights=ntkWeights,
		                         dySFs=dySFs,
		                         qcdTemplates=qcdTemplates,
		                         opt=opt,
		                         dyScale=1.3)
	bghistos_added_dydn = sumBGHistos(processes=mcprocesses,
		                         bghistos=bghistos,
		                         xsecweights=xsecweights,
		                         ntkWeights=ntkWeights,
		                         dySFs=dySFs,
		                         qcdTemplates=qcdTemplates,
		                         opt=opt,
		                         dyScale=0.7)
	bghistos_added_qcdup = sumBGHistos(processes=mcprocesses,
		                         bghistos=bghistos,
		                         xsecweights=xsecweights,
		                         ntkWeights=ntkWeights,
		                         dySFs=dySFs,
		                         qcdTemplates=qcdTemplates,
		                         opt=opt,
		                         qcdScale=1.1)
	bghistos_added_qcddn = sumBGHistos(processes=mcprocesses,
		                         bghistos=bghistos,
		                         xsecweights=xsecweights,
		                         ntkWeights=ntkWeights,
		                         dySFs=dySFs,
		                         qcdTemplates=qcdTemplates,
		                         opt=opt,
		                         qcdScale=0.9)

	## Produce data histograms
	datahistos = makeDataHistos(datafiles, opt)
	datahistos_added = sumDataHistos(datafiles.keys(), datahistos)
	# Rebin also data, if required:
	if opt.rebin>0:
		for hist in datahistos_added.values():
			hist.Rebin(opt.rebin)

	## Save the background only shapes separately as templates for the fit
	cachefile = open(".svlbgtemplates.pck", 'w')
	pickle.dump(bghistos_added, cachefile, pickle.HIGHEST_PROTOCOL)
	print '>>> Dumped bg templates to cache (.svlbgtemplates.pck)'
	cachefile.close()

	## Read syst histos:
	cachefile = open(".svlsysthistos.pck", 'r')
	systhistos = pickle.load(cachefile)
	print '>>> Read systematics histograms from cache (.svlsysthistos.pck)'
	cachefile.close()

	## Read mass scan histos:
	cachefile = open(".svlmasshistos.pck", 'r')
	masshistos = pickle.load(cachefile)
	print '>>> Read mass scan histograms from cache (.svlmasshistos.pck)'
	# (tag, chan, mass, comb)      -> histo
	# (tag, chan, mass, comb, ntk) -> histo
	cachefile.close()

	ofi = ROOT.TFile.Open(osp.join(opt.outDir,'pe_inputs.root'),'RECREATE')
	ofi.cd()

	#####################################################
	## Central mass point and syst samples
	for syst in ([s for s,_,_,_ in ALLSYSTS] +
	             ['dyup','dydown','qcdup','qcddown','ntkmult']):
		odir = ofi.mkdir(syst + '_172v5')
		odir.cd()
		for tag,_,_ in SELECTIONS:
			for ntk,_ in NTRKBINS:
				hname = "SVLMass_%s_%s_%s" % (tag,syst+'_172v5',ntk)
				if not syst in ['dyup','dydown','qcdup','qcddown','ntkmult',
				                'tchscaleup','tchscaledown',
				                'twchscaleup','twchscaledown']:
					hfinal = systhistos[(tag,syst,'tot',ntk)].Clone(hname)
				else:
					hfinal = systhistos[(tag,'nominal','tot',ntk)].Clone(hname)
				try:
					## Systs from separate samples
					if syst in ['tchscaleup','tchscaledown',
					            'twchscaleup','twchscaledown']:
						scale = LUMI*xsecweights[CHANMASSTOPROCNAME[('tt', 172.5)]]
					else:
						scale = LUMI*xsecweights[SYSTTOPROCNAME[syst][0]]
				except KeyError:
					## Systs from event weights
					scale = LUMI*xsecweights[CHANMASSTOPROCNAME[('tt', 172.5)]]
				hfinal.Scale(scale)

				## Renormalize some variations with event weights
				if syst in SYSTSTOBERENORMALIZED:
					normintegral = systhistos[(tag,'nominal','tot',ntk)].Integral()
					normintegral *= LUMI*xsecweights[CHANMASSTOPROCNAME[('tt', 172.5)]]
					normintegral /= hfinal.Integral()
					hfinal.Scale(normintegral)

				## Add single top
				stProcs=['t', 'tbar', 'tW', 'tbarW']
				stSystProcs=[]
				if 'tchscale' in syst:
					stProcs=['tW', 'tbarW']
					stSystProcs=['t', 'tbar']
				if 'twchscale' in syst:
					stProcs=['t', 'tbar']
					stSystProcs=['tW', 'tbarW']
				for st in stProcs:
					hsinglet = masshistos[(tag, st, 172.5,'tot',ntk)].Clone('%s_%s'%(hname,st))
					hsinglet.Scale(LUMI*xsecweights[CHANMASSTOPROCNAME[(st, 172.5)]])
					hfinal.Add(hsinglet)
				for st in stSystProcs:
					hsinglet = systhistos[(tag, syst, 'tot', ntk)].Clone('%s_%s'%(hname,st))
					hsinglet.Scale(LUMI*xsecweights[CHANMASSTOPROCNAME[(st, 172.5)]])
					hfinal.Add(hsinglet)


				## Add the backgrounds
				if not syst in ['dyup','dydown','qcdup','qcddown']:
					hfinal.Add(bghistos_added[(tag,ntk)])
				else: ## From the scaled bghistos if necessary
					bghistos_added_scaled = {
						'dyup'    : bghistos_added_dyup,
						'dydown'  : bghistos_added_dydn,
						'qcdup'   : bghistos_added_qcdup,
						'qcddown' : bghistos_added_qcddn,
					}[syst]
					hfinal.Add(bghistos_added_scaled[(tag,ntk)])

				## Rebin if requested
				if opt.rebin>0:
					hfinal.Rebin(opt.rebin)

				## Scale by SV track multiplicity weights:
				if not syst == 'ntkmult':
					hfinal.Scale(ntkWeights['inclusive'][ntk])

				## Write out to file
				hfinal.Write(hname, ROOT.TObject.kOverwrite)

	#####################################################
	## Non-central mass points
	ROOT.gSystem.Load('libUserCodeTopMassSecVtx.so')
	from ROOT import th1fmorph
	# extract mass points from dictionary
	mass_points = sorted(list(set([key[2] for key in masshistos.keys()])))
	mass_points = mass_points[1:-1] # remove outermost points
	debughistos = []
	for mass in mass_points:
		if mass == 172.5: continue
		mname = 'nominal_%s' % str(mass).replace('.','v')
		odir = ofi.mkdir(mname)
		odir.cd()
		for tag,_,_ in SELECTIONS:
			for ntk,_ in NTRKBINS:
				hname = "SVLMass_%s_%s_%s" % (tag,mname,ntk)
				hfinal = masshistos[(tag,'tt',mass,'tot',ntk)].Clone(hname)
				hfinal.Scale(LUMI*xsecweights[CHANMASSTOPROCNAME[('tt', mass)]])

				## Add single top (t-channel, for which we have the samples)
				for st in ['t', 'tbar']:
					hsinglet = masshistos[(tag, st, mass,'tot',ntk)].Clone('%s_%s'%(hname,st))
					hsinglet.Scale(LUMI*xsecweights[CHANMASSTOPROCNAME[(st, mass)]])
					hfinal.Add(hsinglet)

				## Add single top (tW-channel, for which we don't have samples)
				## Morph between the two extreme mass points to get
				## the non existing ones
				for st in ['tW', 'tbarW']:
					if mass not in [166.5, 178.5]:
						hsingletW = th1fmorph('%s_%s_morph'%(hname,st),
							                  '%s_%s_morphed'%(hname,st),
							                   masshistos[(tag, 'tW', 166.5,'tot',ntk)],
							                   masshistos[(tag, 'tW', 178.5,'tot',ntk)],
							                   166.5, 178.5, mass,
							                   masshistos[(tag, 'tW', 166.5,'tot',ntk)].Integral())
						hsingletW.Scale(LUMI*xsecweights[CHANMASSTOPROCNAME[(st, 166.5)]]
							                * TWXSECS[mass]/TWXSECS[166.5])
						hsingletW.SetDirectory(0)
					else:
						hsingletW = masshistos[(tag, st, mass,'tot',ntk)].Clone('%s_%s'%(hname,st))
						hsingletW.Scale(LUMI*xsecweights[CHANMASSTOPROCNAME[(st, mass)]])
					hfinal.Add(hsingletW)

				## Add the combined backgrounds
				hfinal.Add(bghistos_added[(tag,ntk)])

				## Rebin if requested
				if opt.rebin>0:
					hfinal.Rebin(opt.rebin)

				## Scale by SV track multiplicity weights:
				hfinal.Scale(ntkWeights['inclusive'][ntk])

				## Write out to file
				hfinal.Write(hname, ROOT.TObject.kOverwrite)

	## Write also data histos
	ofi.cd()
	odir = ofi.mkdir('data')
	odir.cd()
	for tag,_,_ in SELECTIONS:
		for ntk,_ in NTRKBINS:
			hname = "SVLMass_%s_data_%s" % (tag,ntk)
			datahistos_added[(tag,ntk)].Write(hname, ROOT.TObject.kOverwrite)


	print ('>>> Wrote pseudo experiment inputs to file (%s)' %
		                      osp.join(opt.outDir,'pe_inputs.root'))

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
	parser.add_option('-r', '--rebin', dest='rebin', action="store",
					  type='int', default=2,
					  help='Rebin the histograms [default: %default]')
	parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
					  help='Output directory [default: %default]')
	parser.add_option('-c', '--cache', dest='cache', action="store_true",
					  help='Read from cache')
	(opt, args) = parser.parse_args()

	exit(main(args, opt))




