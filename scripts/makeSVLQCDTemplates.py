#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot, setTDRStyle
from makeSVLControlPlots import MASSXAXISTITLE, TREENAME, NTRKBINS
from makeSVLControlPlots import getHistoFromTree, getNTrkHistos

SELECTIONS = [
	('e_qcd',         'abs(EvCat)==1100', 'non-isolated e, N_{jets}#geq 4, N_{b-tags} #leq 1'),
	('mu_qcd',        'abs(EvCat)==1300', 'non-isolated #mu, N_{jets}#geq 4, N_{b-tags} #leq 1'),
	('e_mrank1_qcd',
	 'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&abs(EvCat)==1100',
	 'non-isolated e, N_{jets}#geq 4, N_{b-tags} #leq 1'),
	('mu_mrank1_qcd',
	 'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&abs(EvCat)==1300',
	 'non-isolated #mu, N_{jets}#geq 4, N_{b-tags} #leq 1'),
]

def filterUseless(filename, sel=''):
	isdata = 'Data8TeV' in filename
	if not isdata: return True
	if not 'Single' in filename: return False
	if '1100' in sel and not 'SingleElectron' in filename: return False
	if '1300' in sel and not 'SingleMu'       in filename: return False
	return True

def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	try:
		treefiles = {} # procname -> filename
		for filename in os.listdir(args[0]):
			if not os.path.splitext(filename)[1] == '.root': continue
			procname = filename.split('_',1)[1][:-5]
			treefiles[procname] = os.path.join(args[0],filename)

	except OSError:
		print "Not a valid input directory: %s" % args[0]
		return -1

	except IndexError:
		print "Need to provide an input directory"
		return -1

	svltrees = {} # proc -> tree
	for proc in treefiles.keys():
		tfile = ROOT.TFile.Open(treefiles[proc], 'READ')
		if not filterUseless(treefiles[proc]): continue
		svltrees[proc] = tfile.Get(TREENAME)

	if not opt.cache:
		masshistos = {}     # (selection tag, process) -> histo
		methistos  = {}     # (selection tag, process) -> histo
		fittertkhistos = {} # (selection tag, process) -> [h_ntk1, h_ntk2, ...]
		for tag,sel,_ in SELECTIONS:
			for proc, tree in svltrees.iteritems():
				if not filterUseless(treefiles[proc], sel): continue

				htag = ("%s_%s"%(tag, proc)).replace('.','')
				print ' ... processing %-30s %s htag=%s' % (proc, sel, htag)
				masshistos[(tag, proc)] = getHistoFromTree(tree, sel=sel,
					                               var='SVLMass',
		                                           hname="SVLMass_%s"%(htag),
		                                           titlex=MASSXAXISTITLE)

				methistos[(tag, proc)] =  getHistoFromTree(tree, sel=sel,
					                               var='MET',
		                                           hname="MET_%s"%(htag),
		                                           xmin=0,xmax=200,
		                                           titlex="Missing E_{T} [GeV]")

				fittertkhistos[(tag,proc)] = getNTrkHistos(tree, sel=sel,
									   tag=htag,
									   var='SVLMass',
									   titlex=MASSXAXISTITLE)


		cachefile = open(".svlqcdtemplates.pck", 'w')
		pickle.dump(masshistos,     cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(methistos,      cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(fittertkhistos, cachefile, pickle.HIGHEST_PROTOCOL)
		cachefile.close()


	else:
		cachefile = open(".svlqcdtemplates.pck", 'r')
		masshistos     = pickle.load(cachefile)
		methistos      = pickle.load(cachefile)
		fittertkhistos = pickle.load(cachefile)
		cachefile.close()


	## Build the templates from the single histograms
	templates = {} # selection tag -> template histo
	for tag,sel,_ in SELECTIONS:
		for proc in svltrees.keys():
			if not filterUseless(treefiles[proc], sel): continue
			if not 'Data8TeV' in treefiles[proc]: continue

			hist = masshistos[(tag,proc)]
			if not tag in templates:
				templates[tag] = hist
				hist.SetName('%s_template'%tag)
			else:
				templates[tag].Add(hist)

			for tkhist in fittertkhistos[(tag,proc)]:
				try:
					tkbin = int(tkhist.GetName().split('_')[2])
				except ValueError:
					print ('Failed to extract track bin from histo name:%s' %
						                              tkhist.GetName())
					continue
				tktag = '%s_%d' % (tag, tkbin)

				if not tktag in templates:
					templates[tktag] = tkhist
					tkhist.SetName('%s_template'%tktag)
				else:
					templates[tktag].Add(tkhist)

			## MET templates:
			hist = methistos[(tag,proc)]
			mettag = "met_%s"%tag
			if not mettag in templates:
				templates[mettag] = hist
				hist.SetName('%s_template'%mettag)
			else:
				templates[mettag].Add(hist)



	ofi = ROOT.TFile(os.path.join(opt.outDir,'qcd_DataMCHists.root'), 'recreate')
	ofi.cd()
	for hist in [h for h in masshistos.values() + methistos.values()]:
		hist.Write(hist.GetName())
	for hist in [h for hists in fittertkhistos.values() for h in hists]:
		hist.Write(hist.GetName())
	ofi.Write()
	ofi.Close()

	ofi = ROOT.TFile(os.path.join(opt.outDir,'qcd_templates.root'), 'recreate')
	ofi.cd()
	# for hist in [h for h in masshistos.values()]:
	# 	hist.Write(hist.GetName())
	# for hist in [h for hists in fittertkhistos.values() for h in hists]:
	# 	hist.Write(hist.GetName())
	for hist in templates.values(): hist.Write(hist.GetName())
	ofi.Write()
	ofi.Close()

	for tag,_,seltag in SELECTIONS:
		templateplot = RatioPlot('qcdtemplates_%s'%tag)
		for key,hist in sorted(templates.iteritems()):
			if not tag in key: continue
			if 'met' in key: continue

			if key == tag:
				templateplot.add(hist, 'Inclusive')
				templateplot.reference = hist
			else:
				templateplot.add(hist, hist.GetTitle())

		templateplot.tag = 'QCD templates'
		templateplot.subtag = seltag
		templateplot.ratiotitle = 'Ratio wrt Inclusive'
		templateplot.extratext = 'Work in Progress'
		templateplot.ratiorange = (0.2, 2.2)
		templateplot.colors = [ROOT.kBlack, ROOT.kBlue-8, ROOT.kAzure-2,
		                       ROOT.kCyan-3]
		templateplot.show("qcdtemplates_%s"%tag, opt.outDir)
		templateplot.reset()


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
	parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
					  help='Output directory [default: %default]')
	parser.add_option('-c', '--cache', dest='cache', action="store_true",
					  help='Read from cache')
	(opt, args) = parser.parse_args()

	setTDRStyle()
	gROOT.SetBatch(True)
	gStyle.SetOptTitle(0)
	gStyle.SetOptStat(0)

	exit(main(args, opt))




