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

"""
Wrapper to contain the histograms with the results of the pseudo-experiments
"""
class PseudoExperimentResults:

    def __init__(self,genMtop,outFileUrl,selection=None):
        self.genMtop=genMtop
        self.outFileUrl=outFileUrl
        self.histos={}
        self.trees={}
        self.selection = selection

        self.genmtop = numpy.zeros(1, dtype=float)
        self.genmtop[0] = self.genMtop
        self.mtopfit = numpy.zeros(1, dtype=float)
        self.statunc = numpy.zeros(1, dtype=float)
        self.pull    = numpy.zeros(1, dtype=float)
        self.mu      = numpy.zeros(1, dtype=float)

        self.ntt_prefit  = 0
        self.nt_prefit   = 0
        self.nbkg_prefit = 0


    def incrementPreFitExpectation(self, ntt, nt, nbkg):
        self.ntt_prefit  += ntt
        self.nt_prefit   += nt
        self.nbkg_prefit += nbkg


    def addFitResult(self,key,ws):

        #init histogram if needed
        if not (key in self.histos):
            self.initHistos(key)

        #fill the histograms
        if ws.var('mtop').getError()>0:
            mtopfit = ws.var('mtop').getVal()
            bias = mtopfit-self.genMtop
            error = ws.var('mtop').getError()
            self.mtopfit[0] = mtopfit
            self.statunc[0] = error
            self.pull   [0] = bias/error
            self.mu     [0] = ws.var('mu').getVal()

            self.histos[key]['mtopfit']        .Fill(bias)
            self.histos[key]['mtopfit_statunc'].Fill(error)
            self.histos[key]['mtopfit_pull']   .Fill(bias/error)
            self.histos[key]['muvsmtop']       .Fill(bias, ws.var('mu').getVal())
            self.trees[key].Fill()

            # self.ntt  = 0
            # self.nt   = 0
            # self.nbkg = 0

            # for ch in ['em','mm','ee','m','e']:
            #     chsel=ch
            #     if self.selection: chsel += '_' + self.selection
            #     for ntrk in [tklow for tklow,_ in NTRKBINS]: # [3,4,5]
            #         self.ntt  += ws.function("Ntt_%s_%d"%(chsel,ntrk)).getVal()
            #         self.nt   += ws.function("Nt_%s_%d"%(chsel,ntrk)).getVal()
            #         self.nbkg += ws.function("Nbkg_%s_%d"%(chsel,ntrk)).getVal()

    def initHistos(self,key):
        self.histos[key]={}
        pfix=''
        for tk in key: pfix += str(tk)+'_'
        pfix=pfix[:-1]
        self.histos[key]['mtopfit']         = ROOT.TH1F('mtopfit_%s'%pfix,
                                                        ';#Deltam_{t} [GeV];Pseudo-experiments',
                                                        200,-5,5)
        self.histos[key]['mtopfit_statunc'] = ROOT.TH1F('mtopfit_statunc_%s'%pfix,
                                                        ';#sigma_{stat}(m_{t}) [GeV];Pseudo-experiments',
                                                        200,0,1.5)
        self.histos[key]['mtopfit_pull']    = ROOT.TH1F('mtopfit_pull_%s'%pfix,
                                                        ';Pull=(m_{t}-m_{t}^{true})/#sigma_{stat}(m_{t});Pseudo-experiments',
                                                        100,-3.03,2.97)
        self.histos[key]['muvsmtop']        = ROOT.TH2F('muvsmtop_%s'%pfix,
                                                        ';#Delta m_{t} [GeV];#mu=#sigma/#sigma_{th}(172.5 GeV);Pseudo-experiments',
                                                        100,-5,5,100,0.80,1.20)
        for var in self.histos[key]:
            self.histos[key][var].SetDirectory(0)
            self.histos[key][var].Sumw2()

        self.trees[key] = ROOT.TTree('peinfo_%s'%pfix,'SVL Pseudoexperiment info')
        self.trees[key].Branch('genmtop', self.genmtop, 'genmtop/D')
        self.trees[key].Branch('mtopfit', self.mtopfit, 'mtopfit/D')
        self.trees[key].Branch('statunc', self.statunc, 'statunc/D')
        self.trees[key].Branch('pull',    self.pull,    'pull/D')
        self.trees[key].Branch('mu',      self.mu,      'mu/D')



    def saveResults(self):
        peFile=ROOT.TFile(self.outFileUrl,'RECREATE')
        for key in self.histos:
            dirName=''
            for tk in key: dirName+=str(tk)+'_'
            dirName=dirName[:-1]
            peFile.cd()
            outDir=peFile.mkdir(dirName)
            outDir.cd()
            for var in self.histos[key]:
                self.histos[key][var].Write()
            self.trees[key].Write()

            mtopRes=ROOT.TVectorD(6)
            mtopRes[0]=self.histos[key]['mtopfit'].GetMean()
            mtopRes[1]=self.histos[key]['mtopfit'].GetMeanError()
            mtopRes[2]=self.histos[key]['mtopfit_statunc'].GetMean()
            mtopRes[3]=self.histos[key]['mtopfit_statunc'].GetMeanError()
            mtopRes[4]=self.histos[key]['mtopfit_pull'].GetMean()
            mtopRes[5]=self.histos[key]['mtopfit_pull'].GetRMS()
            mtopRes.Write('mtop')

            peFile.cd()

        #all done here
        peFile.cd()
        peFile.Close()


"""
Show PE fit result
"""
def showFinalFitResult(data,pdf,nll,SVLMass,mtop,outDir,tag=None):
    #init canvas
    canvas = ROOT.TCanvas('c','c',500,500)
    ROOT.SetOwnership(canvas, False)

    p1 = ROOT.TPad('p1','p1',0.0,0.85,1.0,0.0)
    p1.SetRightMargin(0.05)
    p1.SetLeftMargin(0.18)
    p1.SetTopMargin(0.01)
    p1.SetBottomMargin(0.15)
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
               ROOT.RooFit.FillStyle(1001),
               ROOT.RooFit.FillColor(0),
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
               ROOT.RooFit.Components('ttshape_*,tshape_*'),
               #ROOT.RooFit.Components('*_ttcor_*'),
               ROOT.RooFit.FillColor(ROOT.kOrange),
               ROOT.RooFit.LineColor(ROOT.kOrange),
               ROOT.RooFit.DrawOption('f'),
               ROOT.RooFit.FillStyle(1001),
               ROOT.RooFit.MoveToBack())
    # pdf.plotOn(frame,
    #            ROOT.RooFit.Name('bgk'),
    #            ROOT.RooFit.ProjWData(data),
    #            ROOT.RooFit.Components('bgprior_*'),
    #            ROOT.RooFit.FillColor(ROOT.kRed),
    #            ROOT.RooFit.LineColor(ROOT.kRed),
    #            ROOT.RooFit.DrawOption('f'),
    #            ROOT.RooFit.FillStyle(1001),
    #            ROOT.RooFit.MoveToBack())
    frame.Draw()
    frame.GetYaxis().SetTitleOffset(1.5)
    frame.GetYaxis().SetRangeUser(0,1.2*frame.GetMaximum())
    frame.GetXaxis().SetTitle("m_{svl} [GeV]")
    frame.GetXaxis().SetLabelFont(43)
    frame.GetXaxis().SetTitleFont(43)
    frame.GetXaxis().SetTitleSize(30)
    frame.GetXaxis().SetLabelSize(24)
    frame.GetYaxis().SetLabelFont(43)
    frame.GetYaxis().SetTitleFont(43)
    frame.GetYaxis().SetTitleSize(30)
    frame.GetYaxis().SetLabelSize(24)

    # FIXME: this should not be hardcoded!
    frame.GetYaxis().SetTitle("Events / 3.9 GeV")

    label = ROOT.TLatex()
    label.SetNDC()
    label.SetTextFont(43)
    label.SetTextSize(28)
    label.DrawLatex(0.21,0.92,'#bf{CMS}')
    label.SetTextSize(20)
    label.DrawLatex(0.34,0.92,'19.7 fb^{-1} (8 TeV)')

    leg = ROOT.TLegend(0.65,0.32,0.95,0.53)
    leg.AddEntry('data',       'Data',         'p')
    leg.AddEntry('tt',         't#bar{t}',     'f')
    leg.AddEntry('singlet',    'Single top',   'f')
    leg.AddEntry('totalexp',   'Background',   'f')
    leg.SetFillStyle(0)
    leg.SetTextFont(43)
    leg.SetTextSize(20)
    leg.SetBorderSize(0)
    leg.Draw()
    ROOT.SetOwnership(leg,0)

    if tag:
        tlat = ROOT.TLatex()
        tlat.SetTextFont(43)
        tlat.SetNDC(1)
        tlat.SetTextAlign(13)
        tlat.SetTextSize(21)
        if type(tag) == str:
            tlat.DrawLatex(0.65, 0.32, tag)
        else:
            ystart = 0.91
            yinc = 0.05
            for n,text in enumerate(tag):
                tlat.DrawLatex(0.22, ystart-n*yinc, text)

    canvas.cd()
    p2 = ROOT.TPad('p2','p2',0.0,0.86,1.0,1.0)
    p2.SetBottomMargin(0.05)
    p2.SetRightMargin(0.05)
    p2.SetLeftMargin(0.18)
    p2.SetTopMargin(0.05)
    p2.Draw()
    p2.cd()
    hpull = frame.pullHist()
    pullFrame = SVLMass.frame()
    pullFrame.addPlotable(hpull,"P") ;
    pullFrame.Draw()
    pullFrame.GetYaxis().SetTitle("Pull")
    pullFrame.GetYaxis().SetTitleFont(43)
    pullFrame.GetYaxis().SetTitleSize(30)
    pullFrame.GetYaxis().SetLabelFont(43)
    pullFrame.GetYaxis().SetLabelSize(24)
    pullFrame.GetYaxis().SetTitleOffset(1.5)
    pullFrame.GetYaxis().SetNdivisions(4)
    pullFrame.GetYaxis().SetRangeUser(-3.1,3.1)

    pullFrame.GetXaxis().SetTitleSize(0)
    pullFrame.GetXaxis().SetLabelSize(0)
    pullFrame.GetXaxis().SetTitleOffset(0.8)

    canvas.cd()
    p3 = ROOT.TPad('p3','p3',0.61,0.45,0.94,0.82)
    p3.SetRightMargin(0.05)
    p3.SetLeftMargin(0.24)
    p3.SetTopMargin(0.008)
    p3.SetBottomMargin(0.24)
    p3.Draw()
    p3.cd()
    frame2=mtop.frame()
    for ill in xrange(0,len(nll)): nll[ill].plotOn(frame2,ROOT.RooFit.ShiftToZero(),ROOT.RooFit.LineStyle(ill+1))
    frame2.Draw()
    frame2.GetYaxis().SetRangeUser(0,12)
    frame2.GetXaxis().SetRangeUser(165,180)
    frame2.GetYaxis().SetNdivisions(3)
    frame2.GetXaxis().SetNdivisions(3)
    frame2.GetXaxis().SetTitle('m_{top} [GeV]')
    frame2.GetYaxis().SetTitle('-2#DeltalogL')

    frame2.GetYaxis().SetTitleOffset(2.5)
    frame2.GetXaxis().SetTitleOffset(2.4)
    frame2.GetYaxis().SetTitleFont(43)
    frame2.GetXaxis().SetTitleFont(43)
    frame2.GetYaxis().SetLabelFont(43)
    frame2.GetXaxis().SetLabelFont(43)

    frame2.GetXaxis().SetTitleSize(20)
    frame2.GetXaxis().SetLabelSize(16)
    frame2.GetYaxis().SetTitleSize(20)
    frame2.GetYaxis().SetLabelSize(16)

    canvas.Modified()
    canvas.Update()
    for ext in ['png','pdf','C']:
        canvas.SaveAs('%s/plots/%s.%s'%(outDir,data.GetName(),ext))
    canvas.Delete()


"""
build the fit model
"""
def buildPDFs(ws, options, channels, calibMap=None, prepend=''):
    allPdfs = {}
    for ch in channels:
        chsel = ch
        if len(options.selection) > 0: chsel += '_%s'%options.selection

        for ntrk in [tklow for tklow,_ in NTRKBINS]: # [3,4,5]
            if options.verbose>4: print prepend+"  chan %s ntk=%d" %(chsel, ntrk)
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

            ## Check for existence of necessary pdfs in Workspace
            for key in [ttcorPDF, ttwroPDF, ttunmPDF, tcorPDF, twrounmPDF, bkgPDF]:
                if not ws.pdf(key):
                    print "ERROR: pdf %s not found in workspace!" %key
                    sys.exit(-1)

            ## Float the fraction of correct pairings
            if options.floatCorrFrac:
                ttcorfrac = ws.factory("ttcorfracshift_%s_%d[0.0,-0.8,0.8]"%(chsel,ntrk))
                ttcorshifted = ws.factory("RooFormulaVar::ttcorshifted_%s_%d('@0*(1+@1)',{%s,ttcorfracshift_%s_%d})"%(chsel,ntrk,ttcor,chsel,ntrk))
                ttwroshifted = ws.factory("RooFormulaVar::ttwroshifted_%s_%d('@0*-@1*@2',{%s,ttcorfracshift_%s_%d,%s})"%(chsel,ntrk,ttwro,chsel,ntrk,ttcor))

                ttShapePDF = ws.factory("SUM::ttshape_%s_%d(%s*%s,%s*%s,%s)"%(chsel,ntrk,ttcorshifted.GetName(),ttcorPDF,
                                                                                         ttwroshifted.GetName(),ttwroPDF,ttunmPDF))
            else:
                ttShapePDF = ws.factory("SUM::ttshape_%s_%d(%s*%s,%s*%s,%s)"%(chsel,ntrk,ttcor,ttcorPDF,ttwro,ttwroPDF,ttunmPDF))

            Ntt        = ws.factory("RooFormulaVar::Ntt_%s_%d('@0*@1',{mu,%s})"%(chsel,ntrk,ttexp))

            tShapePDF  = ws.factory("SUM::tshape_%s_%d(%s*%s,%s)"%(chsel,ntrk,tcor,tcorPDF,twrounmPDF))
            Nt         = ws.factory("RooFormulaVar::Nt_%s_%d('@0*@1*@2',{mu,%s,%s})"%(chsel,ntrk,ttexp,tfrac))

            bkgConstPDF = ws.factory('Gaussian::bgprior_%s_%d(bg0_%s_%d[0,-10,10],bg_nuis_%s_%d[0,-10,10],1.0)'%(chsel,ntrk,chsel,ntrk,chsel,ntrk))
            ws.var('bg0_%s_%d'%(chsel,ntrk)).setVal(0.0)
            ws.var('bg0_%s_%d'%(chsel,ntrk)).setConstant(True)

            #30% unc on background
            Nbkg = ws.factory("RooFormulaVar::Nbkg_%s_%d('@0*max(1+0.30*@1,0.)',{%s,bg_nuis_%s_%d})"%(chsel,ntrk,bkgExp,chsel,ntrk))

            # print '[Expectation] %2s, %d: %8.2f (Ntt: %8.2f) (Nt: %8.2f) (Bkg: %8.2f)' % (
            #                       chsel, ntrk, Ntt.getVal()+Nt.getVal()+Nbkg.getVal(), Ntt.getVal(), Nt.getVal(), Nbkg.getVal())

            #see syntax here https://root.cern.ch/root/html/RooFactoryWSTool.html#RooFactoryWSTool:process
            sumPDF = ws.factory("SUM::uncalibexpmodel_%s_%d( %s*%s, %s*%s, %s*%s )"%(chsel,ntrk,
                                      Ntt.GetName(), ttShapePDF.GetName(),
                                      Nt.GetName(), tShapePDF.GetName(),
                                      Nbkg.GetName(), bkgPDF) )
            ws.factory('PROD::uncalibmodel_%s_%d(%s,%s)'%(chsel,ntrk,
                                                          sumPDF.GetName(),
                                                          bkgConstPDF.GetName()))

            #add calibration for this category if available (read from a pickle file)
            offset, slope = 0.0, 1.0
            if calibMap:
                try:
                    offset, slope = calibMap[options.selection][ '%s_%d'%(ch,ntrk) ]
                except KeyError as e:
                    print prepend+'ERROR: Failed to retrieve calibration for %s' % options.selection
                    sys.exit(-1)
            ws.factory("RooFormulaVar::calibmtop_%s_%d('(@0-%f)/%f',{mtop})"%(chsel,ntrk,offset,slope))
            allPdfs[(chsel,ntrk)] = ws.factory("EDIT::model_%s_%d(uncalibmodel_%s_%d,mtop=calibmtop_%s_%d)"%
                                               (chsel,ntrk,chsel,ntrk,chsel,ntrk))
    return allPdfs


"""
run pseudo-experiments
"""
def runPseudoExperiments(wsfile,pefile,experimentTag,options):
    prepend = '[runPseudoExperiments %s] '%experimentTag

    #read the file with input distributions
    inputDistsF = ROOT.TFile.Open(pefile, 'READ')
    print prepend+'Reading PE input from %s with %s' % (pefile, experimentTag)
    if not checkKeyInFile(experimentTag, inputDistsF, doraise=False):
        print prepend+"ERROR: experiment tag %s not found in input file %s" %(experimentTag, pefile)
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
    try:
        genMtop=float(experimentTag.rsplit('_', 1)[1].replace('v','.'))
    except (IndexError, ValueError) as e:
        print ("%sERROR: Could not extract generated mass value "
               "from experiment tag: '%s'"%(prepend, experimentTag))
        sys.exit(-1)
    print prepend+'Generated top mass is %5.1f GeV'%genMtop

    #prepare results summary
    selTag=''
    if len(options.selection)>0 : selTag='_%s'%options.selection
    summary=PseudoExperimentResults(genMtop=genMtop,
                                    outFileUrl=osp.join(options.outDir,
                                       '%s%s_results.root'%(experimentTag,selTag)),
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
            ws.var(varName).setConstant(True)
            varCtr+=1
        var = varIter.Next()
    print prepend+'setting to constant %d numbers in the model'%varCtr

    ws.var("mtop").setVal(genMtop)
    ws.var("mu").setVal(1.0)

    #build the relevant PDFs
    print prepend+"Building pdfs"
    channels = ['em','mm','ee','m','e','eplus','mplus','eminus','mminus']
    allPdfs = buildPDFs(ws=ws, options=options,
                        channels=channels,
                        calibMap=calibMap,
                        prepend=prepend)

    #throw pseudo-experiments
    poi = ROOT.RooArgSet( ws.var('mtop') )
    if options.verbose>1:
        print prepend+'Running %d experiments' % options.nPexp
        print 80*'-'

    # if not 'nominal' in experimentTag:
    #     cfilepath = osp.abspath(osp.join(osp.dirname(wsfile),'../../'))
    #     # cfilepath = osp.abspath(osp.join(osp.dirname(__file__),'../'))
    #     cfilepath = osp.join(cfilepath, ".svlsysthistos.pck")
    #     cachefile = open(cfilepath, 'r')
    #     systhistos = pickle.load(cachefile)
    #     print prepend+'>>> Read systematics histograms from cache (.svlsysthistos.pck)'
    #     cachefile.close()

    for i in xrange(0,options.nPexp):

        #iterate over available categories to build the set of likelihoods to combine
        indNLLs=[]
        nllMap={}
        allPseudoDataH=[]
        allPseudoData=[]
        if options.verbose>1 and options.verbose<=3:
            printProgress(i, options.nPexp, prepend+' ')

        for key in sorted(allPdfs):
            chsel, trk = key
            mukey=(chsel+'_mu',trk)
            if options.verbose>3:
                sys.stdout.write(prepend+'Exp %-3d (%-12s, %d):' % (i+1, chsel, trk))
                sys.stdout.flush()

            ws.var('mtop').setVal(172.5)
            ws.var('mu').setVal(1.0)

            #read histogram and generate random data
            ihist = inputDistsF.Get('%s/SVLMass_%s_%s_%d'%(experimentTag,chsel,experimentTag,trk))

            # Get number of events to be generated either:
            # - From properly scaled input files for nominal mass variations
            #   to estimate the actual statistical error
            # - From the number of generated MC events, to estimate statistical
            #   uncertainty of variation
            # THIS SCREWS UP THE MASS EXTRACTION: WHY??
            nevtsSeed = ihist.Integral()
            # if not 'nominal' in experimentTag:
            #     try:
            #         nevtsSeed = systhistos[(chsel, experimentTag.replace('_172v5',''),
            #                                 'tot' ,trk)].GetEntries() ## FIXME: GetEntries or Integral?
            #     except KeyError:
            #         print prepend+"  >>> COULD NOT FIND SYSTHISTO FOR",chsel, experimentTag, trk

            # print '[Generation] Will generate PEs with %6.1f events' % nevtsSeed
            nevtsToGen = ROOT.gRandom.Poisson(nevtsSeed)

            pseudoDataH,pseudoData=None,None
            if options.genFromPDF:
                obs = ROOT.RooArgSet(ws.var('SVLMass'))
                pseudoData = allPdfs[key].generateBinned(obs, nevtsToGen)
            else:
                pseudoDataH = ihist.Clone('peh')
                if options.nPexp>1:
                    pseudoDataH.Reset('ICE')
                    pseudoDataH.FillRandom(ihist, nevtsToGen)
                else:
                    print 'Single pseudo-experiment won\'t be randomized'
                pseudoData  = ROOT.RooDataHist('PseudoData_%s_%s_%d'%(experimentTag,chsel,trk),
                                               'PseudoData_%s_%s_%d'%(experimentTag,chsel,trk),
                                               ROOT.RooArgList(ws.var('SVLMass')), pseudoDataH)

            if options.verbose>3:
                sys.stdout.write(' [generated pseudodata]')
                sys.stdout.flush()

            #create likelihood : store it in the appropriate categories for posterior combination
            nll = allPdfs[key].createNLL(pseudoData, ROOT.RooFit.Extended())
            indNLLs.append( nll )

            chType=''
            if chsel in ['em','mm','ee']   : chType='ll'
            if chsel in ['e','m']          : chType='lj'
            if chsel in ['eplus','mplus']  : chType='lplus'
            if chsel in ['eminus','minus'] : chType='lminus'
            nllMapKeys=[('comb%s'%chsel,0),('comb%s'%chType,trk),('comb%s'%chType,0)]
            if chType!='lplus' and chType!='lminus':
                nllMapKeys.insert(0,('comb',trk))
                nllMapKeys.insert(0,('comb',0))
            for nllMapKey in nllMapKeys:
                if not (nllMapKey in nllMap):
                    nllMap[nllMapKey]=[]
                if nllMapKey[0]=='comb' and nllMapKey[1]==0:
                    nllMap[nllMapKey].append( nll )
                else:
                    nllMap[nllMapKey].append( nll )

            if options.verbose>3:
                sys.stdout.write(' [running Minuit]')
                sys.stdout.flush()

            minuit=ROOT.RooMinuit(nll)
            minuit.setErrorLevel(0.5)
            minuit.migrad()
            minuit.hesse()
            minuit.minos(poi)


            #save fit results
            summary.addFitResult(key=key,ws=ws)

            #show, if required
            selstring = options.selection if options.selection else 'inclusive'
            if options.spy and i==0:
                pll=nll.createProfile(poi)
                showFinalFitResult(data=pseudoData,pdf=allPdfs[key], nll=[pll],
                                   SVLMass=ws.var('SVLMass'),mtop=ws.var('mtop'),
                                   outDir=options.outDir,
                                   tag=[selstring,
                                   "%s channel, =%s tracks"%(
                                     str(chsel.split('_',1)[0]),
                                     str(trk))])
                #raw_input('press key to continue...')

            #save to erase later
            if pseudoDataH : allPseudoDataH.append(pseudoDataH)
            allPseudoData.append(pseudoData)
            if options.verbose>3:
                sys.stdout.write('%s DONE %s'
                                 '(mt: %6.2f+-%4.2f GeV, '
                                  'mu: %4.2f+-%4.2f'%
                                (bcolors.OKGREEN, bcolors.ENDC,
                                 ws.var('mtop').getVal(), ws.var('mtop').getError(),
                                 ws.var('mu').getVal(), ws.var('mu').getError()))
                if options.floatCorrFrac:
                    sys.stdout.write(' corfrac: %4.2f+-%4.2f)'% (
                                     ws.var('ttcorfracshift_%s_%d'%(chsel,trk)).getVal()+1.0,
                                     ws.var('ttcorfracshift_%s_%d'%(chsel,trk)).getError()))
                sys.stdout.write('\n')
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

        #free used memory
        for h in allPseudoDataH : h.Delete()
        for d in allPseudoData  : d.Delete()
        for ll in indNLLs       : ll.Delete()

    summary.saveResults()



def submitBatchJobs(wsfile, pefile, experimentTags, options, queue='8nh'):
    import time
    cmsswBase = os.environ['CMSSW_BASE']
    sel=options.selection
    if len(sel)==0 : sel='inclusive'
    baseJobsDir='svlPEJobs'
    if options.calib : baseJobsDir+='_calib'
    jobsDir = osp.join(cmsswBase,'src/UserCode/TopMassSecVtx/%s/%s'%(baseJobsDir,sel),time.strftime('%b%d'))
    if not osp.exists(jobsDir):
        os.system('mkdir -p %s'%jobsDir)

    print 'Single job scripts stored in %s' % jobsDir

    wsfilepath = osp.abspath(wsfile)
    pefilepath = osp.abspath(pefile)
    odirpath = osp.abspath(jobsDir)

    ## Feedback before submitting the jobs
    if not options.noninteractive:
        raw_input('This will submit %d jobs to batch. %s '
                  'Did you remember to run scram b?%s \n '
                  'Continue?'%(len(experimentTags), bcolors.RED, bcolors.ENDC))

    for n,tag in enumerate(experimentTags):
        sys.stdout.write(' ... processing job %2d - %-22s' % (n+1, tag))
        sys.stdout.flush()
        scriptFileN = '%s/runSVLPE_%s.sh'%(jobsDir,tag)
        scriptFile = open(scriptFileN, 'w')
        scriptFile.write('#!/bin/bash\n')
        scriptFile.write('cd %s/src\n'%cmsswBase)
        scriptFile.write('eval `scram r -sh`\n')
        scriptFile.write('cd %s\n'%jobsDir)
        command = ('runSVLPseudoExperiments.py %s %s -o %s -v 3 %s -n %d' %
                      (wsfilepath, pefilepath, odirpath, tag, options.nPexp))
        if options.genFromPDF:
            command += ' --genFromPDF'
        if options.floatCorrFrac:
            command += ' --floatCorrFrac'
        if options.calib:
            command += ' --calib %s' % osp.abspath(options.calib)
        if len(options.selection):
            command += ' --selection %s'%options.selection
        scriptFile.write('%s\n'%command)
        scriptFile.close()
        os.system('chmod u+rwx %s'%scriptFileN)
        os.system("bsub -q %s -J SVLPE_%d_%s \'%s\'"% (queue, n+1, tag, scriptFileN))
    sys.stdout.write(bcolors.OKGREEN+' ALL JOBS SUBMITTED\n' + bcolors.ENDC)
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
    parser.add_option('--genFromPDF', dest='genFromPDF', default=False, action='store_true',
                       help='if true, pseudo-experiments are thrown thrown from the PDF')
    parser.add_option('--spy', dest='spy', default=False, action='store_true',
                       help='if true,shows fit results on the screen')
    parser.add_option('--noninteractive', dest='noninteractive', default=False,
                       action='store_true',
                       help='do not ask for confirmation before submitting jobs')
    parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int,
                       help='Verbose mode')
    parser.add_option('-s', '--selection', dest='selection', default='',
                       help='selection type')
    parser.add_option('-c', '--calib', dest='calib', default='',
                       help='calibration file')
    parser.add_option('-f', '--filter', dest='filter', default='',
                       help='Run only on these variations (comma separated list)')
    parser.add_option('-n', '--nPexp', dest='nPexp', default=250, type=int,
                       help='Total # pseudo-experiments.')
    parser.add_option('-o', '--outDir', dest='outDir', default='svlfits/pexp',
                       help='Output directory [default: %default]')

    parser.add_option('--floatCorrFrac', dest='floatCorrFrac', default=False,
                       action='store_true',
                       help='Let the fraction of correct pairings float in the fit')

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
    try:
        peInputFile = ROOT.TFile.Open(args[1], 'READ')
    except TypeError: ## this sometimes fails (too many accesses to this file?)
        import time
        time.sleep(5)
        peInputFile = ROOT.TFile.Open(args[1], 'READ')

    allTags = [tkey.GetName() for tkey in peInputFile.GetListOfKeys()
                                          if not tkey.GetName() == 'data']
    peInputFile.Close()
    print 'Running pseudo-experiments using PDFs and signal expectations'

    if len(opt.calib) :
        print 'Calibration will be taken from %s' % opt.calib

    ## Run a single experiment
    if len(args)>2:
        if not args[2] in allTags:
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

    #loop over the required number of jobs
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

    print 80*'-'
    return 0



if __name__ == "__main__":
    sys.exit(main())
