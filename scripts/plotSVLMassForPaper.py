#! /usr/bin/env python
import os, sys, re
import os.path as osp
import ROOT
import pickle
from numpy import roots

from makeSVLMassHistos import NTRKBINS
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot

ALLMASSES = [166.5, 169.5, 171.5, 172.5, 173.5, 175.5, 178.5]
MASSESTOPLOT = [166.5, 172.5, 178.5]

def makeMassPlot(histos, outname, tag='', subtag=''):
	ratplot = RatioPlot('ratioplot')
	ratplot.normalized = False
	ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
	ratplot.extratext = ''
	ratplot.tag = tag
	ratplot.subtag = subtag
	ratplot.rebin = 1
	ratplot.legpos = (0.65, 0.15)
	ratplot.ratiorange = (0.7, 1.3)
	ratplot.reference = [histos[172.5]]
        ratplot.titley = "Combinations / %3.1f GeV" %histos['data'].GetXaxis().GetBinWidth(1)

	####################################################
	# Construct dummy data for now
	# dummy = histos[172.5].Clone('dummy_data')
	# dummy.Reset('ICE')
	# dummy.FillRandom(histos[173.5], ROOT.gRandom.Poisson(histos[172.5].Integral()))
	# ratplot.add(dummy,'Pseudo Data (@173.5 GeV)')
	####################################################

	####################################################
	# REAL DATA:
	ratplot.add(histos['data'], 'Data')
	####################################################

	# histos[MASSESTOPLOT[0]].SetLineStyle(2)
	# histos[MASSESTOPLOT[-1]].SetLineStyle(3)


	for mass in MASSESTOPLOT:
		legentry = 'm_{top} = %5.1f GeV' % mass
		try:
			histo = histos[mass]
			ratplot.add(histo, legentry, includeInRatio=(mass != 172.5))
		except KeyError: pass

	# ratplot.colors = [ROOT.kBlack, ROOT.kAzure-4, ROOT.kAzure+1, ROOT.kAzure-6]

	# ratplot.colors = [ROOT.kBlack, ROOT.kAzure-2, ROOT.kGray, ROOT.kOrange+9]
	ratplot.colors = [ROOT.kBlack, ROOT.kSpring-8, ROOT.kGray, ROOT.kOrange+9]

	# ratplot.colors = [ROOT.kBlack, ROOT.kOrange-4, ROOT.kOrange-3, ROOT.kOrange+9]

	ratplot.drawoptions = ['PE', 'hist', 'hist', 'hist']
	ratplot.markerstyles = [20,1,1,1]
	ratplot.markersizes =  [1.5,1,1,1]
	ratplot.show("massscan_paper_%s"%outname, opt.outDir)

def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)

	# Construct histograms
	peInputFile = ROOT.TFile.Open(args[0], 'READ')

	for selection in ['inclusive', 'optmrank']:
		seltag = '' if not selection == 'optmrank' else '_optmrank'
		masshistos = {}
		masshistosntk = {}
		masshistosntk[3] = {}
		masshistosntk[4] = {}
		masshistosntk[5] = {}
		for mass in ALLMASSES+['data']:
			masshist = None
			masstag = mass
			if type(mass) == float:
				masstag = 'nominal_'+str(mass).replace('.','v')

			for trk,_ in NTRKBINS:
				ihist = peInputFile.Get('%s/SVLMass_inclusive%s_%s_%d'%(masstag,seltag,masstag,trk))
				masshistosntk[trk][mass] = ihist.Clone('%s_%d'%(masstag, trk))
				try:
					masshist.Add(ihist)
				except AttributeError:
					try:
						masshist = ihist.Clone(masstag)
					except ReferenceError:
						print "Histogram not found: %s/SVLMass_inclusive%s_%s_%d"%(masstag,seltag,masstag,trk)
						continue
			masshistos[mass] = masshist
		makeMassPlot(histos=masshistos, outname=selection)
		makeMassPlot(histos=masshistosntk[3], outname='%s_3'%selection, tag='N_{tracks} = 3')
		makeMassPlot(histos=masshistosntk[4], outname='%s_4'%selection, tag='N_{tracks} = 4')
		makeMassPlot(histos=masshistosntk[5], outname='%s_5'%selection, tag='N_{tracks} = 5')

	return 0


if __name__ == "__main__":
	from optparse import OptionParser
	usage = """
	usage: %prog [options] pe_inputs.root
	"""
	parser = OptionParser(usage=usage)
	parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
					  help='Output directory [default: %default]')
	(opt, args) = parser.parse_args()


	exit(main(args, opt))




