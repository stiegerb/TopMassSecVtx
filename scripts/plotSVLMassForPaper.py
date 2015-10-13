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

def main(args, opt):
	os.system('mkdir -p %s'%opt.outDir)
	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)

	# Construct histograms
	peInputFile = ROOT.TFile.Open(args[0], 'READ')
	masshistos = {}
	for mass in ALLMASSES+['data']:
		masshist = None
		masstag = mass
		if type(mass) == float:
			masstag = 'nominal_'+str(mass).replace('.','v')

		for trk,_ in NTRKBINS:
			ihist = peInputFile.Get('%s/SVLMass_inclusive_optmrank_%s_%d'%(masstag,masstag,trk))
			try:
				masshist.Add(ihist)
			except AttributeError:
				try:
					masshist = ihist.Clone(masstag)
				except ReferenceError:
					print "Histogram not found: %s/SVLMass_inclusive_optmrank_%s_%d"%(masstag,masstag,trk)
					continue
		masshistos[mass] = masshist

	ratplot = RatioPlot('ratioplot')
	ratplot.normalized = False
	ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
	ratplot.tag = 'All channels combined'
	ratplot.extratext = 'Preliminary'
	ratplot.rebin = 1
	ratplot.legpos = (0.55, 0.15)
	ratplot.ratiorange = (0.5, 1.5)
	ratplot.reference = [masshistos[172.5]]

	####################################################
	# Construct dummy data for now
	dummy = masshistos[172.5].Clone('dummy_data')
	dummy.Reset('ICE')
	dummy.FillRandom(masshistos[173.5], ROOT.gRandom.Poisson(masshistos[172.5].Integral()))
	ratplot.add(dummy,'Pseudo Data (@173.5 GeV)')
	####################################################

	####################################################
	# REAL DATA:
	# ratplot.add(masshistos['data'], 'Data')
	####################################################

	for mass in MASSESTOPLOT:
		legentry = 'MC (m_{top} = %5.1f GeV)' % mass
		try:
			histo = masshistos[mass]
			ratplot.add(histo, legentry, includeInRatio=(mass != 172.5))
		except KeyError: pass

	ratplot.colors = [ROOT.kBlack, ROOT.kAzure-4, ROOT.kAzure+1, ROOT.kAzure-6]
	# ratplot.colors = [ROOT.kBlack, ROOT.kOrange-4, ROOT.kOrange-3, ROOT.kOrange+9]

	ratplot.drawoptions = ['PE', 'hist', 'hist', 'hist']
	ratplot.markerstyles = [20,1,1,1]
	ratplot.markersizes =  [1.5,1,1,1]
	ratplot.show("massscan_paper_optmrank", opt.outDir)

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




