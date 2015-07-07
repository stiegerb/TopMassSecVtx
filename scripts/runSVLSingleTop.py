#! /usr/bin/env python
import os, sys
import ROOT
from ROOT import TMVA
from copy import deepcopy
from makeSVLDataMCPlots import resolveFilename
from makeSVLMassHistos import LUMI
from runPlotter import addPlotterOptions
from UserCode.TopMassSecVtx.storeTools_cff import fillFromStore
import pickle

"""
Get cross sections for use with weight.
"""
def getCrossSections():

	cachefile = open('.xsecweights.pck','r')
	xsecs = pickle.load(cachefile)
	cachefile.close()
#	sample_file = open('samples.txt','r')
#	xsecs = {}
#	lines = sample_file.readlines()
#	sample_file.close()
#	
#	for line in lines:
#		if 'dtag' in line:
#			i=0
#			dtag = ''
#			found_dtag = False
#			found_xsec = False
#			xsec =''
#			while i < len(line):
#				if line[i] == 'd' and i!=len(line)-1 and line[i+1]=='t':
#					found_dtag = True
#					i+=7
#				if found_dtag:
#					if line[i]=='"':
#						found_dtag = False
#					else:
#						dtag+=line[i]
#				if line[i] == 'x' and i!=len(line)-1 and line[i+1]=='s':
#					found_xsec = True
#					i+=6
#				if found_xsec:
#					if line[i]==',':
#						found_xsec = False
#					else:
#						xsec+=line[i]
#				i+=1
#			#xsecs['root://eoscms//eos/cms/store/cmst3/group/top/summer2015/treedir_bbbcb36/singlet/'+dtag+'.root']=float(xsec)
#			xsecs['treedir_bbbcb36/singlet/'+dtag+'.root']=float(xsec)
	return xsecs
	
"""
Attempt at implementing TMVA
"""
def runTMVAAnalysis(filenames,myMethodList=''):
	
	print('\nEntered code.\n')

	Use = {}

	Use['Cuts']=1
	Use['CutsD']=0
	Use['CutsPCA']=0
	Use['CutsGA']=0
	Use['CutsSA']=0

	Use['Likelihood']=0
	Use['LikelihoodD']=0
	Use['LikelihoodPCA']=0
	Use['LikelihoodKDE']=0
	Use['LikelihoodMIX']=0
	
	Use["PDERS"]           = 0
	Use["PDERSD"]          = 0
	Use["PDERSPCA"]        = 0
	Use["PDEFoam"]         = 0
	Use["PDEFoamBoost"]    = 0 
	Use["KNN"]             = 0 
	
	Use["LD"]              = 0 
	Use["Fisher"]          = 1
	Use["FisherG"]         = 0
	Use["BoostedFisher"]   = 0 
	Use["HMatrix"]         = 0
	
	Use["FDA_GA"]          = 0 
	Use["FDA_SA"]          = 0
	Use["FDA_MC"]          = 0
	Use["FDA_MT"]          = 0
	Use["FDA_GAMT"]        = 0
	Use["FDA_MCMT"]        = 0
	
	Use["MLP"]             = 0 
	Use["MLPBFGS"]         = 0 
	Use["MLPBNN"]          = 0 
	Use["CFMlpANN"]        = 0 
	Use["TMlpANN"]         = 0 
	
	Use["SVM"]             = 0
	
	Use["BDT"]             = 1 
	Use["BDTG"]            = 0 
	Use["BDTB"]            = 0 
	Use["BDTD"]            = 0 
	Use["BDTF"]            = 0  
	
	Use["RuleFit"]         = 0

	print('\nDefined Use.\n')
	
	print('\n==> Start TMVA Classification\n')
	
	if myMethodList!='':
		for key in Use.keys():
			Use[key]=0
		mlist = []
		for key in Use.keys():
			mlist.append(key)
		i=0
		while i<len(mlist):
			regMethod = mlist[i]
			if regMethod not in myMethodList.keys():
				print('Method '+regMethod+' not known in TMVA under this name. Choose among the following: \n')
				for key in Use.keys():
					print(key+'\n')
					return 0
			Use[regMethod] = 1

	print('\nPassed method list stuff.\n')

	outfileName = 'TMVA/TMVA_test.root'
	outputFile = ROOT.TFile.Open(outfileName,'RECREATE')

	#factory = TMVA.Factory('TMVAClassification',outputFile,'!V:!Silent:Color:DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Classification')
	factory = TMVA.Factory('TMVAClassification',outputFile,'!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification')

	print('\nCreated factory.\n')

	#Need to AddVariables to the factory here.

	factory.AddVariable('abs(JEta)','F')
	factory.AddVariable('abs(FJEta)','F')
#	factory.AddVariable('abs(FJPhi)','F')
#	factory.AddVariable('abs(JPhi)','F')
	factory.AddVariable('abs(LEta)','F')
#	factory.AddVariable('abs(LPhi)','F')
	factory.AddVariable('LCharge','F')
	factory.AddVariable('DeltaEtaJetFJet:=abs(FJEta - JEta)','F')
	factory.AddVariable('DeltaEtaJetLepton:=abs(JEta - LEta)','F')
	factory.AddVariable('DeltaEtaFJetLepton:=abs(FJEta - LEta)','F')
#	factory.AddVariable('DeltaPhiJetFJet:=abs(FJPhi - JPhi)','F')
#	factory.AddVariable('DeltaPhiJetLepton:=abs(JPhi - LPhi)','F')
#	factory.AddVariable('DeltaPhiFJetLepton:=abs(FJPhi - LPhi)','F')

	factory.AddSpectator('NJets','I')
	factory.AddSpectator('NFJets','I')
	factory.AddSpectator('EvCat','I')
	factory.AddSpectator('NBTags','I')

	print('\nAdded variables.\n')

	sigNames = []
	bkgNames = []
	#print('Filenames:\n')
	for item in filenames:
		#print(item)
		if 'Data' not in item:
#			if 'SingleT_t' or 'SingleTbar_t' in item:
			if item == 'MC8TeV_SingleT_t.root' or item == 'MC8TeV_SingleTbar_t.root':
				print('Sig: '+item)
				sigNames.append('treedir_bbbcb36/singlet/'+item)
			elif '172v5' in item:
#			elif 'SingleT' not in item:
				print('Bkg: '+item)
				bkgNames.append('treedir_bbbcb36/singlet/'+item)
	#print('\n\n')

	sigTrees = []
	bkgTrees = []
	sigWeights = []
	bkgWeights = []
	weights1 = getCrossSections()

	weights = {}
#	print('Printing filenames: \n')
#	for name in filenames:
#		print(name)
#	print('\n\nPrinting sigNames:\n')
#	for name in sigNames:
#		print(name)
#	print('\n\nPrinting bkgNames:\n')
#	for name in bkgNames:
#		print(name)
#	print('\n\nPrinting weights:\n')
	for name in weights1.keys():
		weights['treedir_bbbcb36/singlet/'+name+'.root']=weights1[name]
#	for name in weights.keys():
#		print(name)
#	print('\n\n')

	for name in sigNames:
		if name in weights.keys():
#			print('Entered sig\n')
			inFile = ROOT.TFile.Open(name)
#			print(name)
			myTree = inFile.Get('SVLInfo')
			sigTrees.append(myTree)
			sigWeights.append(weights[name])
	for name in bkgNames:
		if name in weights.keys():
#			if 'TT' in name:
#				print(name)
			inFile = ROOT.TFile.Open(name)
			myTree = inFile.Get('SVLInfo')
			bkgTrees.append(myTree)
			bkgWeights.append(weights[name])

	print('\nAdded Trees.\n')

	#Need to figure out how to access the weights
	#Weights should be the cross sections
	i = 0
	while i < len(sigTrees):
		factory.AddSignalTree(sigTrees[i],sigWeights[i])
#		print(sigWeights[i])
		i+=1
	i=0

#	for tree, weight in zip(sigTrees, sigWeights):
#		factory.AddSignalTree(tree, weight)


	while i < len(bkgTrees):
		factory.AddBackgroundTree(bkgTrees[i],bkgWeights[i])
#		print(sigweights[i])
		i+=1

	#Use electron or muon, exactly 2 jets, exactly 1 btag
	#weight multiplication
	factory.SetWeightExpression('Weight[0]*Weight[1]*Weight[4]*METWeight[0]*BtagWeight[0]*JESWeight[0]')
#	factory.SetWeightExpression('1.0')

	print('\nAdded signal and bkg trees and set weight expression.\n')

	cutS = ROOT.TCut('(abs(EvCat)==11 || abs(EvCat)==13) && (NJets+NFJets) == 2 && NBTags == 1 && abs(FJEta)<=10 && abs(FJPhi)<=10')
	cutB = ROOT.TCut('(abs(EvCat)==11 || abs(EvCat)==13) && (NJets+NFJets) == 2 && NBTags == 1 && abs(FJEta)<=10 && abs(FJPhi)<=10')
	factory.PrepareTrainingAndTestTree(cutS,cutB,"nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V" )

	print('\nPrepared training and test trees.\n')

	if Use['Cuts']:
		factory.BookMethod(TMVA.Types.kCuts,'Cuts','!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart')
	if Use['CutsD']:
		factory.BookMethod(TMVA.Types.kCuts,'CutsD','!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart:VarTransform=Decorrelate')
	if Use['CutsPCA']:
		factory.BookMethod(TMVA.Types.kCuts,'CutsPCA','!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart:VarTransform=PCA')
	if Use['CutsGA']:
		factory.BookMethod(TMVA.Types.kCuts,'CutsGA','H:!V:FitMethod=GA:CutRangeMin[0]=-10:CutRangeMax[0]=10:VarProp[1]=FMax:EffSel:Steps=30:Cycles=3:PopSize=400:SC_steps=10:SC_rate=5:SC_factor=0.95')
	if Use['CutsSA']:
		factory.BookMethod(TMVA.Types.kCuts,'CutsSA','!H:!V:FitMethod=SA:EffSel:MaxCalls=150000:KernelTemp=IncAdaptive:InitialTemp=1e+6:MinTemp=1e-6:Eps=1e-10:UseDefaultScale')
	if Use['Likelihood']:
		factory.BookMethod(TMVA.Types.kLikelihood,'Likelihood','H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmoothBkg[1]=10:NSmooth=1:NAvEvtPerBin=50')
		#factory.BookMethod(TMVA.Types.kLikelihood,'Likelihood','H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=1:NAvEvtPerBin=50')
	if Use['LikelihoodD']:
		factory.BookMethod(TMVA.Types.kLikelihood,'LikelihoodD','!H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=50:VarTransform=Decorrelate')
	if Use['LikelihoodPCA']:
		factory.BookMethod(TMVA.Types.kLikelihood,'LikelihoodPCA','!H:!V:!TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=50:VarTransform=PCA')
	if Use['LikelihoodKDE']:
		factory.BookMethod(TMVA.Types.kLikelihood,'LikelihoodKDE','!H:!V:!TransformOutput:PDFInterpol=KDE:KDEtype=Gauss:KDEiter=Adaptive:KDEFineFactor=0.3:KDEborder=None:NAvEvtPerBin=50')
	if Use['LikelihoodMIX']:
		factory.BookMethod(TMVA.Types.kLikelihood,'LikelihoodMIX','!H:!V:!TransformOutput:PDFInterpolSig[0]=KDE:PDFInterpolBkg[0]=KDE:PDFInterpolSig[1]=KDE:PDFInterpolBkg[1]=KDE:PDFInterpolSig[2]=Spline2:PDFInterpolBkg[2]=Spline2:PDFInterpolSig[3]=Spline2:PDFInterpolBkg[3]=Spline2:KDEtype=Gauss:KDEiter=Nonadaptive:KDEborder=None:NAvEvtPerBin=50')
	if Use['PDERS']:
		factory.BookMethod(TMVA.Types.kPDERS,'PDERS','!H:!V:NormTree=T:VolumeRangeMode=Adaptive:KernelEstimator=Gauss:GaussSigma=0.3:NEventsMin=400:NEventsMax=600')
	if Use['PDERSD']:
		factory.BookMethod(TMVA.Types.kPDERS,'PDERSD','!H:!V:VolumeRangeMode=Adaptive:KernelEstimator=Gauss:GaussSigma=0.3:NEventsMin=400:NEventsMax=600:VarTransform=Decorrelate')
	if Use['PDERSPCA']:
		factory.BookMethod(TMVA.Types.kPDERS,'PDERSPCA','!H:!V:VolumeRangeMode=Adaptive:KernelEstimator=Gauss:GaussSigma=0.3:NEventsMin=400:NEventsMax=600:VarTransform=PCA')
	if Use['PDEFoam']:
		factory.BookMethod(TMVA.Types.kPDEFoam,'PDEFoam','!H:!V:SigBgSeparate=F:TailCut=0.001:VolFrac=0.0666:nActiveCells=500:nSampl=2000:nBin=5:Nmin=100:Kernel=None:Compress=T')
	if Use['PDEFoamBoost']:
		factory.BookMethod(TMVA.Types.kPDEFoam,'PDEFoamBoost','!H:!V:Boost_Num=30:Boost_Transform=linear:SigBgSeparate=F:MaxDepth=4:UseYesNoCell=T:DTLogic=MisClassificationError:FillFoamWithOrigWeights=F:TailCut=0:nActiveCells=500:nBin=20:Nmin=400:Kernel=None:Compress=T')
	if Use['KNN']:
		factory.BookMethod(TMVA.Types.kKNN,'KNN','H:nkNN=20:ScaleFrac=0.8:SigmaFact=1.0:Kernel=Gaus:UseKernel=F:UseWeight=T:!Trim')
	if Use['HMatrix']:
		factory.BookMethod(TMVA.Types.kHMatrix,'HMatrix','!H:!V:VarTransform=None')
	if Use['LD']:
		factory.BookMethod(TMVA.Types.kLD,'LD','H:!V:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10')
	if Use['Fisher']:
		factory.BookMethod(TMVA.Types.kFisher,'Fisher','H:!V:Fisher:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10')
	if Use['FisherG']:
		factory.BookMethod(TMVA.Types.kFisher,'FisherG','H:!V:VarTransform=Gauss')
	if Use['BoostedFisher']:
		factory.BookMethod(TMVA.Types.kFisher,'BoostedFisher','H:!V:Boost_Num=20:Boost_Transform=log:Boost_Type=AdaBoost:Boost_AdaBoostBeta=0.2:!Boost_DetailedMonitoring')
	if Use['FDA_MC']:
		factory.BookMethod(TMVA.Types.kFDA,'FDA_MC','H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=MC:SampleSize=100000:Sigma=0.1')
	if Use['FDA_GA']:
		factory.BookMethod(TMVA.Types.kFDA,'FDA_GA','H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=GA:PopSize=300:Cycles=3:Steps=20:Trim=True:SaveBestGen=1')
	if Use['FDA_SA']:
		factory.BookMethod(TMVA.Types.kFDA,'FDA_SA','H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=SA:MaxCalls=15000:KernelTemp=IncAdaptive:InitialTemp=1e+6:MinTemp=1e-6:Eps=1e-10:UseDefaultScale')
	if Use['FDA_MT']:
		factory.BookMethod(TMVA.Types.kFDA,'FDA_MT','H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=MINUIT:ErrorLevel=1:PrintLevel=-1:FitStrategy=2:UseImprove:UseMinos:SetBatch')
	if Use['FDA_GAMT']:
		factory.BookMethod(TMVA.Types.kFDA,'FDA_GAMT','H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=GA:Converger=MINUIT:ErrorLevel=1:PrintLevel=-1:FitStrategy=0:!UseImprove:!UseMinos:SetBatch:Cycles=1:PopSize=5:Steps=5:Trim')
	if Use['FDA_MCMT']:
		factory.BookMethod(TMVA.Types.kFDA,'FDA_MCMT','H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1);(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=MC:Converger=MINUIT:ErrorLevel=1:PrintLevel=-1:FitStrategy=0:!UseImprove:!UseMinos:SetBatch:SampleSize=20')
	if Use['MLP']:
		factory.BookMethod(TMVA.Types.kMLP,'MLP','H:!V:NeuronType=tanh:VarTransform=N:NCycles=600:HiddenLayers=N+5:TestRate=5:!UseRegulator')
	if Use['MLPBFGS']:
		factory.BookMethod(TMVA.Types.kMLP,'MLPBFGS','H:!V:NeuronType=tanh:VarTransform=N:NCycles=600:HiddenLayers=N+5:TestRate=5:TrainingMethod=BFGS:!UseRegulator')
	if Use['MLPBNN']:
		factory.BookMethod(TMVA.Types.kMLP,'MLPBN','H:!V:NeuronType=tanh:VarTransform=N:NCycles=600:HiddenLayers=N+5:TestRate=5:TrainingMethod=BFGS:UseRegulator')
	if Use['CFMlpANN']:
		factory.BookMethod(TMVA.Types.kCFMlpANN,'CFMlpANN','!H:!V:NCycles=2000:HiddenLayers=N+1,N')
	if Use['TMlpANN']:
		factory.BookMethod(TMVA.Types.kTMlpANN,'TMlpANN','!H:!V:NCycles=200:HiddenLayers=N+1,N:LearningMethod=BFGS:ValidationFraction=0.3')
	if Use['SVM']:
		factory.BookMethod(TMVA.Types.kSVM,'SVM','Gamma=0.25:Tol=0.001:VarTransform=Norm')
	if Use['BDTG']:
		factory.BookMethod(TMVA.Types.kBDT,'BDTG','!H:!V:NTrees=1000:MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=2')
	if Use['BDT']:
		factory.BookMethod(TMVA.Types.kBDT,'BDT','!H:!V:NTrees=850:SeparationType=GiniIndex:nCuts=20')
		#factory.BookMethod(TMVA.Types.kBDT,'BDT','!H:!V:NTrees=850:SeparationType=GiniIndex:nCuts=20:CreateMVAPdfs')
		#factory.BookMethod(TMVA.Types.kBDT,'BDT','!H:!V:NTrees=850:MinNodeSize=2.5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20')
	if Use['BDTB']:
		factory.BookMethod(TMVA.Types.kBDT,'BDTB','!H:!V:NTrees=400:BoostType=Bagging:SeparationType=GiniIndex:nCuts=20')
	if Use['BDTD']:
		factory.BookMethod(TMVA.Types.kBDT,'BDTD','!H:!V:NTrees=400:MinNodeSize=5%:MaxDepth=3:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=20:VarTransform=Decorrelate')
	if Use['BDTF']:
		factory.BookMethod(TMVA.Types.kBDT,'BDTMitFisher','!H:!V:NTrees=50:MinNodeSize=2.5%:UseFisherCuts:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=20')
	if Use['RuleFit']:
		factory.BookMethod(TMVA.Types.kRuleFit,'RuleFit','H:!V:RuleFitModule=RFTMVA:Model=ModRuleLinear:MinImp=0.001:RuleMinDist=0.001:NTrees=20:fEventsMin=0.01:fEventsMax=0.5:GDTau=-1.0:GDTauPrec=0.01:GDStep=0.01:GDNSteps=10000:GDErrScale=1.02')

	print('\nPassed all of the if statements.\n')

	factory.TrainAllMethods()
	print('\nTrained all methods.\n')
	factory.TestAllMethods()
	print('\nTested all methods.\n')
	factory.EvaluateAllMethods()
	print('\nEvaluated all methods.\n')

	outputFile.Close()

	print('\n==> Wrote root file: '+outputFile.GetName()+'\n')
	print('==> TMVAClassification is done!\n')
	print('Now run TMVAGui.\n')

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
			histos['NJets_'+tag]      = ROOT.TH1F('NJets_'+tag,';Number of Jets;Events',10,0,10)
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

	#loop over events in tree
	for i in xrange(0,SVLInfo.GetEntriesFast()):
		
		SVLInfo.GetEntry(i)

		#EDIT: Moved this section up from down below.
		weight = 1 if isData else SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]
		lumiweight = 1 if isData else SVLInfo.XSWeight*LUMI

		cnt_ini_events+=weight

######################################

		#require e or mu events
		if ROOT.TMath.Abs(SVLInfo.EvCat)!=11 and ROOT.TMath.Abs(SVLInfo.EvCat)!=13 : continue
		chCat = 'e' if SVLInfo.EvCat==-11 else 'mu'

		cnt_e_or_mu+=weight

####################################

		#require 1 forward jet
		fwdeta=ROOT.TMath.Abs(SVLInfo.FJEta)
		if fwdeta<3.0 or fwdeta>5: continue

		cnt_1_fwd_jet+=weight

####################################

		#require at least 1 and less than 4 central jets
		if SVLInfo.NJets<1 or SVLInfo.NJets>3 : continue		
		jetCat="%dj" % (SVLInfo.NJets)

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
		if 0 > cjeta or cjeta > 2.0: continue

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
		histos['NJets_'+tag]  .Fill(SVLInfo.NJets,   weight)
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
	filenames = []

	try:
		
		treefiles = {} # procname -> [filename1, filename2, ...]
		if args[0].find('/store')>=0:
			for filename in fillFromStore(args[0]):
				if not os.path.splitext(filename)[1] == '.root': continue	
				isData, pname, splitno = resolveFilename(os.path.basename(filename))
				if not pname in treefiles: treefiles[pname] = []
				taskList.append((filename, isData,options.outDir))
				filenames.append(filename)
		else:
			for filename in os.listdir(args[0]):
				if not os.path.splitext(filename)[1] == '.root': continue	
				isData, pname, splitno = resolveFilename(filename)
				if not pname in treefiles: treefiles[pname] = []
				taskList.append((filename, isData,options.outDir))
				filenames.append(filename)
	except IndexError:
		print "Please provide a valid input directory"
		return -1
	
	#submit tasks in parallel, if required, or run sequentially
#	if opt.jobs>0:
#		print ' Submitting jobs in %d threads' % opt.jobs
#		import multiprocessing as MP
#		pool = MP.Pool(opt.jobs)
#		pool.map(runSingleTopAnalysisPacked,taskList)
#	else:
#		for filename,isData,outDir in taskList:
#			runSingleTopAnalysis(filename=filename,isData=isData,outDir=outDir)
	#EDIT
#	for filename in filenames:
#		filenames.append(filename)
#		print(filename)
	print('\nEntering code.\n')
	runTMVAAnalysis(filenames)

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




