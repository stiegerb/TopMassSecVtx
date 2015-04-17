#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot, setTDRStyle
from makeSVLMassHistos import MASSXAXISTITLE, TREENAME, NTRKBINS, NBINS, XMIN, XMAX
from makeSVLDataMCPlots import getHistoFromTree, projectFromTree
from makeSVLDataMCPlots import addDataMCPlotOptions
from runPlotter import runPlotter, addPlotterOptions, openTFile

SELECTIONS = [
	('e_qcd',        'abs(EvCat)==1100', 'non-isolated e, N_{jets}#geq 4, N_{b-tags} #leq 1'),
	('m_qcd',        'abs(EvCat)==1300', 'non-isolated #mu, N_{jets}#geq 4, N_{b-tags} #leq 1'),
	('e_mrank1_qcd',
	 'SVLMassRank==1&&SVLDeltaR<2.0&&CombCat%2!=0&&abs(EvCat)==1100',
	 'non-isolated e, N_{jets}#geq 4, N_{b-tags} #leq 1'),
	('m_mrank1_qcd',
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

def getNTrkHistos(tree, sel='', var="SVLMass", tag='',
		          nbins=NBINS, xmin=XMIN, xmax=XMAX,
		          titlex='', combsToProject=[('tot','')]):
	hists = []
	for ntk1,ntk2 in NTRKBINS:
		title = "%d #leq N_{trk.} < %d" %(ntk1, ntk2)
		if ntk2 > 100:
			title = "%d #leq N_{trk.}" %(ntk1)


		for comb,combSel in combsToProject:
			hist = ROOT.TH1D("%s_%s_%d_%s"%(var,comb,ntk1,tag),
				             title, nbins, xmin, xmax)
			tksel = "(SVNtrk>=%d && SVNtrk<%d)"%(ntk1,ntk2)
			finalSel=sel
			if finalSel=="": finalSel = "1"
			if combSel=="" : finalSel = "(%s)"%finalSel
			else           : finalSel = "(%s && %s)"%(finalSel,combSel)
			finalSel=finalSel+"&&"+tksel
			projectFromTree(hist, var, finalSel, tree)
			hists.append(hist)

	for x in hists:
		x.SetLineWidth(2)
		x.GetXaxis().SetTitle(titlex)
		x.Sumw2()

	return hists

def main(args, options):
	os.system('mkdir -p %s'%options.outDir)
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

	## Collect all the trees
	svltrees = {} # proc -> tree
	for proc in treefiles.keys():
		tfile = ROOT.TFile.Open(treefiles[proc], 'READ')
		if not filterUseless(treefiles[proc]): continue
		svltrees[proc] = tfile.Get(TREENAME)

	## Produce all the relevant histograms
	if not options.cached:
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


		cachefile = open(".svlqcdmasshistos.pck", 'w')
		pickle.dump(masshistos,     cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(methistos,      cachefile, pickle.HIGHEST_PROTOCOL)
		pickle.dump(fittertkhistos, cachefile, pickle.HIGHEST_PROTOCOL)
		cachefile.close()


	else:
		cachefile = open(".svlqcdmasshistos.pck", 'r')
		masshistos     = pickle.load(cachefile)
		methistos      = pickle.load(cachefile)
		fittertkhistos = pickle.load(cachefile)
		cachefile.close()


	#########################################################
	## Write out the histograms, make data/mc plots
	outputFileName = os.path.join(options.outDir,'qcd_DataMCHists.root')
	ofi = ROOT.TFile(outputFileName, 'recreate')
	ofi.cd()
	for hist in [h for h in masshistos.values() + methistos.values()]:
		hist.Write(hist.GetName())
	for hist in [h for hists in fittertkhistos.values() for h in hists]:
		hist.Write(hist.GetName())
	ofi.Write()
	ofi.Close()

	## Run the plotter to get scaled MET plots
	## Can then use those to subtract non-QCD backgrounds from data template
	## Overwrite some of the options
	options.filter = 'SVLMass,MET' ## only run SVLMass and MET plots
	# options.excludeProcesses = 'QCD'
	options.outFile = 'scaled_met_inputs.root'
	options.cutUnderOverFlow = True
	os.system('rm %s' % os.path.join(options.outDir, options.outFile))
	runPlotter(outputFileName, options)

	#########################################################
	## Build the actual templates from the single histograms
	templates = {} # selection tag -> template histo
	inputfile = openTFile(os.path.join(options.outDir, options.outFile))

	for tag,sel,_ in SELECTIONS:
		categories = ['MET', 'SVLMass']
		for x,_ in NTRKBINS:
			categories.append('SVLMass_tot_%d'%int(x))

		for category in categories:
			plotdirname = '%s_%s'%(category,tag)
			plotdir = inputfile.Get(plotdirname)
			h_bg = None
			h_data = None
			for tkey in plotdir.GetListOfKeys():
				key = tkey.GetName()
				if key.startswith('Graph_from'): continue
				if key.startswith('MC8TeV_QCD'): continue

				hist = inputfile.Get('%s/%s'%(plotdirname,key))
				if key.startswith('MC8TeV'):
					if not h_bg:
						h_bg = hist.Clone("%s_BGs" % tag)
					else:
						h_bg.Add(hist)

				if key.startswith('Data8TeV'):
					h_data = hist.Clone("%s_Data" % tag)

			## Determine a suitable output name
			histname = '%s_template'%tag
			if category == 'MET': histname = "%s_%s" % ('met',histname)
			if 'tot' in category:
				tkbin = int(category.split('_')[2])
				histname = "%s_%d" % (histname, tkbin)
			h_data_subtr = h_data.Clone(histname)

			## Now subtract the combined MC from the data
			h_data_subtr.Add(h_bg, -1)

			dicttag = tag
			if category == 'MET':
				dicttag = 'met_%s'%tag
			if '_tot_' in category:
				dicttag = '%s_%d' % (tag, tkbin)
			templates[dicttag] = h_data_subtr

	ofi = ROOT.TFile(os.path.join(options.outDir,'qcd_templates.root'),
		             'recreate')
	ofi.cd()
	for hist in templates.values(): hist.Write(hist.GetName())
	ofi.Write()
	ofi.Close()

	for key,hist in sorted(templates.iteritems()):
		print key


	#########################################################
	## Make a plot comparing the templates
	for tag,_,seltag in SELECTIONS:
		templateplot = RatioPlot('qcdtemplates_%s'%tag)
		for key,hist in sorted(templates.iteritems()):
			if not tag in key: continue
			if key.startswith('met'): continue

			if key == tag:
				templateplot.add(hist, 'Inclusive')
				templateplot.reference = hist
			else:
				ntrkbin = int(key.rsplit('_',1)[1])
				templateplot.add(hist, 'N_{track} = %d'%ntrkbin)

		templateplot.tag = 'QCD templates'
		templateplot.subtag = seltag
		templateplot.tagpos    = (0.90, 0.85)
		templateplot.subtagpos = (0.90, 0.78)
		templateplot.legpos = (0.75, 0.25)
		templateplot.ratiotitle = 'Ratio wrt Inclusive'
		templateplot.extratext = 'Work in Progress'
		templateplot.ratiorange = (0.2, 2.2)
		templateplot.colors = [ROOT.kBlack, ROOT.kBlue-8, ROOT.kAzure-2,
		                       ROOT.kCyan-3]
		templateplot.show("qcdtemplates_%s"%tag, options.outDir)
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
	addPlotterOptions(parser)
	addDataMCPlotOptions(parser)
	(opt, args) = parser.parse_args()

	setTDRStyle()
	gROOT.SetBatch(True)
	gStyle.SetOptTitle(0)
	gStyle.SetOptStat(0)

	exit(main(args, opt))




