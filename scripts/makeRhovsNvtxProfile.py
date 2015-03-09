#! /usr/bin/env python
import os, sys, pickle
import ROOT
from pprint import pprint
from runPlotter import openTFile, getAllPlotsFrom
from makeSVLDataMCPlots import resolveFilename

PROFNAMES = [
	'Profile_nvx_mu',
	'Profile_nvx_mu_dilep',
	'Profile_nvx_mu_emu',
	'Profile_rho_mu',
	'Profile_rho_mu_dilep',
	'Profile_rho_mu_emu',
]

LUMI = 17123

def makeRhoVsNVtxProfile(args, options):
	try:

		raw_profiles = {} # (procname,isdata,profname) -> profile
		for filename in os.listdir(args[0]):
			if not os.path.splitext(filename)[1] == '.root': continue

			try:
				isdata, pname, splitno = resolveFilename(filename)
			except TypeError:
				continue
			# if not isdata and pname != 'TTJets_MSDecays_172v5': continue
			tfile = openTFile(os.path.join(args[0],filename))
			for profname in PROFNAMES:
				profile = tfile.Get(profname).Clone("%s_%s"%(profname,pname))
				raw_profiles[(pname,isdata,profname)] = profile

	except IndexError:
		print "Please provide a valid input directory"
		return -1

	# pprint(raw_profiles)

	## Now add them up:
	## Get proper scales for MC histos
	cachefile = open(".xsecweights.pck", 'r')
	xsecweights = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read xsec weights from cache (.xsecweights.pck)'

	merged_profiles = {}
	for (pname, isdata, profname), profile in raw_profiles.iteritems():
		datamc = 'data' if isdata else 'mc'
		proftoadd = profile.Clone("%s_%s"%(profname,datamc))
		if not isdata:
			scale = LUMI*xsecweights["MC8TeV_%s"%pname]
		else:
			scale = 1.0
		if not (isdata, profname) in merged_profiles:
			merged_profiles[(isdata, profname)] = proftoadd
		else:
			merged_profiles[(isdata, profname)].Add(proftoadd, scale)

	pprint(merged_profiles)

	## Make the double profiles
	dprofiles = {}
	datarange = range(2,35)
	for isdata in [True, False]:
		cat = 'data' if isdata else 'mc'
		for selection in ['', '_dilep', '_emu']:
			print ' ... processing',cat,selection
			prof_nvx = merged_profiles[(isdata, 'Profile_nvx_mu%s'%selection)]
			prof_rho = merged_profiles[(isdata, 'Profile_rho_mu%s'%selection)]
			assert(prof_nvx.GetNbinsX() == prof_rho.GetNbinsX())

			mu_points_to_sample = datarange if isdata else range(3,prof_nvx.GetNbinsX()+1)

			graph = ROOT.TGraphErrors(len(mu_points_to_sample))
			graph.SetName("g_%s%s"%(cat,selection))

			for n,ibin in enumerate(mu_points_to_sample):
				avnvx = prof_nvx.GetBinContent(ibin)
				avrho = prof_rho.GetBinContent(ibin)
				avnvxe = prof_nvx.GetBinError(ibin)
				avrhoe = prof_rho.GetBinError(ibin)
				# print ibin, "%5.3f +- %5.3f" % (avnvx, avnvxe), "%5.3f +- %5.3f" % (avrho, avrhoe)
				graph.SetPoint(     n, avnvx,  avrho)
				graph.SetPointError(n, avnvxe, avrhoe)

			for ip in reversed(range(graph.GetN())):
				if graph.GetErrorX(ip) == 0: graph.RemovePoint(ip)

			markerstyle = {True:20, False:24}[isdata]
			graph.SetMarkerStyle(markerstyle)
			graph.SetMarkerColor(ROOT.kGreen-2)
			graph.SetLineColor(ROOT.kGreen-2)
			graph.GetXaxis().SetTitle("#LTN_{PV,good} - N_{HS}#GT")
			graph.GetYaxis().SetTitle("#LT#rho#GT (GeV)")

			dprofiles[(selection, cat)] = graph

	ROOT.gROOT.SetBatch(True)
	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	for selection in ['', '_dilep', '_emu']:
		canv = ROOT.TCanvas("canv%s"%selection, 'CANVAS', 800, 800)
		canv.cd()

		axes = ROOT.TH2D("axes%s"%selection, "axes", 1,0,30,1,0,30)
		axes.GetXaxis().SetTitle("#LTN_{PV,good} - N_{HS}#GT")
		axes.GetYaxis().SetTitle("#LT#rho#GT (GeV)")
		axes.Draw("axis")
		dprofiles[(selection, 'mc')].Draw("P")
		dprofiles[(selection, 'data')].Draw("P")

		tleg = ROOT.TLegend(0.15, 0.80, .40, .89)
		tleg.SetBorderSize(0)
		tleg.SetFillColor(0)
		tleg.SetFillStyle(0)
		tleg.SetShadowColor(0)
		tleg.SetTextFont(43)
		tleg.SetTextSize(20)

		tleg.AddEntry(dprofiles[(selection,'data')], 'Data (t#bar{t})', 'p')
		tleg.AddEntry(dprofiles[(selection,'mc')],   'MC (t#bar{t})', 'p')
		tleg.Draw()

		line = ROOT.TLine(0.,0.,30.,30.)
		line.SetLineStyle(3)
		line.Draw()

		canv.SaveAs(os.path.join(args[0],'NpvRho%s.png'%selection))
		canv.SaveAs(os.path.join(args[0],'NpvRho%s.pdf'%selection))

	ofile = ROOT.TFile(os.path.join(args[0],'graphs.root'), 'recreate')
	ofile.cd()
	for key,prof in merged_profiles.iteritems():
		prof.Write(prof.GetName())
	for key,graph in dprofiles.iteritems():
		graph.Write(graph.GetName())
	ofile.Write()
	ofile.Close()
	print " Wrote to %s" % os.path.join(args[0],'graphs.root')


def main(args, opt):
	makeRhoVsNVtxProfile(args, options=opt)
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




