#! /usr/bin/env python
import os, sys, re
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot
from makeSVLControlPlots import NBINS, XMIN, XMAX, MASSXAXISTITLE
from makeSVLControlPlots import NTRKBINS, COMMONWEIGHT
from makeSVLControlPlots import SELECTIONS, TREENAME
from makeSVLControlPlots import getSVLHistos, getNTrkHistos, makeControlPlot


def addTopMassTreesFromDir(dirname, ttbar, singlet, singletW, singlets):
	for filename in os.listdir(dirname):
		if not os.path.splitext(filename)[1] == '.root': continue

		## Select top samples
		if not "TTJets" in filename and not "SingleT" in filename: continue

		## Extract the mass
		matchres = re.match(r'.*([0-9]{3})v5\.root', filename)
		if matchres: mass = float(matchres.group(1)) + 0.5
		else: mass = 172.5

		tfile = ROOT.TFile.Open(os.path.join(dirname,filename),'READ')
		tree = tfile.Get(TREENAME)

		if "TTJets" in filename:
			# print "Found ttbar channel", filename
			ttbar[mass] = tree
		elif 'SingleT' in filename and '_tW' in filename:
			# print "Found tW channel", filename
			if not mass in singletW:
				singletW[mass] = ROOT.TChain(TREENAME)
			singletW[mass].Add(os.path.join(dirname, filename))
		elif 'SingleT' in filename and '_t' in filename:
			# print "Found t channel", filename
			if not mass in singlet:
				singlet[mass] = ROOT.TChain(TREENAME)
			singlet[mass].Add(os.path.join(dirname, filename))
		elif 'SingleT' in filename and '_s' in filename:
			# print "Found s channel", filename
			if not mass in singlets:
				singlets[mass] = ROOT.TChain(TREENAME)
			singlets[mass].Add(os.path.join(dirname, filename))
def getMassTrees(inputdir, verbose=True):
	ttbar    = {}  # mass -> tree
	singlet  = {}  # mass -> tree
	singletW = {}  # mass -> tree
	singlets = {}  # mass -> tree

	addTopMassTreesFromDir(inputdir, ttbar, singlet, singletW, singlets)
	addTopMassTreesFromDir(os.path.join(inputdir, 'mass_scan'),
	                                 ttbar, singlet, singletW, singlets)

	allmasses = list(set(sorted(ttbar.keys() + singlet.keys() +
		                        singletW.keys() + singlets.keys() )))

	alltrees = {} # (mass, tt/t/tW/s) -> tree
	for mass in allmasses:
		if mass in ttbar:
			alltrees[(mass,'tt')] = ttbar[mass]
		if mass in singlet:
			alltrees[(mass,'t')]  = singlet[mass]
		if mass in singletW:
			alltrees[(mass,'tW')] = singletW[mass]
		if mass in singlets:
			alltrees[(mass,'s')]  = singlets[mass]

	if verbose:
		print 80*'-'
		print "Found the following mass points (#entries):"
		for mass in sorted(allmasses):
			line = '  %5.1f GeV '%mass
			if (mass, 'tt') in alltrees:
				line += ' (tt: %7d) '     % alltrees[(mass, 'tt')].GetEntries()
			if (mass, 't') in alltrees:
				line += ' (t: %5d) '  % alltrees[(mass, 't')].GetEntries()
			if (mass, 'tW') in alltrees:
				line += ' (tW: %6d) ' % alltrees[(mass, 'tW')].GetEntries()
			if (mass, 's') in alltrees:
				line += ' (s: %6d) ' % alltrees[(mass, 's')].GetEntries()
			print line
		print 80*'-'

	return alltrees

def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	masstrees = getMassTrees(args[0], verbose=True)

	if not opt.cache:
		masshistos = {}    # (tag, chan, mass) -> h_tot, h_cor, h_wro, h_unm
		massntkhistos = {} # (tag, chan, mass) -> h_tot, h_cor, h_wro, h_unm

		totaltasks, taskcounter = (len(SELECTIONS) * len(masstrees)), 0
		for tag,sel,_ in SELECTIONS:
			for (mass,chan) in masstrees.keys():
				taskcounter += 1
				tree = masstrees[(mass,chan)]
				htag = ("%s_%5.1f"%(tag,mass)).replace('.','')
				if not chan == 'tt':
					htag = ("%s_%s_%5.1f"%(tag,chan,mass)).replace('.','')
				print (' ... processing %3d/%3d: tag=%-25s entries: %7d'%
					                    (taskcounter, totaltasks,
					                     htag, tree.GetEntries()))
				hists = getSVLHistos(tree, sel, var="SVLMass", tag=htag,
								     titlex=MASSXAXISTITLE)
				masshistos[(tag, chan, mass)] = hists

				hists = getNTrkHistos(tree, sel=sel, tag=htag, var='SVLMass',
				                      titlex=MASSXAXISTITLE,
								      combsToProject=[('tot',''),
								                     ('cor','CombInfo==1'),
								                     ('wro','CombInfo==0'),
								                     ('unm','CombInfo==-1')])
				massntkhistos[(tag, chan, mass)] = hists


		cachefile = open(".svlhistos.pck", 'w')
		pickle.dump(masshistos,     cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(massntkhistos, cachefile, pickle.HIGHEST_PROTOCOL)
		cachefile.close()

		ofi = ROOT.TFile(os.path.join(opt.outDir,'masshistos.root'),
			                                                   'recreate')
		ofi.cd()
		for hist in [h for hists in masshistos.values() for h in hists]:
			hist.Write(hist.GetName())
		for hist in [h for hists in massntkhistos.values() for h in hists]:
			hist.Write(hist.GetName())
		ofi.Write()
		ofi.Close()

	else:
		cachefile = open(".svlhistos.pck", 'r')
		masshistos     = pickle.load(cachefile)
		massntkhistos = pickle.load(cachefile)
		cachefile.close()

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)

	errorGetters = {} # tag -> function(chi2) -> error
	systematics = {} # (seltag, systname) -> error
	for tag,sel,seltag in SELECTIONS:
		print "... processing %s"%tag

		for chan in [x for _,x in masstrees.keys()]: ## tt, t, tW, s
			if chan == 's': continue

			ratplot = RatioPlot('ratioplot')

			ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
			ratplot.ratiorange = (0.5, 1.5)

			ratplot.reference = masshistos[(tag,172.5)][0]
			for mass in sorted(massfiles.keys()):
				legentry = 'm_{t} = %5.1f GeV' % mass
				ratplot.add(masshistos[(tag,mass)][0], legentry)
			ratplot.tag = 'All combinations'
			ratplot.subtag = seltag
			ratplot.show("massscan_%s_tot"%tag, opt.outDir)

			chi2s = ratplot.getChiSquares(rangex=FITRANGE)
			chi2stofit = []
			for legentry in sorted(chi2s.keys()):
				chi2stofit.append((float(legentry[8:-4]), chi2s[legentry]))
			errorGetters[tag] = fitChi2(chi2stofit,
										tag=seltag,
										oname=os.path.join(opt.outDir,
									    "chi2_simple_fit_%s.pdf"%tag),
										drawfit=False)
			ratplot.reset()

			ratplot.reference = masshistos[(tag,172.5)][1]
			for mass in sorted(massfiles.keys()):
				legentry = 'm_{t} = %5.1f GeV' % mass
				ratplot.add(masshistos[(tag,mass)][1], legentry)
			ratplot.tag = 'Correct combinations'
			ratplot.subtag = seltag
			ratplot.show("massscan_%s_cor"%tag, opt.outDir)
			ratplot.reset()

			ratplot.reference = masshistos[(tag,172.5)][2]
			for mass in sorted(massfiles.keys()):
				legentry = 'm_{t} = %5.1f GeV' % mass
				ratplot.add(masshistos[(tag,mass)][2], legentry)
			ratplot.tag = 'Wrong combinations'
			ratplot.subtag = seltag
			ratplot.show("massscan_%s_wro"%tag, opt.outDir)
			ratplot.reset()

			ratplot.reference = masshistos[(tag,172.5)][3]
			for mass in sorted(massfiles.keys()):
				legentry = 'm_{t} = %5.1f GeV' % mass
				ratplot.add(masshistos[(tag,mass)][3], legentry)
			ratplot.tag = 'Unmatched combinations'
			ratplot.subtag = seltag
			ratplot.show("massscan_%s_unm"%tag, opt.outDir)
			ratplot.reset()

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
	parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
					  help='Output directory [default: %default]')
	parser.add_option('-c', '--cache', dest='cache', action="store_true",
					  help='Read from cache')
	(opt, args) = parser.parse_args()

	exit(main(args, opt))




