#!/usr/bin/env python
import ROOT
import os,sys
import optparse
import pickle
import os.path as osp
from math import sqrt

from makeSVLMassHistos import CHANMASSTOPROCNAME, LUMI
from makeSVLDataMCPlots import resolveFilename
from runPlotter import openTFile, getHistogramFromFile
from UserCode.TopMassSecVtx.PlotUtils import printProgress, bcolors

CHANNELS = ['e2j', 'm2j']

def buildSigMassCats(masslist,procname):
	"""
	Creates a string with mass categories to be used
	"""
	sig_mass_cats='massCat%s['%(procname)
	for m in sorted(masslist):
		sig_mass_cats+='m%d,'%int(m*10)
	sig_mass_cats = sig_mass_cats[:-1]+']'
	return sig_mass_cats

def fitSignalPermutation((ws, chan, masses, procname, SVLmass, options)):
	"""
	parameterize the signal permutations
	"""

	print ' ...processing %2s chan=%s'%(procname,chan)
	tag='%s_%s'%(chan,procname)

	# free parameters are linear functions of the top mass
	ws.factory("RooFormulaVar::%s_p0('@0*(@1-172.5)+@2',{" ## fraction of gaussian
		       "slope_%s_p0[0.0]," # INDEPENDENT OF MTOP
			   "mtop,"
			   "offset_%s_p0[0.4,0.0,1.0]})"% (tag,tag,tag))

	# AsymGaussian Part
	ws.factory("RooFormulaVar::%s_p1('@0*(@1-172.5)+@2',{" ## mean of gaussian
			   "slope_%s_p1[0.01,0,1],"
			   "mtop,"
			   "offset_%s_p1[40,5,80]})"% (tag,tag,tag))
	ws.factory("RooFormulaVar::%s_p2('@0*(@1-172.5)+@2',{" ## sigma_left of gaussian
			   "slope_%s_p2[0.01,0.001,1],"
			   "mtop,"
			   "offset_%s_p2[15,5,100]})"% (tag,tag,tag))
	ws.factory("RooFormulaVar::%s_p3('@0*(@1-172.5)+@2',{" ## sigma_right of gaussian
			   "slope_%s_p3[0.01,0.001,1],"
			   "mtop,"
			   "offset_%s_p3[25,5,100]})"% (tag,tag,tag))

	# Gamma Part
	ws.factory("RooFormulaVar::%s_p4('@0*(@1-172.5)+@2',{" ## gamma (shape)
			   "slope_%s_p4[0],"  # INDEPENDENT OF MTOP
			   "mtop,"
			   "offset_%s_p4[5,2,10]})"% (tag,tag,tag))
	ws.factory("RooFormulaVar::%s_p5('@0*(@1-172.5)+@2',{" ## beta (scale/normalization)
			   "slope_%s_p5[0],"  # INDEPENDENT OF MTOP
			   "mtop,"
			   "offset_%s_p5[10,1,100]})"% (tag,tag,tag))
	ws.factory("RooFormulaVar::%s_p6('@0*(@1-172.5)+@2',{" ## nu/mu (location)
			   "slope_%s_p6[0.05,0,2],"
			   "mtop,"
			   "offset_%s_p6[0.5,0.1,100]})"% (tag,tag,tag))

	# build the PDF
	sig_mass_cats = buildSigMassCats(masses, procname=procname)
	massCatName = 'massCat%s'%procname

	thePDF, theData, catNames = None, None, None

	## Backgrounds
	if procname == 'bg':
		# freeze the top mass dependent slopes to 0 for the backgrounds
		print 'Freezing all mtop-dependent slopes for %s'%tag
		for i in xrange(0,7):
			ws.var('slope_%s_p%d'%(tag,i)).setRange(0,0)
			ws.var('slope_%s_p%d'%(tag,i)).setVal(0)
		ws.var('offset_%s_p4'%tag).setRange(2,100)
		ws.var('offset_%s_p5'%tag).setRange(1,100)

		thePDF = ws.factory("SUM::model_%s("
				    "%s_p0*RooBifurGauss::%s_f1(SVLMass,%s_p1,%s_p2,%s_p3),"
				    "RooGamma::%s_f2(SVLMass,%s_p4,%s_p5,%s_p6))"%
				    (tag,tag,tag,tag,tag,tag,tag,tag,tag,tag))
		theData = ws.data('SVLMass_%s_%s'%(chan,procname))
		catNames=['']

	## single top + ttbar
	else:
		ws.factory("SUM::simplemodel_%s("
				   "%s_p0*RooBifurGauss::%s_f1(SVLMass,%s_p1,%s_p2,%s_p3),"
				   "RooGamma::%s_f2(SVLMass,%s_p4,%s_p5,%s_p6))"%
				   (tag,tag,tag,tag,tag,tag,tag,tag,tag,tag))

		# Replicate the base signal PDF for different categories
		# (top masses available)
		thePDF = ws.factory("SIMCLONE::model_%s("
							" simplemodel_%s, $SplitParam({mtop},%s))"%
							(tag, tag, sig_mass_cats))

		# Fix mass values and create a mapped data hist
		histMap = ROOT.MappedRooDataHist()
		for mass in masses:
			mcat = '%d' % int(mass*10)
			if not mcat in sig_mass_cats:
				print 'fitSignalPermutation::mcat not found:',mcat
				continue
			massNodeVar = ws.var('mtop_m%s'%mcat)
			massNodeVar.setVal(mass)
			massNodeVar.setConstant(True)
			binnedData = ws.data('SVLMass_%s_%s_%s'%(chan,mcat,procname))
			histMap.add('m%s'%mcat, binnedData)

		# The categorized dataset
		getattr(ws,'import')(
			ROOT.RooDataHist("data_%s"%tag,
							 "data_%s"%tag,
							 ROOT.RooArgList(SVLmass),
							 ws.cat(massCatName),
							 histMap.get()) )
		theData = ws.data("data_%s"%tag)
		catNames = histMap.getCategories()

	theFitResult = thePDF.fitTo(theData, ROOT.RooFit.Save(True))
	# theFitResult = thePDF.fitTo(theData,ROOT.RooFit.Save(True),ROOT.RooFit.SumW2Error(True))

	showFitResult(tag=tag, var=SVLmass, pdf=thePDF,
				  data=theData, cat=ws.cat(massCatName),
				  catNames=catNames,
				  outDir=options.outDir)

def gatherHistos(inputdir, verbose=0):
	hists = {}

	cachefile = open(".xsecweights.pck", 'r')
	xsecweights = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read xsec weights from cache (.xsecweights.pck)'

	# First the single top and ttbar ones
	for key,procname in CHANMASSTOPROCNAME.iteritems():
		if key[0] in ['tW', 'tbarW']: continue
		if verbose>0: print '... processing', procname
		fname = '%s.root' % procname

		#inputdir needs to have outputs of runSVLSingleTop (ie. rootfiles_*) for nominal and additional masses

		if not fname in os.listdir(inputdir):
			if verbose>0: print '%s not found'%(fname)
			continue

		if key[1] in [163.5, 181.5]: continue # skip outermost samples

		tfile = openTFile(osp.join(inputdir,fname))
		massstr = str(key[1]).replace('.5','')

		## Only some permutations are filled:
		perms = []
		if key[0] == 'tt':         perms = ['inc']
		if key[0] in ['t','tbar']: perms = ['cor','wro']

		## tbar is also t in the histname
		pname = key[0] if not (key[0] == 'tbar') else 't'

		## Extract the histograms
		for chan in CHANNELS:
			for pair in perms:
				hkey = '%s_%s_%s_%s'%(pname, chan, massstr, pair)
				histo = getHistogramFromFile(hkey,tfile,verbose)

				## Scale it to lumi (assuming they are unscaled before)
				histo.Scale(LUMI*xsecweights[procname])

				## Combine cor and wro for single top, combine t and tbar
				if (pname,key[1],chan) in hists:
					hists[(pname,key[1],chan)].Add(histo)
				else:
					hists[(pname,key[1],chan)] = histo

	# Now the backgrounds

	# inputdir also needs to have background modeling rootfiles

	for fname in os.listdir(inputdir):
		if not osp.splitext(fname)[1] == '.root': continue
		
		#EDIT
#		isdata, procname, splitno = resolveFilename(fname)
#		if isdata: continue
		if ('QCD' not in fname) and ('WJets' not in fname): continue

#		if ('TTJets' in procname or
#			'SingleT' in procname or
#			'TT_AUET' in procname): continue
		if verbose>0: print '... processing', fname

		tfile = openTFile(osp.join(inputdir,fname))
		for key in tfile.GetListOfKeys():
			name = key.GetName()
			cur_tag = ''
			for chan in ['e2j','mu2j']:
				if chan in name:
					if chan == 'e2j':
						cur_tag = chan
					else:
						cur_tag = 'm2j'
			if cur_tag == '': continue
			hkey = name #'bg_%s_172_unm'%(chan)
			histo = getHistogramFromFile(hkey,tfile,verbose)
			if histo == None: continue

			## Scale it to lumi (assuming they are unscaled before)
			#histo.Scale(LUMI*xsecweights['MC8TeV_'+procname])

			## Combine them all
			if ('bg',cur_tag) in hists: hists[('bg',cur_tag)].Add(histo)
			else:                    hists[('bg',cur_tag)] = histo

	return hists

def createWorkspace(masshistos, options):
	"""
	Converts the histograms to a RooDataHist
	Prepares PDFs
	Saves all to a RooWorkspace
	"""

	# Extract the configurations from the diffhistos dictionary
	proclist = sorted(list(set([k[0] for k in masshistos.keys()])))
	masses = sorted(list(set([k[1] for k in masshistos.keys() if not k[0] == 'bg'])))

	print 'Mass points available: ', masses
	print 'Processes available: ' , proclist
	print 'Channels available: ' , CHANNELS


	# Initiate a workspace where the observable is the SVLMass
	# and the variable to fit is mtop
	ws          = ROOT.RooWorkspace('w')
	SVLmass     = ws.factory('SVLMass[0,300]')
	mtop        = ws.factory('mtop[172.5,100,200]')
	sigStrength = ws.factory('mu[1.0,0.0,5.0]')

	# Fix binning ?!
	SVLmass.setBins(50)

	# Import binned PDFs from histograms read from file
	for chan in CHANNELS:

		# backgrounds
		hbkg = masshistos[('bg',chan)].Clone('SVLMass_%s_bg'%(chan))
		getattr(ws,'import')(ROOT.RooDataHist(hbkg.GetName(),hbkg.GetTitle(), ROOT.RooArgList(SVLmass), hbkg))
		ws.factory('%s_bgexp[%f]'%(chan,hbkg.Integral()))

		#signal
		for mass in masses:
			mcat = int(mass*10)
			# ttbar
			htt = masshistos[('tt',mass,chan)].Clone('SVLMass_%s_%s_tt'%(chan,mcat))
			getattr(ws,'import')(ROOT.RooDataHist(htt.GetName(), htt.GetTitle(), ROOT.RooArgList(SVLmass), htt))

			# single top
			ht = masshistos[('t',mass,chan)].Clone('SVLMass_%s_%s_t'%(chan,mcat))
			getattr(ws,'import')(ROOT.RooDataHist(ht.GetName(), ht.GetTitle(), ROOT.RooArgList(SVLmass), ht))

	print "Done extracting histograms, commencing fits"

	for chan in CHANNELS:
		for procname in proclist:
			fitSignalPermutation((ws, chan, masses, procname, SVLmass, options))

	# Save all to file
	ws.saveSnapshot("model_params", ws.allVars(), True)
	ws.writeToFile(osp.join(options.outDir, 'SVLWorkspace.root'), True)
	print 80*'-'
	print 'Workspace has been created and stored @ SVLWorkspace.root'
	print 80*'-'

	return ws

def showFitResult(tag,var,pdf,data,cat,catNames,outDir):
	"""
	Displays the results of the PDF fits for a list of categories
	"""

	#plot slices one by one to compare with the model
	c = ROOT.TCanvas('c','c',500,500)
	p1 = ROOT.TPad('p1','p1',0.0,0.85,1.0,0.0)
	p1.Draw()
	c.cd()
	p2 = ROOT.TPad('p2','p2',0.0,0.85,1.0,1.0)
	p2.Draw()

	for catName in catNames :
		p1.cd()
		p1.Clear()
		p1.SetRightMargin(0.05)
		p1.SetLeftMargin(0.12)
		p1.SetTopMargin(0.008)
		p1.SetBottomMargin(0.2)
		p1.SetGridx(True)
		frame = var.frame()
		if len(catName)>0 :
			redData = data.reduce(ROOT.RooFit.Cut("%s==%s::%s"%(cat.GetName(),cat.GetName(),catName)))
			redData.plotOn(frame)
			cat.setLabel(catName)
			pdf.plotOn(frame,
					   ROOT.RooFit.Slice(cat,catName),
					   ROOT.RooFit.ProjWData(redData),
					   ROOT.RooFit.Components('*f1*'),
					   ROOT.RooFit.LineColor(ROOT.kRed),
					   # ROOT.RooFit.LineColor(920),
					   ROOT.RooFit.LineWidth(1))
			pdf.plotOn(frame,
					   ROOT.RooFit.Slice(cat,catName),
					   ROOT.RooFit.ProjWData(redData),
					   ROOT.RooFit.Components('*f2*'),
					   ROOT.RooFit.LineColor(ROOT.kMagenta),
					   ROOT.RooFit.LineWidth(1))
			pdf.plotOn(frame,
					   ROOT.RooFit.Slice(cat,catName),
					   ROOT.RooFit.ProjWData(redData))
		else:
			data.plotOn(frame)
			pdf.plotOn(frame,
					   ROOT.RooFit.ProjWData(data),
					   ROOT.RooFit.Components('*f1*'),
					   ROOT.RooFit.LineColor(ROOT.kRed),
					   # ROOT.RooFit.LineColor(920),
					   ROOT.RooFit.LineWidth(1))
			pdf.plotOn(frame,
					   ROOT.RooFit.ProjWData(data),
					   ROOT.RooFit.Components('*f2*'),
					   ROOT.RooFit.LineColor(ROOT.kMagenta),
					   ROOT.RooFit.LineWidth(1))
			pdf.plotOn(frame,
					   ROOT.RooFit.ProjWData(data))

		frame.Draw()
		frame.GetYaxis().SetTitle("Entries")
		frame.GetYaxis().SetTitleOffset(1.0)
		frame.GetYaxis().SetTitleSize(0.05)
		frame.GetYaxis().SetLabelSize(0.04)
		frame.GetXaxis().SetTitle("m(SV,lepton) [GeV]")

		label = ROOT.TLatex()
		label.SetNDC()
		label.SetTextFont(42)
		label.SetTextSize(0.04)
		label.DrawLatex(0.6,0.92,'#bf{CMS} #it{simulation}')
		if len(catName)>0:
			massVal=float( catName.replace('m','') )/10.
			label.DrawLatex(0.6,0.86,'#it{m_{t}=%3.1f GeV}'%massVal)
		# subTags=tag.split('_')
		# permTitle=''
		# if 'cor' in subTags : '#it{correct permutations}'
		# if 'wro' in subTags : permTitle='#it{wrong permutations}'
		# if 'unm' in subTags :
		# 	permTitle='#it{unmatched permutations}'
		# 	if 'wro' in subTags : permTitle='#it{wrong+unmatched permutations}'
		# if 'bg'  in subTags : permTitle='#it{background}'
		# label.DrawLatex(0.6,0.80,permTitle)
		# channelTitle=subTags[0].replace('m','#mu')
		# ntracks = subTags[1] if subTags[1].isdigit() else subTags[2]
		# selCat = subTags[1] if not subTags[1].isdigit() else 'inclusive'
		# channelTitle='#it{%s %s, %s tracks}'%(channelTitle,selCat,ntracks)
		# label.DrawLatex(0.6,0.74,channelTitle)
		label.DrawLatex(0.6,0.74,tag)
		label.DrawLatex(0.6,0.68,'#chi^{2}=%3.2f'%frame.chiSquare())

		p2.cd()
		p2.Clear()
		p2.SetBottomMargin(0.005)
		p2.SetRightMargin(0.05)
		p2.SetLeftMargin(0.12)
		p2.SetTopMargin(0.05)
		p2.SetGridx(True)
		p2.SetGridy(True)

		hpull = frame.pullHist()
		pullFrame = var.frame()
		pullFrame.addPlotable(hpull,"P") ;
		pullFrame.Draw()
		pullFrame.GetYaxis().SetTitle("Pull")
		pullFrame.GetYaxis().SetTitleSize(0.2)
		pullFrame.GetYaxis().SetLabelSize(0.2)
		pullFrame.GetXaxis().SetTitleSize(0)
		pullFrame.GetXaxis().SetLabelSize(0)
		pullFrame.GetYaxis().SetTitleOffset(0.15)
		pullFrame.GetYaxis().SetNdivisions(4)
		pullFrame.GetYaxis().SetRangeUser(-3.1,3.1)
		pullFrame.GetXaxis().SetTitleOffset(0.8)

		c.Modified()
		c.Update()
		plotdir = osp.join(outDir, 'plots')
		os.system('mkdir -p %s' % plotdir)
		for ext in ['png', 'pdf']:
			c.SaveAs(osp.join(plotdir, "%s_%s.%s"%(tag,catName,ext)))

	c.Clear()
	c.Delete()

def main():
	usage = 'usage: %prog [options]'
	parser = optparse.OptionParser(usage)
	parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int,
					   help='Verbose mode')
	parser.add_option('-o', '--outDir', dest='outDir', default='svlfits',
					   help='Output directory [default: %default]')

	(options, args) = parser.parse_args()

	ROOT.gStyle.SetOptStat(0)
	ROOT.gStyle.SetOptTitle(0)
	ROOT.gROOT.SetBatch(True)
	#EDIT: Need to put back in
	#if options.spy : ROOT.gROOT.SetBatch(False)

	ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
	#EDIT: Need to put back in
#	if not options.test:
#		ROOT.AutoLibraryLoader.enable()
#		if not options.verbose > 5:
#			ROOT.shushRooFit()
			# see TError.h - gamma function prints lots of errors when scanning
	ROOT.gROOT.ProcessLine("gErrorIgnoreLevel=kFatal")

	os.system('mkdir -p %s' % options.outDir)
	os.system('mkdir -p %s' % osp.join(options.outDir, 'plots'))

	# Check if one needs to create a new workspace or run pseudo-experiments
	print 80*'-'
	print 'Creating a new workspace file from %s' % args[0]
	histograms = gatherHistos(args[0],verbose=options.verbose)
	ws = createWorkspace(histograms, options=options)
	print 80*'-'
	return 0

if __name__ == "__main__":
	sys.exit(main())
