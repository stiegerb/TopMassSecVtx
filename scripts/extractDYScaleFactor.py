#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from runPlotter import openTFile, getAllPlotsFrom

SIGNAL = 'MC8TeV_DYJetsToLL_50toInf'
HISTSTOPROCESS = [
	'DY_mll_ee',
	'DY_mll_mm'
]

def prepareDYScaleFactors(filename, plotfile, inputdir, options,
	                      dytag="DY+Jets",
	                      unmergedfile="MC8TeV_TTJets_MSDecays_172v5.root"):
	"""
	Prepares a dictionary of (key, process title) -> scale factor,
	to be used in the runPlotter script to scale DY by a data-derived
	scale factor.

	A list of keys to be scaled is generated from a plotfile (for merged
	histograms), and from one file of an input directory (for unmerged ones).
	"""

	## First calculate the actual scalefactors
	DYSFs = extractFactors(filename, options=options)

	## Get a list of all keys that are to be scaled
	allkeys = []

	## Need the list of processes
	tagsToFilter = ['_ee', '_mm', '_mumu']

	## From merged plots:
	allkeys += getAllPlotsFrom(openTFile(plotfile),
		                       tagsToFilter=tagsToFilter,
		                       filterByProcsFromJSON=options.json)

	## From unmerged plots:
	allkeys += getAllPlotsFrom(openTFile(os.path.join(inputdir,
		                                              unmergedfile)),
		                       tagsToFilter=tagsToFilter)

	## Prepare dictionary of (key,tag) -> scale factor
	scaleFactors = {}

	if options.verbose > 0:
		print 'Will scale the following histograms for %s:' % dytag
	for key in allkeys:
		if '_ee' in key:
			scaleFactors[(key, dytag)] = DYSFs['ee']
			if options.verbose > 0:
				print '  %-25s: %5.3f' % (key, DYSFs['ee'])
		else:
			scaleFactors[(key, dytag)] = DYSFs['mm']
			if options.verbose > 0:
				print '  %-25s: %5.3f' % (key, DYSFs['mm'])

	return scaleFactors


def extractFactors(inputFile, options):
	try:
		cachefile = open('.svldyscalefactors.pck','r')
		scaleFactors = pickle.load(cachefile)
		cachefile.close()
		return scaleFactors
	except IOError:
		pass

	try:
		tfile = openTFile(inputFile)
	except ReferenceError:
		print "Please provide a valid input file"

	allkeys = getAllPlotsFrom(tfile, tagsToFilter=HISTSTOPROCESS)
	scaleFactors = {}

	for histname in HISTSTOPROCESS:
		tot_data = 0
		tot_background = 0
		tot_signal = 0

		for key in allkeys:
			if not key.endswith(histname): continue
			integral = tfile.Get(key).Integral()
			if 'Data8TeV' in key:
				tot_data += integral
			elif SIGNAL in key:
				tot_signal += integral
			else:
				tot_background += integral

		channame = histname.rsplit('_',1)[1]
		if options.verbose>0:
			print 30*'-'
			print histname
			print ("Total data: %6.1f, total bg: %6.1f, total signal: %6.1f "
				        % (tot_data, tot_background, tot_signal))
		# tot_background + SF * tot_signal = tot_data
		SF = (tot_data-tot_background)/tot_signal
		if options.verbose>0:
			print " -> scale factor: %5.3f" % SF
		scaleFactors[channame] = SF
	if options.verbose>0: print 30*'-'

	cachefile = open(".svldyscalefactors.pck", 'w')
	pickle.dump(scaleFactors, cachefile, pickle.HIGHEST_PROTOCOL)
	cachefile.close()
	return scaleFactors

def main(args, opt):
	SFs = extractFactors(args[0], options=opt)
	print SFs
	return 0



if __name__ == "__main__":
	import sys
	tmpargv  = sys.argv[:]     # [:] for a copy, not reference
	sys.argv = []
	from ROOT import gROOT, gStyle
	sys.argv = tmpargv
	from optparse import OptionParser
	usage = """
	usage: %prog [options] plotter.root
	"""
	parser = OptionParser(usage=usage)
	(opt, args) = parser.parse_args()

	exit(main(args, opt))




