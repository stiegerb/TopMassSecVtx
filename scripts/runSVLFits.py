#!/usr/bin/env python
import ROOT
import os,sys
import optparse
import pickle
import numpy

from math import sqrt

from runSVLPseudoExperiments import runPseudoExperiments
from makeSVLMassHistos import CHANMASSTOPROCNAME, LUMI
from UserCode.TopMassSecVtx.PlotUtils import printProgress, bcolors


def fitSignalPermutation((ws, ch, ntrk, permName, massList, singleTop, bkg, SVLmass, options)):
	"""
	parameterize the signal permutations
	"""

	procName='tt'
	if singleTop : procName='t'
	if bkg       : procName='bg'
	print ' ...processing %2s ch=%s #tk=%d for %s permutations'%(procName,ch,ntrk,permName)
	tag='%s_%d_%s_%s'%(ch,ntrk,permName,procName)

	# Base correct, signal PDF :
	# free parameters are linear functions of the top mass

	ws.factory("RooFormulaVar::%s_p0('@0*(@1-172.5)+@2',{" ## fraction of gaussian
		       "slope_%s_p0[0.0]," # INDEPENDENT OF MTOP
			   "mtop,"
			   "offset_%s_p0[0.4,0.0,1.0]})"% (tag,tag,tag))
			   # "offset_%s_p0[0.4,0.1,0.9]})"% (tag,tag,tag))

	ws.factory("RooFormulaVar::%s_p1('@0*(@1-172.5)+@2',{" ## mean of gaussian
			   "slope_%s_p1[0.01,0,1],"
			   "mtop,"
			   "offset_%s_p1[40,5,80]})"% (tag,tag,tag))
			   # "offset_%s_p1[40,5,150]})"% (tag,tag,tag))
	ws.factory("RooFormulaVar::%s_p2('@0*(@1-172.5)+@2',{" ## sigma_left of gaussian
			   "slope_%s_p2[0.01,0.001,1],"
			   "mtop,"
			   "offset_%s_p2[15,5,100]})"% (tag,tag,tag))
	ws.factory("RooFormulaVar::%s_p3('@0*(@1-172.5)+@2',{" ## sigma_right of gaussian
			   "slope_%s_p3[0.01,0.001,1],"
			   "mtop,"
			   "offset_%s_p3[25,5,100]})"% (tag,tag,tag))

	ws.factory("RooFormulaVar::%s_p4('@0*(@1-172.5)+@2',{" ## gamma (shape)
			   "slope_%s_p4[0],"  # INDEPENDENT OF MTOP
			   "mtop,"
			   "offset_%s_p4[5,2,10]})"% (tag,tag,tag))
			   # "offset_%s_p4[5,-10,10]})"% (tag,tag,tag))
	ws.factory("RooFormulaVar::%s_p5('@0*(@1-172.5)+@2',{" ## beta (scale/normalization)
			   "slope_%s_p5[0],"  # INDEPENDENT OF MTOP
			   "mtop,"
			   "offset_%s_p5[10,1,100]})"% (tag,tag,tag))
	ws.factory("RooFormulaVar::%s_p6('@0*(@1-172.5)+@2',{" ## nu/mu (location)
			   "slope_%s_p6[0.05,0,2],"
			   "mtop,"
			   "offset_%s_p6[0.5,0.1,100]})"% (tag,tag,tag))

	# build the PDF
	sig_mass_cats=buildSigMassCats(massList,singleTop,permName)
	massCatName=sig_mass_cats.split('[')[0]
	thePDF,theData,catNames=None,None,None
	if 'unm' in tag:
		#freeze the top mass dependent slopes to 0 if unmatched permutations are in the tag
		print 'Freezing all mtop-dependent slopes for %s'%tag
		for i in xrange(0,7):
			ws.var('slope_%s_p%d'%(tag,i)).setRange(0,0)
			ws.var('slope_%s_p%d'%(tag,i)).setVal(0)
		ws.var('offset_%s_p4'%tag).setRange(2,100)
		ws.var('offset_%s_p5'%tag).setRange(1,100)

		#for this case it needs to be put by hand to converge
		if ch=='m' and ntrk==2 and 'tt' in procName     : ws.var('offset_%s_p1'%tag).setRange(0,200)
		if 'opt' in tag and ntrk==5 and 'bg' in procName: ws.var('offset_%s_p1'%tag).setRange(30,100)

		thePDF = ws.factory("SUM::model_%s("
				    "%s_p0*RooBifurGauss::%s_f1(SVLMass,%s_p1,%s_p2,%s_p3),"
				    "RooGamma::%s_f2(SVLMass,%s_p4,%s_p5,%s_p6))"%
				    (tag,tag,tag,tag,tag,tag,tag,tag,tag,tag))
		theData=ws.data('SVLMass_%s_%s_%s_%d'%(permName,ch,procName,ntrk))
		catNames=['']
	else:
		#base PDF
		ws.factory("SUM::simplemodel_%s("
				   "%s_p0*RooBifurGauss::%s_f1(SVLMass,%s_p1,%s_p2,%s_p3),"
				   "RooGamma::%s_f2(SVLMass,%s_p4,%s_p5,%s_p6))"%
				   (tag,tag,tag,tag,tag,tag,tag,tag,tag,tag))

		if singleTop:
			if 'cor' in permName:

				ws.var('slope_%s_p0'%tag).setRange(0,0)
				ws.var('offset_%s_p0'%tag).setRange(0.4,0.9)
				if 'opt' in tag :
					ws.var('offset_%s_p0'%tag).setRange(0.1,0.8)
					ws.var('offset_%s_p1'%tag).setRange(40,90)




		# Replicate the base signal PDF for different categories
		# (top masses available)
		thePDF = ws.factory("SIMCLONE::model_%s("
							" simplemodel_%s, $SplitParam({mtop},%s))"%
							(tag, tag, sig_mass_cats))

		# Fix mass values and create a mapped data hist
		histMap=ROOT.MappedRooDataHist()
		for mass in massList:
			mcat='%d'%int(mass*10)
			if not(mcat in sig_mass_cats): continue
			massNodeVar=ws.var('mtop_m%s'%mcat)
			massNodeVar.setVal(mass)
			massNodeVar.setConstant(True)
			binnedData=ws.data('SVLMass_%s_%s_%s_%s_%d'%(permName,ch,mcat,procName,ntrk))
			histMap.add('m%s'%mcat,binnedData)

		# The categorized dataset
		getattr(ws,'import')(
			ROOT.RooDataHist("data_%s"%tag,
							 "data_%s"%tag,
							 ROOT.RooArgList(SVLmass),
							 ws.cat(massCatName),
							 histMap.get()) )
		theData = ws.data("data_%s"%tag)
		catNames=histMap.getCategories()

	theFitResult = thePDF.fitTo(theData,ROOT.RooFit.Save(True))
	#theFitResult = thePDF.fitTo(theData,ROOT.RooFit.Save(True),ROOT.RooFit.SumW2Error(True))
	showFitResult(tag=tag, var=SVLmass, pdf=thePDF,
				  data=theData, cat=ws.cat(massCatName),
				  catNames=catNames,
				  outDir=options.outDir)

def parameterizeSignalPermutations(ws,permName,config,SVLmass,options,singleTop,bkg=False):
	"""
	instantiates the PDFs needed to parameterize the SVLmass
	histo in a given category for signal events
	"""

	chselList,  massList, trkMultList, combList, procList = config
	print '[parameterizeSignalPermutations] with %s'%permName
	if singleTop:
		print ' \t single top quark mode enabled',
		if not ('t' in procList or 'tW' in procList):
			print ' but process not found in ',procList
			return
		print ''
	if bkg:
		print ' \t background mode enabled'

	tasklist = []
	for ch in chselList:
		# if ch != 'em' : continue
		for ntrk in trkMultList:
			tasklist.append((ws, ch, ntrk, permName, massList, singleTop, bkg, SVLmass, options))

	if options.jobs > 1:
		import multiprocessing
		multiprocessing.Pool(8).map(fitSignalPermutation, tasklist)
	else:
		for task in tasklist:
			fitSignalPermutation(task)

def parameterizeSignalFractions(ws, masshistos, config, xsecweights, options) :
	"""
	Parameterizes the fraction of correct and wrong assignments
	as well as the fraction of single top expected with respect to ttbar
	"""
	chselList, massList, trkMultList, combList, procList = config
	prepend = '[parameterizeSignalFractions]'
	print prepend

	canvas=ROOT.TCanvas('c','c',500,500)
	canvas.SetLeftMargin(0.15)
	canvas.SetRightMargin(0.05)
	for chsel in chselList:
		if options.verbose > 4: print prepend,chsel
		for trk in trkMultList:
			if options.verbose > 4: print "%s  %d tracks" % (prepend,trk)

			grToParametrize={}
			for key,title in [('ttcor','t#bar{t} correct'),
							  ('ttwro','t#bar{t} wrong'),
							  ('ttexp','t#bar{t} expected'),
							  ('tcor', 't correct'),
							  ('tfrac','t / t#bar{t}')]:
				grCtr=len(grToParametrize)
				grToParametrize[key]=ROOT.TGraphErrors()
				grToParametrize[key].SetName(key)
				grToParametrize[key].SetTitle(title)
				grToParametrize[key].SetFillStyle(0)
				grToParametrize[key].SetMarkerStyle(20+grCtr)
				grToParametrize[key].SetLineColor(2*grCtr+1)
				grToParametrize[key].SetMarkerColor(2*grCtr+1)

			for mass in massList:
				if options.verbose > 4: print "%s   %4.1f GeV" % (prepend, mass)

				combCtrs={}
				for comb in combList:
					for proc in procList:

						# For single top, only take points at 166.5, 172.5, 178.5:
						if proc!='tt' and not (mass in [166.5, 172.5, 178.5]): continue
						# Integrate events expected for this category and mass
						h = None
						try:
							h = masshistos[(chsel,proc,mass,comb,trk)]
						except KeyError: pass
						err=ROOT.Double(0)
						val=h.IntegralAndError(1,h.GetXaxis().GetNbins(),err)

						# Add to counters
						key = proc
						if key != 'tt': key ='t' # don't distinguish t chan and tW
						for combKey in [key+comb,key+'exp']:
							if combKey in combCtrs:
								combCtrs[combKey]  [0] += val
								combCtrs[combKey]  [1] += err*err
							else:
								combCtrs[combKey]   = [val,err*err]

				# err^2 -> err
				for key in combCtrs: combCtrs[key][1]=ROOT.TMath.Sqrt(combCtrs[key][1])

				if options.verbose > 4:
					print ("%s    yields: %8.1f+-%5.1f (ttcor) %8.1f+-%5.1f (ttwro) %8.1f+-%5.1f (ttunm)" %
						           (prepend, combCtrs['ttcor'][0],combCtrs['ttcor'][1],
						                     combCtrs['ttwro'][0],combCtrs['ttwro'][1],
						                     combCtrs['ttunm'][0],combCtrs['ttunm'][1]))
					if 'tcor' in combCtrs:
						print ("%s    yields: %8.1f+-%5.1f (tcor)  %8.1f+-%5.1f (twro)  %8.1f+-%5.1f (tunm)" %
						           (prepend, combCtrs['tcor'][0],combCtrs['tcor'][1],
						                     combCtrs['twro'][0],combCtrs['twro'][1],
						                     combCtrs['tunm'][0],combCtrs['tunm'][1]))


				# Normalize fractions by total expectations
				for proc in ['t','tt']:
					for comb in combList:
						try:
							combCtrs[proc+comb][0] /= combCtrs[proc+'exp'][0]
							combCtrs[proc+comb][1] /= combCtrs[proc+'exp'][0]
						except KeyError: pass
				if 'texp' in combCtrs:
					combCtrs['tfrac']=(combCtrs['texp'][0]/combCtrs['ttexp'][0],
									   sqrt( (combCtrs['texp'][0]*combCtrs['ttexp'][1])**2
										   + (combCtrs['ttexp'][0]*combCtrs['texp'][1])**2 )
										   / (combCtrs['ttexp'][0])**2)

				if options.verbose > 4:
					print ("%s    fractions: %4.2f (ttcor) %4.2f (ttwro) %4.2f (ttunm)" % (prepend,
						          combCtrs['ttcor'][0],combCtrs['ttwro'][0],combCtrs['ttunm'][0]))
					if 'tcor' in combCtrs:
						print ("%s    fractions: %4.2f (tcor)  %4.2f (twro) %4.2f  (tunm) %s single top fraction: %4.2f %s" % (prepend,
							          combCtrs['tcor'][0],combCtrs['twro'][0],combCtrs['tunm'][0],
							          bcolors.OKGREEN, combCtrs['tfrac'][0], bcolors.ENDC))


				# Add point to the graph
				for key in combCtrs:
					try:
						np = grToParametrize[key].GetN()
						grToParametrize[key].SetPoint     (np,mass,combCtrs[key][0])
						grToParametrize[key].SetPointError(np,   0,combCtrs[key][1])
					except KeyError: pass


			#extrapolate dependency with straight line and show
			for keys in [['ttcor','ttwro','tcor'],
						 ['tfrac'],
						 ['ttexp']]:
				canvas.Clear()
				drawOpt='ap'
				for key in keys:
					if not(key in grToParametrize): continue
					tag='%s_%s_%s'%(chsel,key,trk)
					grToParametrize[key].Fit('pol1','Q+','same')
					grToParametrize[key].Draw(drawOpt)
					drawOpt='p'
					grToParametrize[key].GetFunction('pol1').SetLineColor(grToParametrize[key].GetLineColor())
					grToParametrize[key].GetXaxis().SetTitle("Top mass [GeV]")
					grToParametrize[key].GetYaxis().SetTitleOffset(1.2)
					if 'exp' in key:
						grToParametrize[key].GetYaxis().SetTitle("Expected t#bar{t} events")
						ws.factory("%s[%f]"%(tag,grToParametrize[key].GetFunction('pol1').Eval(172.5)))
					elif 'frac' in key:
						grToParametrize[key].GetYaxis().SetTitle('t / t#bar{t}')
						ws.factory("RooFormulaVar::%s('%f+@0*(%f)',{mtop})"%
								   (tag,grToParametrize[key].GetFunction('pol1').GetParameter(0),
										grToParametrize[key].GetFunction('pol1').GetParameter(1)))
					else:
						grToParametrize[key].GetYaxis().SetRangeUser(0,1)
						grToParametrize[key].GetYaxis().SetTitle('Fraction wrt to t#bar{t} or t events')
						ws.factory("RooFormulaVar::%s('%f+@0*(%f)',{mtop})"%
								   (tag,grToParametrize[key].GetFunction('pol1').GetParameter(0),
										grToParametrize[key].GetFunction('pol1').GetParameter(1)))

				if drawOpt=='ap': continue
				leg=canvas.BuildLegend()
				leg.SetFillStyle(0)
				leg.SetTextFont(42)
				leg.SetBorderSize(0)
				leg.SetTextSize(0.03)
				leg.SetNColumns(2)
				label = ROOT.TLatex()
				label.SetNDC()
				label.SetTextFont(42)
				label.SetTextSize(0.035)
				channelTitle=chsel.replace('_',' ')
				label.DrawLatex(0.12,0.92,'#bf{CMS} #it{simulation}')
				label.DrawLatex(0.2,0.84,channelTitle)
				label.DrawLatex(0.2,0.8,'%d tracks'%trk)
				canvas.SaveAs('%s/plots/%s_%s.pdf'%(options.outDir,keys[0],tag))
				canvas.SaveAs('%s/plots/%s_%s.png'%(options.outDir,keys[0],tag))

def readConfig(diffhistos):
	"""
	Extracts the channels, combinations, mass values, and
	track multiplicity bins from the dictionary containing
	the histograms.
	"""
	chselList, procList, massList, trkMultList, combList = [], [], [], [], []
	for key,histos in diffhistos.iteritems():
		try:
			if len(key)<5: continue
			if 'inclusive' in key[0]: continue
			if 'tot' in key[3]: continue

			chselList.append( key[0] )
			procList.append( key[1] )
			massList.append( key[2] )
			combList.append( key[3] )
			trkMultList.append( key[4] )
		except Exception, e:
			print key
			print e
			pass

	chselList   = list( set(chselList) )
	massList    = sorted(list( set(massList) ))
	trkMultList = sorted(list( set(trkMultList) ))
	combList    = list( set(combList) )
	procList    = sorted(list(set(procList)) )
	return chselList, massList, trkMultList, combList, procList

def buildSigMassCats(massList,singleTop,permName):
	"""
	Creates a string with mass categories to be used
	"""
	sig_mass_cats='massCat%s%d['%(permName,singleTop)
	if 'unm' in permName :
		sig_mass_cats+='minc]'
	else :
		for m in sorted(massList):
			if singleTop and not m in [166.5,172.5,178.5]: continue
			sig_mass_cats+='m%d,'%int(m*10)
		sig_mass_cats = sig_mass_cats[:-1]+']'
	return sig_mass_cats

def testSignalFit(options):
	# Read file
	cachefile = open(options.input,'r')
	masshistos = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read mass histos from (%s)' % options.input

	## Scale all the mass histograms in one go:
	cachefile = open(".xsecweights.pck", 'r')
	xsecweights = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read xsec weights from cache (.xsecweights.pck)'

	from extractNtrkWeights import extractNTrkWeights
	ntkWeights = extractNTrkWeights()

	for key, hist in masshistos.iteritems():
		## Xsection scaling
		hist.Scale(LUMI*xsecweights[CHANMASSTOPROCNAME[(key[1], key[2])]])

		## Ntrack bin reweighting to data
		try: hist.Scale(ntkWeights['inclusive'][key[4]])
		except IndexError: pass

	bkgmasshistos=None
	try:
		cachefile = open(options.inputBkg,'r')
		bkgmasshistos = pickle.load(cachefile)
		## Note that these are already scaled to xs*lumi
		## and weighted to data ntrack multiplicities
		cachefile.close()
		print '>>> Read background shapes from (%s)' % options.inputBkg
	except IOError:
		print '>>> No valid background shapes file found'


	# Extract the configurations from the diffhistos dictionary
	config = readConfig(masshistos)
	chselList, massList, trkMultList, combList, procList = config
	print 'Selected channels available :', chselList
	print 'Mass points available: ', massList
	print 'Track multiplicities available: ', trkMultList
	print 'Combinations available: ', combList
	print 'Processes available: ' , procList


	if not options.cached:
		# Initiate a workspace where the observable is the SVLMass
		# and the variable to fit is mtop
		ws          = ROOT.RooWorkspace('w')
		SVLmass     = ws.factory('SVLMass[100,0,300]')
		mtop        = ws.factory('mtop[172.5,100,200]')
		sigStrength = ws.factory('mu[1.0,0.0,5.0]')

		# Import binned PDFs from histograms read from file
		for chsel in chselList:
			for trk in trkMultList:

				#backgrounds
				try:
					# These are already properly scaled by xsec
					hbkg = bkgmasshistos[(chsel,trk)]
					name = 'SVLMass_unm_%s_bg_%d'%(chsel,trk)
					getattr(ws,'import')(ROOT.RooDataHist(name,name, ROOT.RooArgList(SVLmass), hbkg))
					ws.factory('%s_bgexp_%d[%f]'%(chsel,trk,hbkg.Integral()))
				except Exception, e:
					raise e

				#signal
				for mass in massList:
					# ttbar
					for comb in ['cor','wro']:
						htt = masshistos[(chsel,'tt',mass,comb,trk)]
						getattr(ws,'import')(ROOT.RooDataHist(htt.GetName(), htt.GetTitle(), ROOT.RooArgList(SVLmass), htt))

					# Only correct combinations for single top
					ht = None
					for stProc in ['t','tbar','tW','tbarW']:
						try: # get all available single top templates
							h = masshistos[(chsel,stProc,mass,'cor',trk)]
							if ht is None:
								ht = h.Clone("SVLMass_%s_%s_%d_t_%d"%('cor',chsel,10*mass,trk))
							else:
								ht.Add(h)
						except KeyError: pass

					if ht:
						getattr(ws,'import')(ROOT.RooDataHist(ht.GetName(), ht.GetTitle(), ROOT.RooArgList(SVLmass), ht))

				# Unmatched for tt and wrong+unmatched for single top are merged
				htt_unm, ht_wrounm = None, None
				for mass in massList:
					htt = masshistos[(chsel,'tt',mass,'unm',trk)]
					if htt_unm is None : htt_unm=htt.Clone("SVLMass_unm_%s_tt_%d"%(chsel,trk))
					else               : htt_unm.Add(htt)

					for comb in ['unm','wro']:
						for stProc in ['t','tbar','tW','tbarW']:
							try: # get all available single top templates
								ht = masshistos[(chsel,stProc,mass,comb,trk)]
								if ht_wrounm is None : ht_wrounm=ht.Clone("SVLMass_wrounm_%s_t_%d"%(chsel,trk))
								else                 : ht_wrounm.Add(ht)
							except KeyError: pass
				if htt_unm:
					getattr(ws,'import')(ROOT.RooDataHist(htt_unm.GetName(), htt_unm.GetTitle(),
										 ROOT.RooArgList(SVLmass), htt_unm))
				if ht_wrounm:
					getattr(ws,'import')(ROOT.RooDataHist(ht_wrounm.GetName(), ht_wrounm.GetTitle(),
										 ROOT.RooArgList(SVLmass), ht_wrounm))


		print "Done extracting histograms, commencing fit"
		ws.writeToFile(os.path.join(options.outDir, 'SVLWorkspace.root'), True)
		print ">>> wrote workspace to file"

	inF = ROOT.TFile.Open(os.path.join(options.outDir, 'SVLWorkspace.root'))
	ws = inF.Get('w')
	inF.Close()
	print ">>> read workspace from file"

	SVLmass = ws.var('SVLMass')

	# ttbar
	print options.test.rsplit('_',3)
	try:
		chan, ntrk, perm, proc = options.test.rsplit('_',3)
		ntrk = int(ntrk)
		isSingleTop = (proc == 't')
		isBackground = (proc == 'bkg' or proc == 'bg')
	except:
		print 'please give the --test option an argument in the form of'
		print ' em_mrank1_5_cor_t or mm_3_wro_tt or em_optmrank_5_wrounm_bkg'
		return -1

	# (ws, ch, ntrk, permName, massList, singleTop, bkg, SVLmass, options)
	fitSignalPermutation((ws, chan, ntrk, perm, massList, isSingleTop, isBackground, SVLmass, options))
	print 50*'#'
	ws.Print()
	print 50*'#'
	print "ALL DONE"
	return 0

def createWorkspace(options):
	"""
	Reads out the histograms from the pickle file and converts them
	to a RooDataHist
	Prepare PDFs
	Save all to a RooWorkspace
	"""

	# Read file
	cachefile = open(options.input,'r')
	masshistos = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read mass histos from (%s)' % options.input

	## Scale all the mass histograms in one go:
	cachefile = open(".xsecweights.pck", 'r')
	xsecweights = pickle.load(cachefile)
	cachefile.close()
	print '>>> Read xsec weights from cache (.xsecweights.pck)'

	from extractNtrkWeights import extractNTrkWeights
	ntkWeights = extractNTrkWeights()

	for key, hist in masshistos.iteritems():
		## Xsection scaling
		hist.Scale(LUMI*xsecweights[CHANMASSTOPROCNAME[(key[1], key[2])]])

		## Ntrack bin reweighting to data
		try: hist.Scale(ntkWeights['inclusive'][key[4]])
		except IndexError: pass

	bkgmasshistos=None
	try:
		cachefile = open(options.inputBkg,'r')
		bkgmasshistos = pickle.load(cachefile)
		## Note that these are already scaled to xs*lumi
		## and weighted to data ntrack multiplicities
		cachefile.close()
		print '>>> Read background shapes from (%s)' % options.inputBkg
	except IOError:
		print '>>> No valid background shapes file found'


	# Extract the configurations from the diffhistos dictionary
	config = readConfig(masshistos)
	chselList, massList, trkMultList, combList, procList = config
	print 'Selected channels available :', chselList
	print 'Mass points available: ', massList
	print 'Track multiplicities available: ', trkMultList
	print 'Combinations available: ', combList
	print 'Processes available: ' , procList

	# Initiate a workspace where the observable is the SVLMass
	# and the variable to fit is mtop
	ws          = ROOT.RooWorkspace('w')
	SVLmass     = ws.factory('SVLMass[100,0,300]')
	mtop        = ws.factory('mtop[172.5,100,200]')
	sigStrength = ws.factory('mu[1.0,0.0,5.0]')

	# Import binned PDFs from histograms read from file
	for chsel in chselList:
		for trk in trkMultList:

			#backgrounds
			try:
				# These are already properly scaled by xsec
				hbkg = bkgmasshistos[(chsel,trk)]
				name = 'SVLMass_unm_%s_bg_%d'%(chsel,trk)
				getattr(ws,'import')(ROOT.RooDataHist(name,name, ROOT.RooArgList(SVLmass), hbkg))
				ws.factory('%s_bgexp_%d[%f]'%(chsel,trk,hbkg.Integral()))
			except Exception, e:
				raise e

			#signal
			for mass in massList:
				# ttbar
				for comb in ['cor','wro']:
					htt = masshistos[(chsel,'tt',mass,comb,trk)]
					getattr(ws,'import')(ROOT.RooDataHist(htt.GetName(), htt.GetTitle(), ROOT.RooArgList(SVLmass), htt))

				# Only correct combinations for single top
				ht = None
				for stProc in ['t','tbar','tW','tbarW']:
					try: # get all available single top templates
						h = masshistos[(chsel,stProc,mass,'cor',trk)]
						if ht is None:
							ht = h.Clone("SVLMass_%s_%s_%d_t_%d"%('cor',chsel,10*mass,trk))
						else:
							ht.Add(h)
					except KeyError: pass

				if ht:
					getattr(ws,'import')(ROOT.RooDataHist(ht.GetName(), ht.GetTitle(), ROOT.RooArgList(SVLmass), ht))

			# Unmatched for tt and wrong+unmatched for single top are merged
			htt_unm, ht_wrounm = None, None
			for mass in massList:
				htt = masshistos[(chsel,'tt',mass,'unm',trk)]
				if htt_unm is None : htt_unm=htt.Clone("SVLMass_unm_%s_tt_%d"%(chsel,trk))
				else               : htt_unm.Add(htt)

				for comb in ['unm','wro']:
					for stProc in ['t','tbar','tW','tbarW']:
						try: # get all available single top templates
							ht = masshistos[(chsel,stProc,mass,comb,trk)]
							if ht_wrounm is None : ht_wrounm=ht.Clone("SVLMass_wrounm_%s_t_%d"%(chsel,trk))
							else                 : ht_wrounm.Add(ht)
						except KeyError: pass
			if htt_unm:
				getattr(ws,'import')(ROOT.RooDataHist(htt_unm.GetName(), htt_unm.GetTitle(),
									 ROOT.RooArgList(SVLmass), htt_unm))
			if ht_wrounm:
				getattr(ws,'import')(ROOT.RooDataHist(ht_wrounm.GetName(), ht_wrounm.GetTitle(),
									 ROOT.RooArgList(SVLmass), ht_wrounm))


	print "Done extracting histograms, commencing fits"

	# Run signal parameterization cycles
	parameterizeSignalFractions(ws=ws, config=config, masshistos=masshistos,
								xsecweights=xsecweights, options=options)

	# ttbar
	parameterizeSignalPermutations(ws=ws, permName='cor', config=config,
								   SVLmass=SVLmass, options=options, singleTop=False)
	parameterizeSignalPermutations(ws=ws, permName='wro', config=config,
								   SVLmass=SVLmass, options=options, singleTop=False)
	parameterizeSignalPermutations(ws=ws, permName='unm', config=config,
								   SVLmass=SVLmass, options=options, singleTop=False)
	# single top
	parameterizeSignalPermutations(ws=ws, permName='cor', config=config,
								   SVLmass=SVLmass, options=options, singleTop=True)
	parameterizeSignalPermutations(ws=ws, permName='wrounm', config=config,
	                               SVLmass=SVLmass, options=options, singleTop=True)
	# backgrounds
	parameterizeSignalPermutations(ws=ws, permName='unm', config=config,
								   SVLmass=SVLmass, options=options, singleTop=False, bkg=True)

	# Save all to file
	ws.saveSnapshot("model_params", ws.allVars(), True)
	ws.writeToFile(os.path.join(options.outDir, 'SVLWorkspace.root'), True)
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
		frame   = var.frame()
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
		subTags=tag.split('_')
		permTitle=''
		if 'cor' in subTags : '#it{correct permutations}'
		if 'wro' in subTags : permTitle='#it{wrong permutations}'
		if 'unm' in subTags :
			permTitle='#it{unmatched permutations}'
			if 'wro' in subTags : permTitle='#it{wrong+unmatched permutations}'
		if 'bg'  in subTags : permTitle='#it{background}'
		label.DrawLatex(0.6,0.80,permTitle)
		channelTitle=subTags[0].replace('m','#mu')
		ntracks = subTags[1] if subTags[1].isdigit() else subTags[2]
		selCat = subTags[1] if not subTags[1].isdigit() else 'inclusive'
		channelTitle='#it{%s %s, %s tracks}'%(channelTitle,selCat,ntracks)
		label.DrawLatex(0.6,0.74,channelTitle)
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
		plotdir = os.path.join(outDir, 'plots')
		os.system('mkdir -p %s' % plotdir)
		for ext in ['png', 'pdf']:
			c.SaveAs(os.path.join(plotdir, "%s_%s.%s"%(tag,catName,ext)))

	c.Clear()
	c.Delete()

def main():
	"""
	steer
	"""
	usage = 'usage: %prog [options]'
	parser = optparse.OptionParser(usage)
	parser.add_option('-i', '--input', dest='input',
					   default='.svlmasshistos.pck',
					   help='input file with histograms.')
	parser.add_option('-b', '--bkg', dest='inputBkg',
					   default='.svlbgtemplates.pck',
					   help='input file with histograms for the background processes.')
	parser.add_option('-w', '--ws', dest='wsFile', default=None,
					   help='ROOT file with previous workspace.')
	parser.add_option('--isData', dest='isData', default=False, action='store_true',
					   help='if true, final fit is performed')
	parser.add_option('--spy', dest='spy', default=False, action='store_true',
					   help='if true,shows fit results on the screen')
	parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int,
					   help='Verbose mode')
	parser.add_option('-n', '--nPexp', dest='nPexp', default=100, type=int,
					   help='Total # pseudo-experiments.')
	parser.add_option('-j', '--jobs', dest='jobs', default=1,
					   type=int, help='Run n jobs in parallel')
	parser.add_option('-o', '--outDir', dest='outDir', default='svlfits',
					   help='Output directory [default: %default]')
	parser.add_option('-t', '--test', dest='test', action='store', type=str,
		              default='',
		              help=('Run only a single fit for one category. '
		              	    'Pass an argument to select it, e.g. \n'
		              	    'em_mrank1_5_cor_t, mm_3_wro_tt, em_optmrank_5_wrounm_bg'))
	parser.add_option('-c', dest='cached', action='store_true',
		              help='Only relevant for -t options: read workspace from file.')

	(opt, args) = parser.parse_args()

	ROOT.gStyle.SetOptStat(0)
	ROOT.gStyle.SetOptTitle(0)
	ROOT.gROOT.SetBatch(True)
	if opt.spy : ROOT.gROOT.SetBatch(False)

	ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
	if not opt.test:
		ROOT.AutoLibraryLoader.enable()
		if not opt.verbose > 5:
			ROOT.shushRooFit()
			# see TError.h - gamma function prints lots of errors when scanning
	ROOT.gROOT.ProcessLine("gErrorIgnoreLevel=kFatal")

	os.system('mkdir -p %s' % opt.outDir)
	os.system('mkdir -p %s' % os.path.join(opt.outDir, 'plots'))

	# Testing
	if opt.test:
		testSignalFit(options=opt)
		return 0

	# Check if one needs to create a new workspace or run pseudo-experiments
	print 80*'-'
	if opt.wsFile is None :
		print 'Creating a new workspace file from %s'%opt.input
		ws = createWorkspace(options=opt)
		return 0
	else:
		print 'Reading workspace file from %s'%opt.wsFile
		inF = ROOT.TFile.Open(opt.wsFile)
		ws = inF.Get('w')
		inF.Close()
	print 80*'-'

	
	print 80*'-'
	return 0

if __name__ == "__main__":
	sys.exit(main())
