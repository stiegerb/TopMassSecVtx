#! /usr/bin/env python
import ROOT
import utils
from array import array
import optparse
import numpy as np
import os,sys
from UserCode.TopMassSecVtx.storeTools_cff import fillFromStore
from makeSVLMassHistos import getMassTrees

"""
useful to list what's in a directory
"""
def getPathToObjects(directory):
    objPath= []
    for key in directory.GetListOfKeys():
        objPath.append('%s/%s' % (directory.GetName(),key.GetName()) )
    return objPath

from UserCode.TopMassSecVtx.PlotUtils import *

"""
Shows the unfolded result and saves histograms to file
"""
def showResult(data,signal,var,outDir):

    outDir= os.path.join(outDir, 'plots')

    #nominal comparison
    varPlot = Plot('%s_unfolded'%var,False)
    varPlot.add(signal,'signal',ROOT.kGray,False)
    varPlot.add(data,  'data',  1,         True)
    varPlot.show(outDir)
    varPlot.appendTo('%s/%s_unfolded.root' % (outDir,var))
    
    #normalized results
    dataPDF=data.Clone('%s_pdf'%data.GetName())
    dataPDF.Scale(1./dataPDF.Integral('width'))
    signalPDF=signal.Clone('%s_pdf'%signal.GetName())
    signalPDF.Scale(1./signal.Integral('width'))
    varPDFPlot = Plot('%sPDF_unfolded'%var,False)
    varPDFPlot.add(signalPDF,'signal',ROOT.kGray,False)
    varPDFPlot.add(dataPDF,  'data',  1,         True)
    varPDFPlot.show(outDir)
    varPDFPlot.appendTo('%s/%s_unfolded.root' % (outDir,var))
    
    #free memory
    varPlot.reset()
    varPDFPlot.reset()

"""
Unfolding cycle
"""
def unfoldVariable(opt):

    histos={}
    
    #open ROOT file
    fIn=ROOT.TFile.Open(opt.root)

    #reconstructed level histograms
    recList       = getPathToObjects(fIn.Get('%s_rec'%(opt.var)))
    for p in recList:
        h=fIn.Get(p)
        hname=h.GetName()
        if 'Data' in hname : 
            histos['data']=h.Clone('data')
        elif 'TTJets' in hname:
            if not 'signal' in histos : 
                histos['signal']=h.Clone('signal')
            else : 
                histos['signal'].Add(h)
        else:
            if not 'bkg' in histos : histos['bkg']=h.Clone('bkg')
            else : histos['bkg'].Add(h)

    #generator level histograms (only signal needed)
    genList       = getPathToObjects(fIn.Get('%s_gen'%(opt.var)))
    for p in genList:
        h=fIn.Get(p)
        hname=h.GetName()
        if 'TTJets' in hname:
            if not 'signal_gen' in histos : 
                histos['signal_gen']=h.Clone('signal_gen')
            else : 
                histos['signal_gen'].Add(h)

    #migration matrix (only signal needed)
    migrationList = getPathToObjects(fIn.Get('%s_migration'%(opt.var)))
    for p in migrationList:
        h=fIn.Get(p)
        hname=h.GetName()
        if 'TTJets' in hname:
            if not 'migration' in histos : 
                histos['migration']=h.Clone('migration')
            else : 
                histos['migration'].Add(h)

    #detach objects from file and close file
    for h in histos: histos[h].SetDirectory(0)
    fIn.Close()

    #dump migration matrix in a root file or use that histogram as migration matrix
    filenamem = 'unfoldResultsRebin/'+opt.var+'/plots/migration_'+opt.var+'_TTJets.root'
    filenamem = '/afs/cern.ch/work/c/cmantill/public/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/unfoldResultsRebin/ptpos/plots/migration_ptpos_TTJets.root'
    #dump migration matrix in a root file to test it
    #filenamem = 'results_test/ptpos/169/migration_ptpos169_SingleT.root'
    #fOut=ROOT.TFile.Open(filenamem,'RECREATE')
    #histos['migration'].Write()
    #print 'Migration histograms saved in %s' % filenamem
    #fOut.Close()

    # Get migration matrix from 172v5 samples
    fInp=ROOT.TFile.Open(filenamem)       
    hmist=ROOT.TH2D() 
    hmist=fInp.Get("migration")
    hmist.SetDirectory(0)
    fInp.Close()

    # Save matrix to check if it is reading correctly
    #filenamet='results_test/ptpos/171/migration_ptpos_TTJets_rebin.root'
    #fOut=ROOT.TFile.Open(filenamet,'RECREATE')
    #hmist.Write()
    #print 'Migration histograms saved in %s'%(filenamet)
    #fOut.Close()

    #
    # UNFOLDING STEP
    # TUnfoldSys provides methods to do systematic error propagation and to do unfolding with background subtraction
    # Regularization of curvature (TUnfold::kRegModeCurvature) is the least intrusive
    # but you can choose one of the other modes or give your own regularization conditions 
    # if this doesn't fit your needs cf. http://root.cern.ch/root/html/TUnfold.html
    #

    # Use migration matrix from each mass sample
    #tunfold=ROOT.TUnfoldSys(histos['migration'], ROOT.TUnfold.kHistMapOutputHoriz, ROOT.TUnfold.kRegModeCurvature)
    
    # Use migration matrix read from filenamem
    hmist=hmist.RebinX()
    tunfold=ROOT.TUnfoldSys(hmist, ROOT.TUnfold.kHistMapOutputHoriz, ROOT.TUnfold.kRegModeCurvature,ROOT.TUnfold.kEConstraintNone)

    # define the data histogram to be unfolded
    tunfold.SetInput(histos['signal'])
    
    # Set a "bias" distribution, i.e. your MC truth distribution
    # corresponding to what you expect to see after unfolding.
    tunfold.SetBias(histos['signal_gen'])

    # Scale factor for the "bias" distribution. 
    # Choose such that normalization will correspond to expected normalization of result. 
    # For example, a simple approximation could be using expectedNUnfolded = n_data / ttbar_selection_efficiency
    # const double scaleBias = expectedNUnfolded / histogram_with_mc_truth->Integral();
    scaleBias = 1.0

    #background subtraction
    bkgScale, bkgUnc = 1.0, 0.15
    tunfold.SubtractBackground(histos['bkg'], "bkg", bkgScale, bkgUnc)

    for name in ['signal','signal_gen','bkg','migration']:
        print histos[name].GetXaxis().GetNbins(),histos[name].GetYaxis().GetNbins()
    raw_input()


    # Regularization parameter, giving the strength of regularization. Will be roughly on the order of 1e-4.
    # You can determine this by performing unfolding with many different values, 
    # for example between 1e-3 and 1e-7 or such, and choosing that value of tau that minimizes tunfold.GetRhoAvg()
    # A different method would be to simply use tunfold.ScanLcurve(..), but this has proven far less reliable.
    # If the regularisation is strong, i.e. large parameter tau,
    # then the distribution x or its derivatives will look like the "bias" (mc truth) distribution. 
    # If the parameter tau is small, the distribution x is independent of the bias but will exhibit
    # many fluctuations and the high correlations between the bins.
    # Another way of crosschecking the tau parameter tuning is to look at the uncertainty of the bins after unfolding:
    # In absence of regularization they will be equal to the statistical (poisson) uncertainty
    # (which is the minimum error "possible", without considering correlations)
    # while introducing the regularization they will become a bit higher, due to the correlations,
    # but "not too much".
    tau=1e-4

    #regularization parameter
    tunfold.DoUnfold(tau, histos['signal'], scaleBias)

    #get the unfolded distribution
    data_unfolded=histos['signal_gen'].Clone('data_unfolded')
    data_unfolded.Reset('ICE')
    tunfold.GetOutput(data_unfolded)

    #divide contents by bin width
    for xbin in xrange(1,data_unfolded.GetXaxis().GetNbins()+1):
        binWidth=data_unfolded.GetXaxis().GetBinWidth(xbin)
        for h in [ data_unfolded, histos['signal_gen'] ] :
            h.SetBinContent(xbin,h.GetBinContent(xbin)/binWidth)
            h.SetBinError(xbin,h.GetBinError(xbin)/binWidth)

    #show result
    showResult(data=data_unfolded,
               signal=histos['signal_gen'],
               var=opt.var,
               outDir=opt.output)

"""
Returns histograms to be filled in the loop, depending on the distribution variable you chose to work with
"""
def getAnalysisHistograms(var,bins_gen,bins_rec) :
    histos={}

    #pT positive lepton
    if var == 'ptpos': 
        title = ';p_{T}(l^{+}) [GeV];Events'
        title_mig = ';Reconstructed p_{T}(l^{+}) [GeV];Generated p_{T}(l^{+}) [GeV];Events'
  
    #pT charged-lepton pair
    if var == 'ptll': 
        title = ';p_{T}(l^{+}l^{-}) [GeV];Events'
        title_mig = ';Reconstructed p_{T}(l^{+}l^{-}) [GeV];Generated p_{T}(l^{+}l^{-}) [GeV];Events'

    #M charged-lepton pair
    if var == 'mll': 
        title = ';M(l^{+}l^{-}) [GeV];Events'
        title_mig = ';Reconstructed M(l^{+}l^{-}) [GeV];Generated M(l^{+}l^{-}) [GeV];Events'

    #Scalar sum of E
    if var == 'EposEm': 
        title = ';E(l^{+})+E(l^{-}) [GeV];Events'
        title_mig = ';Reconstructed E(l^{+})+E(l^{-}) [GeV];Generated E(l^{+})+E(l^{-}) [GeV];Events'
    
    #Scalar sum of Pt
    if var == 'ptposptm': 
        title = ';p_{T}(l^{+})+p_{T}(l^{-}) [GeV];Events'
        title_mig = ';Reconstructed p_{T}(l^{+})+p_{T}(l^{-}) [GeV];Generated p_{T}(l^{+})+p_{T}(l^{-}) [GeV];Events'

    # Labeling histograms
    rec = var+'_rec'
    wgt = rec+'_wgt'
    gen = var+'_gen'
    mig = var+'_migration'

    # Declaring histos
    histos[rec]=ROOT.TH1F(rec,title,len(bins_rec)-1,array('d',bins_rec))
    histos[wgt]=ROOT.TH1F(wgt,title,len(bins_rec)-1,array('d',bins_rec))
    histos[gen]=ROOT.TH1F(gen,title,len(bins_gen)-1,array('d',bins_gen))
    histos[mig]=ROOT.TH2F(mig,title_mig,len(bins_gen)-1,array('d',bins_gen),len(bins_rec)-1,array('d',bins_rec))

    for h in histos:
        histos[h].Sumw2()
        histos[h].SetDirectory(0)

    return histos

"""
Loop over a tree and fill histograms you declared before
If q is True, you get the quantiles from your histograms returned in an array, q_gen or q_rec depending on your histogram
It could also work to return the quantiles from just one of the histograms - see commented lines
"""
def createHistos(var,filename,isData,histos,q):
    
    #Getting histograms labeling
    rec = var+'_rec'
    wgt = rec+'_wgt'
    gen = var+'_gen'
    mig = var+'_migration'
    
    #open file
    fIn=ROOT.TFile.Open(filename)
    
    #loop over events in the tree and fill histos
    tree=fIn.Get('DileptonInfo')
    for i in xrange(0,tree.GetEntriesFast()):
        tree.GetEntry(i)

        #select only emu events
        if tree.EvCat != -11*13 : continue
        if not isData: 
           if tree.GenLpPt == 0 or tree.GenLmPt == 0: continue

        #base weight: BR fix for ttbar x pileup x lepton selection x xsec weight
        baseWeight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4] #*tree.XSWeight
                        
        #event weight
        weight = 1 if isData else baseWeight
        
        #positive lepton
        lp=ROOT.TLorentzVector()
        lp.SetPtEtaPhiM(tree.LpPt,tree.LpEta,tree.LpPhi,0.)
        glp=ROOT.TLorentzVector()
        glp.SetPtEtaPhiM(tree.GenLpPt,tree.GenLpEta,tree.GenLpPhi,0.)

        #negative lepton
        lm=ROOT.TLorentzVector()
        lm.SetPtEtaPhiM(tree.LmPt,tree.LmEta,tree.LmPhi,0.)       
        glm=ROOT.TLorentzVector()
        glm.SetPtEtaPhiM(tree.GenLmPt,tree.GenLmEta,tree.GenLmPhi,0.)

        #charged lepton pair - pt
        ll=ROOT.TLorentzVector()
        ll = lp + lm
        gll=ROOT.TLorentzVector()
        gll = glp + glm

        #fill the histograms according to the distrubution variable
        #pT positive lepton
        if var == 'ptpos': 
            histos[rec].Fill(lp.Pt(),weight)
            binWidth = histos[wgt].GetXaxis().GetBinWidth(histos[wgt].GetXaxis().FindBin(lp.Pt() ) )
            histos[wgt].Fill(lp.Pt(),weight/binWidth)
            if not isData:
                    histos[gen].Fill(glp.Pt(),weight)
                    histos[mig].Fill(glp.Pt(),lp.Pt(),weight)

        #Second distribution: Pt(l+l-) = ll.Pt      
        if var == 'ptll': 
            histos[rec].Fill(ll.Pt(),weight)
            binWidth = histos[wgt].GetXaxis().GetBinWidth(histos[wgt].GetXaxis().FindBin(ll.Pt() ) )
            histos[wgt].Fill(ll.Pt(),weight/binWidth)
            if not isData:
                    histos[gen].Fill(gll.Pt(),weight)
                    histos[mig].Fill(gll.Pt(),ll.Pt(),weight)

        #Third distribution: M(l+l-) = ll.M
        if var == 'mll': 
            histos[rec].Fill(ll.M(),weight)
            binWidth = histos[wgt].GetXaxis().GetBinWidth(histos[wgt].GetXaxis().FindBin(ll.M() ) )
            histos[wgt].Fill(ll.M(),weight/binWidth)
            if not isData:
                    histos[gen].Fill(gll.M(),weight)
                    histos[mig].Fill(gll.M(),ll.M(),weight)

        #Fourth distribution: E(l+)+E(l-) = lp.E() + lm.E()
        if var == 'EposEm': 
            histos[rec].Fill(lp.E() + lm.E(),weight)
            binWidth = histos[wgt].GetXaxis().GetBinWidth(histos[wgt].GetXaxis().FindBin(lp.E() + lm.E() ) )
            histos[wgt].Fill(lp.E() + lm.E(),weight/binWidth)
            if not isData:
                    histos[gen].Fill(glp.E() + glm.E(),weight)
                    histos[mig].Fill(glp.E() + glm.E(),lp.E() + lm.E(),weight)

        #Fifth distribution: Pt(l+)+Pt(l-) = lp.Pt() + lm.Pt()
        if var == 'ptposptm': 
            histos[rec].Fill(lp.Pt() + lm.Pt(),weight)
            binWidth = histos[wgt].GetXaxis().GetBinWidth(histos[wgt].GetXaxis().FindBin(lp.Pt() + lm.Pt() ) )
            histos[wgt].Fill(lp.Pt() + lm.Pt(),weight/binWidth)
            if not isData:
                    histos[gen].Fill(glp.Pt() + glm.Pt(),weight)
                    histos[mig].Fill(glp.Pt() + glm.Pt(),lp.Pt() + lm.Pt(),weight)

    #close file
    fIn.Close()

    # Gets quantiles from histos if q is True
    # GetQuantiles just works for TH1 not TH2, therefore h != migration
    if q == True:
        #print 'Getting quantiles from %s' %filename
        for h in histos:
            if h == gen:
                q_gen=[]
                q_gen=utils.quantiles(histos[h])
                #print 'quantiles lenght for gen %s' %len(q_gen)
                #for i in xrange(0,len(q_gen)): print q_gen[i]

                #there should be an easier way to rebin the histograms just using the function rebin that I defined in utils.py but it doesn't seem to be working
                #histos[h]=utils.rebin(hist,q_gen[h])
            
            #if h == wgt or h == rec:
            if h == rec:    
                q_rec=[]
                q_rec=utils.quantiles(histos[h])
                for i in xrange(0,len(q_rec)): print q_rec[i]

        return q_gen,q_rec

"""
Create histograms, get quantiles and re run histograms
Used to get the quantiles from each sample
"""
def createSummary(bins_gen,bins_rec,var,filename,isData,outDir):
    
    #define histograms
    histos=getAnalysisHistograms(var,bins_gen,bins_rec)
    
    #getting quantiles option    
    q = True
    
    #filling histograms and getting quantiles array
    bins_gen_b,bins_rec_b=createHistos(var,filename,isData,histos,q)
    
    #define histograms with new binning
    binhistos = getAnalysisHistograms(var,bins_gen_b,bins_rec_b)
    
    q = False
    #filling histograms with new binning
    createHistos(var,filename,isData,binhistos,q)

    #dump histograms to a file
    fOut=ROOT.TFile.Open(os.path.join(outDir,os.path.basename(filename)),'RECREATE')
    for h in binhistos: binhistos[h].Write()
    print 'Histograms saved in %s' % fOut.GetName()
    fOut.Close()
 
"""
Wrapper for when the analysis is run in parallel
Also creates histograms, get quantiles from just one file and re run histograms
"""
def createSummaryPacked(args):
    var,filename,isData,outDir = args
    try:
        #labeling
        rec = var+'_rec'
        wgt = var+'_wgt'
        gen = var+'_gen'
        mig = var+'_migration'

        # to get quantiles just for one file e.g. Data8TeV_MuEG2012A - lots of hardcoding :/

        # define histograms according to the distribution variable opt.var and according to the quantiles if you've already got them
        #bins_gen=[0,20,40,60,80,100,120,140,160,180,200]
        
        # binning defined using the quantiles
        #pT positive lepton
        if var == 'ptpos': bins_gen=[20,24,28,32,36,40,44,48,52,60,68,76,84,92,100,120,140,160,180]
   
        #pT charged-lepton pair
        if var == 'ptll': bins_gen=[10,20,30,36,42,48,52,56,60,65,70,75,80,85,90,100,110,130,150,198]

        #M charged-lepton pair
        if var == 'mll': bins_gen=[20,30,40,48,56,68,74,80,86,93,100,115,130,145,165,195,235,275,375]
   
        #Scalar sum of E
        if var == 'EposEm': bins_gen=[55,75,87,99,111,122,131,140,149,160,170,180,190,205,225,250,275,375,475]

        #Scalar sum of Pt        
        if var == 'ptposptm': bins_gen=[40,56,64,72,80,88,96,102,107,113,119,127,137,147,163,187,205,235,250]

        # define bins_rec using bins_gen 
        bins_rec=bins_gen
        #bins_rec=[]
        #for i in xrange(0,len(bins_gen)):
        #        bins_rec.append(bins_gen[i]+0.5)
        #        if i<len(bins_gen)-1:
        #                bins_rec.append(bins_gen[i+1]+0.5)
        #        else:
        #                bins_rec.append(bins_gen[-1]+50)

        # this wraps it up and get histograms rebinned with the quantiles respectively

        # analysis of just one file
        '''
        if 'Data8TeV_MuEG2012A' in filename: 
            
            #define histograms
            histos={}
            histos[rec]=ROOT.TH1F(rec,'test',100,0,200)
            histos[wgt]=ROOT.TH1F(wgt,'test',100,0,200)
            histos[gen]=ROOT.TH1F(gen,'test',100,0,200)
            histos[mig]=ROOT.TH2F(mig,'test',100,0,200,100,0,200)

            #get quantiles arrays bins_gen_b and bins_rec_b
            q = True
            bins_gen_b,bins_rec_b=createHistos(var,filename,isData,histos,q)
            print 'lenght %s' %len(bins_rec_b)
            #for i in xrange(0,len(bins_rec_b)): print bins_rec_b[i]

            #dump histograms just for this file in the outDir
            fOut=ROOT.TFile.Open(os.path.join(outDir,os.path.basename(filename)),'RECREATE')
            for h in histos: histos[h].Write()
            print 'Histograms saved in %s' % fOut.GetName()
            fOut.Close()
        '''
        # to get histograms with the binning defined according to the quantiles obtained
        #'''
        #define histograms
        binhistos = getAnalysisHistograms(var,bins_gen,bins_rec)
        q = False

        #filling histograms with new binning
        createHistos(var,filename,isData,binhistos,q)

        #dump histograms in a file
        fOut=ROOT.TFile.Open(os.path.join(outDir,os.path.basename(filename)),'RECREATE')
        for h in binhistos: binhistos[h].Write()
        print 'Histograms saved in %s' % fOut.GetName()
        fOut.Close()
        #'''

    except ReferenceError:
        print 50*'<'
        print "  Problem with", name, "continuing without"
        print 50*'<'
        return False
    
"""
Create summary distributions to unfold
"""
def createSummaryTasks(opt):

    #get files from directory
    tasklist=[]
    if opt.ma == False:
        if opt.input.find('/store')>=0:
            for filename in fillFromStore(opt.input):
                if not os.path.splitext(filename)[1] == '.root': continue   
                isData = True if 'Data' in filename else False
                tasklist.append((opt.var,filename,isData,opt.output))
        else:
            for filename in os.listdir(args[0]):
                if not os.path.splitext(filename)[1] == '.root': continue   
                isData = True if 'Data' in filename else False
                tasklist.append((opt.var,filename,isData,opt.output))

        #loop over tasks
        if opt.jobs>0:
            print ' Submitting jobs in %d threads' % opt.jobs
            import multiprocessing as MP
            pool = MP.Pool(opt.jobs)
            pool.map(createSummaryPacked,tasklist)
        else:
            for var,filename,isData,outDir in tasklist:
                createSummary(var=var,filename=filename,isData=isData,outDir=outDir)
    else:
        #masstrees, massfiles = getMassTrees(opt.input, verbose=True)
        #masspoints = sorted(list(set([mass for mass,_ in masstrees.keys()])))
    
        # Create an array with the different masses
        mass = [166, 169, 171, 173, 175, 178]

        # A bit of hardcoding until I understand Benjamin's code
        for m in mass:
	    print m
      	    m = str(m)
            output = opt.output + m
            os.system('mkdir -p %s' % output)
            print 'Creating new directory'
            for filename in fillFromStore(opt.input):
                direct = 'root://eoscms//eos/cms/store/cmst3/group/top/summer2015/treedir_bbbcb36/ttbar/mass_scan/'
                if not (filename == direct+'MC8TeV_SingleT_tW_'+m+'v5.root' or
                        filename == direct+'MC8TeV_SingleT_t_'+m+'v5.root' or
                        filename == direct+'MC8TeV_SingleTbar_tW_'+m+'v5.root' or
                        filename == direct+'MC8TeV_SingleTbar_t_'+m+'v5.root' or
                        filename == direct+'MC8TeV_TTJets_'+m+'v5.root' or
                        filename == direct+'MC8TeV_TTJets_MSDecays_'+m+'v5.root'):
                    continue
		print 'Going to analyze %s' %filename  
                isData = True if 'Data' in filename else False
                tasklist.append((opt.var,filename,isData,output))

            print ' Submitting jobs in %d threads for %s' % (opt.jobs,m)
            import multiprocessing as MP
            pool = MP.Pool(opt.jobs)
            pool.map(createSummaryPacked,tasklist)			
	return 0

"""
steer
"""
def main():
	usage = 'usage: %prog [options]'
	parser = optparse.OptionParser(usage)
	parser.add_option('-i', '--input',
                          dest='input',   
                          default='/afs/cern.ch/user/p/psilva/work/Top/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/treedir_d0827e4', 
                          help='input directory with the files [default: %default]')
	parser.add_option('-r', '--root',
                          dest='root', 
                          default=None,
                          help='ROOT file with distributions to unfold [default: %default]')
	parser.add_option('-v', '--var',
                          dest='var', 
                          default='ptpos',
                          help='Variable to unfold (note requires var_rec,var_gen,var_migration plots stored in the ROOT file [default: %default]')
	parser.add_option('--jobs',
                          dest='jobs', 
                          default=1,
                          type=int,
                          help='# of jobs to process in parallel the trees [default: %default]')
        parser.add_option('--mass',
                          dest='mass', 
                          default=None,
                          type=int,
                          help='mass [default: %default]')
        parser.add_option('-m',
                          dest='ma', 
                          default=False,
                          help='Take information from mass files [default: %default]')
	parser.add_option('-o', '--output',
                          dest='output', 
                          default='unfoldResults',                                                                       
                          help='Output directory [default: %default]')

    #parser.add_option('-m', '--mass', dest='mass', default='None', help='Mass files [default: %default]')
	(opt, args) = parser.parse_args()

	ROOT.gStyle.SetOptStat(0)
	ROOT.gStyle.SetOptTitle(0)
	ROOT.gROOT.SetBatch(True)
	setTDRStyle()
        ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
	ROOT.AutoLibraryLoader.enable()
	os.system('mkdir -p %s' % opt.output)

	# Check if one needs to create a new workspace or run pseudo-experiments	
	if opt.root is None :
             print 80*'-'
             print 'Creating ROOT file with migration matrices, data and background distributions of %s from %s'%(opt.var,opt.input)
             createSummaryTasks(opt)
             print 80*'-'
        else:
             print 80*'-'
             print 'Unfolding variable %s from %s'%(opt.var,opt.root)
             unfoldVariable(opt)
             print 80*'-'
        return 0

if __name__ == "__main__":
	sys.exit(main())
