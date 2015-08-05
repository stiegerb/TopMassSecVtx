#!/usr/bin/env python
import ROOT
import os,sys
import os.path as osp
import optparse
import pickle

from UserCode.TopMassSecVtx.PlotUtils import printProgress, bcolors
from runSVLPseudoExperiments import PseudoExperimentResults, showFinalFitResult, submitBatchJobs
from runSVLSingleTopFits import CHANNELS

def runPseudoExperiments(wsfile, pefile, experimentTag, options):
    """
    Run the Pseudo-experiments.
    wsfile is the root file containing the RooFit workspace created by
           the runSVLSingleTopFit.py script
    pefile is the root file containing the input histograms to use for
           generating pseudo data
    experimentTag is the name of the variation to pick from the pefile
    """

    # Read the file with input distributions
    inputDistsF = ROOT.TFile.Open(pefile, 'READ')
    prepend = '[runPseudoExperiments %s] ' % experimentTag
    print prepend+'Reading PE input from %s' % pefile
    print prepend+'with %s' % experimentTag

    # Retrieve the workspace
    wsInputFile = ROOT.TFile.Open(wsfile, 'READ')
    ws = wsInputFile.Get('w')
    wsInputFile.Close()
    print prepend+'Read workspace from %s' % wsfile

    # Readout calibration from a file
    calibMap=None
    if options.calib:
         cachefile = open(options.calib,'r')
         calibMap  = pickle.load(cachefile)
         cachefile.close()
         print prepend+'Read calibration from %s'%options.calib

    # Extract generated top mass
    genMtop = 172.5
    try:
        genMtop = float(experimentTag.split('_')[2]) # either mass_check_172_e2j or syst_toppt_mu2j_e2j, etc.
        genMtop += 0.5
    except ValueError: pass
    except IndexError: pass
    print prepend+'Generated top mass is %5.1f GeV'%genMtop

    # Prepare results summary
    summary = PseudoExperimentResults(genMtop = genMtop,
                                      outFileUrl = osp.join(options.outDir,
                                                        '%s_results.root'%(experimentTag)),
                                      statuncrange=(0,3.0),
                                      dmrange=(-10,10),
                                      murange=(0.70,1.30))

    # Load the model parameters and set all to constant
    ws.loadSnapshot("model_params")
    allVars = ws.allVars()
    varIter = allVars.createIterator()
    var = varIter.Next()
    varCtr = 0
    while var:
        varName=var.GetName()
        if not varName in ['mtop', 'SVLMass', 'mu']:
            ws.var(varName).setConstant(True)
            varCtr+=1
        var = varIter.Next()
    print prepend+'setting to constant %d numbers in the model'%varCtr

    # Build the relevant PDFs
    allPdfs = {}
    for chan in CHANNELS: # ['e2j', 'm2j']
        texp       = '%s_t'  %(chan)
        tPDF       = 'simplemodel_%s_t'  %(chan)
        ttfrac     = '%s_ttfrac'         %(chan)
        ttPDF      = 'simplemodel_%s_tt' %(chan)
        bkgExp     = '%s_bgexp'          %(chan)
        bkgPDF     = 'model_%s_bg'   %(chan)

        # Construct number of expected events in single top and ttbar
        Nt  = ws.factory("RooFormulaVar::Nt_%s('@0*@1',{mu,%s})"%(chan,texp)) # mu * Nt
        Ntt = ws.factory("RooFormulaVar::Ntt_%s('@0*@1*@2',{mu,%s,%s})"%(chan,texp,ttfrac)) # mu * Nt * ttfrac

        bkgConstPDF = ws.factory('Gaussian::bgprior_%s('
                                     'bg0_%s[0,-10,10],'
                                     'bg_nuis_%s[0,-10,10],1.0)'%(chan,chan,chan))
        ws.var('bg0_%s'%(chan)).setVal(0.0)
        ws.var('bg0_%s'%(chan)).setConstant(True)

        # 30% uncertainty on background
        Nbkg =  ws.factory("RooFormulaVar::Nbkg_%s('@0*max(1+0.30*@1,0.)',{%s,bg_nuis_%s})"%(chan,bkgExp,chan))

        # print '[Expectation] %2s, %d: %8.2f' % (chan, ntrk, Ntt.getVal()+Nt.getVal()+Nbkg.getVal())

        #see syntax here https://root.cern.ch/root/html/RooFactoryWSTool.html#RooFactoryWSTool:process
        sumPDF = ws.factory("SUM::uncalibexpmodel_{chan}("
                                  "Nt_{chan}*{tPDF}, "
                                  "Ntt_{chan}*{ttPDF}, "
                                  "Nbkg_{chan}*{bkgPDF} )"
                                       .format(chan=chan, tPDF=tPDF,
                                               ttPDF=ttPDF, bkgPDF=bkgPDF))
        ws.factory('PROD::uncalibmodel_%s(%s,%s)'%(chan, sumPDF.GetName(),
                                                   bkgConstPDF.GetName()))

        #add calibration for this category if available (read from a pickle file)
        offset, slope = 0.0, 1.0
        if calibMap:
            try:
                offset, slope = calibMap[chan]
            except KeyError, e:
                print 'Failed to retrieve calibration with',e
        ws.factory("RooFormulaVar::calibmtop_%s('(@0-%f)/%f',{mtop})"%(chan,offset,slope))
        allPdfs[(chan)] = ws.factory("EDIT::model_{chan}(uncalibmodel_{chan},mtop=calibmtop_{chan})".format(chan=chan))

    #throw pseudo-experiments
    poi = ROOT.RooArgSet( ws.var('mtop') )
    if options.verbose>1:
        print prepend+'Running %d experiments' % options.nPexp
        print 80*'-'

    # if not 'nominal' in experimentTag:
    #     cfilepath = osp.abspath(osp.join(osp.dirname(wsfile),'../../'))
    #     cfilepath = osp.join(cfilepath, ".svlsysthistos.pck")
    #     cachefile = open(cfilepath, 'r')
    #     systhistos = pickle.load(cachefile)
    #     print prepend+'>>> Read systematics histograms from cache (.svlsysthistos.pck)'
    #     cachefile.close()

    for i in xrange(0,options.nPexp):

        #iterate over available categories to build the set of likelihoods to combine
        nllMap={}
        allPseudoDataH=[]
        allPseudoData=[]
        if options.verbose>1 and options.verbose<=3:
            printProgress(i, options.nPexp, prepend+' ')

        for chan in CHANNELS:
            if options.verbose > 3:
                sys.stdout.write(prepend+'Exp %-3d (%-2s):' % (i+1, chan))
                sys.stdout.flush()

            ws.var('mtop').setVal(172.5)
            ws.var('mu').setVal(1.0)

            # Read histogram and generate random data
            ihist = inputDistsF.Get('%s_%s'%(experimentTag,chan))
            if experimentTag.startswith('syst'):
                print '###########################'
                print 'syst input histograms are ambiguous'
                print '###########################'
                return -1

            nevtsSeed = ihist.Integral()
            nevtsToGen = ROOT.gRandom.Poisson(nevtsSeed)


            pseudoData = None
            pseudoDataH = ihist.Clone('peh')
            if options.nPexp > 1:
                pseudoDataH.Reset('ICE')
                pseudoDataH.FillRandom(ihist, nevtsToGen)
            else:
                print 'Single pseudo-experiment won\'t be randomized'
            pseudoData  = ROOT.RooDataHist('PseudoData_%s_%s'%(experimentTag,chan),
                                           'PseudoData_%s_%s'%(experimentTag,chan),
                                           ROOT.RooArgList(ws.var('SVLMass')), pseudoDataH)

            if options.verbose>3:
                sys.stdout.write(' [generated pseudodata]')
                sys.stdout.flush()

            # Create likelihood
            # Store it in the appropriate categories for posterior combination
            if not ('comb' in nllMap): nllMap['comb'] = []
            nllMap['comb'].append( allPdfs[chan].createNLL(pseudoData, ROOT.RooFit.Extended()) )

            if options.verbose>3:
                sys.stdout.write(' [running Minuit]')
                sys.stdout.flush()
            minuit = ROOT.RooMinuit(nllMap['comb'][-1])
            minuit.setErrorLevel(0.5)
            minuit.migrad()
            minuit.hesse()
            minuit.minos(poi)

            # Save fit results
            summary.addFitResult(key=chan, ws=ws)

            # Show, if required
            if options.spy and i==0:
                pll=nllMap['comb'][-1].createProfile(poi)
                showFinalFitResult(data=pseudoData,pdf=allPdfs[key], nll=[pll,nllMap['comb'][-1]],
                                   SVLMass=ws.var('SVLMass'),mtop=ws.var('mtop'),
                                   outDir=options.outDir,
                                   tag=["%s channel"%(chan)])

            # Save to erase later
            if pseudoDataH : allPseudoDataH.append(pseudoDataH)
            allPseudoData.append(pseudoData)
            if options.verbose > 3:
                sys.stdout.write('%s DONE %s'
                                 '(mt: %6.2f+-%4.2f GeV, '
                                  'mu: %4.2f+-%4.2f)\n'%
                                (bcolors.OKGREEN,bcolors.ENDC,
                                 ws.var('mtop').getVal(), ws.var('mtop').getError(),
                                 ws.var('mu').getVal(), ws.var('mu').getError()) )
                sys.stdout.flush()

        # Combined likelihoods
        if options.verbose>3:
            sys.stdout.write(prepend+'[combining %d channels] '%len(CHANNELS))
            sys.stdout.flush()
        for key in nllMap:

            #reset to central values
            ws.var('mtop').setVal(172.5)
            ws.var('mu').setVal(1.0)

            #add the log likelihoods and minimize
            llSet = ROOT.RooArgSet()
            for ll in nllMap[key]: llSet.add(ll)
            combll = ROOT.RooAddition("combll","combll",llSet)
            minuit=ROOT.RooMinuit(combll)
            minuit.setErrorLevel(0.5)
            minuit.migrad()
            minuit.hesse()
            minuit.minos(poi)
            summary.addFitResult(key=key,ws=ws)
            combll.Delete()

            if options.verbose>3:
                sys.stdout.write(' %s%s DONE%s%s '
                                 '(mt: %6.2f+-%4.2f GeV, '
                                 'mu: %5.3f+-%5.3f)%s \n'%
                                 (bcolors.OKGREEN, bcolors.BOLD, bcolors.ENDC, bcolors.BOLD,
                                  ws.var('mtop').getVal(), ws.var('mtop').getError(),
                                  ws.var('mu').getVal(), ws.var('mu').getError(),
                                  bcolors.ENDC))
                sys.stdout.flush()
                print 80*'-'

        #free used memory
        for h in allPseudoDataH : h.Delete()
        for d in allPseudoData  : d.Delete()
        for ll in nllMap['comb']: ll.Delete()

    summary.saveResults()

"""
steer
"""
def main():
    usage = """
    Run a set of PEs on a single variation:
    usage: %prog [options] SVLWorkspace.root pe_inputs.root mass_check_172
           %prog [options] SVLWorkspace.root pe_inputs.root syst_toppt
    Run all PEs on batch
           %prog [options] SVLWorkspace.root pe_inputs.root
    """
    parser = optparse.OptionParser(usage)
    parser.add_option('--isData', dest='isData', default=False, action='store_true',
                       help='if true, final fit is performed')
    parser.add_option('--spy', dest='spy', default=False, action='store_true',
                       help='if true,shows fit results on the screen')
    parser.add_option('--noninteractive', dest='noninteractive', default=False,
                       action='store_true',
                       help='do not ask for confirmation before submitting jobs')
    parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int,
                       help='Verbose mode')
    parser.add_option('-c', '--calib', dest='calib', default='',
                       help='calibration file')
    parser.add_option('-f', '--filter', dest='filter', default='',
                       help='Run only on these variations (comma separated list)')
    parser.add_option('-n', '--nPexp', dest='nPexp', default=250, type=int,
                       help='Total # pseudo-experiments.')
    parser.add_option('-o', '--outDir', dest='outDir', default='svlfits',
                       help='Output directory [default: %default]')

    (opt, args) = parser.parse_args()

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gROOT.SetBatch(True)
    #if opt.spy : ROOT.gROOT.SetBatch(False)
    ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
    ROOT.AutoLibraryLoader.enable()
    if not opt.verbose > 5:
        ROOT.shushRooFit()
    # see TError.h - gamma function prints lots of errors when scanning
    ROOT.gROOT.ProcessLine("gErrorIgnoreLevel=kFatal")

    print 'Storing output in %s' % opt.outDir
    os.system('mkdir -p %s' % opt.outDir)
    os.system('mkdir -p %s' % osp.join(opt.outDir, 'plots'))

    # launch pseudo-experiments
    if not opt.isData:
        try:
            peInputFile = ROOT.TFile.Open(args[1], 'READ')
        except TypeError: ## this sometimes fails (too many accesses to this file?)
            import time
            time.sleep(5)
            peInputFile = ROOT.TFile.Open(args[1], 'READ')

        # Check all the existing variations
        allTags = [tkey.GetName() for tkey in peInputFile.GetListOfKeys()]
        allSysts  = sorted(list(set([t.rsplit('_',2)[0] for t in allTags if
                                                     t.startswith('syst')])))
        allMasses = sorted(list(set([t.rsplit('_',1)[0] for t in allTags if
                                                     t.startswith('mass')])))
        peInputFile.Close()
        print 'Running pseudo-experiments using PDFs and signal expectations'

        ## Run a single experiment
        if len(args)>2:
            if not args[2] in allSysts+allMasses:
                print ("ERROR: variation not "
                       "found in input file! Aborting")
                return -2

            ## Only run one PE for spy option
            if opt.spy:
                opt.nPexp = 1

            runPseudoExperiments(wsfile=args[0], pefile=args[1],
                                 experimentTag=args[2],
                                 options=opt)
            return 0

        # Loop over the required number of jobs
        print 'Submitting PE jobs to batch'
        if len(opt.filter)>0:
            filteredTags = opt.filter.split(',')
            for tag in filteredTags:
                if not tag in allTags:
                    print ("ERROR: variation not "
                           "found in input file! Aborting")
                    return -3
            allTags = filteredTags
        submitBatchJobs(args[0], args[1], allTags, opt)

        return 0
    else:
        print 'Ready to unblind?'
        print '...ah ah this is not even implemented'
        return -1
    print 80*'-'
    return 0



if __name__ == "__main__":
    sys.exit(main())
