#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from pprint import pprint
from runPlotter import openTFile, getAllPlotsFrom

HISTSTOPROCESS = ['LJNtk', 'LJNtk_e', 'LJNtk_m']

def extractLJNTrkWeights(inputFile=None, verbose=0):
	try:
		tfile = openTFile(inputFile)
	except ReferenceError:
		print "[extractLJNTrkWeights] Please provide a valid input file"

	allkeys = getAllPlotsFrom(tfile, tagsToFilter=HISTSTOPROCESS)

	ofile = ROOT.TFile.Open('ljntkweights.root','recreate')
	ofile.cd()

	for histname in HISTSTOPROCESS:
		tot_data, tot_mc = None, None

		for key in allkeys:
			if not key.endswith(histname): continue
			hist = tfile.Get(key)

			integral = hist.Integral()
			if 'Data8TeV' in key:
				if not tot_data:
					tot_data = hist.Clone("SVNtrk_data")
					tot_data.SetDirectory(0)
				else:
					print "WARNING: Found two data histograms"
					tot_data = hist.Clone("SVNtrk_data")
					tot_data.SetDirectory(0)

			if 'MC8TeV_TTJets_MSDecays_172v5' in key:
				if not tot_mc:
					tot_mc = hist.Clone("SVNtrk_mc")
					tot_mc.SetDirectory(0)
				else:
					tot_mc.Add(hist)

		## Normalize them
		tot_data.Scale(1.0/tot_data.Integral())
		tot_mc.Scale(1.0/tot_mc.Integral())
		ratio = tot_data.Clone("%s_weights"%histname)
		ratio.Divide(tot_mc)

		ofile.cd()
		ratio.Write(ratio.GetName())
	ofile.Write()
	ofile.Close()
	print ">>> Wrote light jet ntrk weights to ljntkweights.root"

def main(args, opt):
	extractLJNTrkWeights(inputFile=args[0], verbose=opt.verbose)
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




