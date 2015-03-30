#!/usr/bin/env python
import ROOT
import os,sys
import optparse
import pickle
import numpy

from UserCode.TopMassSecVtx.PlotUtils import printProgress


"""
parameterize the signal permutations
"""
def fitSignalPermutation((ws, ch, ntrk, permName, massList, singleTop, bkg, SVLmass, options)):

    print ' ...processing ch=%s #tk=%d for %s permutations'%(ch,ntrk,permName)
    procName='tt'
    if singleTop : procName='t'
    if bkg       : procName='bg'
    tag='%s_%d_%s_%s'%(ch,ntrk,permName,procName)

    # Base correct, signal PDF :
    # free parameters are linear functions of the top mass
    ws.factory("RooFormulaVar::%s_p0('@0*(@1-172.5)+@2',{"
               "slope_%s_p0[0.0],"
               "mtop,"
               "offset_%s_p0[0.4,0.1,0.9]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p1('@0*(@1-172.5)+@2',{"
               "slope_%s_p1[0.01,0,5],"
               "mtop,"
               "offset_%s_p1[40,5,150]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p2('@0*(@1-172.5)+@2',{"
               "slope_%s_p2[0.01,0.001,5],"
               "mtop,"
               "offset_%s_p2[15,5,100]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p3('@0*(@1-172.5)+@2',{"
               "slope_%s_p3[0.01,0.001,5],"
               "mtop,"
               "offset_%s_p3[25,5,100]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p4('@0*(@1-172.5)+@2',{"
               #"slope_%s_p4[0,-1,1],"
               "slope_%s_p4[0],"
               "mtop,"
               "offset_%s_p4[5,-10,10]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p5('@0*(@1-172.5)+@2',{"
               #"slope_%s_p5[0.05,0,2],"
               "slope_%s_p5[0],"
               "mtop,"
               "offset_%s_p5[10,1,100]})"% (tag,tag,tag))
    ws.factory("RooFormulaVar::%s_p6('@0*(@1-172.5)+@2',{"
               "slope_%s_p6[0.05,0,2],"
               #"slope_%s_p6[0],"
               "mtop,"
               "offset_%s_p6[0.5,0.1,100]})"% (tag,tag,tag))

    # build the PDF
    sig_mass_cats=buildSigMassCats(massList,singleTop,permName)
    massCatName=sig_mass_cats.split('[')[0]
    thePDF,theData,catNames=None,None,None
    if 'unm' in tag:
        #freeze the top mass dependent slopes to 0 if unmatched permutations are in the tag
        print 'Freezing all mtop-dependent slopes for %s'%tag
        for i in xrange(0,6):
            ws.var('slope_%s_p%d'%(tag,i)).setVal(0)
            ws.var('slope_%s_p%d'%(tag,i)).setRange(0,0)
        ws.var('offset_%s_p4'%tag).setRange(2,100)
        ws.var('offset_%s_p5'%tag).setRange(1,100)

        thePDF = ws.factory("SUM::model_%s("
                            "%s_p0*RooBifurGauss::%s_f1(SVLMass,%s_p1,%s_p2,%s_p3),"
                            "RooGamma::%s_f2(SVLMass,%s_p4,%s_p5,%s_p6))"%
                            (tag,tag,tag,tag,tag,tag,tag,tag,tag,tag))
        theData=ws.data('SVLMass_%s_%s_%s_%d'%(permName,ch,procName,ntrk))
        catNames=['']
    else:
        #base PDF
        ws.factory("SUM::simplemodel_%s("
                   "%s_p0*RooBifurGauss::%s_f1(SVLMass,%s_p1,%s_p2,%s_p3),"
                   "RooGamma::%s_f2(SVLMass,%s_p4,%s_p5,%s_p6))"%
                   (tag,tag,tag,tag,tag,tag,tag,tag,tag,tag))

        if 'cor' in permName and singleTop==True:
            ws.var('slope_%s_p0'%tag).setRange(0,0)
            ws.var('offset_%s_p0'%tag).setRange(0.4,1.0)


        # Replicate the base signal PDF for different categories
        # (top masses available)
        thePDF = ws.factory("SIMCLONE::model_%s("
                            " simplemodel_%s, $SplitParam({mtop},%s))"%
                            (tag, tag, sig_mass_cats))

        # Fix mass values and create a mapped data hist
        histMap=ROOT.MappedRooDataHist()
        for mass in massList:
            mcat='%d'%int(mass*10)
            if not(mcat in sig_mass_cats): continue
            massNodeVar=ws.var('mtop_m%s'%mcat)
            massNodeVar.setVal(mass)
            massNodeVar.setConstant(True)
            binnedData=ws.data('SVLMass_%s_%s_%s_%s_%d'%(permName,ch,mcat,procName,ntrk))
            histMap.add('m%s'%mcat,binnedData)

        # The categorized dataset
        getattr(ws,'import')(
            ROOT.RooDataHist("data_%s"%tag,
                             "data_%s"%tag,
                             ROOT.RooArgList(SVLmass),
                             ws.cat(massCatName),
                             histMap.get()) )
        theData = ws.data("data_%s"%tag)
        catNames=histMap.getCategories()

    theFitResult = thePDF.fitTo(theData,ROOT.RooFit.Save(True))
    #theFitResult = thePDF.fitTo(theData,ROOT.RooFit.Save(True),ROOT.RooFit.SumW2Error(True))
    showFitResult(tag=tag, var=SVLmass, pdf=thePDF,
                  data=theData, cat=ws.cat(massCatName),
                  catNames=catNames,
                  outDir=options.outDir)

"""
instantiates the PDFs needed to parameterize the SVLmass histo in a given category for signal events
"""
def parameterizeSignalPermutations(ws,permName,config,SVLmass,options,singleTop,bkg=False):

    chselList,  massList, trkMultList, combList, procList = config
    print '[parameterizeSignalPermutations] with %s'%permName
    if singleTop:
        print ' \t single top quark mode enabled',
        if not ('t' in procList or 'tW' in procList):
            print ' but process not found in ',procList
            return
        print ''
    if bkg:
        print ' \t backgroumd mode enabled'

    tasklist = []
    for ch in chselList:
        # if ch != 'em' : continue
        for ntrk in trkMultList:
            tasklist.append((ws, ch, ntrk, permName, massList, singleTop, bkg, SVLmass, options))

    if options.jobs > 1:
        import multiprocessing
        multiprocessing.Pool(8).map(fitSignalPermutation, tasklist)
    else:
        for task in tasklist:
            fitSignalPermutation(task)

"""
Parameterizes the fraction of correct and wrong assignments
as well as the fraction of single top expected with respect to ttbar
"""
def parameterizeSignalFractions(ws, masshistos, config, options) :
    chselList,  massList, trkMultList, combList, procList = config
    print '[parameterizeSignalFractions]'

    canvas=ROOT.TCanvas('c','c',500,500)
    canvas.SetLeftMargin(0.15)
    canvas.SetRightMargin(0.05)
    for chsel in chselList:
        for trk in trkMultList:

            grToParametrize={}
            for key,title in [('ttcor','t#bar{t} correct'),
                              ('ttwro','t#bar{t} wrong'),
                              ('ttexp','t#bar{t} expected'),
                              ('tcor','t correct'),
                              ('tfrac','t / t#bar{t}')]:
                grCtr=len(grToParametrize)
                grToParametrize[key]=ROOT.TGraphErrors()
                grToParametrize[key].SetName(key)
                grToParametrize[key].SetTitle(title)
                grToParametrize[key].SetFillStyle(0)
                grToParametrize[key].SetMarkerStyle(20+grCtr)
                grToParametrize[key].SetLineColor(2*grCtr+1)
                grToParametrize[key].SetMarkerColor(2*grCtr+1)

            for mass in massList:

                combCtrs={}
                for comb in combList:
                    for proc in procList:

                        if proc!='tt' and not (mass in [166.5, 172.5, 178.5]): continue

                        #integrate events expected for this category and mass
                        h=None
                        try:
                            h=masshistos[(chsel,proc,mass,comb,trk)]
                        except:
                            continue
                        err=ROOT.Double(0)
                        val=h.IntegralAndError(1,h.GetXaxis().GetNbins(),err)

                        #add to counters
                        key = proc
                        if key != 'tt' : key ='t'
                        for combKey in [key+comb,key+'exp']:
                            if combKey in combCtrs:
                                combCtrs[combKey]  [0] += val
                                combCtrs[combKey]  [1] += err*err
                            else:
                                combCtrs[combKey]   = [val,err*err]

                #finalize errors
                for key in combCtrs: combCtrs[key][1]=ROOT.TMath.Sqrt(combCtrs[key][1])

                #normalize fractions by total expectations
                for proc in ['t','tt']:
                    for comb in combList:
                        try:
                            combCtrs[proc+comb][0] /= combCtrs[proc+'exp'][0]
                            combCtrs[proc+comb][1] /= combCtrs[proc+'exp'][0]
                        except:
                            pass
                if 'texp' in combCtrs:
                    combCtrs['tfrac']=(combCtrs['texp'][0]/combCtrs['ttexp'][0],
                                       ROOT.TMath.Sqrt( ROOT.TMath.Power(combCtrs['texp'][0]*combCtrs['ttexp'][1],2)
                                                      + ROOT.TMath.Power(combCtrs['ttexp'][0]*combCtrs['texp'][1],2) )
                                                      / ROOT.TMath.Power(combCtrs['ttexp'][0],2))

                #fill add point to the graph
                for key in combCtrs:
                    try:
                        np=grToParametrize[key].GetN()
                        grToParametrize[key].SetPoint     (np,mass,combCtrs[key][0])
                        grToParametrize[key].SetPointError(np,0,combCtrs[key][1])
                    except:
                        pass

            #extrapolate dependency with straight line and show
            for keys in [['ttcor','ttwro','tcor'],
                         ['tfrac'],
                         ['ttexp']]:
                canvas.Clear()
                drawOpt='ap'
                for key in keys:
                    if not(key in grToParametrize): continue
                    tag='%s_%s_%s'%(chsel,key,trk)
                    grToParametrize[key].Fit('pol1','Q+','same')
                    grToParametrize[key].Draw(drawOpt)
                    drawOpt='p'
                    grToParametrize[key].GetFunction('pol1').SetLineColor(grToParametrize[key].GetLineColor())
                    grToParametrize[key].GetXaxis().SetTitle("Top mass [GeV]")
                    grToParametrize[key].GetYaxis().SetTitleOffset(1.2)
                    if 'exp' in key:
                        grToParametrize[key].GetYaxis().SetTitle("Expected t#bar{t} events")
                        ws.factory("%s[%f]"%(tag,grToParametrize[key].GetFunction('pol1').Eval(172.5)))
                    elif 'frac' in key:
                        grToParametrize[key].GetYaxis().SetTitle('t / t#bar{t}')
                        ws.factory("RooFormulaVar::%s('%f+@0*(%f)',{mtop})"%
                                   (tag,grToParametrize[key].GetFunction('pol1').GetParameter(0),
                                        grToParametrize[key].GetFunction('pol1').GetParameter(1)))
                    else:
                        grToParametrize[key].GetYaxis().SetRangeUser(0,1)
                        grToParametrize[key].GetYaxis().SetTitle('Fraction wrt to t#bar{t} or t events')
                        ws.factory("RooFormulaVar::%s('%f+@0*(%f)',{mtop})"%
                                   (tag,grToParametrize[key].GetFunction('pol1').GetParameter(0),
                                        grToParametrize[key].GetFunction('pol1').GetParameter(1)))

                if drawOpt=='ap': continue
                leg=canvas.BuildLegend()
                leg.SetFillStyle(0)
                leg.SetTextFont(42)
                leg.SetBorderSize(0)
                leg.SetTextSize(0.03)
                leg.SetNColumns(2)
                label = ROOT.TLatex()
                label.SetNDC()
                label.SetTextFont(42)
                label.SetTextSize(0.035)
                channelTitle=chsel.replace('_',' ')
                label.DrawLatex(0.12,0.92,'#bf{CMS} #it{simulation}')
                label.DrawLatex(0.2,0.84,channelTitle)
                label.DrawLatex(0.2,0.8,'%d tracks'%trk)
                canvas.SaveAs('%s/plots/%s_%s.pdf'%(options.outDir,keys[0],tag))
                canvas.SaveAs('%s/plots/%s_%s.png'%(options.outDir,keys[0],tag))


"""
Extracts the channels, combinations, mass values, and
track multiplicity bins from the dictionary containing
the histograms.
"""
def readConfig(diffhistos):
    chselList, procList, massList, trkMultList, combList = [], [], [], [], []
    for key,histos in diffhistos.iteritems():
        try:
            if len(key)<5: continue
            if 'inclusive' in key[0]: continue
            if 'tot' in key[3]: continue

            chselList.append( key[0] )
            procList.append( key[1] )
            massList.append( key[2] )
            combList.append( key[3] )
            trkMultList.append( key[4] )
        except:
            print key

    chselList   = list( set(chselList) )
    massList    = sorted(list( set(massList) ))
    trkMultList = sorted(list( set(trkMultList) ))
    combList    = list( set(combList) )
    procList    = sorted(list(set(procList)) )
    return chselList, massList, trkMultList, combList, procList

"""
Creates a string with mass categories to be used
"""
def buildSigMassCats(massList,singleTop,permName):
    sig_mass_cats='massCat%s%d['%(permName,singleTop)
    if 'unm' in permName :
        sig_mass_cats+='minc]'
    else :
        for m in sorted(massList):
            if singleTop and not m in [166.5,172.5,178.5]: continue
            sig_mass_cats+='m%d,'%int(m*10)
        sig_mass_cats = sig_mass_cats[:-1]+']'
    return sig_mass_cats

"""
Reads out the histograms from the pickle file and converts them
to a RooDataHist
Prepare PDFs
Save all to a RooWorkspace
"""
def createWorkspace(options):

    # Read file
    cachefile = open(options.input,'r')
    masshistos = pickle.load(cachefile)
    cachefile.close()
    bkgmasshistos=None
    try:
        cachefile = open(options.inputBkg,'r')   
        bkgmasshistos = pickle.load(cachefile)
        cachefile.close()
    except:
        print 'No valid background shapes file found'

    # Extract the configurations from the diffhistos dictionary
    config = readConfig(masshistos)
    chselList, massList, trkMultList, combList,procList = config
    print 'Selected channels available :', chselList
    print 'Mass points available: ', massList
    print 'Track multiplicities available: ', trkMultList
    print 'Combinations available: ', combList
    print 'Processes available: ' , procList

    # Initiate a workspace where the observable is the SVLMass
    # and the variable to fit is mtop
    ws          = ROOT.RooWorkspace('w')
    SVLmass     = ws.factory('SVLMass[100,0,300]')
    mtop        = ws.factory('mtop[172.5,100,200]')
    sigStrength = ws.factory('mu[1.0,0.0,5.0]')

    # Import binned PDFs from histograms read from file
    for chsel in chselList:
        for trk in trkMultList:

            #backgrounds
            try:
                hbkg=bkgmasshistos[(chsel,trk)]
                name='SVLMass_unm_%s_bg_%d'%(chsel,trk)
                getattr(ws,'import')(ROOT.RooDataHist(name,name, ROOT.RooArgList(SVLmass), hbkg))
            except:
                pass

            #signal
            for comb in ['cor','wro']:
                for mass in massList:

                    #ttbar
                    htt=masshistos[(chsel,'tt',mass,comb,trk)]
                    getattr(ws,'import')(ROOT.RooDataHist(htt.GetName(), htt.GetTitle(), ROOT.RooArgList(SVLmass), htt))

                    #correct combinations for single top
                    if comb!='cor': continue
                    ht=None
                    for stProc in ['t','tbar','tW','tbarW']:
                        try:
                            h=masshistos[(chsel,stProc,mass,comb,trk)]
                            if ht is None:
                                ht=h.Clone("SVLMass_%s_%s_%d_t_%d"%(comb,chsel,10*mass,trk))
                            else:
                                ht.Add(h)
                        except:
                            pass
                    if ht is None : continue
                    getattr(ws,'import')(ROOT.RooDataHist(ht.GetName(), ht.GetTitle(), ROOT.RooArgList(SVLmass), ht))

            #unmatched for tt and wrong+unmatched for single top are merged
            htt_unm, ht_wrounm = None, None
            for mass in massList:
                htt=masshistos[(chsel,'tt',mass,'unm',trk)]
                if htt_unm is None : htt_unm=htt.Clone("SVLMass_unm_%s_tt_%d"%(chsel,trk))
                else               : htt_unm.Add(htt)

                for comb in ['unm','wro']:
                    for stProc in ['t','tbar','tW','tbarW']:
                        try:
                            h=masshistos[(chsel,stProc,mass,comb,trk)]
                            if ht_wrounm is None : ht_wrounm=h.Clone("SVLMass_wrounm_%s_t_%d"%(chsel,trk))
                            else                 : ht_wrounm.Add(h)
                        except:
                            pass
            if not (htt_unm is None):
                getattr(ws,'import')(ROOT.RooDataHist(htt_unm.GetName(), htt_unm.GetTitle(),
                                     ROOT.RooArgList(SVLmass), htt_unm))
            if not (ht_wrounm is None):
                getattr(ws,'import')(ROOT.RooDataHist(ht_wrounm.GetName(), ht_wrounm.GetTitle(),
                                     ROOT.RooArgList(SVLmass), ht_wrounm))


    # Run signal parameterization cycles
    parameterizeSignalFractions(ws=ws, config=config, masshistos=masshistos, options=options)
    parameterizeSignalPermutations(ws=ws, permName='cor', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=False)
    parameterizeSignalPermutations(ws=ws, permName='wro', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=False)
    parameterizeSignalPermutations(ws=ws, permName='unm', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=False)
    parameterizeSignalPermutations(ws=ws, permName='cor', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=True)
    parameterizeSignalPermutations(ws=ws, permName='wrounm', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=True)
    parameterizeSignalPermutations(ws=ws, permName='unm', config=config,
                                   SVLmass=SVLmass, options=options, singleTop=False, bkg=True)

    # Save all to file
    ws.saveSnapshot("model_params", ws.allVars(), True)
    ws.writeToFile(os.path.join(options.outDir, 'SVLWorkspace.root'), True)
    print 80*'-'
    print 'Workspace has been created and stored @ SVLWorkspace.root'
    print 80*'-'

    return ws


"""
Displays the results of the PDF fits for a list of categories
"""
def showFitResult(tag,var,pdf,data,cat,catNames,outDir):

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
        if len(catName)>0 :
            redData = data.reduce(ROOT.RooFit.Cut("%s==%s::%s"%(cat.GetName(),cat.GetName(),catName)))
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
        else:
            data.plotOn(frame)
            pdf.plotOn(frame,
                       ROOT.RooFit.ProjWData(data),
                       ROOT.RooFit.Components('*f1*'),
                       ROOT.RooFit.LineColor(920),
                       ROOT.RooFit.LineWidth(1))
            pdf.plotOn(frame,
                       ROOT.RooFit.ProjWData(data))

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
        if len(catName)>0:
            massVal=float( catName.replace('m','') )/10.
            label.DrawLatex(0.6,0.86,'#it{m_{t}=%3.1f GeV}'%massVal)
        subTags=tag.split('_')
        permTitle=''
        if 'cor' in subTags : '#it{correct permutations}'
        if 'wro' in subTags : permTitle='#it{wrong permutations}'
        if 'unm' in subTags : 
            permTitle='#it{unmatched permutations}'
            if 'wro' in subTags : permTitle='#it{wrong+unmatched permutations}'
        if 'bg'  in subTags : permTitle='#it{background}'
        label.DrawLatex(0.6,0.80,permTitle)
        channelTitle=subTags[0].replace('m','#mu')
        ntracks = subTags[1] if subTags[1].isdigit() else subTags[2]
        selCat = subTags[1] if not subTags[1].isdigit() else 'inclusive'
        channelTitle='#it{%s %s, %s tracks}'%(channelTitle,selCat,ntracks)
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
        plotdir = os.path.join(outDir, 'plots')
        os.system('mkdir -p %s' % plotdir)
        for ext in ['png', 'pdf']:
            c.SaveAs(os.path.join(plotdir, "%s_%s.%s"%(tag,catName,ext)))

    c.Clear()
    c.Delete()

"""
Show fit result
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
    nll.plotOn(frame2,ROOT.RooFit.ShiftToZero())
    frame2.Draw()
    frame2.GetYaxis().SetRangeUser(0,12)
    frame2.GetXaxis().SetRangeUser(165,180)
    frame2.GetYaxis().SetNdivisions(3)
    frame2.GetXaxis().SetNdivisions(3)
    frame2.GetXaxis().SetTitle('Top mass [GeV]')
    frame2.GetYaxis().SetTitle('-log L/L_{max}')
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
def runPseudoExperiments(ws,experimentTag,options):

    #read the file with input distributions
    inputDistsF=ROOT.TFile.Open(options.input)
    print '[runPseudoExperiments] with %s' % experimentTag

    #FIXME: correct if another mass is being used
    genMtop=172.5

    #load the model parameters and set all to constant
    ws.loadSnapshot("model_params")
    allVars = ws.allVars()
    varIter = allVars.createIterator()
    var = varIter.Next()
    varCtr=0
    while var :
        varName=var.GetName()
        if not varName in ['mtop', 'SVLMass','mu']:
            ws.var(varName).setConstant(True)
            varCtr+=1
        var = varIter.Next()
    print '[runPseudoExperiments] setting to constant %d numbers in the model'%varCtr

    #build the relevant PDFs
    allPdfs = {}
    for chsel in ['em','mm','ee','m','e']:
        for ntrk in [2,3,4]:
            ttexp      = '%s_ttexp_%s'              %(chsel,ntrk)
            ttcor      = '%s_ttcor_%s'              %(chsel,ntrk)
            ttcorPDF   = 'simplemodel_%s_%d_cor_tt' %(chsel,ntrk)
            ttwro      = '%s_ttwro_%s'              %(chsel,ntrk)
            ttwroPDF   = 'simplemodel_%s_%d_wro_tt' %(chsel,ntrk)
            ttunmPDF   = 'model_%s_%d_unm_tt'       %(chsel,ntrk)
            tfrac      = '%s_tfrac_%s'              %(chsel,ntrk)
            tcor       = '%s_tcor_%s'               %(chsel,ntrk)
            tcorPDF    = 'simplemodel_%s_%d_cor_t'  %(chsel,ntrk)
            twrounmPDF = 'model_%s_%d_wrounm_t'     %(chsel,ntrk)

            ttShapePDF = ws.factory("SUM::ttshape_%s_%d(%s*%s,%s*%s,%s)"%(chsel,ntrk,ttcor,ttcorPDF,ttwro,ttwroPDF,ttunmPDF))
            Ntt        = ws.factory("RooFormulaVar::Ntt_%s_%d('@0*@1',{mu,%s})"%(chsel,ntrk,ttexp))

            tShapePDF  = ws.factory("SUM::tshape_%s_%d(%s*%s,%s)"%(chsel,ntrk,tcor,tcorPDF,twrounmPDF))
            Nt         = ws.factory("RooFormulaVar::Nt_%s_%d('@0*@1*@2',{mu,%s,%s})"%(chsel,ntrk,ttexp,tfrac))

            allPdfs[ (chsel,ntrk) ] = ws.factory("SUM::model_%s_%d( %s*%s, %s*%s )"%(chsel,ntrk,
                                                                         Ntt.GetName(), ttShapePDF.GetName(),
                                                                         Nt.GetName(), tShapePDF.GetName()))

    #throw pseudo-experiments
    allFitVals  = {('comb',0):[], ('comb_mu',0):[]}
    allFitErrs  = {('comb',0):[], ('comb_mu',0):[]}
    allFitPulls = {('comb',0):[], ('comb_mu',0):[]}
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
            pseudoData  = ROOT.RooDataHist('PseudoData_%s_%d'%(chsel,trk),
                                           'PseudoData_%s_%d'%(chsel,trk),
                                           ROOT.RooArgList(ws.var('SVLMass')), pseudoDataH)

            #fit and generate likelihood for combination
            allPdfs[key].fitTo(pseudoData, ROOT.RooFit.Extended())

            allNLL.append(allPdfs[key].createNLL(pseudoData,ROOT.RooFit.Extended()))
            ROOT.RooMinuit(allNLL[-1]).migrad()

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
               showFinalFitResult(data=pseudoData,pdf=allPdfs[key],nll=allNLL[-1],
                                  SVLMass=ws.var('SVLMass'),mtop=ws.var('mtop'),
                                  outDir=options.outDir)
               # raw_input('press key to continue...')

            #save to erase later
            allPseudoDataH.append(pseudoDataH)
            allPseudoData.append(pseudoData)

        #combined likelihood
        llSet = ROOT.RooArgSet()
        for ll in allNLL: llSet.add(ll)
        combll = ROOT.RooAddition("combll","combll",llSet)
        ROOT.RooMinuit(combll).migrad()
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
    peFile=ROOT.TFile(os.path.join(options.outDir,'%s_results.root'%experimentTag), 'RECREATE')
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
        fitCorrH = ROOT.TH2F('muvsmtopcorr_%s_%d'%(chsel,trk),';Top quark mass [GeV];#mu=#sigma/#sigma_{th}(172.5 GeV);Pseudo-experiments',200,150,200,100,0.5,1.5)
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

"""
steer
"""
def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-i', '--input', dest='input',
                       default='.svlmasshistos.pck',
                       help='input file with histograms.')
    parser.add_option('-b', '--bkg', dest='inputBkg',
                       default='.svlbgtemplates.pck',
                       help='input file with histograms for the background processes.')
    parser.add_option('-w', '--ws', dest='wsFile', default=None,
                       help='ROOT file with previous workspace.')
    parser.add_option('--isData', dest='isData', default=False, action='store_true',
                       help='if true, final fit is performed')
    parser.add_option('--spy', dest='spy', default=False, action='store_true',
                       help='if true,shows fit results on the screen')
    parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int,
                       help='Verbose mode')
    parser.add_option('-n', '--nPexp', dest='nPexp', default=100, type=int,
                       help='Total # pseudo-experiments.')
    parser.add_option('-j', '--jobs', dest='jobs', default=1,
                       type=int, help='Run n jobs in parallel')
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

    os.system('mkdir -p %s' % opt.outDir)
    os.system('mkdir -p %s' % os.path.join(opt.outDir, 'plots'))

    # Check if one needs to create a new workspace or run pseudo-experiments
    print 80*'-'
    if opt.wsFile is None :
        print 'Creating a new workspace file from %s'%opt.input
        ws = createWorkspace(options=opt)
        return 0
    else:
        print 'Reading workspace file from %s'%opt.wsFile
        inF = ROOT.TFile.Open(opt.wsFile)
        ws = inF.Get('w')
        inF.Close()
    print 80*'-'

    # launch pseudo-experiments
    if not opt.isData :
        print 'Running pseudo-experiments using PDFs and signal expectations'

        runPseudoExperiments(ws=ws, options=opt, experimentTag='nominal')
        return 0

        ## Get the experimentTag's from the PE input file:
        peInputFile = ROOT.TFile.Open(opt.input, 'READ')
        allTags = [tkey.GetName() for tkey in peInputFile.GetListOfKeys()]
        print allTags

        ## loop over them, run them in parallel (batch?)

    else:
        print 'Ready to unblind?'
        print '...ah ah this is not even implemented'
        return -1
    print 80*'-'
    return 0



if __name__ == "__main__":
    sys.exit(main())
