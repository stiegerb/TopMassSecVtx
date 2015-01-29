#!/usr/bin/env python

import ROOT
import os,sys
import optparse
import pickle

"""
parameterize the signal permutations
"""
def parameterizeSignalPermutations(ws,permName,chList,combList,trkMultList,sig_mass_cats,massList,SVLmass) :

    print '[parameterizeSignalPermutations] with %s'%permName

    for ch in chList:
        if ch=='inclusive': continue
        for comb in combList:
            for ntrk in trkMultList:
                tag='%s_%d_%s'%(permName,ntrk,ch)
                if len(comb)>0 : tag += '_' + comb
                
                print ' ...processing %s'%tag

                #base correct, signal PDF : free parameters are linear functions of the top mass
                ws.factory("RooFormulaVar::%s_p0('@0*(@1-172.5)+@2',{"
                           "slope_%s_p0[0.0],"
                           "mtop,"
                           "offset_%s_p0[0.4,0.1,0.9]})"%
                           (tag,tag,tag))
                ws.factory("RooFormulaVar::%s_p1('@0*(@1-172.5)+@2',{"
                           "slope_%s_p1[0.01,0,5],"
                           "mtop,"
                           "offset_%s_p1[40,5,150]})"%
                           (tag,tag,tag))
                ws.factory("RooFormulaVar::%s_p2('@0*(@1-172.5)+@2',{"
                           "slope_%s_p2[0.01,0.001,5],"
                           "mtop,"
                           "offset_%s_p2[15,5,100]})"%
                           (tag,tag,tag))
                ws.factory("RooFormulaVar::%s_p3('@0*(@1-172.5)+@2',{"
                           "slope_%s_p3[0.01,0.001,5],"
                           "mtop,"
                           "offset_%s_p3[25,5,100]})"%
                           (tag,tag,tag))
                ws.factory("RooFormulaVar::%s_p4('@0*(@1-172.5)+@2',{"
                           #"slope_%s_p4[0,-1,1],"
                           "slope_%s_p4[0],"
                           "mtop,"
                           "offset_%s_p4[5,-10,10]})"%
                           (tag,tag,tag))
                ws.factory("RooFormulaVar::%s_p5('@0*(@1-172.5)+@2',{"
                           #"slope_%s_p5[0.05,0,2],"
                           "slope_%s_p5[0],"
                           "mtop,"
                           "offset_%s_p5[10,0.5,100]})"%
                           (tag,tag,tag))
                ws.factory("RooFormulaVar::%s_p6('@0*(@1-172.5)+@2',{"
                           "slope_%s_p6[0.05,0,2],"
                           #"slope_%s_p6[0],"
                           "mtop,"
                           "offset_%s_p6[0.5,0.1,100]})"%
                           (tag,tag,tag))

                ws.factory("SUM::simplemodel_%s("
                           "%s_p0*RooBifurGauss::%s_f1("
                           "SVLMass,%s_p1,%s_p2,%s_p3),"
                           "RooGamma::%s_f2("
                           "SVLMass,%s_p4,%s_p5,%s_p6))"%
                           (tag,tag,tag,tag,tag,tag,tag,tag,tag,tag))

                #replicate the base signal PDF for different categories (top masses available)
                thePDF=ws.factory("SIMCLONE::model_%s( simplemodel_%s, $SplitParam({mtop},%s))"% (tag,tag,sig_mass_cats))

                #fix mass values and create a mapped data hist
                histMap=ROOT.MappedRooDataHist()
                for mass in massList:
                    mcat='%d'%int(mass*10)
                    massNodeVar=ws.var('mtop_m%s'%mcat)
                    massNodeVar.setVal(mass)
                    massNodeVar.setConstant(True)
                    binnedData=ws.data('SVLMass_%s_%s'%(tag,mcat))
                    histMap.add('m%s'%mcat,binnedData)
              
                #the categorized dataset
                getattr(ws,'import')( ROOT.RooDataHist("data_%s"%tag,
                                                       "data_%s"%tag,
                                                       ROOT.RooArgList(SVLmass),
                                                       ws.cat('massCat'),
                                                       histMap.get()) )
                theData=ws.data("data_%s"%tag)
                theFitResult = thePDF.fitTo(theData,ROOT.RooFit.Save(True))
                showFitResult(tag=tag,var=SVLmass,pdf=thePDF,data=theData,cat=ws.cat('massCat'),catNames=histMap.getCategories())


"""
Reads out the histograms from the picke file  converts them RooDataHist 
Prepare PDFs 
Save all to a RooWorkspace
"""
def createWorkspace(opt):

    #read file
    cachefile = open(opt.input,'r')
    inchistos  = pickle.load(cachefile)
    diffhistos = pickle.load(cachefile)
    cachefile.close()

    # Initiate a workspace where the observable is the SVLMass
    # and the variable to fit is mtop
    ws   = ROOT.RooWorkspace('w')
    SVLmass  = ws.factory('SVLMass[100,0,300]')
    mtop = ws.factory('mtop[172.5,100,200]')

    #import binned PDFs from histograms read from file
    chList=[]
    combList=[]
    massList=[]
    trkMultList=[]
    for key,histos in diffhistos.iteritems(): 

        chTags=key[0].split('_')
        chList.append( chTags[0] )

        combType=''
        if len(chTags)>1 : combType=chTags[1]
        combList.append(combType)

        massList.append( key[1] )

        for h in histos:
            hname=h.GetName()
            trkMultList.append( int(hname.split('_')[2]) )
            getattr(ws,'import')(ROOT.RooDataHist(hname,h.GetTitle(),ROOT.RooArgList(SVLmass),h))
        
    chList=list( set(chList) )
    combList=list( set(combList) )
    massList=list( set(massList) )
    trkMultList=list( set(trkMultList) )
    sig_mass_cats='massCat['
    for m in massList:
        sig_mass_cats+='m%d,'%int(m*10)
    sig_mass_cats = sig_mass_cats[:-1]+']'
    
    print 'Channels available :',chList
    print 'Combinations available: ',combList
    print 'Masses categories  available: ',sig_mass_cats
    print 'Track multiplicities available: ',trkMultList

    #run signal parameterization cycles
    parameterizeSignalPermutations(ws=ws,permName='cor',chList=chList,combList=combList,trkMultList=trkMultList,sig_mass_cats=sig_mass_cats,massList=massList,SVLmass=SVLmass)
    parameterizeSignalPermutations(ws=ws,permName='wro',chList=chList,combList=combList,trkMultList=trkMultList,sig_mass_cats=sig_mass_cats,massList=massList,SVLmass=SVLmass)
    parameterizeSignalPermutations(ws=ws,permName='unm',chList=chList,combList=combList,trkMultList=trkMultList,sig_mass_cats=sig_mass_cats,massList=massList,SVLmass=SVLmass)

    #save all to file
    ws.writeToFile('SVLWorkspace.root',True)
    print 80*'-'
    print 'Workspace has been created and stored @ SVLWorkspace.root'
    print 80*'-'

    return ws







    # Fraction
    #    ws.factory("RooFormulaVar::sig_frac('@0*(@1-172.5)+@2',{"
    #                  "a_sig_frac[0.,-2.0,2.0],"
    #                  "mtop,"
    #                 "b_sig_frac[0.90,0.0,1]})")



    # cov = fitresult.covarianceMatrix()
    # cor = fitresult.correlationMatrix()

    #
    # parameterization for wrong combinations
    #
 #   ws.factory("SUM::sig_wrong(sig_wrong_frac[0.9,0,1.0]*"
 #                  "BifurGauss::sig_wrong_agauss(mbl,"
 #                     "sig_wrong_agauss_mean[70,0,100],"
 #                     "sig_wrong_agauss_sigmaL[20,0,50],"
 #                     "sig_wrong_agauss_sigmaR[70,20,100]),"
 #                  "RooGamma::sig_wrong_ngauss(mbl,"
 #                     "sig_wrong_ngauss_gamma[3.2,2.5,4.0],"
 #                     "sig_wrong_ngauss_beta[14,10,20],"
 #                     "sig_wrong_ngauss_mu[8,0,15]))")
 #   # raw_input()
 #   ws.pdf('sig_wrong').fitTo(ws.data('wrong'), ROOT.RooFit.Save(True))
 #
 #   # These are the current values
#    ws.saveSnapshot("model_params", ws.allVars(), True)

    # Save workspace to file and return the name
#    wsFile = os.path.join(outdir, 'mSVL_Workspace_%s.root'%selection)
#    ws.writeToFile(wsFile)

#    return ws

"""

"""
def showFitResult(tag,var,pdf,data,cat,catNames):

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
        redData = data.reduce(ROOT.RooFit.Cut("massCat==massCat::%s"%catName))
        redData.plotOn(frame)
        cat.setLabel(catName)
        pdf.plotOn(frame,
                   ROOT.RooFit.Slice(cat,catName),
                   ROOT.RooFit.ProjWData(redData),
                   ROOT.RooFit.Components('*f1*'),
                   ROOT.RooFit.LineColor(920),
                   ROOT.RooFit.LineWidth(1))
        pdf.plotOn(frame,
                   ROOT.RooFit.Slice(cat,catName),
                   ROOT.RooFit.ProjWData(redData))
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
        massVal=float( catName.replace('m','') )/10.
        label.DrawLatex(0.6,0.86,'#it{m_{t}=%3.1f GeV}'%massVal)
        subTags=tag.split('_')
        permTitle='#it{correct permutations}'
        if subTags[0]=='wro' : permTitle='#it{wrong permutations}'
        if subTags[0]=='unm' : permTitle='#it{unmatched permutations}'
        label.DrawLatex(0.6,0.80,permTitle)
        channelTitle=subTags[2].replace('mu','#mu')
        channelTitle='#it{%s, %s tracks}'%(channelTitle,subTags[1])
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
        c.SaveAs("%s_%s.png"%(tag,catName))


def runPseudoExperiments(ws,peFileName,nTotal,fCorrect,nPexp):
    """
    run pseudo-experiments
    """

    #load the model parameters and set all to constant
    ws.loadSnapshot("model_params")
    allVars=ws.allVars()
    varIter = allVars.createIterator()
    var = varIter.Next()
    print 'Setting to constant:',
    while var :
        varName=var.GetName()
        if not varName in ['mtop', 'mbl']:
            ws.var(varName).setConstant(True)
            print varName,
        var = varIter.Next()

    #create the fit model
    ws.factory('nCorrect[%f,%f,%f]'%(nTotal*fCorrect,0,2*nTotal))
    ws.factory('nWrong[%f,%f,%f]'%(nTotal*(1-fCorrect),0,2*nTotal))
    ws.factory("SUM::mtopfit( nCorrect*sigmodel, nWrong*sig_wrong )")

    #pseudo-experiments
    wrongH=ws.data('wrong').createHistogram('mbl')
    wrongH.SetName('wrongH')
    fitBiasesH={}
    fitStatUncH={}
    fitPullH={}
    for mass in MASSES:
        iCat = str(mass).replace('.','')

        trueMtop=float(iCat.replace('m','').replace('v','.'))
        fitBiasesH[trueMtop]=ROOT.TH1F(iCat+'_biasH',';m_{t}-m_{t}^{true} [GeV];Pseudo-experiments',100,-2.02,1.98)
        fitBiasesH[trueMtop].SetDirectory(0)
        fitStatUncH[trueMtop]=ROOT.TH1F(iCat+'_statuncH',';#sigma(m_{t}) [GeV];Pseudo-experiments',200,0,2.0)
        fitStatUncH[trueMtop].SetDirectory(0)
        fitPullH[trueMtop]=ROOT.TH1F(iCat+'_pullH',';(m_{t}-m_{t}^{true})/#sigma(m_{t});Pseudo-experiments',100,-2.02,1.98)
        fitPullH[trueMtop].SetDirectory(0)

        #correct assignments for new top mass
        redData=ws.data('combcorrect').reduce( ROOT.RooFit.Cut("sig_mass_cats==sig_mass_cats::%s"%iCat) )
        correctH=redData.createHistogram('mbl')
        correctH.SetName(iCat+'correctH')

        pseudoDataH=correctH.Clone(iCat+'pseudoDataH')
        for i in xrange(0,nPexp):

            #generate new pseudo-data
            pseudoDataH.Reset('ICE')
            for nev in xrange(0,ROOT.gRandom.Poisson(nTotal*fCorrect))     : pseudoDataH.Fill(correctH.GetRandom())
            for nev in xrange(0,ROOT.gRandom.Poisson(nTotal*(1-fCorrect))) : pseudoDataH.Fill(wrongH.GetRandom())
            pseudoData=ROOT.RooDataHist('pseudoData','pseudoData',ROOT.RooArgList(ws.var('mbl')),pseudoDataH)

            ws.pdf('mtopfit').fitTo(pseudoData,ROOT.RooFit.Extended())
            mtopFit=ws.var('mtop')

            #create the likelihood
            #nll = ws.pdf('mtopfit').createNLL(pseudoData,ROOT.RooFit.Extended())
            #ROOT.RooMinuit(nll).migrad() ;

            #profile mtop
            #pll = nll.createProfile(ROOT.RooArgSet(ws.var('mtop')))
            #ROOT.RooMinuit(pll).migrad()
            #mtopFit=pll.bestFitObs().find('mtop')

            fitBiasesH[trueMtop].Fill(mtopFit.getVal()-trueMtop)
            fitStatUncH[trueMtop].Fill(mtopFit.getError())
            fitPullH[trueMtop].Fill((mtopFit.getVal()-trueMtop)/mtopFit.getError())

    #save results to a file
    peFile=ROOT.TFile(peFileName,'RECREATE')
    for cat in fitBiasesH:
        fitBiasesH[cat].Fit('gaus','LMQ+')
        fitBiasesH[cat].SetDirectory(peFile)
        fitBiasesH[cat].Write()
        fitStatUncH[cat].SetDirectory(peFile)
        fitStatUncH[cat].Write()
        fitPullH[cat].Fit('gaus','LMQ+')
        fitPullH[cat].SetDirectory(peFile)
        fitPullH[cat].Write()
    peFile.Close()


"""
steer
"""
def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-s', '--selection', dest='selection',
                       default='drrank',
                       help=('Selection type. [mrank, drrank, mrankinc, '
                             ' drrankinc, mrank12, drrank12]'))
    parser.add_option('-i', '--input', dest='input',
                       default='.svlhistos.pck',
                       help='input file with histograms.')
    parser.add_option('-w', '--ws', dest='wsFile', default=None,
                       help='ROOT file with previous workspace.')
    parser.add_option('-n', '--nPexp', dest='nPexp', default=250, type=int,
                       help='Total # pseudo-experiments.')
    parser.add_option('-t', '--nTotal', dest='nTotal', default=66290,
                       type=float, help='Total # events.')
    parser.add_option('-f', '--fCorrect', dest='fCorrect', default=0.75,
                       type=float, help='Fraction of correct assignments.')
    parser.add_option('-o', '--outDir', dest='outDir', default='svlfits',
                       help='Output directory [default: %default]')

    (opt, args) = parser.parse_args()

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gROOT.SetBatch(True)
    ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
    ROOT.AutoLibraryLoader.enable()
    ROOT.shushRooFit()
    ROOT.gROOT.ProcessLine("gErrorIgnoreLevel=kFatal") # see TError.h - gamma function prints lots of errors when scanning

    # Check if one needs to create a new workspace or run pseudo-experiments
    print 80*'-'
    if opt.wsFile is None :
        print 'Creating a new workspace file from %s'%opt.input
        ws = createWorkspace(opt)
    else:
        print 'Reading workspace file from %s'%opt.wsFile
        inF = ROOT.TFile.Open(opt.wsFile)
        ws = inF.Get('w')
        inF.Close()
    print 80*'-'


#    doPEs = True
#    if doPEs:
#        print 80*'-'
#        print ('Running pseudo-experiments for workspace retrieved from %s'
#                 % opt.wsFile)
#        runPseudoExperiments(ws=ws,
#                             peFileName=opt.wsFile.replace('.root','_pe.root'),
#                             nTotal=opt.nTotal,
#                             fCorrect=opt.fCorrect,
#                             nPexp=opt.nPexp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
