#! /usr/bin/env python
import os, sys, re
import ROOT
import pickle
from runPlotter import openTFile, getAllPlotsFrom
from math import sqrt
from pprint import pprint

DSETNAMETOPROC = {
	'MC8TeV_DYJetsToLL_50toInf':  'MC8TeV_DYJets',
	'MC8TeV_DY1JetsToLL_50toInf': 'MC8TeV_DYJets',
	'MC8TeV_QCDPt80to170':        'MC8TeV_QCD',
	'MC8TeV_QCDPt170to250':       'MC8TeV_QCD',
	'MC8TeV_QCDPt250to350':       'MC8TeV_QCD',
	'MC8TeV_QCDPt350toInf':       'MC8TeV_QCD',
	'MC8TeV_WJets':               'MC8TeV_WJets',
	'MC8TeV_W1Jets':              'MC8TeV_WJets',
	'MC8TeV_W2Jets':              'MC8TeV_WJets',
	'MC8TeV_W3Jets':              'MC8TeV_WJets',
	'MC8TeV_W4Jets':              'MC8TeV_WJets',
}

PROCTOPROCNAME = {
	'total'                           : 'total',
	'MC8TeV_SingleTbar_tW'            : 'Single top',
    'Data'                            : 'Data',
    'MC8TeV_QCD'                      : 'QCD multijets',
    'MC8TeV_WJets'                    : 'W+jets',
    'MC8TeV_TTWJets'                  : 'ttV',
    'MC8TeV_TTJets_MSDecays_172v5'    : 'ttbar',
    'MC8TeV_WW'                       : 'Diboson',
    'MC8TeV_DYJets'                   : 'DY+jets',
}

def printYields(yields):
	cleanyields = {}
	for chan,dset in yields:
		proc = dset
		try:
			proc = DSETNAMETOPROC[proc]
		except KeyError:
			proc = dset
		if proc.startswith('Data8TeV'):
			proc = 'Data'

		cleanyields[(chan, proc)] = yields[(chan,dset)]
	yields = cleanyields

	# Build total:
	totals = {}
	for chan,proc in yields:
		totals[(chan,proc)] = yields[(chan,proc)]
		try:
			previous = totals[(chan, 'total')]
			totals[(chan, 'total')] = ( previous[0]+yields[(chan, proc)][0],
			                            sqrt(previous[1]**2+(yields[(chan, proc)][1])**2) )
		except KeyError:
			totals[(chan, 'total')] = ( yields[(chan, proc)][0],
				                        yields[(chan, proc)][1] )


	# pprint(totals)


	channels = list(set([c for c,_ in totals.keys()]))
	processes = list(set([p for _,p in totals.keys() if not p =='total']))

	print 105*'-'
	print 20*" ",
	for chan in sorted(channels):
		print ("   %-12s" % chan),
	print ''
	for proc in processes+['total']:
		procname = PROCTOPROCNAME[proc]
		print "%-20s"%procname,
		for chan in sorted(channels):
			try:
				if totals[(chan, proc)][0]>0.5:
					print "%7.0f +- %4.0f"%(totals[(chan, proc)]),
				else:
					raise KeyError
			except KeyError:
				print 15*' ',

		print ' '
	print 105*'-'
	return 0


def main(args, opt):
	try:
		cachefile = open(".eventyields.pck", 'r')
		yields = pickle.load(cachefile)
		cachefile.close()
		return printYields(yields)

	except EOFError:
		print "Error loading pickle file, please delete it and try again"
		return -1
	except IOError:
		pass

	try:
		tfile = openTFile(args[0])
	except ReferenceError:
		print "Please provide a valid input file"
		return -1

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)

	allkeys = getAllPlotsFrom(tfile, tagsToFilter=[opt.dist])

	channels = ['e', 'ee', 'em', 'm', 'mm']

	print 30*'-'
	yields = {}

	for chan in channels:
		for key in allkeys:
			histname = "%s_%s"%(opt.dist,chan)
			if not key.endswith(histname): continue
			hist = tfile.Get(key)
			err = ROOT.Double(0.0)
			integral = hist.IntegralAndError(1,hist.GetXaxis().GetNbins(), err)
			err = float(err)

			proc = key.rsplit('/',1)[1]
			proc = proc.replace('_%s'%histname, '')

			yields[(chan,proc)] = (integral, err)

	cachefile = open(".eventyields.pck", 'w')
	pickle.dump(yields, cachefile, pickle.HIGHEST_PROTOCOL)
	cachefile.close()

	return printYields(yields)


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
	parser.add_option('-o', '--outDir', dest='outDir', default='genmlb',
					  help='Output directory [default: %default]')
	parser.add_option('-d', '--dist', dest='dist', default='NJets',
					  help='Which distribution to use [default: %default]')
	(opt, args) = parser.parse_args()

	exit(main(args, opt))




