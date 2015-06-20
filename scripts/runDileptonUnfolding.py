import ROOT
from array import array
import optparse
import os,sys
from UserCode.TopMassSecVtx.storeTools_cff import fillFromStore

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
        elif 'TTJets' in hname or 'SingleT' in hname:
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
        if 'TTJets' in hname or 'SingleT' in hname:
            if not 'signal_gen' in histos : 
                histos['signal_gen']=h.Clone('signal_gen')
            else : 
                histos['signal_gen'].Add(h)

    #migration matrix (only signal needed)
    migrationList = getPathToObjects(fIn.Get('%s_migration'%(opt.var)))
    for p in migrationList:
        h=fIn.Get(p)
        hname=h.GetName()
        if 'TTJets' in hname or 'SingleT' in hname:
            if not 'migration' in histos : 
                histos['migration']=h.Clone('migration')
            else : 
                histos['migration'].Add(h)
                
    #detach objects from file and close file
    for h in histos : histos[h].SetDirectory(0)
    fIn.Close()
                    
    #
    # UNFOLDING STEP
    # TUnfoldSys provides methods to do systematic error propagation and to do unfolding with background subtraction
    # Regularization of curvature (TUnfold::kRegModeCurvature) is the least intrusive
    # but you can choose one of the other modes or give your own regularization conditions 
    # if this doesn't fit your needs cf. http://root.cern.ch/root/html/TUnfold.html
    #
    tunfold=ROOT.TUnfoldSys(histos['migration'], ROOT.TUnfold.kHistMapOutputHoriz, ROOT.TUnfold.kRegModeCurvature)

    # define the data histogram to be unfolded
    tunfold.SetInput(histos['data'])
    
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
    tunfold.DoUnfold(tau, histos['data'], scaleBias);

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
Returns histograms to be filled in the loop
"""
def getAnalysisHistograms() :

    histos={}

    #pT positive lepton
    bins_ptpos_gen=[20,25,30,35,40,45,50,55,60,65,70,80,90,100,125,150,200]
    bins_ptpos_rec=[]
    for i in xrange(0,len(bins_ptpos_gen)):
        bins_ptpos_rec.append(bins_ptpos_gen[i]+0.5)
        if i<len(bins_ptpos_gen)-1:
            bins_ptpos_rec.append(bins_ptpos_gen[i+1]+0.5)
        else:
            bins_ptpos_rec.append(bins_ptpos_gen[-1]+50)
    histos['ptpos_rec']=ROOT.TH1F('ptpos_rec',';p_{T}(l^{+}) [GeV];Events',len(bins_ptpos_rec)-1,array('d',bins_ptpos_rec))
    histos['ptpos_rec_wgt']=ROOT.TH1F('ptpos_rec_wgt',';p_{T}(l^{+}) [GeV];Events',len(bins_ptpos_rec)-1,array('d',bins_ptpos_rec))
    histos['ptpos_gen']=ROOT.TH1F('ptpos_gen',';p_{T}(l^{+}) [GeV];Events',len(bins_ptpos_gen)-1,array('d',bins_ptpos_gen))
    histos['ptpos_migration']=ROOT.TH2F('ptpos_migration',
                                        ';Reconstructed p_{T}(l^{+}) [GeV];Generated p_{T}(l^{+}) [GeV];Events',
                                        len(bins_ptpos_gen)-1,array('d',bins_ptpos_gen),len(bins_ptpos_rec)-1,array('d',bins_ptpos_rec))
    for h in histos:
        histos[h].Sumw2()
        histos[h].SetDirectory(0)

    return histos


"""
Loop over a tree and create histograms
"""
def createSummary(filename,isData,outDir):
    
    #define histograms
    histos=getAnalysisHistograms()
    
    #open file
    fIn=ROOT.TFile.Open(filename)
    
    #loop over events in the tree and fill histos
    tree=fIn.Get('DileptonInfo')
    for i in xrange(0,tree.GetEntriesFast()):
        tree.GetEntry(i)

        #select only emu events
        if tree.EvCat != -11*13 : continue
            
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

        #fill the histograms
        histos['ptpos_rec'].Fill(lp.Pt(),weight)
        binWidth=histos['ptpos_rec_wgt'].GetXaxis().GetBinWidth( histos['ptpos_rec_wgt'].GetXaxis().FindBin(lp.Pt() ) )
        histos['ptpos_rec_wgt'].Fill(lp.Pt(),weight/binWidth)
        if not isData:
            histos['ptpos_gen'].Fill(glp.Pt(),weight)
            histos['ptpos_migration'].Fill(glp.Pt(),lp.Pt(),weight)

    #close file
    fIn.Close()
    
    #dump histograms to file
    fOut=ROOT.TFile.Open(os.path.join(outDir,os.path.basename(filename)),'RECREATE')
    for h in histos: histos[h].Write()
    print 'Histograms saved in %s' % fOut.GetName()
    fOut.Close()


"""
Wrapper for when the analysis is run in parallel
"""
def createSummaryPacked(args):
    filename,isData,outDir = args
    try:
        return createSummary(filename=filename,isData=isData,outDir=outDir)
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
    if opt.input.find('/store')>=0:
        for filename in fillFromStore(opt.input):
            if not os.path.splitext(filename)[1] == '.root': continue	
            isData = True if 'Data' in filename else False
            tasklist.append((filename,isData,opt.output))
    else:
        for filename in os.listdir(args[0]):
            if not os.path.splitext(filename)[1] == '.root': continue	
            isData = True if 'Data' in filename else False
            tasklist.append((filename,isData,opt.output))

    #loop over tasks
    if opt.jobs>0:
        print ' Submitting jobs in %d threads' % opt.jobs
        import multiprocessing as MP
        pool = MP.Pool(opt.jobs)
        pool.map(createSummaryPacked,tasklist)
    else:
        for filename,isData,outDir in tasklist:
            createSummary(filename=filename,isData=isData,outDir=outDir)
			
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
	parser.add_option('-o', '--output',
                          dest='output', 
                          default='unfoldResults',                                                                       
                          help='Output directory [default: %default]')
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
            print 'Creating ROOT file with migration matrices, data and background distributions from %s'%opt.input
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
