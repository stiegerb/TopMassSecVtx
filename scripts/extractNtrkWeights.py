#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from pprint import pprint
from runPlotter import openTFile, getAllPlotsFrom

SIGNAL = 'MC8TeV_DYJetsToLL_50toInf'
HISTSTOPROCESS = ['SVNtrk_inclusive', 'SVNtrk_inclusive_optmrank'] #'SVNtrk_inclusive_mrank1']

def extractNTrkWeights(inputFile=None, verbose=0):
	try:
		cachefile = open('.svntrkweights.pck','r')
		ntkWeights = pickle.load(cachefile)
		cachefile.close()
		print ('>>> Read SV ntrk weights from cache '
			   '(.svntrkweights.pck)')
		return ntkWeights
	except IOError:
		pass

	try:
		tfile = openTFile(inputFile)
	except ReferenceError:
		print "[extractNTrkWeights] Please provide a valid input file"

	allkeys = getAllPlotsFrom(tfile, tagsToFilter=HISTSTOPROCESS)

	ntkWeights = {}
	for histname in HISTSTOPROCESS:
		tot_data, tot_mc = None, None

		for key in allkeys:
			if not key.endswith(histname): continue
			hist = tfile.Get(key)

			integral = hist.Integral()
			if 'Data8TeV' in key:
				if not tot_data:
					tot_data = hist.Clone("SVNtrk_data")
				else:
					print "WARNING: Found two data histograms"
					tot_data = hist.Clone("SVNtrk_data")

			else:
				if not tot_mc:
					tot_mc = hist.Clone("SVNtrk_mc")
				else:
					tot_mc.Add(hist)

		ratio = tot_data.Clone("ratio")
		ratio.Divide(tot_mc)

		key = 'inclusive'
		if len(histname.split('_'))>2:
			key = histname.rsplit('_',1)[1]

		if not key in ntkWeights:
			ntkWeights[key] = {}

		if verbose>0:
			print '---------------------------'
			print histname
		for x in xrange(1,ratio.GetNbinsX()+1):
			if verbose>0:
				print ("Ntrk=%1d: Ndata: %6d / Nmc: %8.1f , weight = %5.3f" %
					    (x+1,
					     tot_data.GetBinContent(x),
					     tot_mc.GetBinContent(x),
					     ratio.GetBinContent(x)))
			ntkWeights[key][x+1] = ratio.GetBinContent(x)

	cachefile = open(".svntrkweights.pck", 'w')
	pickle.dump(ntkWeights, cachefile, pickle.HIGHEST_PROTOCOL)
	cachefile.close()
	print ">>> Dumped SV ntrk weights to .svntrkweights.pck"
	return ntkWeights

def main(args, opt):
	ntkWeights = extractNTrkWeights(inputFile=args[0],
		                            verbose=opt.verbose)
	pprint(ntkWeights)
	return 0



if __name__ == "__main__":
	from optparse import OptionParser
	usage = """
	usage: %prog [options] plotter.root
	"""
	parser = OptionParser(usage=usage)
	parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int,help='Verbose mode')
	(opt, args) = parser.parse_args()

	exit(main(args, opt))




