#! /usr/bin/env python
import os, sys, re
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot
from makeSVLMassHistos import NBINS, XMIN, XMAX, MASSXAXISTITLE
from makeSVLMassHistos import NTRKBINS, COMMONWEIGHT, TREENAME
from makeSVLMassHistos import SELECTIONS, COMBINATIONS
from makeSVLMassHistos import runSVLInfoTreeAnalysis, runTasks
from makeSVLDataMCPlots import resolveFilename
from numpy import roots
from pprint import pprint


CONTROLVARS = [
	('SVLDeltaR' , NBINS, 0  , 5   , '#Delta R(Sec.Vtx., lepton)'),
	('SVLxy'     , NBINS, 0  , 5   , 'SV flight distance (Lxy) [cm]'),
	('LPt'       , NBINS, 20 , 100 , 'Lepton pt [GeV]'),
	('SVPt'      , NBINS, 0  , 100 , 'Sec.Vtx. pt [GeV]'),
	('JPt'       , NBINS, 30 , 200 , 'Jet pt [GeV]'),
]

SYSTSFROMFILES = [
	('scaleup', 'Q^{2} Scale up',
	 ['MC8TeV_TTJets_MSDecays_scaleup.root'],
	  ['tot']),
	('scaledown', 'Q^{2} Scale down',
	 ['MC8TeV_TTJets_MSDecays_scaledown.root'],
	 ['tot']),
	('tchscaleup', 't-ch Q^{2} Scale up',
	 ['MC8TeV_SingleT_t_scaleup.root','MC8TeV_SingleTbar_t_scaleup.root'],
	 ['tot']),
	('tchscaledown', 't-ch Q^{2} Scale down',
	 ['MC8TeV_SingleT_t_scaledown.root','MC8TeV_SingleTbar_t_scaledown.root'],
	 ['tot']),
	('twchscaleup', 'tW-ch Q^{2} Scale up',
	 ['MC8TeV_SingleT_tW_scaleup.root','MC8TeV_SingleTbar_tW_scaleup.root'],
	 ['tot']),
	('twchscaledown', 'tW-ch Q^{2} Scale down',
	 ['MC8TeV_SingleT_tW_scaledown.root','MC8TeV_SingleTbar_tW_scaledown.root'],
	 ['tot']),
	('width', 'Top width (x5)',
	 ['MC8TeV_TTJets_widthx5.root'],
	 ['tot']),
	('matchingup', 'ME/PS maching Scale up',
	 ['MC8TeV_TTJets_MSDecays_matchingup.root'],
	 ['tot']),
	('matchingdown', 'ME/PS maching Scale down',
	 ['MC8TeV_TTJets_MSDecays_matchingdown.root'],
	 ['tot']),
	('p11', 'P11 nominal',
	 ['MC8TeV_TTJets_TuneP11.root'],
	 ['tot']),
	('p11nocr', 'P11 no color-reconnection',
	 ['MC8TeV_TTJets_TuneP11noCR.root'],
	 ['tot']),
	('p11tev', 'P11 Tevatron tune',
	 ['MC8TeV_TTJets_TuneP11TeV.root'],
	 ['tot']),
	('p11mpihi', 'P11 high multi-parton interaction',
	 ['MC8TeV_TTJets_TuneP11mpiHi.root'],
	 ['tot']),
	('mcatnlohw', 'MCatNLO/HERWIG AUET2',
	 ['MC8TeV_TT_mcatnlo.root'],
	 ['tot']),
	('powherw', 'Powheg/HERWIG AUET2',
	 ['MC8TeV_TT_AUET2_powheg_herwig.root'],
	 ['tot']),
	('powpyth', 'Powheg/PYTHIA Z2*',
	 ['MC8TeV_TT_Z2star_powheg_pythia.root'],
	 ['tot','cor','wro','unm']),	
	]

SYSTTOPROCNAME = dict([(k,[v.replace('.root','') for v in vlist]) for k,_,vlist,_ in SYSTSFROMFILES])

SYSTSFROMWEIGHTS = [
	('nominal',     'Nominal',                   '1',                      ['tot','cor','wro','unm']),
	('puup',        'Pileup up',                 'Weight[2]/Weight[1]',    ['tot']),
	('pudn',        'Pileup down',               'Weight[3]/Weight[1]',    ['tot']),
	('lepselup',    'Lepton selection up',       'Weight[5]',    ['tot']),
	('lepseldn',    'Lepton selection down',     'Weight[6]',    ['tot']),
	('umetup',      'Uncl. MET up',              'METWeight[1]',           ['tot']),
	('umetdn',      'Uncl. MET down',            'METWeight[2]',           ['tot']),
	('toppt',       'Top p_{T} weight applied',  'Weight[10]',             ['tot','cor','wro']),
	('topptup',     'Top p_{T} weight up',       'Weight[7]',              ['tot','cor','wro']),
	('bfrag',       'Z2* rb LEP',                '1',                      ['tot']), ## bfrag is nominal now
	('bfragz2s',    'Z2*',                       '1./SVBfragWeight[0]',    ['tot']), ## Z2s is without weight
	('bfragup',     'Z2* rb LEP hard',           'SVBfragWeight[1]/SVBfragWeight[0]', ['tot']),
	('bfragdn',     'Z2* rb LEP soft',           'SVBfragWeight[2]/SVBfragWeight[0]', ['tot']),
	('bfragp11',    'P11 fragmentation',         'SVBfragWeight[3]/SVBfragWeight[0]', ['tot']),
	('bfragpete',   'Z2* Peterson',              'SVBfragWeight[4]/SVBfragWeight[0]', ['tot']),
	('bfraglund',   'Z2* Lund',                  'SVBfragWeight[5]/SVBfragWeight[0]', ['tot']),
	('jesup',       'Jet energy scale up',       'JESWeight[1]',           ['tot']),
	('jesdn',       'Jet energy scale down',     'JESWeight[2]',           ['tot']),
	('jerup',       'Jet energy resolution up',  'JESWeight[3]',           ['tot']),
	('jerdn',       'Jet energy resolution down','JESWeight[4]',           ['tot']),
	('btagup',      'b-tag eff up',              'BtagWeight[1]',          ['tot']),
	('btagdn',      'b-tag eff down',            'BtagWeight[2]',          ['tot']),
	('lesup',       'Lepton energy scale up',    '1',                      ['tot']),
	('lesdn',       'Lepton energy scale down',  '1',                      ['tot']),
	('bhadcomp',    'B hadron composition',
	 '(1.05125*(abs(BHadId)>=510&&abs(BHadId)<520)+1.06429*(abs(BHadId)>=520&&abs(BHadId)<530)+0.753548*(abs(BHadId)>=530&&abs(BHadId)<540)+0.807828*(abs(BHadId)>=540)+(BHadId==0))',
	 ['tot']),

	('ttHFup',      'Extra heavy flavour up', '((CombInfo<0 && abs(BHadId)!=0)*1.66+((CombInfo<0 && abs(BHadId)==0) || CombInfo>=0)*1.0)*1.0', ['tot']),
	('ttHFdn',    'Extra heavy flavour down', '((CombInfo<0 && abs(BHadId)!=0)*0.60+((CombInfo<0 && abs(BHadId)==0) || CombInfo>=0)*1.0)*1.0', ['tot']),
	('bfnuup',      'B hadron semi-lep BF up',
	 '((BHadNeutrino==0)*0.984+(BHadNeutrino==1)*1.048+(BHadNeutrino==-1))', ['tot']),
	('bfnudn',   'B hadron semi-lep BF down',
	 '((BHadNeutrino==0)*1.012+(BHadNeutrino==1)*0.988+(BHadNeutrino==-1))', ['tot']),
	('svmass',      'SV mass reweighting',       'SVMassWeight',           ['tot']),
	('mgmcfmnloprod',    'NLO decay',        'MCFMWeight[0]',   ['tot','cor','wro','unm']),
	('mgmcfmnloproddec', 'NLO prod+decay',   'MCFMWeight[1]',   ['tot','cor','wro','unm']),
	]

#fun...
for i in xrange(1,53): SYSTSFROMWEIGHTS.append( ('pdf%d'%i, 'PDF variation %d'%i,'PDFWeight[%d]'%i, ['tot']) )

ALLSYSTS = SYSTSFROMFILES + SYSTSFROMWEIGHTS

#ALLSYSTS = SYSTSFROMFILES


SYSTNAMES = dict([(syst,name) for syst,name,_,_ in ALLSYSTS])
SELNAMES = dict([(tag,name) for tag,_,name in SELECTIONS])
COMBNAMES = {
	'tot':'',
	'cor':' (Correct comb.)',
	'wro':' (Wrong comb.)',
	'unm':' (Unmatched comb.)'
}

SYSTPLOTS = [
	('toppt', 'Top p_{T} reweighting',
	 ['nominal', 'toppt', 'topptup'],
	 [ROOT.kBlack, ROOT.kRed, ROOT.kRed-6],'tot'),

	('toppt', 'Top p_{T} reweighting',
	 ['nominal', 'toppt', 'topptup'],
	 [ROOT.kBlack, ROOT.kRed, ROOT.kRed-6],'cor'),

	('toppt', 'Top p_{T} reweighting',
	 ['nominal', 'toppt', 'topptup'],
	 [ROOT.kBlack, ROOT.kRed, ROOT.kRed-6],'wro'),

	('scale', 'Q^{2} Scale',
	 ['nominal', 'scaleup', 'scaledown'],
	 [ROOT.kBlack, ROOT.kGreen+1, ROOT.kRed+1],'tot'),

	('matching', 'ME/PS matching scale',
	 ['nominal', 'matchingup', 'matchingdown'],
	 [ROOT.kBlack, ROOT.kGreen+1, ROOT.kRed+1],'tot'),

	('width', 'Top quark width',
	 ['nominal', 'width'],
	 [ROOT.kBlack, ROOT.kGreen+1], 'tot'),

	('uecr', 'Underlying event / Color reconnection',
	 ['p11', 'p11tev', 'p11mpihi', 'p11nocr', 'nominal'],
	 [ROOT.kMagenta, ROOT.kMagenta+2, ROOT.kMagenta-9,
	  ROOT.kViolet+2, ROOT.kBlack],'tot'),

	('bfrag', 'b fragmentation',
	 ['nominal', 'bfragz2s', 'bfragup', 'bfragdn', 'bfragp11',
	  'bfraglund', 'bfragpete'],
	 [ROOT.kBlack, ROOT.kMagenta, ROOT.kMagenta+2, ROOT.kMagenta-9,
	  ROOT.kRed+1,ROOT.kAzure+7, ROOT.kBlue-7],'tot'),

	('jes', 'Jet energy scale',
	 ['nominal', 'jesup', 'jesdn'],
	 [ROOT.kBlack, ROOT.kAzure+7, ROOT.kBlue-7],'tot'),

	('jer', 'Jet energy resolution',
	 ['nominal', 'jerup', 'jerdn'],
	 [ROOT.kBlack, ROOT.kAzure+7, ROOT.kBlue-7],'tot'),

	('btag', 'b-tag efficiency',
	 ['nominal', 'btagup', 'btagdn'],
	 [ROOT.kBlack, ROOT.kAzure+7, ROOT.kBlue-7],'tot'),

	('les', 'Lepton energy scale',
	 ['nominal', 'lesup', 'lesdn'],
	 [ROOT.kBlack, ROOT.kAzure+7, ROOT.kBlue-7],'tot'),

	('umet', 'Unclustered MET',
	 ['nominal', 'umetup', 'umetdn'],
	 [ROOT.kBlack, ROOT.kAzure+7, ROOT.kBlue-7],'tot'),

	('lepsel', 'Lepton selection efficiency',
	 ['nominal', 'lepselup', 'lepseldn'],
	 [ROOT.kBlack, ROOT.kAzure+7, ROOT.kBlue-7],'tot'),

	('pu', 'Pileup',
	 ['nominal', 'puup', 'pudn'],
	 [ROOT.kBlack, ROOT.kAzure+7, ROOT.kBlue-7],'tot'),

	('bfnu', 'B-hadron branching fractions',
	 ['nominal', 'bfnuup', 'bfnudn'],
	 [ROOT.kBlack, ROOT.kYellow-3, ROOT.kYellow+3],'tot'),

	('ttHF', 'Extra heavy flavor in t#bar{t}',
	 ['nominal', 'ttHFup','ttHFdn'],
	 [ROOT.kBlack, ROOT.kYellow-3],'tot'),

	('svmass', 'SV Mass reweighting',
	 ['nominal', 'svmass'],
	 [ROOT.kBlack, ROOT.kMagenta-9],'tot'),
]


#fun...
PDFPLOTDESC=('pdf', 'PDF variations',	 ['nominal'], [ROOT.kBlack], 'tot')
for i in xrange(1,53):
	PDFPLOTDESC[2].append('pdf%d'%i)
	PDFPLOTDESC[3].append(ROOT.kGray)
SYSTPLOTS.append(PDFPLOTDESC)


def makeControlPlot(systhistos, syst, tag, seltag, opt):
	hists = tuple([systhistos[(tag, syst, c)] for c in COMBINATIONS.keys()])
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
	ctrlplot.show("control_%s_%s"%(syst,tag), os.path.join(opt.outDir, 'syst_plots'))
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

def makeSystTask(tag, sel, syst, hname_to_keys, weight='1',combs=['tot']):
	tasks = []
	htag = "%s_%s"%(tag,syst)
	for comb in combs:
		hname = "SVLMass_%s_%s" % (comb, htag)
		combsel = COMBINATIONS[comb]
		finalsel = "%s*%s*(%s&&%s)"%(COMMONWEIGHT, weight, sel, combsel)

		## Fix the duplicate weight in case of JES/MET/Btag/Lep sel Weights
		if syst in ['jesup', 'jesdn', 'jerup', 'jerdn']:
			finalsel = finalsel.replace('JESWeight[0]*','')
		if syst in ['btagup','btagdn']:
			finalsel = finalsel.replace('BtagWeight[0]*','')
		if syst in ['umetup','umetdn']:
			finalsel = finalsel.replace('METWeight[0]*','')
		if syst in ['lepselup','lepseldn']:
			finalsel = finalsel.replace('Weight[4]*','')

		## Remove the BR weight for the POWHEG samples
		if (syst in ['powherw', 'powpyth', 'mcatnlohw']	or 'p11' in syst):
			# Remove 'Weight[0]*', but not 'XXWeight[0]*'
			finalsel = re.sub('(^|\*)Weight\[0\]\*', '', finalsel)

		#add scale factor
		svlmassVar='SVLMass'
		if syst=='lesdn' : svlmassVar='SVLMass*SVLMass_sf[0]'
		if syst=='lesup' : svlmassVar='SVLMass*SVLMass_sf[1]'


		tasks.append((hname, svlmassVar, finalsel,
			          NBINS, XMIN, XMAX, MASSXAXISTITLE))
		hname_to_keys[hname] = (tag, syst, comb)

		for ntk1,ntk2 in NTRKBINS:
			tksel = "(SVNtrk>=%d&&SVNtrk<%d)"%(ntk1,ntk2)
			finalsel = "%s*%s*(%s&&%s&&%s)"%(COMMONWEIGHT, weight,
							 sel, combsel,tksel)
			## Fix the duplicate weight in case of JES/MET/Btag Weight
			if syst in ['jesup', 'jesdn', 'jerup', 'jerdn']:
				finalsel = finalsel.replace('JESWeight[0]*','')
			if syst in ['btagup','btagdn']:
				finalsel = finalsel.replace('BtagWeight[0]*','')
			if syst in ['umetup','umetdn']:
				finalsel = finalsel.replace('METWeight[0]*','')
			if syst in ['lepselup','lepseldn']:
				finalsel = finalsel.replace('Weight[4]*','')


			## Remove the BR weight for the POWHEG samples
			if (syst in ['powherw', 'powpyth', 'mcatnlohw'] or 'p11' in syst):
				# Remove 'Weight[0]*', but not 'XXWeight[0]*'
				finalsel = re.sub('(^|\*)Weight\[0\]\*', '', finalsel)

			#add scale factor
			svlmassVar='SVLMass'
			if syst=='lesdn' : svlmassVar='SVLMass*SVLMass_sf[0]'
			if syst=='lesup' : svlmassVar='SVLMass*SVLMass_sf[1]'

			hname = "SVLMass_%s_%s_%d" % (comb, htag, ntk1)
			tasks.append((hname, svlmassVar, finalsel,
				          NBINS, XMIN, XMAX, MASSXAXISTITLE))
			### DEBUG
			# if 'bfrag' in syst:
			# 	print 50*'#'
			# 	print syst
			# 	print finalsel
			hname_to_keys[hname] = (tag, syst, comb, ntk1)
	return tasks

def gatherHistosFromFiles(tasklist, files, dirname, hname_to_keys):
	## First extract a list of ALL histogram names from the tasklist
	hnames = [t[0] for tasks in tasklist.values() for t in tasks]

	histos = {}
	for ifilen in os.listdir(dirname):
		if not os.path.splitext(ifilen)[1] == '.root': continue
		ifile = ROOT.TFile.Open(os.path.join(dirname,ifilen), 'READ')
		print ifilen
		for hname in hnames:
			keys = hname_to_keys[hname]
			syst = keys[1]

			## Skip histo names that are not in this file
			if syst in [x[0] for x in SYSTSFROMFILES]:
				tfilens = [os.path.basename(x) for x in files[syst]]
				if not ifilen in tfilens: continue

			if syst in [x[0] for x in SYSTSFROMWEIGHTS]:
				tfilens = [os.path.basename(x) for x in files['nominal']]
				if not ifilen in tfilens: continue

			# if 'scale' in syst: print syst,ifilen

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

def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	systfiles = {} # procname -> filename
	try:
		for fname in os.listdir(os.path.join(args[0],'syst')):
			if not os.path.splitext(fname)[1] == '.root': continue
			for syst,_,systfile,_ in SYSTSFROMFILES:
				if fname in systfile:
					systfiles[syst] = [os.path.join(args[0], 'syst', fname)]

		# Get the split nominal files
		systfiles['nominal'] = []
		for fname in os.listdir(os.path.join(args[0],'Chunks')):
			if not os.path.splitext(fname)[1] == '.root': continue
			isdata,procname,splitno = resolveFilename(fname)
			if not procname == 'TTJets_MSDecays_172v5': continue
			if not splitno: continue # file is split

			systfiles['nominal'].append(os.path.join(args[0],'Chunks',fname))
		if len(systfiles['nominal']) < 20:
			print "ERROR >>> Missing files for split nominal sample?"
			return -1

	except IndexError:
		print "Please provide a valid input directory"
		exit(-1)

	hname_to_keys = {} # hname -> (tag, syst, comb)
	tasklist = {} # treefile -> tasklist

	for fsyst in systfiles.keys():
		if not fsyst in tasklist: tasklist[fsyst] = []
		for tag,sel,_ in SELECTIONS:
			if fsyst == 'nominal':
				for syst,_,weight,combs in SYSTSFROMWEIGHTS:
					tasks = makeSystTask(tag, sel, syst,
						                 hname_to_keys, weight=weight,
						                 combs=combs)
					tasklist[fsyst] += tasks

				tasks = []
				for comb,combsel in COMBINATIONS.iteritems():
					for var,nbins,xmin,xmax,titlex in CONTROLVARS:
						hname = "%s_%s_%s" % (var, comb, tag)
						finalsel = "%s*(%s&&%s)"%(COMMONWEIGHT, sel, combsel)
						tasks.append((hname, var, finalsel,
							                 nbins, xmin, xmax, titlex))
						hname_to_keys[hname] = (tag, var, comb)

				tasklist[fsyst] += tasks

				tasks = []
				for name, nus in [('nu', 1), ('nonu', 0), ('nuunm', -1)]:
					hname = "SVLMass_%s_%s_%s" % ('tot', tag, name)
					finalsel = "%s*(%s&&BHadNeutrino==%d)"%(
						                 COMMONWEIGHT, sel, nus)
					tasks.append((hname, 'SVLMass', finalsel,
						          NBINS, XMIN, XMAX, MASSXAXISTITLE))
					hname_to_keys[hname] = (tag, name, 'tot')

				tasklist[fsyst] += tasks


			else:
				tasks = makeSystTask(tag, sel, fsyst, hname_to_keys)
				tasklist[fsyst] += tasks

	if not opt.cache:
		# print '  Will process the following tasks:'
		# for filename,tasks in sorted(tasklist.iteritems()):
		# 	print filename
		# 	for task in tasks:
		# 		print task
		# raw_input("Press any key to continue...")
		runTasks(systfiles, tasklist, opt, 'syst_histos')

		systhistos = {} # (tag, syst, comb) -> histo
		systhistos = gatherHistosFromFiles(tasklist, systfiles,
			                           os.path.join(opt.outDir, 'syst_histos'),
			                           hname_to_keys)


		cachefile = open(".svlsysthistos.pck", 'w')
		pickle.dump(systhistos, cachefile, pickle.HIGHEST_PROTOCOL)
		cachefile.close()


		# print "Wrote syst histos to cache file"
		# raw_input("press key")

	cachefile = open(".svlsysthistos.pck", 'r')
	systhistos = pickle.load(cachefile)
	print '>>> Read syst histos from cache (.svlsysthistos.pck)'
	cachefile.close()

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)


	for var,_,_,_,_ in CONTROLVARS:
		for sel,tag in [
			#('inclusive', 'Fully Inclusive'),
			#('inclusive_mrank1', 'Mass ranked, leading p_{T}'),
			#('inclusive_mrank1dr', 'Mass ranked, #DeltaR<2, leading p_{T}'),
			#('inclusive_drrank1dr', '#DeltaR ranked, #DeltaR<2, leading p_{T}'),
			('inclusive_optmrank', 'Optimized mass rank')]:
			try: makeControlPlot(systhistos, var, sel, tag, opt)
			except KeyError:
				print 'control plots for %s selection not found' % sel

	for tag,_,_ in SELECTIONS:
		if not 'inclusive' in tag : continue
		print "... processing %s"%tag

		# Make plot of mass with and without neutrino:
		# for comb in COMBINATIONS.keys():
		# plot = RatioPlot('neutrino_%s'%tag)
		# plot.rebin = 2
		# plot.add(systhistos[(tag,'nonu', 'tot')], 'Without neutrino')
		# plot.add(systhistos[(tag,'nu',   'tot')], 'With neutrino')
		# plot.add(systhistos[(tag,'nuunm','tot')], 'Unmatched')
		# plot.reference = systhistos[(tag,'nominal','tot')]
		# plot.tag = "Mass shape with and without neutrinos"
		# plot.subtag = SELNAMES[tag] + COMBNAMES['tot']
		# plot.ratiotitle = 'Ratio wrt Total'
		# plot.ratiorange = (0.7, 1.3)
		# plot.colors = [ROOT.kBlue-3, ROOT.kRed-4, ROOT.kOrange-3]
		# plot.show("neutrino_%s_%s"%(tag,'tot'),
		# 	      os.path.join(opt.outDir, 'syst_plots'))
		# plot.reset()

		for name, title, systs, colors, comb in SYSTPLOTS:
			print name, title, systs, colors, comb
			plot = RatioPlot('%s_%s'%(name,comb))
			plot.rebin = 2

			for syst in systs:
				try:
					plot.add(systhistos[(tag,syst,comb)], SYSTNAMES[syst])
				except:
					print 'failed to add',(tag,syst,comb),syst

			plot.tag = title
			subtag = SELNAMES[tag] + COMBNAMES[comb]
			plot.subtag = subtag
			plot.ratiotitle = 'Ratio wrt %s' % SYSTNAMES[systs[0]]
			plot.ratiorange = (0.85, 1.15)
			plot.colors = colors
			filename = "%s_%s"%(name,tag)
			if comb != 'tot': filename += '_%s'%comb
			plot.show(filename, os.path.join(opt.outDir,'syst_plots'))
			plot.reset()

		# Make top pt plot with both correct and wrong
		plot = RatioPlot('toppt_paper_cor_wro')
		plot.canvassize = (600,600)
		plot.tag = 'Top quark p_{T} mismodeling'
		plot.rebin = 2
		plot.subtag = 'Inclusive channels'
		plot.tagpos = (0.92,0.85)
		plot.subtagpos = (0.92,0.78)
		plot.titlex = 'm_{svl} [GeV]'
		plot.ratiotitle = '1 / Nominal'
		# plot.ratiorange = (0.85, 1.15)
		plot.ratiorange = (0.92, 1.08)
		plot.legpos = (0.55, 0.38)
		plot.ratioydivisions = 405
		plot.colors = [ROOT.kGreen+2, ROOT.kGreen-6, ROOT.kRed+2, ROOT.kRed-6]
		plot.add(systhistos[(tag,'nominal','cor')], 'Nominal (correct)',      includeInRatio=False)
		plot.add(systhistos[(tag,'toppt','cor')], 'p_{T} weighted (correct)', includeInRatio=True)
		plot.add(systhistos[(tag,'nominal','wro')], 'Nominal (wrong)',        includeInRatio=False)
		plot.add(systhistos[(tag,'toppt','wro')], 'p_{T} weighted (wrong)',   includeInRatio=True)
		plot.reference = [systhistos[(tag,'nominal','cor')], systhistos[(tag,'nominal','wro')]]

		plot.show('toppt_cor_wro_forpaper_%s'%tag, os.path.join(opt.outDir,'syst_plots'))
		plot.reset()

		# Make b fragmentation plot for paper
		plot = RatioPlot('bfrag_paper')
		plot.canvassize = (600,600)
		plot.tag = 'b fragmentation'
		plot.titlex = 'm_{svl} [GeV]'
		plot.rebin = 2
		plot.subtag = 'Inclusive channels'
		plot.tagpos = (0.92,0.85)
		plot.subtagpos = (0.92,0.78)
		plot.ratiotitle = '1 / Z2* #it{r}_{b} LEP'
		# plot.ratiorange = (0.85, 1.15)
		plot.ratiorange = (0.92, 1.08)
		plot.legpos = (0.65, 0.20)
		plot.ratioydivisions = 405
		plot.colors = [ROOT.kMagenta, ROOT.kMagenta+2, ROOT.kMagenta-9, ROOT.kAzure+7]
		plot.add(systhistos[(tag,'nominal', 'tot')], 'Z2* #it{r}_{b} LEP', includeInRatio=False)
		plot.add(systhistos[(tag,'bfragdn', 'tot')], 'Z2* #it{r}_{b} LEP soft')
		plot.add(systhistos[(tag,'bfragup', 'tot')], 'Z2* #it{r}_{b} LEP hard')
		plot.add(systhistos[(tag,'bfragz2s','tot')], 'Z2* nominal')
		plot.reference = [systhistos[(tag,'nominal','tot')]]
		plot.show('bfrag_paper_%s'%tag, os.path.join(opt.outDir,'syst_plots'))
		plot.reset()


	# for tag,sel,seltag in SELECTIONS:
	# 	print 70*'-'
	# 	print '%-10s: %s' % (tag, sel)
	# 	fcor, fwro, funm = {}, {}, {}
	# 	for mass in sorted(massfiles.keys()):
	# 	# mass = 172.5
	# 		hists = masshistos[(tag, mass)]
	# 		n_tot, n_cor, n_wro, n_unm = (x.GetEntries() for x in hists)
	# 		fcor[mass] = 100.*(n_cor/float(n_tot))
	# 		fwro[mass] = 100.*(n_wro/float(n_tot))
	# 		funm[mass] = 100.*(n_unm/float(n_tot))
	# 		print ('  %5.1f GeV: %7d entries \t'
	# 			   '(%4.1f%% corr, %4.1f%% wrong, %4.1f%% unmatched)' %
	# 			   (mass, n_tot, fcor[mass], fwro[mass], funm[mass]))

	# 	oname = os.path.join(opt.outDir, 'fracvsmt_%s'%tag)
	# 	plotFracVsTopMass(fcor, fwro, funm, tag, seltag, oname)

	# print 112*'-'
	# print 'Estimated systematics (from a crude chi2 fit)'
	# print '%20s | %-15s | %-15s | %-15s | %-15s | %-15s' % (
	# 									 'selection', 'bfrag', 'scale',
	# 									 'toppt', 'matching', 'uecr')
	# for tag,_,_ in SELECTIONS:
	# 		sys.stdout.write("%20s | " % tag)
	# 		for syst in ['bfrag', 'scale', 'toppt', 'matching', 'uecr']:
	# 			err, chi2 = systematics[(tag,syst)]
	# 			sys.stdout.write('%4.1f (%4.1f GeV)' % (chi2*1e5, err))
	# 			# sys.stdout.write('%4.1f (%4.1f GeV)' % (chi2, err))
	# 			sys.stdout.write(' | ')
	# 		sys.stdout.write('\n')
	# print 112*'-'

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
	parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
					  help='Output directory [default: %default]')
	parser.add_option('-c', '--cache', dest='cache', action="store_true",
					  help='Read from cache')
	(opt, args) = parser.parse_args()

	exit(main(args, opt))




