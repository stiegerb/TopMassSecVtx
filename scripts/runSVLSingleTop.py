#! /usr/bin/env python
import os, sys
import ROOT
from copy import deepcopy
from makeSVLDataMCPlots import resolveFilename
from makeSVLMassHistos import LUMI
from runPlotter import addPlotterOptions
from UserCode.TopMassSecVtx.storeTools_cff import fillFromStore

import pickle
from ROOT import TMVA
import array

"""
Get cross sections for use with weight using .pck file created with runPlotter.py
"""
def getCrossSections():

	cachefile = open('.xsecweights.pck','r')
	xsecs = pickle.load(cachefile)
	cachefile.close()
	return xsecs
	
"""
TMVA training -- must be completed before the analysis is run.
"""
def runTMVAAnalysis(filenames,myMethodList=''):
	
	print('\nEntered code.\n')

	#Define dictionary for possible optimization methods
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
	
	#Taken directly from example that comes with the TMVA package download
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

	#Define the output root file
	outfileName = 'TMVA/TMVA_test.root'
	outputFile = ROOT.TFile.Open(outfileName,'RECREATE')

	#Define the factory
	#factory = TMVA.Factory('TMVAClassification',outputFile,'!V:!Silent:Color:DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Classification')
	factory = TMVA.Factory('TMVAClassification',outputFile,'!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification')

	print('\nCreated factory.\n')

	#Add variables to the factory which will be used for the optimization

	factory.AddVariable('abs(JEta)','F')
	factory.AddVariable('abs(FJEta)','F')
	factory.AddVariable('abs(LEta)','F')
	factory.AddVariable('LCharge','F')
	factory.AddVariable('DeltaEtaJetFJet:=abs(FJEta - JEta)','F')
	factory.AddVariable('DeltaEtaJetLepton:=abs(JEta - LEta)','F')
	factory.AddVariable('DeltaEtaFJetLepton:=abs(FJEta - LEta)','F')
	factory.AddVariable('NBTags','I')
	
	#Add variables to the factory which will not be considered in the optimization
	factory.AddSpectator('MT','F')
	factory.AddSpectator('NJets','I')
	factory.AddSpectator('NFJets','I')
	factory.AddSpectator('EvCat','I')
	factory.AddSpectator('SVMass','F')
	factory.AddSpectator('FJPt','F')
	factory.AddSpectator('JPt','F')
	factory.AddSpectator('MET','F')

	print('\nAdded variables.\n')

	#Create lists of the files considered signal and background
	sigNames = []
	bkgNames = []
	for item in filenames:
		if 'Data' not in item:
			if item == 'MC8TeV_SingleT_t.root' or item == 'MC8TeV_SingleTbar_t.root':
				sigNames.append('treedir_bbbcb36/singlet/'+item)
			elif '172v5' in item:
				bkgNames.append('treedir_bbbcb36/singlet/'+item)

	#Create lists of the signal and background weights and trees
	sigTrees = []
	bkgTrees = []
	sigWeights = []
	bkgWeights = []
	weights1 = getCrossSections()

	weights = {}
	for name in weights1.keys():
		weights['treedir_bbbcb36/singlet/'+name+'.root']=weights1[name]

	for name in sigNames:
		if name in weights.keys():
			inFile = ROOT.TFile.Open(name)
			myTree = inFile.Get('SVLInfo')
			sigTrees.append(myTree)
			sigWeights.append(weights[name])
		else:
			print('ERROR: '+name+' not in weights dictionary.\n')
	for name in bkgNames:
		if name in weights.keys():
			inFile = ROOT.TFile.Open(name)
			myTree = inFile.Get('SVLInfo')
			bkgTrees.append(myTree)
			bkgWeights.append(weights[name])
		else:
			print('ERROR: '+name+' not in weights dictionary.\n')

	print('\nAdded Trees.\n')

	#Add the weighted trees to the factory for processing
	i = 0
	while i < len(sigTrees):
		factory.AddSignalTree(sigTrees[i],sigWeights[i])
		i+=1
	i=0

	while i < len(bkgTrees):
		factory.AddBackgroundTree(bkgTrees[i],bkgWeights[i])
		i+=1

	#Create the event-by-event weight expression
	factory.SetWeightExpression('Weight[0]*Weight[1]*Weight[4]*METWeight[0]*BtagWeight[0]*JESWeight[0]')

	print('\nAdded signal and bkg trees and set weight expression.\n')

	#Add the cuts to be performed before the optimization.  These must match those in the analysis.
	cutS = ROOT.TCut('((abs(EvCat)==11 && MET >= 45) || abs(EvCat)==13) && (NJets+NFJets) == 2 && SVMass > 0 && abs(FJEta)<=20 && NBTags > 0 && MT >= 50 && JPt > 40 && FJPt > 40')
	cutB = ROOT.TCut('((abs(EvCat)==11 && MET >= 45) || abs(EvCat)==13) && (NJets+NFJets) == 2 && SVMass > 0 && abs(FJEta)<=20 && NBTags > 0 && MT >= 50 && JPt > 40 && FJPt > 40')
	factory.PrepareTrainingAndTestTree(cutS,cutB,"nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V" )

	print('\nPrepared training and test trees.\n')

	#Book the methods used
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

	#Run the optimization
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
	histos['EventYields'] = ROOT.TH1F('EventYields',';Channel;Events',4,0,4)
	histos['EventYields'].GetXaxis().SetBinLabel(1,'e,2j')
	histos['EventYields'].GetXaxis().SetBinLabel(2,'#mu,2j')
	histos['EventYields'].GetXaxis().SetBinLabel(3,'e,3j')
	histos['EventYields'].GetXaxis().SetBinLabel(4,'#mu,3j')
	for chCat in ['e','mu']:
		for jetCat in ['2j','3j']:
			#for nTrack in ['1t','2t','3t','4t','5t']:
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
				histos['BDToutput_'+tag]  = ROOT.TH1F('BDToutput_'+tag,';BDT Output;Events',25,-0.4,0.45)
				histos['BDToutputoriginal_'+tag]  = ROOT.TH1F('BDToutputoriginal_'+tag,';BDT Output;Events',25,-0.4,0.45)
				histos['SVLMassWJets_'+tag]       = ROOT.TH1F('SVLMassWJets_'+tag,';m(SV,lepton) [GeV]',50,0,200)
				histos['BDToutputQCD_'+tag]       = ROOT.TH1F('BDToutputQCD_'+tag,'BDT Output; Events',25,-0.4,0.45)
				histos['SVLMassQCD_' +tag]        = ROOT.TH1F('SVLMassQCD_'+tag,';m(SV,lepton) [GeV]',50,0,200)
				#Create histos to be filled with reweighted signal only
				if 'SingleT' in filename:
					histos['SVLMass_nominal_'+tag] = ROOT.TH1F('SVLMass_nominal_'+tag,';m(SV,lepton) [GeV] Nominal',50,0,200)
					histos['SVLMass_puup_'+tag] = ROOT.TH1F('SVLMass_puup_'+tag,';m(SV,lepton) [GeV] Pileup up',50,0,200)
					histos['SVLMass_pudn_'+tag] = ROOT.TH1F('SVLMass_pudn_'+tag,';m(SV,lepton) [GeV] Pileup down',50,0,200)
					histos['SVLMass_lepselup_'+tag] = ROOT.TH1F('SVLMass_lepselup_'+tag,';m(SV,lepton) [GeV] Lepton selection up',50,0,200)
					histos['SVLMass_lepseldn_'+tag] = ROOT.TH1F('SVLMass_lepseldn_'+tag,';m(SV,lepton) [GeV] Lepton selection down',50,0,200)
					histos['SVLMass_umetup_'+tag] = ROOT.TH1F('SVLMass_umetup_'+tag,';m(SV,lepton) [GeV] Uncl. MET up',50,0,200)
					histos['SVLMass_umetdn_'+tag] = ROOT.TH1F('SVLMass_umetdn_'+tag,';m(SV,lepton) [GeV] Uncl. MET down',50,0,200)
					histos['SVLMass_toppt_'+tag] = ROOT.TH1F('SVLMass_toppt_'+tag,';m(SV,lepton) [GeV] Top p_{T} weight applied',50,0,200)
					histos['SVLMass_topptup_'+tag] = ROOT.TH1F('SVLMass_topptup_'+tag,';m(SV,lepton) [GeV] Top p_{T} weight up',50,0,200)
					histos['SVLMass_bfrag_'+tag] = ROOT.TH1F('SVLMass_bfrag_'+tag,';m(SV,lepton) [GeV] Z2* rb LEP',50,0,200)
					histos['SVLMass_bfragup_'+tag] = ROOT.TH1F('SVLMass_bfragup_'+tag,';m(SV,lepton) [GeV] Z2* rb LEP hard',50,0,200)
					histos['SVLMass_bfragdn_'+tag] = ROOT.TH1F('SVLMass_bfragdn_'+tag,';m(SV,lepton) [GeV] Z2* rb LEP soft',50,0,200)
					histos['SVLMass_bfragp11_'+tag] = ROOT.TH1F('SVLMass_bfragp11_'+tag,';m(SV,lepton) [GeV] P11 fragmentation',50,0,200)
					histos['SVLMass_bfragpete_'+tag] = ROOT.TH1F('SVLMass_bfragpete_'+tag,';m(SV,lepton) [GeV] Z2* Peterson',50,0,200)
					histos['SVLMass_bfraglund_'+tag] = ROOT.TH1F('SVLMass_bfraglund_'+tag,';m(SV,lepton) [GeV] Z2* Lund',50,0,200)
					histos['SVLMass_jesup_'+tag] = ROOT.TH1F('SVLMass_jesup_'+tag,';m(SV,lepton) [GeV] Jet energy scale up',50,0,200)
					histos['SVLMass_jesdn_'+tag] = ROOT.TH1F('SVLMass_jesdn_'+tag,';m(SV,lepton) [GeV] Jet energy scale down',50,0,200)
					histos['SVLMass_jerup_'+tag] = ROOT.TH1F('SVLMass_jerup_'+tag,';m(SV,lepton) [GeV] Jet energy resolution up',50,0,200)
					histos['SVLMass_jerdn_'+tag] = ROOT.TH1F('SVLMass_jerdn_'+tag,';m(SV,lepton) [GeV] Jet energy resolution down',50,0,200)
					histos['SVLMass_btagup_'+tag] = ROOT.TH1F('SVLMass_btagup_'+tag,';m(SV,lepton) [GeV] b-tag eff up',50,0,200)
					histos['SVLMass_btagdn_'+tag] = ROOT.TH1F('SVLMass_btagdn_'+tag,';m(SV,lepton) [GeV] b-tag eff down',50,0,200)
					histos['SVLMass_lesup_'+tag] = ROOT.TH1F('SVLMass_lesup_'+tag,';m(SV,lepton) [GeV] Lepton energy scale up',50,0,200)
					histos['SVLMass_lesdn_'+tag] = ROOT.TH1F('SVLMass_lesdn_'+tag,';m(SV,lepton) [GeV] Lepton energy scale down',50,0,200)
					histos['SVLMass_bfnuup_'+tag] = ROOT.TH1F('SVLMass_bfnuup_'+tag,';m(SV,lepton) [GeV] B hadron semi-lep BF up',50,0,200)
					histos['SVLMass_bfnudn_'+tag] = ROOT.TH1F('SVLMass_bfnudn_'+tag,';m(SV,lepton) [GeV] B hadron semi-lep BF down',50,0,200)

	mass = '172'
	if '166' in filename:
		mass = '166'
	elif '169' in filename:
		mass = '169'
	elif '171' in filename:
		mass = '171'
	elif '173' in filename:
		mass = '173'
	elif '175' in filename:
		mass = '175'
	elif '178' in filename:
		mass = '178'
	elif '181' in filename:
		mass = '181'
	elif '163' in filename:
		mass = '163'

	for tag in ['t','tt','bg']:
		for ch in ['e','m']:
			for comb in ['cor','wro','inc','unm']:
				for n in ['2j','3j']:
					name = tag+'_'+ch+n+'_'+mass+'_'+comb
					histos[name] = ROOT.TH1F(name,';m(SV,lepton) [GeV]',50,0,200)
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

	#TMVA Addition
	tmva_reader=None
	try:
		TMVA.Tools.Instance()
		tmva_reader = TMVA.Reader()

		abs_jeta = array.array('f',[0])
		abs_fjeta = array.array('f',[0])
		abs_leta = array.array('f',[0])
		lcharge = array.array('f',[0])
		deltaetajetfjet = array.array('f',[0])
		deltaetajetlepton = array.array('f',[0])
		deltaetafjetlepton = array.array('f',[0])
		nbtags_tmva = array.array('f',[0])
		mt_tmva = array.array('f',[0])
		
		spec_njets = array.array('i',[0])
		spec_nfjets = array.array('i',[0])
		spec_evcat = array.array('i',[0])
		spec_svmass = array.array('f',[0])
		spec_fjpt = array.array('f',[0])
		spec_jpt = array.array('f',[0])
		spec_met = array.array('f',[0])

		tmva_reader.AddVariable('abs(JEta)',abs_jeta)
		tmva_reader.AddVariable('abs(FJEta)',abs_fjeta)
		tmva_reader.AddVariable('abs(LEta)',abs_leta)
		tmva_reader.AddVariable('LCharge',lcharge)
		tmva_reader.AddVariable('DeltaEtaJetFJet:=abs(FJEta - JEta)',deltaetajetfjet)
		tmva_reader.AddVariable('DeltaEtaJetLepton:=abs(JEta - LEta)',deltaetajetlepton)
		tmva_reader.AddVariable('DeltaEtaFJetLepton:=abs(FJEta - LEta)',deltaetafjetlepton)
		tmva_reader.AddVariable('NBTags',nbtags_tmva)
		
		tmva_reader.AddSpectator('MT',mt_tmva)
		tmva_reader.AddSpectator('NJets',spec_njets)
		tmva_reader.AddSpectator('NFJets',spec_nfjets)
		tmva_reader.AddSpectator('EvCat',spec_evcat)
		tmva_reader.AddSpectator('SVMass',spec_svmass)
		tmva_reader.AddSpectator('FJPt',spec_fjpt)
		tmva_reader.AddSpectator('JPt',spec_jpt)
		tmva_reader.AddSpectator('MET',spec_met)

		bdtWeightsFile='weights/TMVAClassification_BDT.weights.xml'
		if os.path.isfile(bdtWeightsFile): tmva_reader.BookMVA('BDT',bdtWeightsFile)
		else : raise IOError
	except:
		tmva_reader = None
		print 'Unable to book TMVA reader, BDT will be discarded'

	#loop over events in tree
	for i in xrange(0,SVLInfo.GetEntriesFast()):
		
		SVLInfo.GetEntry(i)
		weight = 1 
		if isData:
			weight = 1
		else:
			weight = SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]
		lumiweight = 1 if isData else SVLInfo.XSWeight*LUMI

		#Reweighting dictionary for single top
		weight_opts = {}
		if 'SingleT' in filename:
			weight_opts = {
				'nominal':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0],
				'puup':SVLInfo.Weight[0]*SVLInfo.Weight[2]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0],
				'pudn':SVLInfo.Weight[0]*SVLInfo.Weight[3]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0],
				'lepselup':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[5]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0],
				'lepseldn':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[6]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0],
				'umetup':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[1]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0],
				'umetdn':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[2]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0],
				'toppt':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]*SVLInfo.Weight[10],
				'topptup':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]*SVLInfo.Weight[7],
				'bfrag':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]*SVLInfo.SVBfragWeight[0],
				'bfragup':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]*SVLInfo.SVBfragWeight[1],
				'bfragdn':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]*SVLInfo.SVBfragWeight[2],
				'bfragp11':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]*SVLInfo.SVBfragWeight[3],
				'bfragpete':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]*SVLInfo.SVBfragWeight[4],
				'bfraglund':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]*SVLInfo.SVBfragWeight[5],
				'jesup':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[1],
				'jesdn':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[2],
				'jerup':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[3],
				'jerdn':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[4],
				'btagup':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[1]*SVLInfo.JESWeight[0],
				'btagdn':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[2]*SVLInfo.JESWeight[0],
				'lesup':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0],
				'lesdn':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0],
				'bfnuup':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]*((SVLInfo.BHadNeutrino==0)*0.984+(SVLInfo.BHadNeutrino==1)*1.048+(SVLInfo.BHadNeutrino==-1)),
				'bfnudn':SVLInfo.Weight[0]*SVLInfo.Weight[1]*SVLInfo.Weight[4]*SVLInfo.METWeight[0]*SVLInfo.BtagWeight[0]*SVLInfo.JESWeight[0]*((SVLInfo.BHadNeutrino==0)*1.012+(SVLInfo.BHadNeutrino==1)*0.988+(SVLInfo.BHadNeutrino==-1))
				}
			
######################################
		#TMVA Definitions - adjust mt and nbtags

		abs_jeta[0] = ROOT.TMath.Abs(SVLInfo.JEta)
		abs_fjeta[0] = ROOT.TMath.Abs(SVLInfo.FJEta)
		abs_leta[0] = ROOT.TMath.Abs(SVLInfo.LEta)
		lcharge[0] = SVLInfo.LCharge
		deltaetajetfjet[0] = ROOT.TMath.Abs(SVLInfo.JEta-SVLInfo.FJEta)
		deltaetajetlepton[0] = ROOT.TMath.Abs(SVLInfo.JEta-SVLInfo.LEta)
		deltaetafjetlepton[0] = ROOT.TMath.Abs(SVLInfo.FJEta-SVLInfo.LEta)
		nbtags_tmva[0] = SVLInfo.NBTags
		mt_tmva[0] = SVLInfo.MT
		spec_njets[0] = SVLInfo.NJets
		spec_nfjets[0] = SVLInfo.NFJets
		spec_evcat[0] = SVLInfo.EvCat
		spec_svmass[0] = SVLInfo.SVMass
		spec_fjpt[0] = SVLInfo.FJPt
		spec_jpt[0] = SVLInfo.JPt
		spec_met[0] = SVLInfo.MET

######################################

		#require e or mu events
		chCat=''
		if ROOT.TMath.Abs(SVLInfo.EvCat)==1100 or ROOT.TMath.Abs(SVLInfo.EvCat)==1300:
			if ROOT.TMath.Abs(SVLInfo.FJEta) <= 20 and SVLInfo.FJPt >= 40 and SVLInfo.JPt >= 40 and ((SVLInfo.NJets+SVLInfo.NFJets) == 2 or (SVLInfo.NJets+SVLInfo.NFJets) == 3) and SVLInfo.SVMass > 0 and SVLInfo.NBTags > 0 and SVLInfo.MT >= 50 and tmva_reader.EvaluateMVA('BDT') < 0.11:
				mvaBDT = tmva_reader.EvaluateMVA('BDT')
				if ROOT.TMath.Abs(SVLInfo.EvCat)==1100 and SVLInfo.MET >= 45:
					if (SVLInfo.NJets+SVLInfo.NFJets) == 2:
						histos['SVLMassQCD_e2j'].Fill(SVLInfo.SVLMass, weight)
						histos['BDToutputQCD_e2j'].Fill(mvaBDT,weight)
					elif (SVLInfo.NJets+SVLInfo.NFJets) == 3:
						histos['SVLMassQCD_e3j'].Fill(SVLInfo.SVLMass, weight)
						histos['BDToutputQCD_e3j'].Fill(mvaBDT,weight)
				elif ROOT.TMath.Abs(SVLInfo.EvCat)==1300:
					if (SVLInfo.NJets+SVLInfo.NFJets) == 2:
						histos['SVLMassQCD_mu2j'].Fill(SVLInfo.SVLMass, weight)
						histos['BDToutputQCD_mu2j'].Fill(mvaBDT,weight)
					elif (SVLInfo.NJets+SVLInfo.NFJets) == 3:
						histos['SVLMassQCD_mu3j'].Fill(SVLInfo.SVLMass, weight)
						histos['BDToutputQCD_mu3j'].Fill(mvaBDT,weight)
				
		if ROOT.TMath.Abs(SVLInfo.EvCat)!=11 and ROOT.TMath.Abs(SVLInfo.EvCat)!=13 : continue
		chCat = 'e' if ROOT.TMath.Abs(SVLInfo.EvCat)==11 else 'mu'

####################################

		#require 1 forward jet
		fwdeta=ROOT.TMath.Abs(SVLInfo.FJEta)
		if fwdeta > 20: continue
		if SVLInfo.FJPt < 40: continue

####################################

		#require at least one high pT central jet, but not more than 2 central jets
		if SVLInfo.JPt < 40 :continue
		if (SVLInfo.NJets+SVLInfo.NFJets) < 2 or (SVLInfo.NJets+SVLInfo.NFJets) > 3: continue
		jetCat="%dj" % (SVLInfo.NJets+SVLInfo.NFJets)

###################################

		#require 1 SecVtx, and re-inforce b-tag requirement
		if SVLInfo.SVMass<=0 : continue
		if SVLInfo.NBTags<=0: continue

###################################

		#re-inforce the cut in MT
		if SVLInfo.MT<50 : continue
		if chCat == 'e' and SVLInfo.MET<45 : continue

###################################

		#Calculate central jet eta
		cjeta=ROOT.TMath.Abs(SVLInfo.JEta)

		#separate into nTracks
#		if SVLInfo.SVNtrk < 1 or SVLInfo.SVNtrk > 5: continue
#		if SVLInfo.SVNtrk == 1:
#			nTrack = '1t'
#		elif SVLInfo.SVNtrk == 2:
#			nTrack = '2t'
#		elif SVLInfo.SVNtrk == 3:
#			nTrack = '3t'
#		elif SVLInfo.SVNtrk == 4:
#			nTrack = '4t'
#		else:
#			nTrack = '5t'

		tag=chCat+jetCat#+nTrack

		#TMVA Cuts (if available)
		mvaBDT=-1
		if tmva_reader:
			mvaBDT = tmva_reader.EvaluateMVA('BDT')
			histos['BDToutputoriginal_'+tag].Fill(mvaBDT,    weight)
		
		if -0.05 <= mvaBDT < 0.11:
			histos['SVLMassWJets_'+tag].Fill(SVLInfo.SVLMass,weight)
		if mvaBDT < 0.11: continue

###################################

		#fill histograms with variables of interest
		if tag=='e2j'  : histos['EventYields'].Fill(0,weight)
		if tag=='mu2j' : histos['EventYields'].Fill(1,weight)
		if tag=='e3j'  : histos['EventYields'].Fill(2,weight)
		if tag=='mu3j' : histos['EventYields'].Fill(3,weight)

		tag1 = ''
		if 'SingleT' in filename:
			tag1+='t_'
		elif ('TT' in filename) and ('TTW' not in filename) and ('TTZ' not in filename) and ('AUET' not in filename):
			tag1+='tt_'
		else:
			tag1+='bg_'
		if 'e2j' in tag:
			tag1+='e2j_'
		elif 'e3j' in tag:
			tag1+='e3j_'
		elif 'mu2j' in tag:
			tag1+='m2j_'
		else:
			tag1+='m3j_'
		tag1+=(mass+'_')
		if 'tt' in tag1:
			tag1+='inc'
		elif 't_' in tag1:
			if SVLInfo.CombInfo==1:
				tag1+='cor'
			else:
				tag1+='wro'
		else:
			tag1+='unm'

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
		histos['NJets_'+tag]  .Fill((SVLInfo.NJets+SVLInfo.NFJets),   weight)
		histos['NBTags_'+tag] .Fill(SVLInfo.NBTags,  weight)
		histos['LPt_'+tag]    .Fill(SVLInfo.LPt,     weight)
		histos['SVLDeltaR_'+tag]   .Fill(SVLInfo.SVLDeltaR,         weight)
		histos['SVNtrk_'+tag] .Fill(SVLInfo.SVNtrk,  weight)
		histos['CombInfo_'+tag].Fill(SVLInfo.CombInfo,  weight)
		histos['BDToutput_'+tag].Fill(mvaBDT,        weight)
		histos[tag1].Fill(SVLInfo.SVLMass,weight)
		tag=chCat+jetCat

		#Fill histos for reweighted signal
		if 'SingleT' in filename:
			for key in weight_opts.keys():
				histos['SVLMass_'+key+'_'+tag].Fill(SVLInfo.SVLMass,weight_opts[key])
		
	#close input file, after analysis
	fIn.Close()

	#dump histograms to ROOT file
	fOut=ROOT.TFile.Open(os.path.join(outDir,os.path.basename(filename)),'RECREATE')
	for h in histos: histos[h].Write()
	print '   output stored in %s' % fOut.GetName()
	fOut.Close()


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
#				print(filename)
		else:
			for filename in os.listdir(args[0]):
				if not os.path.splitext(filename)[1] == '.root': continue	
				isData, pname, splitno = resolveFilename(filename)
				if not pname in treefiles: treefiles[pname] = []
				taskList.append((os.path.join(args[0],filename), isData,options.outDir))
				filenames.append(filename)
#				print(filename)

	except IndexError:
		print "Please provide a valid input directory"
		return -1
	
	#submit tasks in parallel, if required, or run sequentially - comment out to run TMVA optimization
	if opt.jobs>0:
		print ' Submitting jobs in %d threads' % opt.jobs
		import multiprocessing as MP
		pool = MP.Pool(opt.jobs)
		pool.map(runSingleTopAnalysisPacked,taskList)
	else:
		for filename,isData,outDir in taskList:
			runSingleTopAnalysis(filename=filename,isData=isData,outDir=outDir)

	#Run TMVA optimization - comment out to run analysis
#	print('\nEntering code.\n')
#	runTMVAAnalysis(filenames)

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




