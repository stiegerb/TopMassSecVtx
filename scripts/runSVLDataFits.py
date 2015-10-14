#!/usr/bin/env python
import ROOT
import os,sys
import os.path as osp
import optparse
import pickle
import numpy

from UserCode.TopMassSecVtx.PlotUtils import printProgress, bcolors
from makeSVLMassHistos import NTRKBINS
from summarizeSVLresults import CATTOLABEL
from myRootFunctions import checkKeyInFile

from runSVLPseudoExperiments import PseudoExperimentResults, showFinalFitResult
from runSVLPseudoExperiments import buildPDFs

"""
run the fits on the data
"""
def runDataFits(wsfile,pefile,options):
    prepend = '[runDataFits] '

    #read the file with input distributions
    inputDistsF = ROOT.TFile.Open(pefile, 'READ')
    print prepend+'Reading data histos from %s with' % (pefile)
    if not checkKeyInFile('data', inputDistsF, doraise=False):
        print prepend+"ERROR: data histos not found in input file %s" %(pefile)
        sys.exit(-1)

    wsInputFile = ROOT.TFile.Open(wsfile, 'READ')
    ws = wsInputFile.Get('w')
    wsInputFile.Close()
    print prepend+'Read workspace from %s' % wsfile

    #readout calibration from a file
    calibMap=None
    if options.calib:
         cachefile = open(options.calib,'r')
         calibMap  = pickle.load(cachefile)
         cachefile.close()
         print prepend+'Read calibration from %s'%options.calib

    genMtop=172.5
    print prepend+'Assuming top mass is %5.1f GeV'%genMtop

    #prepare results summary
    selTag=''
    if len(options.selection)>0 : selTag='_%s'%options.selection
    summary=PseudoExperimentResults(genMtop=genMtop,
                                    outFileUrl=osp.join(options.outDir,'data%s_results.root'%(selTag)),
                                    selection=options.selection)

    #load the model parameters and set all to constant
    ws.loadSnapshot("model_params")
    allVars = ws.allVars()
    varIter = allVars.createIterator()
    var = varIter.Next()
    varCtr=0
    while var :
        varName=var.GetName()
        if not varName in ['mtop', 'SVLMass', 'mu']:
        # if not varName in ['mtop', 'SVLMass']:
            ws.var(varName).setConstant(True)
            varCtr+=1
        var = varIter.Next()
    print prepend+'setting to constant %d numbers in the model'%varCtr

    ws.var("mtop").setVal(genMtop)
    ws.var("mu").setVal(1.0)

    #build the relevant PDFs
    print prepend+"Building pdfs"
    allPdfs = buildPDFs(ws=ws, options=options,
                        calibMap=calibMap,
                        prepend=prepend)

    poi = ROOT.RooArgSet( ws.var('mtop') )

    # Iterate over available categories to build the set of likelihoods to combine
    nllMap={}

    for key in sorted(allPdfs):
        chsel, trk = key
        mukey=(chsel+'_mu',trk)

        if options.verbose>3:
            sys.stdout.write(prepend+'(%-12s, %d):' % (chsel, trk))
            sys.stdout.flush()

        ws.var('mtop').setVal(172.5)
        ws.var('mu').setVal(1.0)

        #read histogram and generate random data
        ihist = inputDistsF.Get('data/SVLMass_%s_data_%d'%(chsel,trk))

        dataHisto, data = None,None
        dataHisto = ihist.Clone('eh')
        data  = ROOT.RooDataHist('Data_data_%s_%d'%(chsel,trk),
                                       'Data_data_%s_%d'%(chsel,trk),
                                        ROOT.RooArgList(ws.var('SVLMass')),
                                        dataHisto)
        # Create likelihood
        # Store it in the appropriate categories for posterior combination
        for nllMapKey in [('comb',0),('comb',trk),('comb%s'%chsel,0)]:
            if not (nllMapKey in nllMap):
                nllMap[nllMapKey]=[]
            if nllMapKey[0]=='comb' and nllMapKey[1]==0:
                nllMap[nllMapKey].append( allPdfs[key].createNLL(data, ROOT.RooFit.Extended()) )
            else:
                nllMap[nllMapKey].append( nllMap[('comb',0)][-1] )

        if options.verbose>3:
            sys.stdout.write(' [running Minuit]')
            sys.stdout.flush()
        minuit=ROOT.RooMinuit(nllMap[('comb',0)][-1])
        minuit.setErrorLevel(0.5)
        minuit.migrad()
        minuit.hesse()
        minuit.minos(poi)

        #save fit results
        summary.addFitResult(key=key, ws=ws)

        #show, if required
        selstring = options.selection if options.selection else 'inclusive'
        pll=nllMap[('comb',0)][-1].createProfile(poi)

        # showFinalFitResult(data=data,pdf=allPdfs[key], nll=[pll,nllMap[('comb',0)][-1]],
        #                    SVLMass=ws.var('SVLMass'),mtop=ws.var('mtop'),
        #                    outDir=options.outDir,
        #                    tag=[selstring,
        #                    "%s channel, =%s tracks"%(
        #                      str(chsel.split('_',1)[0]),
        #                      str(trk))])

        if options.verbose>3:
            sys.stdout.write('%s DONE %s'
                             '(mt: %6.2f+-%4.2f GeV, '
                              'mu: %4.2f+-%4.2f, '
                              'corfrac: %5.2f+-%5.2f)\n'%
                            (bcolors.OKGREEN, bcolors.ENDC,
                             ws.var('mtop').getVal(), ws.var('mtop').getError(),
                             ws.var('mu').getVal(), ws.var('mu').getError(),
                             ws.var('ttcorfracshift_%s_%d'%(chsel,trk)).getVal()+1.0,
                             ws.var('ttcorfracshift_%s_%d'%(chsel,trk)).getError()))
            sys.stdout.flush()

    #combined likelihoods
    if options.verbose>3:
        print '%s------ Combining channels and categories'%(prepend)

    for key in sorted(nllMap.keys()):

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
            try: catlabel = CATTOLABEL[('%s_%d'%key)]
            except KeyError: catlabel = CATTOLABEL[('%s_%d'%key).replace('_%s'%options.selection, '')]
            sys.stdout.write(prepend)
            sys.stdout.write('%8s (%2d cats): ' % (catlabel,len(nllMap[key])))
            resultstring = ('mt: %6.2f+-%4.2f GeV, mu: %5.3f+-%5.3f \n' % (
                               ws.var('mtop').getVal(), ws.var('mtop').getError(),
                               ws.var('mu').getVal(), ws.var('mu').getError()) )
            if key == ('comb', 0):
                resultstring = bcolors.BOLD + resultstring + bcolors.ENDC
            sys.stdout.write(resultstring)
            sys.stdout.flush()
    print 80*'-'

    summary.saveResults()
    return 0

"""
steer
"""
def main():
    usage = """
    Run the mass fit on the data distributions:
    usage: %prog [options] SVLWorkspace.root pe_inputs.root
    """
    parser = optparse.OptionParser(usage)
    parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int,
                       help='Verbose mode')
    parser.add_option('-s', '--selection', dest='selection', default='',
                       help='selection type')
    parser.add_option('-c', '--calib', dest='calib', default='',
                       help='calibration file')
    parser.add_option('-o', '--outDir', dest='outDir', default='svlfits/pexp',
                       help='Output directory [default: %default]')

    parser.add_option('--floatCorrFrac', dest='floatCorrFrac', default=False,
                       action='store_true',
                       help='Let the fraction of correct pairings float in the fit')

    (opt, args) = parser.parse_args()

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gROOT.SetBatch(True)
    ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
    ROOT.AutoLibraryLoader.enable()
    if not opt.verbose > 5:
        ROOT.shushRooFit()
    # see TError.h - gamma function prints lots of errors when scanning
    ROOT.gROOT.ProcessLine("gErrorIgnoreLevel=kFatal")

    print 'Storing output in %s' % opt.outDir
    os.system('mkdir -p %s' % opt.outDir)
    os.system('mkdir -p %s' % osp.join(opt.outDir, 'plots'))

    opt.verbose = 5
    runDataFits(wsfile=args[0], pefile=args[1], options=opt)

    print 80*'-'
    return 0



if __name__ == "__main__":
    sys.exit(main())
