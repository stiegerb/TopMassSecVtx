#! /usr/bin/env python
import ROOT
import os,sys
import pickle
import optparse
from UserCode.TopMassSecVtx.KinematicsMoments import defineBinsOfInterest,analyzeCorrelationOfMoments
from UserCode.TopMassSecVtx.PlotUtils import setTDRStyle
from UserCode.TopMassSecVtx.rounding import *
import numpy
import math
import scipy.optimize as optimization

def linearFunc(x, offset, slope) : return offset + slope*x

SYSTS=[ 
    ['Pileup',                ['ttbar_puup',     'ttbar_pudn'],         'calib'],
    ['Lepton selection',      ['ttbar_lepselup', 'ttbar_lepseldn'],     'calib'],
    ['Lepton energy scale',   ['ttbar_lesup',    'ttbar_lesdn'],        'calib'],
    ['Jet energy scale',      ['ttbar_jesup',    'ttbar_jesdn'],        'calib'],
    ['Jet energy resolution', ['ttbar_jerup',    'ttbar_jerdn'],        'calib'],
    ['B-tag efficiency',      ['ttbar_btagup',   'ttbar_btagdn'],       'calib'],
    ['Mistag rate',           ['ttbar_mistagup', 'ttbar_mistagdn'],     'calib'],
    ['Top p_{t}',             ['ttbar_toppt'],                          'calib'],
    ['ME-PS',                 ['ttbar_mepsdn',     'ttbar_mepsup'],     'calib'],
    ['t#bar{t} Q^{2}',        ['ttbar_qcdscaledn', 'ttbar_qcdscaleup'], 'calib'],
    ['tW Q^{2}',              ['tW_qcdscaledn',    'tW_qcdscaleup'],    'calib'],
    ['UE',                    ['ttbar_p11tev',     'ttbar_p11mpihi'],   'ttbar_p11'],
    ['CR',                    ['ttbar_p11nocr'],                        'ttbar_p11'],
    ['NLO',                   ['ttbar_nlo'],                            'calib'],
    ['tW DS',                 ['tW_int'],                               'calib'],
    ['tW norm',               ['tW_up','tW_dn'],                        'calib'],
    ['Bkg. norm',             ['otherbg_up','otherbg_dn'],              'calib'],
    ['PDF',                   [],                                       'calib'],
    ]
for i in xrange(1,52): SYSTS[-1][1].append('ttbar_pdf%d'%i)

OBSERVABLES=[ 
 #   ['O^{1} p_{T}(+)',          ('#splitline{#scale[0.6]{ptpos}}{O^{1}}',    '#splitline{#scale[0.6]{ptpos}}{O^{2}}',    '#splitline{#scale[0.6]{ptpos}}{O^{0}}')],
 #   ['O^{2} p_{T}(+)',          ('#splitline{#scale[0.6]{ptpos}}{O^{2}}',    '#splitline{#scale[0.6]{ptpos}}{O^{4}}',    '#splitline{#scale[0.6]{ptpos}}{O^{0}}')],
 #   ['O^{1} E(+)',              ('#splitline{#scale[0.6]{enpos}}{O^{1}}',    '#splitline{#scale[0.6]{enpos}}{O^{2}}',    '#splitline{#scale[0.6]{enpos}}{O^{0}}')],
#    ['O^{2} E(+)',              ('#splitline{#scale[0.6]{enpos}}{O^{2}}',    '#splitline{#scale[0.6]{enpos}}{O^{4}}',    '#splitline{#scale[0.6]{enpos}}{O^{0}}')],
#    ['O^{1} p_{T}(+)+p_{T}(-)', ('#splitline{#scale[0.6]{ptposptm}}{O^{1}}', '#splitline{#scale[0.6]{ptposptm}}{O^{2}}', '#splitline{#scale[0.6]{ptposptm}}{O^{0}}')],
#    ['O^{2} p_{T}(+)+p_{T}(-)', ('#splitline{#scale[0.6]{ptposptm}}{O^{2}}', '#splitline{#scale[0.6]{ptposptm}}{O^{4}}', '#splitline{#scale[0.6]{ptposptm}}{O^{0}}')],
    ['O^{1} p_{T}(ll)',         ('#splitline{#scale[0.6]{ptll}}{O^{1}}',     '#splitline{#scale[0.6]{ptll}}{O^{2}}',     '#splitline{#scale[0.6]{ptll}}{O^{0}}')],
    ['O^{2} p_{T}(ll)',         ('#splitline{#scale[0.6]{ptll}}{O^{2}}',     '#splitline{#scale[0.6]{ptll}}{O^{4}}',     '#splitline{#scale[0.6]{ptll}}{O^{0}}')],
#    ['O^{1} M(ll)',             ('#splitline{#scale[0.6]{mll}}{O^{1}}',      '#splitline{#scale[0.6]{mll}}{O^{2}}',      '#splitline{#scale[0.6]{mll}}{O^{0}}')],
#    ['O^{2} M(ll)',             ('#splitline{#scale[0.6]{mll}}{O^{2}}',      '#splitline{#scale[0.6]{mll}}{O^{4}}',      '#splitline{#scale[0.6]{mll}}{O^{0}}')],
#    ['O^{1} E(+)+E(-)',         ('#splitline{#scale[0.6]{EposEm}}{O^{1}}',   '#splitline{#scale[0.6]{EposEm}}{O^{2}}',   '#splitline{#scale[0.6]{EposEm}}{O^{0}}')],
#    ['O^{2} E(+)+E(-)',         ('#splitline{#scale[0.6]{EposEm}}{O^{2}}',   '#splitline{#scale[0.6]{EposEm}}{O^{4}}',   '#splitline{#scale[0.6]{EposEm}}{O^{0}}')],
    ]

"""
show calibration curves
"""
def prepareCalibration(opt,file_list):
    
    binsOfInterest=[]

    #
    # MASS SCAN
    #

    #tW 
    tW_MassScan={}
    for mass,tagList in [
        [166.5,('MC8TeV_SingleTbar_tW_166v5', 'MC8TeV_SingleT_tW_166v5')],
        [172.5,('MC8TeV_SingleTbar_tW',       'MC8TeV_SingleT_tW')],
        [178.5,('MC8TeV_SingleTbar_tW_178v5', 'MC8TeV_SingleT_tW_178v5')],
        ]:
        tW_Corr={}
        for tag in tagList:
            url,xsecWgt=file_list[tag]
            fIn=ROOT.TFile.Open(url)
            for key in fIn.GetListOfKeys():
                varName=key.GetName().replace(opt.tier,'')
                obj=fIn.Get('%s%s/obscorr%s%s'%(varName,opt.tier,varName,opt.tier))
                if not obj: continue
                obj.Scale(xsecWgt)
                if not varName in tW_Corr:
                    tW_Corr[varName]=obj.Clone()
                    tW_Corr[varName].SetDirectory(0)
                else:
                    tW_Corr[varName].Add(obj)
            fIn.Close()
        if len(binsOfInterest)==0 : binsOfInterest=defineBinsOfInterest(tW_Corr['nominal'],OBSERVABLES)
        tW_MassScan[mass]=tW_Corr
    print binsOfInterest
    #ttbar
    ttbar_MassScan={}
    for mass,tagList in [                 
        [166.5,('MC8TeV_TTJets_MSDecays_166v5',)],
        [169.5,('MC8TeV_TTJets_MSDecays_169v5',)],
        [171.5,('MC8TeV_TTJets_MSDecays_171v5',)],
        [172.5,('MC8TeV_TTJets_MSDecays_172v5',)], 
        [173.5,('MC8TeV_TTJets_MSDecays_173v5',)],
        [175.5,('MC8TeV_TTJets_MSDecays_175v5',)],
        [178.5,('MC8TeV_TTJets_MSDecays_178v5',)]
        ]:
        
        ttbarCorr={}
        for tag in tagList:
            url,xsecWgt=file_list[tag]
            fIn=ROOT.TFile.Open(url)
            for key in fIn.GetListOfKeys():
                varName=key.GetName().replace(opt.tier,'')
                obj=fIn.Get('%s%s/obscorr%s%s'%(varName,opt.tier,varName,opt.tier))
                if not obj: continue
                obj.Scale(xsecWgt)
                if not varName in ttbarCorr:
                    ttbarCorr[varName]=obj.Clone()
                    ttbarCorr[varName].SetDirectory(0)
                else:
                    ttbarCorr[varName].Add(obj)
            fIn.Close()
        ttbar_MassScan[mass]=ttbarCorr

    #derive calibration curves
    mtopCalib={}
    for obsTitle,muBin,stdBin,ctrBin in binsOfInterest:

        #interpolate the tW simulations
        x_tW, yn_tW, yobs_tW, sigman_tW,sigmaobs_tW=[],[],[],[],[]
        for mass in tW_MassScan:
            n=tW_MassScan[mass]['nominal'].GetBinContent(ctrBin,ctrBin)
            nerr=tW_MassScan[mass]['nominal'].GetBinError(ctrBin,ctrBin)
            mu=tW_MassScan[mass]['nominal'].GetBinContent(ctrBin,muBin)/n
            std=math.sqrt(tW_MassScan[mass]['nominal'].GetBinContent(ctrBin,stdBin)/n-mu**2)/(n/nerr)
            x_tW.append( mass )
            yn_tW.append( n )
            sigman_tW.append( nerr )
            yobs_tW.append( mu )
            sigmaobs_tW.append( std )
        tWobsParam = numpy.array([0.0,0.0])
        tWobsParam = optimization.curve_fit(linearFunc, numpy.array(x_tW), numpy.array(yobs_tW), tWobsParam, numpy.array(sigmaobs_tW))[0]
        tWnParam   = numpy.array([0.0,0.0])
        tWnParam   = optimization.curve_fit(linearFunc, numpy.array(x_tW), numpy.array(yn_tW),   tWnParam,   numpy.array(sigman_tW))[0]

        #interpolate the ttbar simulations
        x_ttbar, yn_ttbar, yobs_ttbar, sigman_ttbar,sigmaobs_ttbar=[],[],[],[],[]
        for mass in ttbar_MassScan:
            n=ttbar_MassScan[mass]['nominal'].GetBinContent(ctrBin,ctrBin)
            nerr=ttbar_MassScan[mass]['nominal'].GetBinError(ctrBin,ctrBin)
            mu=ttbar_MassScan[mass]['nominal'].GetBinContent(ctrBin,muBin)/n
            std=math.sqrt(ttbar_MassScan[mass]['nominal'].GetBinContent(ctrBin,stdBin)/n-mu**2)/(n/nerr)
            x_ttbar.append( mass )
            yn_ttbar.append( n )
            sigman_ttbar.append( nerr )
            yobs_ttbar.append( mu )
            sigmaobs_ttbar.append( std )
        ttbarobsParam = numpy.array([0.0,0.0])
        ttbarobsParam = optimization.curve_fit(linearFunc, numpy.array(x_ttbar), numpy.array(yobs_ttbar), ttbarobsParam, numpy.array(sigmaobs_ttbar))[0]
        ttbarnParam   = numpy.array([0.0,0.0])
        ttbarnParam   = optimization.curve_fit(linearFunc, numpy.array(x_ttbar), numpy.array(yn_ttbar),   ttbarnParam,   numpy.array(sigman_ttbar))[0]

        #get calibration
        mtopCalib[obsTitle]=showMomentCalibration(
            tW     = [x_tW,    yobs_tW,    sigmaobs_tW,    tWobsParam,    tWnParam],
            ttbar  = [x_ttbar, yobs_ttbar, sigmaobs_ttbar, ttbarobsParam, ttbarnParam],
            title  = obsTitle,
            outDir = opt.output
            )

    #build syst scan
    systScan={}
    systVariationsToUse = [ ['calib',              ()],
                            ['ttbar_puup',         ()],
                            ['ttbar_pudn',         ()],
                            ['ttbar_lepselup',     ()],
                            ['ttbar_lepseldn',     ()],
                            ['ttbar_lesup',        ()],
                            ['ttbar_lesdn',        ()],
                            ['ttbar_jesup',        ()],
                            ['ttbar_jesdn',        ()],  
                            ['ttbar_jerup',        ()],
                            ['ttbar_jerdn',        ()], 
                            ['ttbar_btagup',       ()],
                            ['ttbar_btagdn',       ()],
                            ['ttbar_mistagup',     ()],
                            ['ttbar_mistagdn',     ()],
                            ['ttbar_toppt',        ()],
                            ['ttbar_mepsup',       ('MC8TeV_TTJets_MSDecays_matchingup',)],
                            ['ttbar_mepsdn',       ('MC8TeV_TTJets_MSDecays_matchingdown','MC8TeV_TTJets_MSDecays_matchingdown_v2')],
                            ['ttbar_qcdscaleup',   ('MC8TeV_TTJets_MSDecays_scaleup',)],
                            ['ttbar_qcdscaledn',   ('MC8TeV_TTJets_MSDecays_scaledown',)],        
                            ['ttbar_p11',          ('MC8TeV_TTJets_TuneP11',)],
                            ['ttbar_p11tev',       ('MC8TeV_TTJets_TuneP11TeV',)],
                            ['ttbar_p11mpihi',     ('MC8TeV_TTJets_TuneP11mpiHi',)],
                            ['ttbar_p11nocr',      ('MC8TeV_TTJets_TuneP11noCR',)],
                            ['ttbar_nlo',          ('MC8TeV_TT_Z2star_powheg_pythia',)],
                            ['tW_qcdscaleup',      ('MC8TeV_SingleTbar_tW_scaleup','MC8TeV_SingleT_tW_scaleup',)],
                            ['tW_qcdscaledn',    ('MC8TeV_SingleTbar_tW_scaledown','MC8TeV_SingleT_tW_scaledown',)],
                            ['tW_int',             ('MC8TeV_SingleTbar_tW_DS','MC8TeV_SingleT_tW_DS',)],
                            ['tW_up',              ()],
                            ['tW_dn',            ()],
                            ['otherbg_up',         ('MC8TeV_DY1JetsToLL_50toInf',  'MC8TeV_DY3JetsToLL_50toInf',  'MC8TeV_DYJetsToLL_10to50', 'MC8TeV_DY2JetsToLL_50toInf', 'MC8TeV_DY4JetsToLL_50toInf',  'MC8TeV_DYJetsToLL_50toInf')],
                            ['otherbg_dn',         ('MC8TeV_DY1JetsToLL_50toInf',  'MC8TeV_DY3JetsToLL_50toInf',  'MC8TeV_DYJetsToLL_10to50', 'MC8TeV_DY2JetsToLL_50toInf', 'MC8TeV_DY4JetsToLL_50toInf',  'MC8TeV_DYJetsToLL_50toInf')],
                            ]
    for i in xrange(1,52): systVariationsToUse.append( ['ttbar_pdf%d'%i,()] )

    for syst,tagList in systVariationsToUse:

        icorr={}
        for tag in tagList:
            url,xsecWgt=file_list[tag]
            fIn=ROOT.TFile.Open(url)         
            for key in fIn.GetListOfKeys():
                varName=key.GetName().replace(opt.tier,'')
                obj=fIn.Get('%s%s/obscorr%s%s'%(varName,opt.tier,varName,opt.tier))
                if not obj: continue
                obj.Scale(xsecWgt)
                if not varName in icorr:
                    icorr[varName]=obj.Clone()
                    icorr[varName].SetDirectory(0)
                else:
                    icorr[varName].Add(obj)
            fIn.Close()
            
        #init with ttbar
        ttbarH = ttbar_MassScan[172.5]['nominal']
        if 'ttbar_' in syst:
            systName=syst.split('_')[1]
            if systName in ttbar_MassScan[172.5]:
                ttbarH=ttbar_MassScan[172.5][systName]
            elif 'nominal' in icorr:                
                ttbarH=icorr['nominal']
        totalH = ttbarH.Clone('total_%s'%syst)
        
        #add tW
        tWH = tW_MassScan[172.5]['nominal']    
        if 'tW_up' == syst     : 
            totalH.Add(tWH,1.07)
        elif 'tW_dn' == syst : 
            totalH.Add(tWH,0.93)
        elif 'tW_' in syst     :             
            tWH=icorr['nominal']
            totalH.Add(tWH)
        else:
            totalH.Add(tWH)
        
        #background variations
        if 'otherbg_up'==syst:
            totalH.Add(icorr['nominal'],0.2)
        elif 'otherbg_dn'==syst:
            totalH.Add(icorr['nominal'],-0.2)

        #save
        totalH.SetDirectory(0)
        systScan[syst]=totalH

    systsTable=[]
    for obsTitle,muBin,stdBin,ctrBin in binsOfInterest:

        systsTable.append( [obsTitle, [] ] )
        for systTitle,systVars,refVar in SYSTS:
            
            refMu,mtopRef=0,172.5
            if refVar in systScan :
                refMu=systScan[refVar].GetBinContent(ctrBin,muBin)/systScan[refVar].GetBinContent(ctrBin,ctrBin)
                mtopRef=mtopCalib[obsTitle].GetX(refMu)

            if systTitle=='PDF':
                
                refMu=systScan['ttbar_pdf1'].GetBinContent(ctrBin,muBin)/systScan['ttbar_pdf1'].GetBinContent(ctrBin,ctrBin)
                mtopRef=mtopCalib[obsTitle].GetX(refMu)

                #cf http://www.hep.ucl.ac.uk/pdf4lhc/PDF4LHC_practical_guide.pdf#2
                upVar,dnVar=0,0
                for i in xrange(0,len(systVars)/2):

                    systUp=systVars[2*i+1]
                    mtopUp=mtopCalib[obsTitle].GetX( systScan[systUp].GetBinContent(ctrBin,muBin)/systScan[systUp].GetBinContent(ctrBin,ctrBin) )
                    systDn=systVars[2*i+2]
                    mtopDn=mtopCalib[obsTitle].GetX( systScan[systDn].GetBinContent(ctrBin,muBin)/systScan[systDn].GetBinContent(ctrBin,ctrBin) )
                    
                    #upVar += ROOT.TMath.Max(mtopUp-mtopRef,mtopDn-mtopRef)**2
                    #dnVar += ROOT.TMath.Max(mtopRef-mtopUp,mtopRef-mtopDn)**2
                    
                    upVar += (mtopUp-mtopDn)**2
                    dnVar += (mtopUp-mtopDn)**2


                c90=1.64485
                upVar=0.5*ROOT.TMath.Sqrt(upVar)/c90
                dnVar=0.5*ROOT.TMath.Sqrt(dnVar)/c90
                systsTable[-1][1].append( (systTitle,upVar,-dnVar) )
            else:
                upVar,dnVar=0,0
                systCtr=0
                for syst in systVars:
                    systCtr+=1
                    diffVal=systScan[syst].GetBinContent(ctrBin,muBin)/systScan[syst].GetBinContent(ctrBin,ctrBin)
                    diffMtop=mtopCalib[obsTitle].GetX(diffVal)-mtopRef
                    if systCtr==1 : upVar = diffMtop
                    else : dnVar=diffMtop

                systsTable[-1][1].append( (systTitle,upVar,dnVar) )
    printSystsTable(systsTable,outDir=opt.output)


    if not opt.unblind : return
    print 'Results in data'
   
    #build the background to subtract
    bgList=('MC8TeV_DYJetsToLL_50toInf', 'MC8TeV_DY1JetsToLL_50toInf', 'MC8TeV_DY2JetsToLL_50toInf', 'MC8TeV_DY3JetsToLL_50toInf', 'MC8TeV_DY4JetsToLL_50toInf','MC8TeV_DYJetsToLL_10to50',
            'MC8TeV_SingleT_s', 'MC8TeV_SingleTbar_s',
            'MC8TeV_SingleT_t', 'MC8TeV_SingleTbar_t',
            'MC8TeV_WJets', 'MC8TeV_W1Jets', 'MC8TeV_W2Jets', 'MC8TeV_W3Jets', 'MC8TeV_W4Jets',
            'MC8TeV_WW', 'MC8TeV_WZ', 'MC8TeV_ZZ',
            'MC8TeV_TTWJets', 'MC8TeV_TTZJets'
            )
    bgH=None
    for tag in bgList:
        url,xsecWgt=file_list[tag]
        fIn=ROOT.TFile.Open(url)         
        obj=fIn.Get('nominal%s/obscorrnominal%s'%(opt.tier,opt.tier))
        obj.Scale(xsecWgt)
        if bgH is None:
            bgH=obj.Clone('bg')
            bgH.SetDirectory(0)
        else:
            bgH.Add(obj)
        fIn.Close()
    bgH.Scale(opt.lumi)

    #build the data histograms
    dataList=('Data8TeV_MuEG2012A','Data8TeV_MuEG2012B','Data8TeV_MuEG2012C','Data8TeV_MuEG2012D')
    dataH=None
    for tag in dataList:
        url,_=file_list[tag]
        fIn=ROOT.TFile.Open(url)
        obj=fIn.Get('nominal/obscorrnominal')
        if dataH is None:
            dataH=obj.Clone('data')
            dataH.SetDirectory(0)
        else:
            dataH.Add(obj)
        fIn.Close()
    dataSubH=dataH.Clone('datasub')
    dataSubH.SetDirectory(0)
    dataSubH.Add(bgH,-1)
    for obsTitle,muBin,stdBin,ctrBin in binsOfInterest:
        
        calibMuOffset=systScan['calib'].GetBinContent(ctrBin,muBin)/systScan['calib'].GetBinContent(ctrBin,ctrBin)
        calibMtopOffset=172.5-mtopCalib[obsTitle].GetX(calibMuOffset)

        dataN       = dataH.GetBinContent(ctrBin,ctrBin)
        dataMu      = dataH.GetBinContent(ctrBin,muBin)/dataN
        dataMuUnc   = math.sqrt(dataH.GetBinContent(ctrBin,stdBin)/dataN-dataMu**2)/math.sqrt(dataN)
        dataMtop    = mtopCalib[obsTitle].GetX(dataMu)+calibMtopOffset
        dataMtopUnc = mtopCalib[obsTitle].GetX(dataMu+dataMuUnc)-dataMtop

        dataSubN     = dataSubH.GetBinContent(ctrBin,ctrBin)
        dataSubMu    = dataSubH.GetBinContent(ctrBin,muBin)/dataSubN
        dataSubMuUnc = math.sqrt( dataSubH.GetBinContent(ctrBin,stdBin)/dataSubN-dataSubMu**2)/math.sqrt(dataSubN)
        dataSubMtop  = mtopCalib[obsTitle].GetX(dataSubMu)+calibMtopOffset
        dataSubMtopUnc = mtopCalib[obsTitle].GetX(dataSubMu+dataSubMuUnc)-dataSubMtop

        print '%15s & %d & %15s & %15s & %15s & %3.2f $\\pm$ %3.2f\\\\'%(obsTitle,
                                                                         dataN,
                                                                         toLatexRounded(dataMu,dataMuUnc),
                                                                         toLatexRounded(dataSubMu,dataSubMuUnc),
                                                                         toLatexRounded(dataMtop,dataMtopUnc),
                                                                         dataSubMtop,dataSubMtopUnc
                                                                         )
        
        #


"""
Build a combination datacard in the format required by BlueFin
cf. https://svnweb.cern.ch/trac/bluefin
"""
def runCombinationDataCard(mass,avgX,uncX,modelUncs,cXY,mtopCalib,outDir):

    bluefinCard=[]

    #iterate over the observables
    uncList=[]
    idx=0
    for title,name in OBSERVABLES:
        offset,slope=mtopCalib[idx]
        mtopMeas=(avgX[idx]-offset)/slope
        statUnc=uncX['Stat.'][0][idx]/slope

        #header of the datacard: name of variables, observable, measurement and individual uncertainties
        if len(bluefinCard)==0:
            bluefinCard.append('%20s %12s'%('MEANAME',name))
            bluefinCard.append('%20s %12s'%('OBSNAME','mtop'))
            bluefinCard.append('%20s %12s'%('MEAVAL','%3.3f'%mtopMeas) )
            bluefinCard.append('%20s %12s'%('stat','%3.3f'%statUnc) )
        else:
            bluefinCard[0] += '%12s'%name
            bluefinCard[1] += '%12s'%'mtop'
            bluefinCard[2] += '%12s'%('%3.3f'%mtopMeas)
            bluefinCard[3] += '%12s'%('%3.3f'%statUnc)

        isyst=0
        for systVar in uncX:
            if systVar=='Stat.' : continue

            #get the name for this systematic variation
            name=''
            for iSystVar,_,_,iSystName in WGTSYSTS:
                if iSystVar==systVar: 
                    name=iSystName
                    break
            if len(uncList)<=isyst : uncList.append(name)
        
            #take the max. variation as estimate
            systUnc=0
            for iest in uncX[systVar]:
                systUnc=ROOT.TMath.Max(systUnc,ROOT.TMath.Abs(iest[idx]))
            systUnc /= slope

            if len(bluefinCard)-4<=isyst:
                bluefinCard.append('%20s %12s'%(name,'%3.3f'%systUnc))
            else:
                bluefinCard[4+isyst] +='%12s'%('%3.3f'%systUnc)

            isyst+=1

        #model uncertainties
        for systVar in modelUncs:

            #get the name for this systematic variation
            name=''
            for iSystVar,_,_,iSystName in FILESYSTS:
                if iSystVar==systVar: 
                    name=iSystName
                    break
            if len(uncList)<=isyst : uncList.append(name)

            #take the max. variation as estimate
            systUnc=0
            for iest in modelUncs[systVar]:
                systUnc=ROOT.TMath.Max(systUnc,ROOT.TMath.Abs(iest[idx]))
            systUnc /= slope

            if len(bluefinCard)-4<=isyst:
                bluefinCard.append('%20s %12s'%(name,'%3.3f'%systUnc))
            else:
                bluefinCard[4+isyst] +='%12s'%('%3.3f'%systUnc)            
            isyst+=1

        idx+=1

    bluefinCard.append( '%10s %10s %12s'%('CMEA1','CMEA2','stat') )
    for systVarName in uncList: bluefinCard[-1] += '%12s'%systVarName
    idx=0
    for _,iname in OBSERVABLES:
        jdx=0
        for _,jname in OBSERVABLES:
            if jdx<=idx : continue
            bluefinCard.append('%10s %10s %12s'%(iname,jname,'%3.3f'%cXY[jdx][idx]))
            for systVarName in uncList: bluefinCard[-1] += '%12s'%'1'
            jdx+=1
        idx+=1

    #dump the datacard to a file
    card=open('%s/bluefin_%3.1f.bfin'%(outDir,mass),'w')
    card.write('#\n# BlueFin input data file for m=%3.1f\n#\n'%mass)    
    card.write('TITLE \"Top mass mesurement from kinematics moments\"\n')
    card.write('NOBS 1\n')
    card.write('NMEA %d\n'%len(OBSERVABLES))
    card.write('NERR %d\n'%(len(uncList)+1))
    card.write('# '+'='*50 +'\n')
    for line in bluefinCard:
        card.write(line +'\n')
    card.write('# '+'='*50 +'\n')
    card.close()

#
#    #show correlation
#    showCorrelation(momentCalibration[172.5][4],momentCalibration[172.5][5],opt.output)
#
#    #show calibration
#
#    table=[]
#    for idx,title,name in [(0, 'O^{1} p_{T}(ll) [GeV]',             'ptll_o1'),
#                           (1, 'O^{2} p_{T}(ll) [GeV^{2}]',         'ptll_o2'),
#                           (2, 'O^{3} p_{T}(ll) [GeV^{3}]',         'ptll_o3'),
#                           (3, 'O^{1} p_{T}(+)+p_{T}(-) [GeV]',     'ptsum_o1'),
#                           (4, 'O^{2} p_{T}(+)+p_{T}(-) [GeV^{2}]', 'ptsum_o2'),
#                           (5, 'O^{3} p_{T}(+)+p_{T}(-) [GeV^{3}]', 'ptsum_o3'),
#                           (6, 'O^{1} E(+)+E(-) [GeV]',             'ensum_o1'),
#                           (7, 'O^{2} E(+)+E(-) [GeV^{2}]',         'ensum_o2'),
#                           (8, 'O^{3} E(+)+E(-) [GeV^{3}]',         'ensum_o3'),
#                           (9, 'O^{1} M(ll) [GeV]',                 'mll_o1'),
#                           (10,'O^{2} M(ll) [GeV^{2}]',             'mll_o2'),
#                           (11,'O^{3} M(ll) [GeV^{3}]',             'mll_o3'),
#                           (12,'O^{1} p_{T}(+) [GeV]',              'ptpos_o1'),
#                           (13,'O^{2} p_{T}(+) [GeV^{2}]',          'ptpos_o2'),
#                           (14,'O^{3} p_{T}(+) [GeV^{3}]',          'ptpos_o3')]:
#        offset,slope=showMomentCalibration(momentCalibration,idx,title,opt.output)
#
#        if not 'O^{1}' in title: continue
#
#        avgX=momentCalibration[172.5][0]
#        uncX=momentCalibration[172.5][1]
#

"""
Prints the results for the measurement of the moments
"""
def printSystsTable(systsTable,outDir):

    finalTable=[]
    finalTable.append('%25s &'%'Variable')
    for obs, _ in systsTable:
        finalTable[-1] += '%25s &'%obs
    finalTable[-1]=finalTable[-1][:-1]
    
    for i in xrange(0,len(systsTable[0][1])):

        systName,_,_=systsTable[0][1][i]
        finalTable.append( '%25s &'%systName )
        for j in xrange(0,len(systsTable)):
            _,varUp,varDn = systsTable[j][1][i]
            finalTable[-1] += '%25s &'% (' %3.2f/%3.2f' % (varUp,varDn))
        finalTable[-1]=finalTable[-1][:-1]


    #dump the table to a file
    card=open('%s/systs.dat'%(outDir),'w')
    for line in finalTable:
        card.write(line+'\\\\\n')
        print line
    card.close()



"""
Prints the results for the measurement of the moments
"""
def printMomentTable(mass,avgX,uncX,modelUncs,cXY,mtopCalib,outDir):

    momentTable=[]
    idx=0
    for title,name in OBSERVABLES:
        statUnc=100*uncX['Stat.'][0][idx]/avgX[idx]
        if len(momentTable)==0 : 
            momentTable.append('Variable & $%s$ &'%name)
            momentTable.append('MC statistics & %3.1f &'%statUnc)
        else:
            momentTable[0]+= ' %s &'%name
            momentTable[1]+='%3.1f &'%statUnc

        irow=2
        for systVar in uncX:
            if systVar=='Stat.': continue

            for diff in uncX[systVar]:
                relDiff=100*diff[idx]/avgX[idx]
                if len(momentTable)<=irow:
                    momentTable.append('%s & %3.2f/'%(systVar,relDiff))
                else:
                    momentTable[irow]+='%3.2f/'%relDiff
            momentTable[irow]=momentTable[irow][:-1]
            momentTable[irow]+=' & '
            irow+=1

        for systVar in modelUncs:
            for diff in modelUncs[systVar]:
                relDiff=100*diff[idx]/avgX[idx]
                if len(momentTable)<=irow:
                    momentTable.append('%s & %3.2f/'%(systVar,relDiff))
                else:
                    momentTable[irow]+='%3.2f/'%relDiff
            momentTable[irow]=momentTable[irow][:-1]
            momentTable[irow]+=' & '
            irow+=1
        idx+=1

    #dump the table to a file
    card=open('%s/mellinmomentunc.dat'%(outDir),'w')
    for line in momentTable:
        card.write(line[:-2]+'\\\\\n')
    card.write('# '+'='*50 +'\n')
    card.close()






def showCorrelation(cXY,cXYstab,outDir):

    cXYH=ROOT.TH2F('cxyh','cxy',cXY.GetNcols(),0,cXY.GetNcols(),cXY.GetNrows(),0,cXY.GetNrows())
    cXYstabH=cXYH.Clone('cxystabh')
    for i in xrange(0,cXY.GetNrows()):
        for j in xrange(0,cXY.GetNcols()):
            if cXY[j][i]==0 : continue
            cXYH.Fill(i,j,cXY[j][i])

            if i==j : continue
            diff2=0
            for systVar in cXYstab:
                print systVar
                if systVar=='Top p_{T}' : continue

                maxDiff=0
                for diff in cXYstab[systVar]:
                    maxDiff=ROOT.TMath.Max(maxDiff,diff[j][i])
                maxDiff=maxDiff/cXY[j][i]
                diff2+=maxDiff**2
            cXYstabH.Fill(i,j,100*ROOT.TMath.Sqrt(diff2))

    c=ROOT.TCanvas('c','c',500,500)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.2)
    for h,name in [(cXYH,'cxy'),(cXYstabH,'cxystab')]:
        c.Clear()
        h.Draw('colztext')
        h.GetXaxis().SetNdivisions(0)
        h.GetYaxis().SetNdivisions(0)

        txt=ROOT.TLatex()
        txt.SetNDC(True)
        txt.SetTextFont(42)
        txt.SetTextSize(0.035)
        txt.SetTextAlign(12)
        txt.DrawLatex(0.12,0.95,'#bf{CMS} #it{preliminary}')
        txt.DrawLatex(0.6,0.95,'19.7 fb^{-1} (8 TeV)')

        c.Modified()
        c.Update()
        for ext in ['png','pdf','C']:
            c.SaveAs('%s/%s.%s'%(outDir,name,ext))



"""
"""
def showMomentCalibration(tW,ttbar,title,outDir):
    c=ROOT.TCanvas('c','c',500,500)

    leg=ROOT.TLegend(0.45,0.93,0.65,0.99)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    #leg.SetNColumns(2)
    leg.SetTextFont(42)
    leg.SetTextSize(0.025)

    allGr,allFunc=[],[]
    minY,maxY=9e+20,-9e+20
    for data in [ttbar,tW]:
        x,y,sigma,obsParam,nParam=data
        i=len(allGr)
        allGr.append( ROOT.TGraphErrors() )
        allGr[-1].SetMarkerStyle(20+i)
        allGr[-1].SetMarkerColor(1+i)
        allGr[-1].SetLineColor(1+i)
        grTitle='t#bar{t}' if i==0 else 'tW'
        allGr[-1].SetTitle(grTitle)
        
        for np in xrange(0,len(x)):
            allGr[-1].SetPoint(np,x[np],y[np])
            allGr[-1].SetPointError(np,0,sigma[np])            
            minY=ROOT.TMath.Min(minY,y[np])
            maxY=ROOT.TMath.Max(maxY,y[np])
        allGr[-1].Sort()
        drawOpt='ap' if i==0 else 'p'
        allGr[-1].Draw(drawOpt)
        allGr[-1].Fit('pol1','MQ+')
        pol=allGr[-1].GetFunction('pol1')
        slope,slopeUnc=pol.GetParameter(1),pol.GetParError(1)
        offset,offsetUnc=pol.GetParameter(0),pol.GetParError(0)
        allGr[-1].GetXaxis().SetTitle('Mass [GeV]')
        allGr[-1].GetYaxis().SetTitle(title)
        leg.AddEntry(allGr[-1],'%s offset=%3.0f#pm%3.0f slope=%3.3f#pm%3.3f'%(allGr[-1].GetTitle(),offset,offsetUnc,slope,slopeUnc),'p')

    allGr[0].GetYaxis().SetRangeUser(minY*0.97,maxY*1.03)
    leg.Draw()

    #calibration function
    #obstop = [nst(mtop) x obsttbar(mtop) + nttbar(ntop) x obsttbar(mtop) ] / [nst(mtop)+nttbar(mtop)]
    calibFunc=ROOT.TF1('calibfunc',
                       '(([0]*x+[1])*([2]*x+[3])+([4]*x+[5])*([6]*x+[7]))/(([0]+[4])*x+([1]+[5]))',
                       100,200)
    calibFunc.SetParameter(0,tW[4][1])
    calibFunc.SetParameter(1,tW[4][0])
    calibFunc.SetParameter(2,tW[3][1])
    calibFunc.SetParameter(3,tW[3][0])
    calibFunc.SetParameter(4,ttbar[4][1])
    calibFunc.SetParameter(5,ttbar[4][0])
    calibFunc.SetParameter(6,ttbar[3][1])
    calibFunc.SetParameter(7,ttbar[3][0])
    calibFunc.SetLineColor(ROOT.kBlue)
    calibFunc.Draw('same')

    txt=ROOT.TLatex()
    txt.SetNDC(True)
    txt.SetTextFont(42)
    txt.SetTextSize(0.035)
    txt.SetTextAlign(12)
    txt.DrawLatex(0.18,0.95,'#bf{CMS} #it{simulation}')
    
    c.Modified()
    c.Update()
    outTitle=title
    for rep in [' ','{','}','#','^','[','(',')',']']:
        outTitle=outTitle.replace(rep,'')
    outTitle=outTitle.replace('+','pos')
    outTitle=outTitle.replace('+','neg')
    for ext in ['png','pdf','C']:
        c.SaveAs('%s/momcalib_%s.%s'%(outDir,outTitle,ext))

    return calibFunc
        

"""
steer
"""
def main():
	usage = 'usage: %prog [options]'
	parser = optparse.OptionParser(usage)
	parser.add_option('-i', '--input',
                          dest='input',   
                          default='dileptonMoments-new/',
                          help='input directory with the files [default: %default]')
	parser.add_option('-l', '--lumi',
                          dest='lumi',   
                          default=19701,
                          help='luminosity, for background subtraction in data [default: %default]')
	parser.add_option('-u', '--unblind',
                          dest='unblind',
                          default=False,
                          action='store_true',
                          help='if you are really sure, take a look at the data [default: %default]')
	parser.add_option('-t', '--tier',
                          dest='tier',
                          default='',
                          help='if nothing is passed use reco/ _gen=use gen [default: %default]')
	parser.add_option('-o', '--output',
                          dest='output', 
                          default='dileptonMoments-new/plots',
                          help='Output directory [default: %default]')
	parser.add_option('-c', '--cache',
                          dest='cache', 
                          default='.xsecweights.pck',
                          help='Output directory [default: %default]')
	(opt, args) = parser.parse_args()

        #ROOT config
        ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
	ROOT.AutoLibraryLoader.enable()
        setTDRStyle()
        ROOT.gROOT.SetBatch(True)
        ROOT.gStyle.SetOptTitle(0)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptFit(0)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetPaintTextFormat('4.2f') 

        #prepare output
	os.system('mkdir -p %s' % opt.output)

        #create file list
        file_list={}

        #read normalization
        cachefile = open(opt.cache, 'r')
        xsecWeights = pickle.load(cachefile)
        cachefile.close()

        #read files in the directory and assign normalization
        allFiles=os.listdir(opt.input)
        for f in allFiles:
            tag=os.path.splitext(f)[0]
            if not tag in xsecWeights : continue
            file_list[ tag ]=( os.path.join(opt.input,f), xsecWeights[tag] )

        #run the analysis
        prepareCalibration(opt,file_list)
        

if __name__ == "__main__":
	sys.exit(main())
