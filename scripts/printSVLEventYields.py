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
    'MC8TeV_WJets'                    : '\\PW+jets',
    'MC8TeV_TTWJets'                  : '\\ttV',
    'MC8TeV_TTJets_MSDecays_172v5'    : '\\ttbar',
    'MC8TeV_WW'                       : 'Diboson',
    'MC8TeV_DYJets'                   : 'DY+jets',
}

PROCNAMETORANK = {
	'Data'          : -1,
	'total'         : 0,
	'\\ttbar'       : 1,
	'Single top'    : 2,
	'\\PW+jets'     : 3,
	'DY+jets'       : 4,
	'QCD multijets' : 5,
	'Diboson'       : 6,
	'\\ttV'         : 7,
}

CHANTORANK = {'em':0, 'mm':1, 'ee':2, 'm':3, 'e':4}

def printYields(yields):
	cleanyields = {}

	## Change keys to be uniform
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

	## Build total:
	totals = {}
	for chan,proc in yields:
		totals[(chan,proc)] = yields[(chan,proc)]
		if 'Data' in proc: continue
		try:
			previous = totals[(chan, 'total')]
			totals[(chan, 'total')] = ( previous[0]+yields[(chan, proc)][0],
			                            sqrt(previous[1]**2+(yields[(chan, proc)][1])**2) )
		except KeyError:
			totals[(chan, 'total')] = ( yields[(chan, proc)][0],
				                        yields[(chan, proc)][1] )


	channels  = list(set([c for c,_ in totals.keys()]))
	channels.sort(key=lambda p: CHANTORANK[p], reverse=True)
	processes = list(set([p for _,p in totals.keys()]))
	processes.sort(key=lambda p: PROCNAMETORANK[PROCTOPROCNAME[p]], reverse=True)

	print 127*'-'
	print 20*" "+' &',
	for chan in channels:
		print ("   %-15s &" % chan),
	print ''
	for proc in processes:
		procname = PROCTOPROCNAME[proc]
		print "%-20s &" % procname,
		for chan in channels:
			try:
				if totals[(chan, proc)][0]>0.5:
					print " $%6.0f \pm %4.0f$ &" % (totals[(chan, proc)]),
				else:
					print " $    <1         $ &",
			except KeyError:
				print " $    <1         $ &",

		print ' '
	print 127*'-'
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
			firstBin=opt.firstBin
			lastBin=hist.GetXaxis().GetNbins()  if opt.lastBin<opt.firstBin else opt.lastBin
			integral = hist.IntegralAndError(firstBin,lastBin, err)
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
	parser.add_option(      '--firstBin', dest='firstBin', default=1, type=int,
					  help='first bin to use for the integral [default: %default]')
	parser.add_option(      '--lastBin', dest='lastBin', default=-1, type=int,
					  help='last bin to use for the integral [default: %default]')
	parser.add_option('-d', '--dist', dest='dist', default='NJets',
					  help='Which distribution to use [default: %default]')
	(opt, args) = parser.parse_args()

	exit(main(args, opt))




