#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from pprint import pprint
from makeSVLMassHistos import LUMI
from runPlotter import openTFile, getAllPlotsFrom, readXSecWeights
from UserCode.TopMassSecVtx.PlotUtils import *

def compareNtrk(inputFile=None, verbose=0):

	xsecweights=readXSecWeights()
	try:
		tfile = openTFile(inputFile)
	except ReferenceError:
		print "Please provide a valid input file"

	for reg in ['regA','regB','regC']:
		for ch in ['e','m','mm','em','ee']:
			histToProcess='SVNtrk_%s_optmrank' % ch
			allkeys = getAllPlotsFrom(tfile, tagsToFilter=[histToProcess])
			data=None
			mc=None
			for key in allkeys:
				if not (reg in key) : continue

				weight=1.0
				for xsecKey in xsecweights:
					procName=xsecKey.replace('MC8TeV','')+'_'
					if procName in key : weight =xsecweights[xsecKey]*LUMI
				
				if '2012' in key:
					try:
						data.Add( tfile.Get(key), weight )
					except:
						data=tfile.Get(key).Clone('data')
						data.Scale(weight)
				else:
					try:
						mc.Add( tfile.Get(key), weight )
					except:
						mc=tfile.Get(key).Clone('mc')
						mc.Scale(weight)

			varPlot = Plot('%s_%s_ntrks'%(ch,reg),False)
			varPlot.add(mc,   'expected', ROOT.kGray, False)
			varPlot.add(data, 'data',  1,         True)
			varPlot.show('~/www/tmp')
			varPlot.reset()

					
def main(args, opt):
	setTDRStyle()
	compareNtrk(inputFile=args[0],verbose=opt.verbose)
	return 0



if __name__ == "__main__":
	from optparse import OptionParser
	usage = """
	usage: %prog [options] extractBcomp.py
	"""
	parser = OptionParser(usage=usage)
	parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int,help='Verbose mode')
	(opt, args) = parser.parse_args()

	exit(main(args, opt))




