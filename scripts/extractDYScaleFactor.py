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

def extractFactors(inputFile):
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
			if key.startswith('Data8TeV'):
				tot_data += integral
			elif SIGNAL in key:
				tot_signal += integral
			else:
				tot_background += integral

		channame = histname.rsplit('_',1)[1]
		print 30*'-'
		print histname
		print ("Total data: %6.1f, total bg: %6.1f, total signal: %6.1f "%
		                         (tot_data, tot_background, tot_signal))
		# tot_background + SF * tot_signal = tot_data
		SF = (tot_data-tot_background)/tot_signal
		print " -> scale factor: %5.3f" % SF
		scaleFactors[channame] = SF
	print 30*'-'
	return scaleFactors

def main(args, opt):
	SFs = extractFactors(args[0])
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




