#! /usr/bin/env python
import os, sys
import ROOT
from copy import deepcopy
from makeSVLDataMCPlots import resolveFilename
from makeSVLMassHistos import LUMI
from runPlotter import addPlotterOptions
from UserCode.TopMassSecVtx.storeTools_cff import fillFromStore

"""
single top selection
"""
def runSingleTopAnalysis(filename,isData,outDir):

	#prepare histograms to store
	histos={}
	for chCat in ['e','mu']:
		for jetCat in ['2j','3j']:
			#for nTracks in ['1t','2t','3t']:
			tag=chCat+jetCat
			histos['NPVtx_'+tag]      = ROOT.TH1F('NPVtx_'+tag,';N_{PV}-N_{HP};Events',30,0,30)
			histos['MT_'+tag]         = ROOT.TH1F('MT_'+tag,';Transverse mass [GeV];Events',50,0,250)
			histos['MET_'+tag]        = ROOT.TH1F('MET_'+tag,';Missing transverse energy [GeV];Events',50,0,200)
			histos['FJPt_'+tag]       = ROOT.TH1F('FJPt_'+tag,';Transverse momentum [GeV];Events',10,30,230)
			histos['FJEta_'+tag]      = ROOT.TH1F('FJEta_'+tag,';Pseudo-rapidity;Events',50,0,5)
			histos['DeltaEtaJB_'+tag] = ROOT.TH1F('DeltaEtaJB_'+tag,';|#eta_{j}-#eta_{b}|;Events',25,0,8)
			histos['EtaJxEtaB_'+tag]  = ROOT.TH1F('EtaJxEtaB_'+tag,';#eta_{j}.#eta_{b};Events',20,-10,10)
			histos['SVLMass_'+tag]    = ROOT.TH1F('SVLMass_'+tag,';m(SV,lepton) [GeV]',50,0,200)
			histos['SVMass_'+tag]     = ROOT.TH1F('SVMass_'+tag,';m(SV) [GeV]',12,0,6)
			histos['CJEta_'+tag]      = ROOT.TH1F('CJEta_'+tag,';Pseudo-rapidity;Events',25,0,2.5)
			histos['CJPt_'+tag]       = ROOT.TH1F('CJPt_'+tag,';Transverse momentum [GeV];Events',10,30,230)
			histos['NJets_'+tag]      = ROOT.TH1F('NJets_'+tag,';Number of Jets (forward and central);Events',10,0,10)
			histos['NBTags_'+tag]     = ROOT.TH1F('NBTags_'+tag,';Number of Tags;Events',10,0,10)
			histos['LPt_'+tag]        = ROOT.TH1F('LPt_'+tag,';Transverse momentum [GeV];Events',30,0,300)
			histos['SVLDeltaR_'+tag]  = ROOT.TH1F('SVLDeltaR_'+tag,';#Delta_{R};Events',10,0,5)
			histos['SVNtrk_'+tag]     = ROOT.TH1F('SVNtrk_'+tag,';Number of Tracks;Events',10,0,10)
			histos['CombInfo_'+tag]   = ROOT.TH1F('CombInfo_'+tag,';Correct Combination?;Events',3,-1.5,1.5)
	for h in histos:
		histos[h].Sumw2()
		histos[h].SetDirectory(0)


	#open input file and get tree for analysis
	print ' ... processing',filename
	fIn=ROOT.TFile.Open(filename)
	SVLInfo=fIn.Get('SVLInfo')

	#EDIT: Counts for sig/bkg calculations.
	cnt_ini_events = 0
	cnt_e_or_mu = 0
	cnt_1_fwd_jet = 0
	cnt_central_jets = 0
	cnt_1_sec_vtx = 0
	cnt_MT_cut = 0
	cnt_final_events = 0

	#tmva_reader = TMVA.Reader()

	#loop over events in tree
	for i in xrange(0,SVLInfo.GetEntriesFast()):
		
		SVLInfo.GetEntry(i)

		#EDIT: Moved this section up from down below.
		weight = 1 if isData else SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]
		lumiweight = 1 if isData else SVLInfo.XSWeight*LUMI

		cnt_ini_events+=weight

######################################

		#require e or mu events
#		if ROOT.TMath.Abs(SVLInfo.EvCat)!=11 and ROOT.TMath.Abs(SVLInfo.EvCat)!=13 : continue
#		chCat = 'e' if ROOT.TMath.Abs(SVLInfo.EvCat)==11 else 'mu'

                if SVLInfo.EvCat!=11 and SVLInfo.EvCat!=13: continue
                chCat = 'e' if SVLInfo.EvCat==11 else 'mu'
		cnt_e_or_mu+=weight

####################################

		#require 1 forward jet
		fwdeta=ROOT.TMath.Abs(SVLInfo.FJEta)
		if fwdeta<2.5 or fwdeta>5: continue

		cnt_1_fwd_jet+=weight

####################################

		#require at least 1 and less than 4 central jets
#		if (SVLInfo.NJets+SVLInfo.NFJets)<1 or (SVLInfo.NJets+SVLInfo.NFJets)>3 : continue		
                if SVLInfo.NJets < 1 or SVLInfo.NJets > 3: continue
		jetCat="%dj" % (SVLInfo.NJets)#+SVLInfo.NFJets)

		cnt_central_jets+=weight

###################################

		#require 1 SecVtx
		if SVLInfo.SVMass<=0 : continue

		cnt_1_sec_vtx+=weight

###################################

		#re-inforce the cut in MT
		if SVLInfo.MT<50 : continue

		cnt_MT_cut+=weight

###################################

		#require 1 or 2 btagged jets
		if SVLInfo.NBTags!=1 and SVLInfo.NBTags!=2: continue

###################################

		#require CJEta < 2
		cjeta=ROOT.TMath.Abs(SVLInfo.JEta)
#		if 0 > cjeta or cjeta > 2.0: continue

###################################

		#separate into nTracks
		#if SVLInfo.SVNtrk < 1 or SVLInfo.SVNtrk > 3: continue
		#if SVLInfo.SVNtrk == 1:
		#nTrack = '1t'
		#elif SVLInfo.SVNtrk == 2:
		#nTrack = '2t'
		#else:
		#nTrack = '3t'

		cnt_final_events+=weight

		#EDIT: Commented out weight and moved up
		#event weights to fill histograms appropriately
		#weight = 1 if isData else SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]
		#lumiweight = 1 if isData else SVLInfo.XSWeight*LUMI

		#fill histograms with variables of interest
		tag=chCat+jetCat#+'_'+nTrack
		histos['NPVtx_'+tag]  .Fill(SVLInfo.NPVtx-1, weight)
		histos['MT_'+tag]     .Fill(SVLInfo.MT,      weight)
		histos['MET_'+tag]    .Fill(SVLInfo.MET,     weight)
		histos['FJPt_'+tag]   .Fill(SVLInfo.FJPt,    weight)
		histos['FJEta_'+tag]  .Fill(fwdeta,          weight)
		histos['DeltaEtaJB_'+tag].Fill(ROOT.TMath.Abs(SVLInfo.FJEta-SVLInfo.JEta), weight)
		histos['EtaJxEtaB_'+tag].Fill(SVLInfo.FJEta*SVLInfo.JEta, weight)
		histos['SVLMass_'+tag].Fill(SVLInfo.SVLMass, weight)
		histos['SVMass_'+tag] .Fill(SVLInfo.SVMass,  weight)
		histos['CJEta_'+tag]  .Fill(cjeta,           weight)
		histos['CJPt_'+tag]   .Fill(SVLInfo.JPt,     weight)
		histos['NJets_'+tag]  .Fill((SVLInfo.NJets),weight) #+SVLInfo.NFJets),   weight)
		histos['NBTags_'+tag] .Fill(SVLInfo.NBTags,  weight)
		histos['LPt_'+tag]    .Fill(SVLInfo.LPt,     weight)
		histos['SVLDeltaR_'+tag]   .Fill(SVLInfo.SVLDeltaR,         weight)
		histos['SVNtrk_'+tag] .Fill(SVLInfo.SVNtrk,  weight)
		histos['CombInfo_'+tag].Fill(SVLInfo.CombInfo,  weight)

	#close input file, after analysis
	fIn.Close()

	#dump histograms to ROOT file
	fOut=ROOT.TFile.Open(os.path.join(outDir,os.path.basename(filename)),'RECREATE')
	for h in histos: histos[h].Write()
	print '   output stored in %s' % fOut.GetName()
	fOut.Close()

	#EDIT: Make file with sig/bkg
#	sigbkg = open('sig_bkg.txt','a')
#	sigbkg.write('#####################'+filename+'\n')
#	sigbkg.write('Initial Events: '+str(cnt_ini_events)+'\n')
#	sigbkg.write('e or mu Events: '+str(cnt_e_or_mu)+'\n')
#	sigbkg.write('Forward Jet Ct: '+str(cnt_1_fwd_jet)+'\n')
#	sigbkg.write('Central Jet Ct: '+str(cnt_central_jets)+'\n')
#	sigbkg.write('Sec Vertex Cut: '+str(cnt_1_sec_vtx)+'\n')
#	sigbkg.write('MT Checked Cut: '+str(cnt_MT_cut)+'\n')
#	sigbkg.write('Num. Fnal Evts: '+str(cnt_final_events)+'\n'+'\n')
#	sigbkg.close()


"""
Wrapper for when the analysis is run in parallel
"""
def runSingleTopAnalysisPacked(args):
	filename,isData,outDir = args
	try:
		return runSingleTopAnalysis(filename=filename,isData=isData,outDir=outDir)
	except ReferenceError:
		print 50*'<'
		print "  Problem with", name, "continuing without"
		print 50*'<'
		return False

"""
"""
def main(args, options):

	#prepare output directory 
	if args[0]==options.outDir:
		options.outDir += '/singleTop'
		print 'Warning output directory is the same, renaming as %s' % options.outDir
	os.system('mkdir -p %s'%options.outDir)
	
	#prepare one task per file to process
	taskList=[]
	#EDIT
#	filenames = []

	try:
		
		treefiles = {} # procname -> [filename1, filename2, ...]
		if args[0].find('/store')>=0:
			for filename in fillFromStore(args[0]):
				if not os.path.splitext(filename)[1] == '.root': continue	
				isData, pname, splitno = resolveFilename(os.path.basename(filename))
				if not pname in treefiles: treefiles[pname] = []
				taskList.append((filename, isData,options.outDir))
#				filenames.append(filename)
		else:
			for filename in os.listdir(args[0]):
				if not os.path.splitext(filename)[1] == '.root': continue	
				isData, pname, splitno = resolveFilename(filename)
				if not pname in treefiles: treefiles[pname] = []
				taskList.append((filename, isData,options.outDir))
#				filenames.append(filename)

	except IndexError:
		print "Please provide a valid input directory"
		return -1
	
	#submit tasks in parallel, if required, or run sequentially
	if opt.jobs>0:
		print ' Submitting jobs in %d threads' % opt.jobs
		import multiprocessing as MP
		pool = MP.Pool(opt.jobs)
		pool.map(runSingleTopAnalysisPacked,taskList)
	else:
		for filename,isData,outDir in taskList:
			runSingleTopAnalysis(filename=filename,isData=isData,outDir=outDir)

#	print('\nEntering code.\n')
#	runTMVAAnalysis(filenames)

	#EDIT: Write current cuts to sig/bkg file
	sigbkg = open('sig_bkg.txt','a')
	sigbkg.write('#####################The Cuts:\n')
	sigbkg.write('Must be an e or mu Event\n')
	sigbkg.write('Exactly 1 Forward Jet with eta<3.2 or eta>4.7\n')
	sigbkg.write('1 < Num, Central Jets < 3\n')
	sigbkg.write('Exactly 1 Sec Vertex\n')
	sigbkg.write('MT > 50\n')
	sigbkg.close()
			
	return 0

"""
"""
if __name__ == "__main__":
	import sys
	tmpargv  = sys.argv[:]     # [:] for a copy, not reference
	sys.argv = []
	from ROOT import gROOT, gStyle, gSystem
	sys.argv = tmpargv
	from optparse import OptionParser
	usage = """
	usage: %prog [options] input_directory
	"""
	parser = OptionParser(usage=usage)
	addPlotterOptions(parser)
	parser.set_default(dest='outDir',value='singleTop')
	(opt, args) = parser.parse_args()

	gROOT.SetBatch(True)
	gStyle.SetOptTitle(0)
	gStyle.SetOptStat(0)
	gSystem.Load('libUserCodeTopMassSecVtx.so')

	exit(main(args, opt))




