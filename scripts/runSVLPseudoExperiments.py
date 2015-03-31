#!/usr/bin/env python
import ROOT
import os,sys
import optparse
import pickle
import numpy

from UserCode.TopMassSecVtx.PlotUtils import printProgress

"""
Show PE fit result
"""
def showFinalFitResult(data,pdf,nll,SVLMass,mtop,outDir):
    #init canvas
    canvas=ROOT.TCanvas('c','c',500,500)

    p1 = ROOT.TPad('p1','p1',0.0,0.85,1.0,0.0)
    p1.SetRightMargin(0.05)
    p1.SetLeftMargin(0.12)
    p1.SetTopMargin(0.01)
    p1.SetBottomMargin(0.1)
    p1.Draw()

    #fit results
    p1.cd()
    frame=SVLMass.frame()
    data.plotOn(frame,ROOT.RooFit.Name('data'))
    pdf.plotOn(frame,
               ROOT.RooFit.Name('totalexp'),
               ROOT.RooFit.ProjWData(data),
               ROOT.RooFit.LineColor(ROOT.kBlue),
               ROOT.RooFit.LineWidth(2),
               ROOT.RooFit.MoveToBack())
    pdf.plotOn(frame,
               ROOT.RooFit.Name('singlet'),
               ROOT.RooFit.ProjWData(data),
               ROOT.RooFit.Components('tshape_*'),
               ROOT.RooFit.FillColor(ROOT.kOrange+2),
               ROOT.RooFit.LineColor(ROOT.kOrange+2),
               ROOT.RooFit.FillStyle(1001),
               ROOT.RooFit.DrawOption('f'),
               ROOT.RooFit.MoveToBack())
    pdf.plotOn(frame,
               ROOT.RooFit.Name('tt'),
               ROOT.RooFit.ProjWData(data),
               ROOT.RooFit.Components('ttshape_*'),
               ROOT.RooFit.FillColor(ROOT.kOrange),
               ROOT.RooFit.LineColor(ROOT.kOrange),
               ROOT.RooFit.DrawOption('f'),
               ROOT.RooFit.FillStyle(1001),
               ROOT.RooFit.MoveToBack())
    frame.Draw()
    frame.GetYaxis().SetTitleOffset(1.5)
    frame.GetXaxis().SetTitle("m(SV,lepton) [GeV]")
    label=ROOT.TLatex()
    label.SetNDC()
    label.SetTextFont(42)
    label.SetTextSize(0.04)
    label.DrawLatex(0.18,0.94,'#bf{CMS} #it{simulation}')
    leg=ROOT.TLegend(0.7,0.35,0.95,0.55)
    leg.AddEntry('data',       'data',      'p')
    leg.AddEntry('totalexp',   'total',     'l')
    leg.AddEntry('tt',         't#bar{t}',  'f')
    leg.AddEntry('singlet',    'single top','f')
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)
    leg.SetBorderSize(0)
    leg.Draw()
    ROOT.SetOwnership(leg,0)

    canvas.cd()
    p2 = ROOT.TPad('p2','p2',0.0,0.86,1.0,1.0)
    p2.SetBottomMargin(0.05)
    p2.SetRightMargin(0.05)
    p2.SetLeftMargin(0.12)
    p2.SetTopMargin(0.05)
    p2.Draw()
    p2.cd()
    hpull = frame.pullHist()
    pullFrame = SVLMass.frame()
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

    canvas.cd()
    p3 = ROOT.TPad('p3','p3',0.6,0.47,0.95,0.82)
    p3.SetRightMargin(0.05)
    p3.SetLeftMargin(0.12)
    p3.SetTopMargin(0.008)
    p3.SetBottomMargin(0.2)
    p3.Draw()
    p3.cd()
    frame2=mtop.frame()
    for ill in xrange(0,len(nll)): nll[ill].plotOn(frame2,ROOT.RooFit.ShiftToZero(),ROOT.RooFit.LineStyle(ill+1))
    frame2.Draw()
    frame2.GetYaxis().SetRangeUser(0,12)
    frame2.GetXaxis().SetRangeUser(165,180)
    frame2.GetYaxis().SetNdivisions(3)
    frame2.GetXaxis().SetNdivisions(3)
    frame2.GetXaxis().SetTitle('Top mass [GeV]')
    frame2.GetYaxis().SetTitle('pLL and LL')
    frame2.GetYaxis().SetTitleOffset(1.5)
    frame2.GetXaxis().SetTitleSize(0.08)
    frame2.GetXaxis().SetLabelSize(0.08)
    frame2.GetYaxis().SetTitleSize(0.08)
    frame2.GetYaxis().SetLabelSize(0.08)

    canvas.Modified()
    canvas.Update()
    canvas.SaveAs('%s/plots/%s_fit.png'%(outDir,data.GetName()))
    canvas.SaveAs('%s/plots/%s_fit.pdf'%(outDir,data.GetName()))
    canvas.Delete()

"""
run pseudo-experiments
"""
def runPseudoExperiments(wsfile,pefile,experimentTag,options):

    #read the file with input distributions
    inputDistsF = ROOT.TFile.Open(pefile, 'READ')
    print '[runPseudoExperiments] Reading PE input from %s' % pefile
    print '[runPseudoExperiments] with %s' % experimentTag

    wsInputFile = ROOT.TFile.Open(wsfile, 'READ')
    ws = wsInputFile.Get('w')
    wsInputFile.Close()
    print '[runPseudoExperiments] Read workspace from %s' % wsfile

    #readout calibration from a file
    calibMap=None
    if options.calib:
         cachefile = open(options.calib,'r')
         calibMap  = pickle.load(cachefile)
         cachefile.close()
         print '[runPseudoExperiments] Read calibration from %s'%cachefile

    try:
        genMtop=float(experimentTag.rsplit('_', 1)[1].replace('v','.'))
    except Exception, e:
        raise e
    print '[runPseudoExperiments] Generated top mass is %5.1f GeV'%genMtop

    #load the model parameters and set all to constant
    ws.loadSnapshot("model_params")
    allVars = ws.allVars()
    varIter = allVars.createIterator()
    var = varIter.Next()
    varCtr=0
    while var :
        varName=var.GetName()
        if not varName in ['mtop', 'SVLMass', 'mu']:
            ws.var(varName).setConstant(True)
            varCtr+=1
        var = varIter.Next()
    print '[runPseudoExperiments] setting to constant %d numbers in the model'%varCtr

    #build the relevant PDFs
    allPdfs = {}
    for chsel in ['em','mm','ee','m','e']:
        if options.selection : chsel += '_' + options.selection
        for ntrk in [2,3,4]:
            ttexp      = '%s_ttexp_%d'              %(chsel,ntrk)
            ttcor      = '%s_ttcor_%d'              %(chsel,ntrk)
            ttcorPDF   = 'simplemodel_%s_%d_cor_tt' %(chsel,ntrk)
            ttwro      = '%s_ttwro_%d'              %(chsel,ntrk)
            ttwroPDF   = 'simplemodel_%s_%d_wro_tt' %(chsel,ntrk)
            ttunmPDF   = 'model_%s_%d_unm_tt'       %(chsel,ntrk)
            tfrac      = '%s_tfrac_%d'              %(chsel,ntrk)
            tcor       = '%s_tcor_%d'               %(chsel,ntrk)
            tcorPDF    = 'simplemodel_%s_%d_cor_t'  %(chsel,ntrk)
            twrounmPDF = 'model_%s_%d_wrounm_t'     %(chsel,ntrk)
            bkgExp     = '%s_bgexp_%d'              %(chsel,ntrk)
            bkgPDF     = 'model_%s_%d_unm_bg'       %(chsel,ntrk)

            ttShapePDF = ws.factory("SUM::ttshape_%s_%d(%s*%s,%s*%s,%s)"%(chsel,ntrk,ttcor,ttcorPDF,ttwro,ttwroPDF,ttunmPDF))
            Ntt        = ws.factory("RooFormulaVar::Ntt_%s_%d('@0*@1',{mu,%s})"%(chsel,ntrk,ttexp))

            tShapePDF  = ws.factory("SUM::tshape_%s_%d(%s*%s,%s)"%(chsel,ntrk,tcor,tcorPDF,twrounmPDF))
            Nt         = ws.factory("RooFormulaVar::Nt_%s_%d('@0*@1*@2',{mu,%s,%s})"%(chsel,ntrk,ttexp,tfrac))

            bkgConstPDF =  ws.factory('Gaussian::bgprior_%s_%d(bg0_%s_%d[0,-10,10],bg_nuis_%s_%d[0,-10,10],1.0)'%(chsel,ntrk,chsel,ntrk,chsel,ntrk))
            ws.var('bg0_%s_%d'%(chsel,ntrk)).setVal(0.0)
            ws.var('bg0_%s_%d'%(chsel,ntrk)).setConstant(True)
            #10% unc on background
            Nbkg        =  ws.factory("RooFormulaVar::Nbkg_%s_%d('@0*max(1+0.30*@1,0.)',{%s,bg_nuis_%s_%d})"%(chsel,ntrk,bkgExp,chsel,ntrk))

            #see syntax here https://root.cern.ch/root/html/RooFactoryWSTool.html#RooFactoryWSTool:process
            sumPDF = ws.factory("SUM::uncalibexpmodel_%s_%d( %s*%s, %s*%s, %s*%s )"%(chsel,ntrk,
                                                                              Ntt.GetName(), ttShapePDF.GetName(),
                                                                              Nt.GetName(), tShapePDF.GetName(),
                                                                              Nbkg.GetName(), bkgPDF
                                                                              ))
            ws.factory('PROD::uncalibmodel_%s_%d(%s,%s)'%(chsel,ntrk,
                                                          sumPDF.GetName(),bkgConstPDF.GetName()))

            #add calibration for this category if available (read from a pickle file?)
            offset, slope = 0.0, 1.0
            try:
                offset, slope = calibMap[ (chsel,ntrk) ]
            except:
                pass
            allPdfs[ (chsel,ntrk) ] = ws.factory("EDIT::model_%s_%d(uncalibmodel_%s_%d, mtop=expr('(@0-%f)/%f',mtop) )"%(chsel,ntrk,chsel,ntrk,offset,slope) )



    #throw pseudo-experiments
    allFitVals  = {('comb',0):[], ('comb_mu',0):[]}
    allFitErrs  = {('comb',0):[], ('comb_mu',0):[]}
    allFitPulls = {('comb',0):[], ('comb_mu',0):[]}
    poi = ROOT.RooArgSet( ws.var('mtop') )
    for i in xrange(0,options.nPexp):

        #iterate over available categories to build the set of likelihoods to combine
        allNLL=[]
        allPseudoDataH=[]
        allPseudoData=[]
        if options.verbose>1:
            printProgress(i, options.nPexp, '[runPseudoExperiments] ')
        for key in allPdfs:
            chsel, trk = key
            mukey=(chsel+'_mu',trk)

            ws.var('mtop').setVal(172.5)
            ws.var('mu').setVal(1.0)

            #init results map if not yet available
            if not (key in allFitVals):
                allFitVals[key]    = []
                allFitVals[mukey]  = []
                allFitErrs[key]    = []
                allFitErrs[mukey]  = []
                allFitPulls[key]   = []
                allFitPulls[mukey] = []

            #read histogram and generate random data
            ihist       = inputDistsF.Get('%s/SVLMass_%s_%s_%d'%(experimentTag,chsel,experimentTag,trk))
            pseudoDataH = ihist.Clone('peh')
            pseudoDataH.Reset('ICE')
            pseudoDataH.FillRandom(ihist, ROOT.gRandom.Poisson(ihist.Integral()) )
            pseudoData  = ROOT.RooDataHist('PseudoData_%s_%s_%d'%(experimentTag,chsel,trk),
                                           'PseudoData_%s_%s_%d'%(experimentTag,chsel,trk),
                                           ROOT.RooArgList(ws.var('SVLMass')), pseudoDataH)

            #minimize likelihood
            #allNLL.append( allPdfs[key].createNLL(pseudoData,ROOT.RooFit.Extended()) )
            allNLL.append( allPdfs[key].createNLL(pseudoData) )
            minuit=ROOT.RooMinuit(allNLL[-1])
            minuit.setErrorLevel(0.5)
            minuit.migrad()
            minuit.hesse()
            #error level from minos is equivalent to profile likelihood
            #but seems overestimated ?
            minuit.minos(poi)

            #save fit results
            fitVal, fitErr = ws.var('mtop').getVal(), ws.var('mtop').getError()
            allFitVals[key] .append(fitVal)
            allFitErrs[key] .append(fitErr)
            allFitPulls[key].append((fitVal-genMtop)/fitErr)

            fitVal_mu, fitErr_mu = ws.var('mu').getVal(), ws.var('mu').getError()
            allFitVals[mukey] .append(fitVal_mu)
            allFitErrs[mukey] .append(fitErr_mu)
            allFitPulls[mukey].append((fitVal_mu-1.0)/fitErr_mu)

            #show if required
            #FIXME: this is making the combined fit crash? something with TPads getting free'd up
            if options.spy and i==0:
                pll=allNLL[-1].createProfile(poi)
                showFinalFitResult(data=pseudoData,pdf=allPdfs[key], nll=[pll,allNLL[-1]],
                                   SVLMass=ws.var('SVLMass'),mtop=ws.var('mtop'),
                                   outDir=options.outDir)
               # raw_input('press key to continue...')

            #save to erase later
            allPseudoDataH.append(pseudoDataH)
            allPseudoData.append(pseudoData)

        #combined likelihood
        ws.var('mtop').setVal(172.5)
        ws.var('mu').setVal(1.0)
        llSet = ROOT.RooArgSet()
        for ll in allNLL: llSet.add(ll)
        combll = ROOT.RooAddition("combll","combll",llSet)
        minuit=ROOT.RooMinuit(combll)
        minuit.setErrorLevel(0.5)
        minuit.migrad()
        minuit.hesse()
        #error level from minos is equivalent to profile likelihood
        #but seems overestimated?
        minuit.minos(poi)

        fitVal, fitErr = ws.var('mtop').getVal(), ws.var('mtop').getError()
        combKey = ('comb',0)
        allFitVals[combKey].append(fitVal)
        allFitErrs[combKey].append(fitErr)
        allFitPulls[combKey].append((fitVal-genMtop)/fitErr)

        fitVal_mu, fitErr_mu = ws.var('mu').getVal(), ws.var('mu').getError()
        muCombKey = ('comb_mu',0)
        allFitVals[muCombKey].append(fitVal_mu)
        allFitErrs[muCombKey].append(fitErr_mu)
        allFitPulls[muCombKey].append((fitVal_mu-1.0)/fitErr_mu)

        #free used memory
        for h in allPseudoDataH : h.Delete()
        for d in allPseudoData  : d.Delete()

    #show and save final results
    selTag=''
    if options.selection : selTag='_%s'%options.selection
    peFile=ROOT.TFile(os.path.join(options.outDir,'%s%s_results.root'%(experimentTag,selTag)), 'RECREATE')
    for key in allFitVals:
        chsel,trk = key
        if '_mu' in chsel : continue

        #fill the histograms
        mtopfitH = ROOT.TH1F('mtopfit_%s_%d'%(chsel,trk),';Top quark mass [GeV];Pseudo-experiments',200,150,200)
        mtopfitH.SetDirectory(0)
        mtopfitStatUncH = ROOT.TH1F('mtopfit_statunc_%s_%d'%(chsel,trk),';#sigma_{stat}(m_{t}) [GeV];Pseudo-experiments',200,0,1.5)
        mtopfitStatUncH.SetDirectory(0)
        mtopfitPullH = ROOT.TH1F('mtopfit_pull_%s_%d'%(chsel,trk),';Pull=(m_{t}-m_{t}^{true})/#sigma_{stat}(m_{t});Pseudo-experiments',100,-2.02,1.98)
        mtopfitPullH.SetDirectory(0)
        mufitStatUncH = ROOT.TH1F('mufit_statunc_%s_%d'%(chsel,trk),';#sigma_{stat}(#mu);Pseudo-experiments',100,0,0.1)
        mufitStatUncH.SetDirectory(0)
        fitCorrH = ROOT.TH2F('muvsmtopcorr_%s_%d'%(chsel,trk),';Top quark mass [GeV];#mu=#sigma/#sigma_{th}(172.5 GeV);Pseudo-experiments',200,150,200,100,0.85,1.15)
        fitCorrH.SetDirectory(0)
        for i in xrange(0,len(allFitVals[key])):
            mtopfitH         .Fill( allFitVals[key][i] )
            mtopfitStatUncH  .Fill( allFitErrs[key][i] )
            mtopfitPullH     .Fill( allFitPulls[key][i] )
            mufitStatUncH    .Fill( allFitErrs[(chsel+'_mu',trk)][i] )
            fitCorrH         .Fill( allFitVals[key][i], allFitVals[(chsel+'_mu',trk)][i] )

        #show results
        canvas=ROOT.TCanvas('c','c',1200,800)
        canvas.Divide(3,2)
        canvas.cd(1)
        mtopfitH.Draw()
        channelTitle=chsel.replace('_',' ')
        label=ROOT.TLatex()
        label.SetNDC()
        label.SetTextFont(42)
        label.SetTextSize(0.04)
        label.DrawLatex(0.1,0.92,'#bf{CMS} #it{simulation}')
        label.DrawLatex(0.15,0.84,channelTitle)
        if trk>1 : label.DrawLatex(0.15,0.8,'%d tracks'%trk)
        canvas.cd(2)
        mtopfitStatUncH.Draw()
        canvas.cd(3)
        mtopfitPullH.Draw()
        canvas.cd(4)
        fitCorrH.Draw('colz')
        fitCorrH.GetZaxis().SetTitleOffset(-0.5)
        canvas.cd(5)
        mufitStatUncH.Draw()
        canvas.cd(6)
        label.DrawLatex(0.15,0.90,'# pseudo-experiments: %d'%(options.nPexp))
        mtopkey=(chsel,trk)
        mtopAvg, mtopUncAvg, mtopPullAvg = numpy.mean(allFitVals[mtopkey]), numpy.mean(allFitErrs[mtopkey]), numpy.mean(allFitPulls[mtopkey])
        mtopStd, mtopUncStd, mtopPullStd = numpy.std(allFitVals[mtopkey]),  numpy.std(allFitErrs[mtopkey]),  numpy.std(allFitPulls[mtopkey])
        label.DrawLatex(0.15,0.80,'<m_{t}>=%3.3f  #sigma(m_{t})=%3.3f'%(mtopAvg,mtopStd))
        label.DrawLatex(0.15,0.75,'<#sigma_{stat}>=%3.3f #sigma(#sigma_{stat})=%3.3f'%(mtopUncAvg,mtopUncStd))
        label.DrawLatex(0.15,0.70,'<Pull>=%3.3f #sigma(Pull)=%3.3f'%(mtopPullAvg,mtopPullStd))
        mukey=(chsel+'_mu',trk)
        muAvg, muUncAvg, muPullAvg = numpy.mean(allFitVals[mukey]), numpy.mean(allFitErrs[mukey]), numpy.mean(allFitPulls[mukey])
        muStd, muUncStd, muPullStd = numpy.std(allFitVals[mukey]),  numpy.std(allFitErrs[mukey]),  numpy.std(allFitPulls[mukey])
        label.DrawLatex(0.15,0.60,'<#mu>=%3.3f #sigma(#mu)=%3.3f'%(muAvg,muStd))
        label.DrawLatex(0.15,0.55,'<#sigma_{stat}>=%3.5f #sigma(#sigma_{stat})=%3.5f'%(muUncAvg,muUncStd))
        label.DrawLatex(0.15,0.50,'<Pull>=%3.3f #sigma(Pull)=%3.3f'%(muPullAvg,muPullStd))
        label.DrawLatex(0.15,0.40,'#rho(m_{t},#mu)=%3.3f'%fitCorrH.GetCorrelationFactor())
        canvas.cd()
        canvas.Modified()
        canvas.Update()
        canvas.SaveAs('%s/plots/%s_%d_%s_pesummary.png'%(options.outDir,chsel,trk,experimentTag))
        canvas.SaveAs('%s/plots/%s_%d_%s_pesummary.pdf'%(options.outDir,chsel,trk,experimentTag))

        #save to file
        peFile.cd()

        outDir=peFile.mkdir('%s_%d'%(chsel,trk))
        outDir.cd()
        mtopfitH.Write()
        mtopfitStatUncH.Write()
        mtopfitPullH.Write()
        mufitStatUncH.Write()
        fitCorrH.Write()

        npeRes=ROOT.TVectorD(1)
        npeRes[0]=float(options.nPexp)
        npeRes.Write('norm')

        mtopRes=ROOT.TVectorD(6)
        mtopRes[0]=mtopAvg
        mtopRes[1]=mtopStd
        mtopRes[2]=mtopUncAvg
        mtopRes[3]=mtopUncStd
        mtopRes[4]=mtopPullAvg
        mtopRes[5]=mtopPullStd
        mtopRes.Write('mtop')

        muRes=ROOT.TVectorD(6)
        muRes[0]=muAvg
        muRes[1]=muStd
        muRes[2]=muUncAvg
        muRes[3]=muUncStd
        muRes[4]=muPullAvg
        muRes[5]=muPullStd
        muRes.Write('mu')

        peFile.cd()

    #all done here
    peFile.cd()
    peFile.Close()

def submitBatchJobs(wsfile, pefile, experimentTags, options, queue='8nh'):
    import time
    cmsswBase = os.environ['CMSSW_BASE']
    jobsDir = os.path.join(cmsswBase,'src/UserCode/TopMassSecVtx/svlPEJobs',
                           time.strftime('%b%d'))
    # jobsDir = os.path.join(cmsswBase,'src/UserCode/TopMassSecVtx/svlPEJobs',
    #                        time.strftime('%b%d'), time.strftime('%H%M%S'))
    if os.path.exists(jobsDir):
        os.system('rm -r %s/*.sh'%jobsDir)
    else:
        os.system('mkdir -p %s'%jobsDir)

    print 'Single job scripts stored in %s' % jobsDir

    wsfilepath = os.path.abspath(wsfile)
    pefilepath = os.path.abspath(pefile)
    odirpath = os.path.abspath(options.outDir)

    for n,tag in enumerate(experimentTags):
        sys.stdout.write(' ... processing job %2d - %-22s' % (n, tag))
        sys.stdout.flush()
        scriptFileN = '%s/runSVLPE_%s.sh'%(jobsDir,tag)
        scriptFile = open(scriptFileN, 'w')
        scriptFile.write('#!/bin/bash\n')
        scriptFile.write('cd %s/src\n'%cmsswBase)
        scriptFile.write('eval `scram r -sh`\n')
        scriptFile.write('cd %s\n'%jobsDir)
        command = ('runSVLPseudoExperiments.py %s %s -o %s -v 3 %s -n %d' %
                      (wsfilepath, pefilepath, odirpath, tag, options.nPexp))
        scriptFile.write('%s\n'%command)
        scriptFile.close()
        os.system('chmod u+rwx %s'%scriptFileN)
        os.system("bsub -q %s -J SVLPE%d \'%s\'"% (queue, n+1, scriptFileN))
        sys.stdout.write('\033[92m SUBMITTED\n\033[0m')
    return 0

"""
steer
"""
def main():
    usage = """
    Run a set of PEs on a single variation:
    usage: %prog [options] SVLWorkspace.root pe_inputs.root nominal_172v5
    Run all PEs on batch
           %prog [options] SVLWorkspace.root pe_inputs.root
    """
    parser = optparse.OptionParser(usage)
    parser.add_option('--isData', dest='isData', default=False, action='store_true',
                       help='if true, final fit is performed')
    parser.add_option('--spy', dest='spy', default=False, action='store_true',
                       help='if true,shows fit results on the screen')
    parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int,
                       help='Verbose mode')
    parser.add_option('-s', '--selection', dest='selection', default=None,
                       help='selection type')
    parser.add_option('-c', '--calib', dest='calib', default=None,
                       help='calibration file')
    parser.add_option('-n', '--nPexp', dest='nPexp', default=100, type=int,
                       help='Total # pseudo-experiments.')
    parser.add_option('-o', '--outDir', dest='outDir', default='svlfits',
                       help='Output directory [default: %default]')

    (opt, args) = parser.parse_args()

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gROOT.SetBatch(True)
    if opt.spy : ROOT.gROOT.SetBatch(False)
    ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
    ROOT.AutoLibraryLoader.enable()
    if not opt.verbose > 5:
        ROOT.shushRooFit()
    # see TError.h - gamma function prints lots of errors when scanning
    ROOT.gROOT.ProcessLine("gErrorIgnoreLevel=kFatal")

    print 'Storing output in %s' % opt.outDir
    os.system('mkdir -p %s' % opt.outDir)
    os.system('mkdir -p %s' % os.path.join(opt.outDir, 'plots'))


    # launch pseudo-experiments
    if not opt.isData:
        peInputFile = ROOT.TFile.Open(args[1], 'READ')
        allTags = [tkey.GetName() for tkey in peInputFile.GetListOfKeys()]
        peInputFile.Close()
        print 'Running pseudo-experiments using PDFs and signal expectations'

        ## Run a single experiment
        if len(args)>2:
            if not args[2] in allTags:
                print ("[runPseudoExperiments] ERROR: variation not "
                       "found in input file! Aborting")
                return -2

            runPseudoExperiments(wsfile=args[0], pefile=args[1],
                                 experimentTag=args[2],
                                 options=opt)
            return 0

        #loop over the required number of jobs
        print 'Submitting PE jobs to batch'
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
