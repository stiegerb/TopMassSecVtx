#! /usr/bin/env python
import os, sys, re
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot

# MASSES = [163.5, 166.5, 169.5, 171.5, 172.5, 173.5, 175.5, 178.5, 181.5]
NBINS = 100
XMIN = 5.
XMAX = 200.
FITRANGE = (20., 140.)
MASSXAXISTITLE = 'm(SV,lepton) [GeV]'
LUMI = 19701.0

# NTRKBINS = [(2,3), (3,4), (4,5), (5,6) ,(6,7), (7,1000)]
# NTRKBINS = [(2,3), (3,4), (4,1000)]
NTRKBINS = [(3,4), (4,5), (5,6)]
# BR fix x PU x Lep Sel x JES
COMMONWEIGHT = "Weight[0]*Weight[1]*Weight[4]*METWeight[0]*BtagWeight[0]*JESWeight[0]*SVBfragWeight[0]"
LUMIWEIGHT = "XSWeight*%f"%LUMI  # x XS weight
TREENAME = 'SVLInfo'
MSEL   = '(abs(EvCat)==13 && NJets>=4)'
ESEL   = '(abs(EvCat)==11 && NJets>=4)'
MplusSEL   = '(EvCat==13 && NJets>=4)'
EplusSEL   = '(EvCat==11 && NJets>=4)'
MminusSEL   = '(EvCat==-13 && NJets>=4)'
EminusSEL   = '(EvCat==-11 && NJets>=4)'
EESEL  = '(EvCat==-121 && NJets>=2)'
EMSEL  = '(EvCat==-143 && NJets>=2)'
MMSEL  = '(EvCat==-169 && NJets>=2)'
INCSEL = '(%s || %s || %s || %s || %s)' % (MSEL, ESEL, EESEL , EMSEL, MMSEL)
SELECTIONS = [
	 ('inclusive', ''+INCSEL, '#geq 1 lepton'),
	 ('ee',        ''+EESEL,  'ee'),
	 ('em',        ''+EMSEL,  'e#mu'),
	 ('mm',        ''+MMSEL,  '#mu#mu'),
	 ('e',         ''+ESEL,   'e'),
	 ('m',         ''+MSEL,   '#mu'),
	 ('eplus',         ''+EplusSEL,   'e+'),
	 ('mplus',         ''+MplusSEL,   '#mu+'),
	 ('eminus',         ''+EminusSEL,   'e-'),
	 ('mminus',         ''+MminusSEL,   '#mu-'),

	# ('inclusive_mrank1', 'SVLMassRank==1&&CombCat%2!=0&&'+INCSEL, '#geq 1 lepton'),
	# ('ee_mrank1',        'SVLMassRank==1&&CombCat%2!=0&&'+EESEL,  'ee'),
	# ('em_mrank1',        'SVLMassRank==1&&CombCat%2!=0&&'+EMSEL,  'e#mu'),
	# ('mm_mrank1',        'SVLMassRank==1&&CombCat%2!=0&&'+MMSEL,  '#mu#mu'),
	# ('e_mrank1',         'SVLMassRank==1&&CombCat%2!=0&&'+ESEL,   'e'),
	# ('m_mrank1',         'SVLMassRank==1&&CombCat%2!=0&&'+MSEL,   '#mu'),

	# ('inclusive_mrank1dr', 'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+INCSEL, '#geq 1 lepton'),
	# ('ee_mrank1dr',        'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+EESEL,  'ee'),
	# ('em_mrank1dr',        'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+EMSEL,  'e#mu'),
	# ('mm_mrank1dr',        'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+MMSEL,  '#mu#mu'),
	# ('e_mrank1dr',         'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+ESEL,   'e'),
	# ('m_mrank1dr',         'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+MSEL,   '#mu'),

	# ('inclusive_drrank1dr', 'SVLDeltaRRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+INCSEL, '#geq 1 lepton'),
	# ('ee_drrank1dr',        'SVLDeltaRRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+EESEL,  'ee'),
	# ('em_drrank1dr',        'SVLDeltaRRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+EMSEL,  'e#mu'),
	# ('mm_drrank1dr',        'SVLDeltaRRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+MMSEL,  '#mu#mu'),
	# ('e_drrank1dr',         'SVLDeltaRRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+ESEL,   'e'),
	# ('m_drrank1dr',         'SVLDeltaRRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&'+MSEL,   '#mu'),

	('inclusive_optmrank', 'SVLCombRank>0 && '+INCSEL, '#geq 1 lepton'),
	('ee_optmrank',        'SVLCombRank>0 && '+EESEL,  'ee'),
	('em_optmrank',        'SVLCombRank>0 && '+EMSEL,  'e#mu'),
	('mm_optmrank',        'SVLCombRank>0 && '+MMSEL,  '#mu#mu'),
	('e_optmrank',         'SVLCombRank>0 && '+ESEL,   'e'),
	('m_optmrank',         'SVLCombRank>0 && '+MSEL,   '#mu'),

	('eplus_optmrank',         'SVLCombRank>0 && '+EplusSEL,   'e+'),
	('mplus_optmrank',         'SVLCombRank>0 && '+MplusSEL,   '#mu+'),
	('eminus_optmrank',         'SVLCombRank>0 && '+EminusSEL,   'e-'),
	('mminus_optmrank',         'SVLCombRank>0 && '+MminusSEL,   '#mu-'),
]

COMBINATIONS = {
	'tot': '1',
	'cor': 'CombInfo==1',
	'wro': 'CombInfo==0',
	'unm': 'CombInfo==-1',
}


CHANMASSTOPROCNAME = {
## (chan, mass) -> xsecweights key
	('tt',    163.5) : 'MC8TeV_TTJets_163v5',
	('tt',    166.5) : 'MC8TeV_TTJets_MSDecays_166v5',
	('tt',    169.5) : 'MC8TeV_TTJets_MSDecays_169v5',
	('tt',    171.5) : 'MC8TeV_TTJets_MSDecays_171v5',
	('tt',    172.5) : 'MC8TeV_TTJets_MSDecays_172v5',
	('tt',    173.5) : 'MC8TeV_TTJets_MSDecays_173v5',
	('tt',    175.5) : 'MC8TeV_TTJets_MSDecays_175v5',
	('tt',    178.5) : 'MC8TeV_TTJets_MSDecays_178v5',
	('tt',    181.5) : 'MC8TeV_TTJets_181v5',
	('t',     166.5) : 'MC8TeV_SingleT_t_166v5',
	('t',     169.5) : 'MC8TeV_SingleT_t_169v5',
	('t',     171.5) : 'MC8TeV_SingleT_t_171v5',
	('t',     172.5) : 'MC8TeV_SingleT_t',
	('t',     173.5) : 'MC8TeV_SingleT_t_173v5',
	('t',     175.5) : 'MC8TeV_SingleT_t_175v5',
	('t',     178.5) : 'MC8TeV_SingleT_t_178v5',
	('tbar',  166.5) : 'MC8TeV_SingleTbar_t_166v5',
	('tbar',  169.5) : 'MC8TeV_SingleTbar_t_169v5',
	('tbar',  171.5) : 'MC8TeV_SingleTbar_t_171v5',
	('tbar',  172.5) : 'MC8TeV_SingleTbar_t',
	('tbar',  173.5) : 'MC8TeV_SingleTbar_t_173v5',
	('tbar',  175.5) : 'MC8TeV_SingleTbar_t_175v5',
	('tbar',  178.5) : 'MC8TeV_SingleTbar_t_178v5',
	('tW',    166.5) : 'MC8TeV_SingleT_tW_166v5',
	('tW',    172.5) : 'MC8TeV_SingleT_tW',
	('tW',    178.5) : 'MC8TeV_SingleT_tW_178v5',
	('tbarW', 166.5) : 'MC8TeV_SingleTbar_tW_166v5',
	('tbarW', 172.5) : 'MC8TeV_SingleTbar_tW',
	('tbarW', 178.5) : 'MC8TeV_SingleTbar_tW_178v5',
}


def addTopMassTreesFromDir(dirname, trees, files):
	for filename in os.listdir(dirname):
		if not os.path.splitext(filename)[1] == '.root': continue

		## Select top samples
		if not "TTJets" in filename and not "SingleT" in filename: continue

		## Extract the mass (and splitting index, if it's there)
		matchres = re.match(r'.*([0-9]{3})v5\_?([0-9]+)?\.root', filename)
		if matchres: mass = float(matchres.group(1)) + 0.5
		else: mass = 172.5

		treefile = os.path.join(dirname, filename)
		tfile = ROOT.TFile.Open(treefile,'READ')
		tree = tfile.Get(TREENAME)

		chan = 'tt'

		if '_tW' in filename:
			if 'SingleTbar' in filename : chan = 'tbarW'
			else                        : chan = 'tW'
		elif '_t' in filename:
			if 'SingleTbar' in filename : chan = 'tbar'
			else                        : chan = 't'
		elif 'SingleT' in filename and '_s' in filename:
			continue

		if not (mass,chan) in trees:
			trees[(mass, chan)] = ROOT.TChain(TREENAME)
			files[(mass, chan)] = []
		trees[(mass,chan)].Add(treefile)
		files[(mass,chan)].append(treefile)

def getMassTrees(inputdir, verbose=True):
	"""
	build a map with available trees and files
	"""
	alltrees = {} # (mass,chan) -> chain
	allfiles = {} # (mass,chan) -> [locations]

	addTopMassTreesFromDir(inputdir, alltrees, allfiles)
	addTopMassTreesFromDir(os.path.join(inputdir, 'mass_scan'),alltrees, allfiles)

	allmasses = sorted(list(set([mass for mass,_ in alltrees.keys()])))
	if verbose:
		print 80*'-'
		print "Found the following mass points (#entries):"
		for mass in sorted(allmasses):
			line = '  %5.1f GeV '%mass
			if (mass, 'tt') in alltrees:
				line += ' (tt: %7d) ' % alltrees[(mass, 'tt')].GetEntries()
			if (mass, 't') in alltrees:
				line += ' (t: %5d) ' % alltrees[(mass, 't')].GetEntries()
			if (mass, 'tbar') in alltrees:
				line += ' (tbar: %5d) ' % alltrees[(mass, 'tbar')].GetEntries()
			if (mass, 'tW') in alltrees:
				line += ' (tW: %6d) ' % alltrees[(mass, 'tW')].GetEntries()
			if (mass, 'tbarW') in alltrees:
				line += ' (tbarW: %6d) ' % alltrees[(mass, 'tbarW')].GetEntries()
			print line
		print 80*'-'

	return alltrees, allfiles

def runSVLInfoTreeAnalysis((treefiles, histos, outputfile)):
	taskname = os.path.basename(outputfile)[:-5]
	chain = ROOT.TChain(TREENAME)
	for filename in treefiles:
		if not os.path.exists(filename):
			print "ERROR: file %s does not exist! Aborting" % filename
			return -1
		chain.Add(filename)
	print ' ... processing %-36s for %4d histos from %7d entries' %(taskname, len(histos), chain.GetEntries())

	from ROOT import gSystem
	gSystem.Load('libUserCodeTopMassSecVtx.so')
	from ROOT import SVLInfoTreeAnalysis
	ana = SVLInfoTreeAnalysis(chain)
	for hname,var,sel,nbins,xmin,xmax,xtitle in histos:
		ana.AddPlot(hname, var, sel, nbins, xmin, xmax, xtitle)
	ana.RunJob(outputfile)
	print '         %s done' % taskname

def runTasks(inputfiles, tasklist, opt, subdir, interactive=True):
	assert set(inputfiles.keys()) == set(tasklist.keys())
	tasks = []

	os.system('mkdir -p %s' % os.path.join(opt.outDir, subdir))

	for key, task in tasklist.iteritems():
		## Apply filter
		if hasattr(opt,'filter'):
			if len(opt.filter)>0:
				if not key in opt.filter.split(','): continue

		#### DEBUG: run only central mass point for tt
		####        to speed things up
		# if not key == (172.5, 'tt'): continue
		# if not key == 'nominal': continue

		for ifilep in inputfiles[key]:
			ofilen = os.path.basename(ifilep)
			ofilep = os.path.join(opt.outDir, subdir, ofilen)
			#### DEBUG: run only single split files
			# if not (ifilep.endswith('_0.root') or ifilep.endswith('_13.root')):
			# 	continue

			tasks.append(([ifilep], task, ofilep))


	print ">>> runTasks: Will process these files:"
	for t in tasks: print t[0]
	if interactive: raw_input("press key to continue...")

	if opt.jobs > 1:
		import multiprocessing as MP
		pool = MP.Pool(opt.jobs)
		pool.map(runSVLInfoTreeAnalysis, tasks)
	else:
		for task in tasks:
			runSVLInfoTreeAnalysis(task)

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

def gatherHistosFromFiles(tasklist, massfiles, dirname, hname_to_keys):
	## First extract a list of ALL histogram names from the tasklist
	hnames = [t[0] for tasks in tasklist.values() for t in tasks]

	histos = {}
	for ifilen in os.listdir(dirname):
		if not os.path.splitext(ifilen)[1] == '.root': continue
		ifile = ROOT.TFile.Open(os.path.join(dirname,ifilen), 'READ')

		for hname in hnames:
			keys = hname_to_keys[hname]
			tag = keys[0]
			chan = keys[1]
			mass = keys[2]

			## Skip histo names that are not in this file
			tfilens = [os.path.basename(x) for x in massfiles[(mass,chan)]]
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

"""
"""
def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	masstrees, massfiles = getMassTrees(args[0], verbose=True)
	masspoints = sorted(list(set([mass for mass,_ in masstrees.keys()])))

	hname_to_keys = {} # hname -> (tag, chan, mass, comb, [ntk1])

	tasklist = {} ## (mass,chan) -> tasks
	for (mass,chan) in masstrees.keys():
		tasks = []
		for tag,sel,_ in SELECTIONS:

			#htag = ("%s_%5.1f_tt"%(tag,mass)).replace('.','')
			#if not chan == 'tt':
			htag = ("%s_%5.1f_%s"%(tag,mass,chan)).replace('.','')

			for comb,combsel in COMBINATIONS.iteritems():
				hname = "SVLMass_%s_%s" % (comb, htag)
				finalsel = "%s*(%s&&%s)"%(COMMONWEIGHT,sel,combsel)
				tasks.append((hname, 'SVLMass', finalsel,
							  NBINS, XMIN, XMAX, MASSXAXISTITLE))
				hname_to_keys[hname] = (tag, chan, mass, comb)

				for ntk1,ntk2 in NTRKBINS:
					tksel = "(SVNtrk>=%d && SVNtrk<%d)"%(ntk1,ntk2)
					finalsel = "%s*(%s&&%s&&%s)"%(COMMONWEIGHT, sel,
												  combsel,tksel)
					hname = "SVLMass_%s_%s_%d" % (comb, htag, ntk1)
					tasks.append((hname, 'SVLMass', finalsel,
								  NBINS, XMIN, XMAX, MASSXAXISTITLE))
					hname_to_keys[hname] = (tag, chan, mass, comb, ntk1)

		tasklist[(mass,chan)] = tasks

	if not opt.cache:
		runTasks(massfiles, tasklist, opt, 'mass_histos')

		## Retrieve the histograms from the individual files
		# (tag, chan, mass, comb)      -> histo
		# (tag, chan, mass, comb, ntk) -> histo
		masshistos = gatherHistosFromFiles(tasklist, massfiles,
						   os.path.join(opt.outDir,
								'mass_histos'),
						   hname_to_keys)

		cachefile = open(".svlmasshistos.pck", 'w')
		pickle.dump(masshistos, cachefile, pickle.HIGHEST_PROTOCOL)
		cachefile.close()
		print 'Wrote .svlmasshistos.pck with all the mass histos'

	else:
		## Read mass scan histos:
		cachefile = open(".svlmasshistos.pck", 'r')
		masshistos = pickle.load(cachefile)
		print '>>> Read mass scan histograms from cache (.svlmasshistos.pck)'
		cachefile.close()

	# ofi = ROOT.TFile(os.path.join(opt.outDir,'masshistos.root'),
	# 													   'recreate')
	# ofi.cd()

	# for key in masshistos.keys():
	# 	tag, chan, mass = key[0],key[1],key[2]
	# 	if not ofi.cd(tag):
	# 		outDir = ofi.mkdir(tag)
	# 		outDir.cd()

	# 	for comb in COMBINATIONS.keys():
	# 		masshistos[(tag,chan,mass,comb)].Write()
	# 		for ntk,_ in NTRKBINS:
	# 			masshistos[(tag,chan,mass,comb,ntk)].Write()
	# ofi.Write()
	# ofi.Close()

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)


	cachefile = open(".xsecweights.pck", 'r')
	xsecweights = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read xsec weights from cache (.xsecweights.pck)'

	## Scale all the histograms for the plotting:
	for key, hist in masshistos.iteritems():
		hist.Scale(LUMI*xsecweights[CHANMASSTOPROCNAME[(key[1], key[2])]])


	errorGetters = {} # tag -> function(chi2) -> error
	systematics = {} # (seltag, systname) -> error
	mass_scan_dir = os.path.join(opt.outDir, 'mass_scans')
	for tag,sel,seltag in SELECTIONS:
		print "... processing %s"%tag
		pairing = 'inclusive'
		try: pairing = tag.split('_',1)[1]
		except IndexError: pass

		for chan in ['tt', 't', 'tbar', 'tW', 'tbarW']:
			# print "   %s channel" % chan
			## Skip some useless combinations:
			chanTitle=chan
			if chanTitle=='tt' : chanTitle='ttbar'
			chanTitle=chanTitle.replace('tbar','#bar{t}')
			if chan in ['t','tbar'] and ('ee' in tag or 'mm' in tag or 'em' in tag):
				continue
			if chan in ['tW','tbarW'] and tag in ['e', 'm', 
							      'eplus','eminus', 'mplus','mminus',
							      'e_optmrank', 'm_optmrank',
							      'eplus_optmrank','eminus_optmrank', 'mplus_optmrank','mminus_optmrank']:
				continue

			ratplot = RatioPlot('ratioplot')
			ratplot.normalized = False
			ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
			ratplot.ratiorange = (0.5, 1.5)
			ratplot.rebin = 2

			reference = masshistos[(tag,chan,172.5,'tot')]
			ratplot.reference = reference

			for mass in masspoints:
				legentry = 'm_{t} = %5.1f GeV' % mass
				try:
					histo = masshistos[(tag,chan,mass,'tot')]
					ratplot.add(histo, legentry)
				except KeyError: pass
					# print "Can't find ", (tag,chan,mass,'tot')


			ratplot.tag = 'All combinations'
			ratplot.subtag = '%s %s' % (seltag, chanTitle)
			ratplot.show("massscan_%s_%s_tot"%(tag,chan), mass_scan_dir)

			# chi2s = ratplot.getChiSquares(rangex=FITRANGE)
			# chi2stofit = []
			# for legentry in sorted(chi2s.keys()):
			# 	chi2stofit.append((float(legentry[8:-4]), chi2s[legentry]))
			# errorGetters[tag] = fitChi2(chi2stofit,
			# 							tag=seltag,
			# 							oname=os.path.join(mass_scan_dir,
			# 						    "chi2_simple_fit_%s.pdf"%tag),
			# 							drawfit=False)
			ratplot.reset()

			ratplot.reference = masshistos[(tag,chan,172.5,'cor')]
			for mass in masspoints:
				legentry = 'm_{t} = %5.1f GeV' % mass
				try: ratplot.add(masshistos[(tag,chan,mass,'cor')], legentry)
				except KeyError: pass
			ratplot.tag = 'Correct combinations'
			ratplot.subtag = '%s %s' % (seltag, chanTitle)
			ratplot.show("massscan_%s_%s_cor"%(tag,chan), mass_scan_dir)
			ratplot.reset()

			ratplot.reference = masshistos[(tag,chan,172.5,'wro')]
			for mass in masspoints:
				legentry = 'm_{t} = %5.1f GeV' % mass
				try: ratplot.add(masshistos[(tag,chan,mass,'wro')], legentry)
				except KeyError: pass
			ratplot.tag = 'Wrong combinations'
			ratplot.subtag = '%s %s' % (seltag, chanTitle)
			ratplot.show("massscan_%s_%s_wro"%(tag,chan), mass_scan_dir)
			ratplot.reset()

			ratplot.reference = masshistos[(tag,chan,172.5,'unm')]
			for mass in masspoints:
				legentry = 'm_{t} = %5.1f GeV' % mass
				try: ratplot.add(masshistos[(tag,chan,mass,'unm')], legentry)
				except KeyError: pass
			ratplot.tag = 'Unmatched combinations'
			ratplot.subtag = '%s %s' % (seltag, chanTitle)
			ratplot.show("massscan_%s_%s_unm"%(tag,chan), mass_scan_dir)
			ratplot.reset()


		## ntkscan plot
		if 'inclusive' in tag:
			ntkmassplot = RatioPlot('ntkmassplot_%s'%tag)
			ntkmassplot.rebin = 2
			ntkmassplot.reference = [masshistos[(tag, 'tt', 172.5, 'tot')]]
			ntkmassplot.add(masshistos[(tag, 'tt', 172.5, 'tot')], 'Sum', includeInRatio=False)
			for ntk1,ntk2 in NTRKBINS:
				title = "%d #leq N_{trk.} < %d" %(ntk1, ntk2)
				if ntk2 > 100:
					title = "%d #leq N_{trk.}" %(ntk1)
				ntkmassplot.add(masshistos[(tag, 'tt', 172.5, 'tot', ntk1)],
					            title)
			ntkmassplot.colors = [ROOT.kOrange+8,
			                      ROOT.kGreen+3, ROOT.kGreen+1,
								  ROOT.kGreen, ROOT.kGreen-10,
								  ROOT.kYellow-3, ROOT.kYellow-5]
			ntkmassplot.ratiorange = (0,3.0)
			ntkmassplot.ratiotitle = "Ratio wrt Sum"
			ntkmassplot.tag = 'm_{t} = 172.5 GeV'
			ntkmassplot.subtag = '%s, %s' %(pairing, seltag)
			ntkmassplot.show("ntkscan_%s"%tag, opt.outDir)
			ntkmassplot.reset()

	#fractions
	for tag,sel,seltag in SELECTIONS:
		print 70*'-'
	 	print '%-10s: %s %s' % (tag, sel,seltag)
		if not('inclusive' in tag): continue
	 	fcor, fwro, funm = {}, {}, {}
	 	for mass,proc in sorted(massfiles.keys()):
			# mass = 172.5
			ncount={}
			for comb in ['tot','cor','wro','unm']:
				hist = masshistos[(tag,proc, mass,comb)]
				ncount[comb]=hist.Integral()
			fcor[mass] = 100.*(ncount['cor']/float(ncount['tot']))
	 		fwro[mass] = 100.*(ncount['wro']/float(ncount['tot']))
	 		funm[mass] = 100.*(ncount['unm']/float(ncount['tot']))
	 		print ('  %-6s %5.1f GeV: %7d entries \t'
	 			   '(%4.1f%% corr, %4.1f%% wrong, %4.1f%% unmatched)' %
	 			   (proc, mass, ncount['tot'],
	 			   	fcor[mass], fwro[mass], funm[mass]))
		oname = os.path.join(opt.outDir, 'fracvsmt_%s'%tag)
		plotFracVsTopMass(fcor, fwro, funm, tag, seltag, oname)


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




