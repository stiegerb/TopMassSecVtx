#! /usr/bin/env python
import ROOT
import os,sys
import optparse
from UserCode.TopMassSecVtx.KinematicsMoments import defineBinsOfInterest,analyzeCorrelationOfMoments
from UserCode.TopMassSecVtx.PlotUtils import setTDRStyle
from UserCode.TopMassSecVtx.rounding import *

WGTSYSTS=[ #('Pileup',                ['puup','pudn'],          'nominal', 'pu'),
           #('Lepton selection',      ['lepselup','lepseldn'],  'nominal', 'lepsel'),
           #('Lepton energy scale',   ['lesup','lesdn'],        'nominal', 'lepscale'),
           #('Jet energy scale',      ['jesup','jesdn'],        'nominal', 'jes'),
           #('Jet energy resolution', ['jerup','jerdn'],        'nominal', 'jer'),
           #('B-tag efficiency',      ['btagup','btagdn'],      'nominal', 'beff'),
           #('Mistag rate',           ['mistagup', 'mistagdn'], 'nominal', 'mistag'),
           #('Top p_{t}',             ['toppt'],                'nominal', 'toppt')
           ]
FILESYSTS=[#('ME-PS', ['matchingdown','matchingup'], 'nominal', 'meps'),
           #('Q^{2}', ['scaledown',   'scaleup'],    'nominal', 'qcdscale'),
           #('UE',    ['p11tev',      'p11mpihi'],   'p11',     'ue'),
           #('CR',    ['p11nocr'],                   'p11',     'cr'),
           #('NLO',   ['powpyth'],                   'nominal', 'nlo')      
           ]
OBSERVABLES=[('O^{1} p_{T}(ll) [GeV]',             'ptllo1'),
             ('O^{2} p_{T}(ll) [GeV^{2}]',         'ptllo2'),
             ('O^{3} p_{T}(ll) [GeV^{3}]',         'ptllo3'),
             # ('O^{1} p_{T}(+)+p_{T}(-) [GeV]',     'ptsumo1'),
             #('O^{2} p_{T}(+)+p_{T}(-) [GeV^{2}]', 'ptsumo2'),
             #('O^{3} p_{T}(+)+p_{T}(-) [GeV^{3}]', 'ptsumo3'),
             #('O^{1} E(+)+E(-) [GeV]',             'ensumo1'),
             #('O^{2} E(+)+E(-) [GeV^{2}]',         'ensumo2'),
             #('O^{3} E(+)+E(-) [GeV^{3}]',         'ensumo3'),
             #('O^{1} M(ll) [GeV]',                 'mllo1'),
             #('O^{2} M(ll) [GeV^{2}]',             'mllo2'),
             #('O^{3} M(ll) [GeV^{3}]',             'mllo3'),
             #('O^{1} p_{T}(+) [GeV]',              'ptposo1'),
             #('O^{2} p_{T}(+) [GeV^{2}]',          'ptposo2'),
             #('O^{3} p_{T}(+) [GeV^{3}]',          'ptposo3')
             #('O^{1} E(+) [GeV]',              'enposo1'),
             #('O^{2} E(+) [GeV]',              'enposo2'),
             #('O^{3} E(+) [GeV]',              'enposo3'),
             ]

"""
show calibration curves
"""
def prepareCalibration(opt):

    file_list=os.listdir(opt.input)

    binsOfInterest=[]

    #ttbar model variations
    avgXmodelVars={}
    for syst,tag in [('matchingdown','MSDecays_matchingdown'),
                     ('matchingup',  'MSDecays_matchingup'),
                     ('p11',         'TuneP11'),
                     ('p11nocr',     'TuneP11noCR'),
                     ('p11tev',      'TuneP11TeV'),
                     ('p11mpihi',    'TuneP11mpiHi'),
                     ('scaledown',   'MSDecays_scaledown'),
                     ('scaleup',     'MSDecays_scaleup'),
                     ('powpyth',     'TT_Z2star_powheg_pythia'),
                     ('powhw',       'TT_AUET2_powheg_herwig')
        ]:

        #sum up correlation histograms are RECO levels
        ObsCorrHistos={}
        for f in file_list:
            if not tag in f : continue
            fIn=ROOT.TFile.Open(os.path.join(opt.input,f))
            for key in fIn.GetListOfKeys():
                varName=key.GetName()
                obj=fIn.Get('%s/obscorr%s'%(varName,varName))
                if not obj: continue
                if not varName in ObsCorrHistos:
                    ObsCorrHistos[varName]=obj.Clone()
                    ObsCorrHistos[varName].SetDirectory(0)
                else:
                    ObsCorrHistos[varName].Add(obj)
            fIn.Close()        

        #check which are the relevant bins
        if len(binsOfInterest)==0 : binsOfInterest=defineBinsOfInterest(ObsCorrHistos['nominal'],OBSERVABLES)
        avgX,sigmaX,cXY,avgX0=analyzeCorrelationOfMoments(ObsCorrHistos['nominal'],binsOfInterest,False)
        raw_input()
        avgXmodelVars[syst]=avgX

    
    #mass scan
    momentCalibration={}
    for mass,tag in [
        (166.5,'TTJets_MSDecays_166v5'),
        (169.5,'TTJets_MSDecays_169v5'),
        (171.5,'TTJets_MSDecays_171v5'),
        (172.5,'TTJets_MSDecays_172v5'),
        (173.5,'TTJets_MSDecays_173v5'),
        (175.5,'TTJets_MSDecays_175v5'),
        (178.5,'TTJets_MSDecays_178v5')
        ]:

        #sum up correlation histograms are RECO and GEN levels
        ObsCorrHistos={}
        for f in file_list:
            if not tag in f : continue
            fIn=ROOT.TFile.Open(os.path.join(opt.input,f))
            for key in fIn.GetListOfKeys():
                varName=key.GetName()
                obj=fIn.Get('%s/obscorr%s'%(varName,varName))
                if not obj: continue
                if not varName in ObsCorrHistos:
                    ObsCorrHistos[varName]=obj.Clone()
                    ObsCorrHistos[varName].SetDirectory(0)
                else:
                    ObsCorrHistos[varName].Add(obj)
            fIn.Close()

        #analyze correlations
        avgX,sigmaX,cXY,avgX0=analyzeCorrelationOfMoments(ObsCorrHistos['nominal'],binsOfInterest,False)
        avgX_gen,sigmaX_gen,cXY_gen,avgX0_gen=analyzeCorrelationOfMoments(ObsCorrHistos['nominal_gen'],binsOfInterest,False)
        
        #statistical uncertainty
        uncX,uncX_gen={},{}
        for i in xrange(0,sigmaX.GetNoElements()): 
            sigmaX[i]=sigmaX[i]/ROOT.TMath.Sqrt(avgX0)
            sigmaX_gen[i]=sigmaX_gen[i]/ROOT.TMath.Sqrt(avgX0_gen)
        uncX['Stat.']=[sigmaX]
        uncX_gen['Stat.']=[sigmaX_gen]

        #experimental uncertainties 
        cXYstab={}
        for syst in WGTSYSTS:

            title=syst[0]
            subsources=syst[1]
            name=syst[3]

            uncX[title]=[]
            cXYstab[title]=[]
            for systVar in subsources:

                #only for 172.5 GeV these are filled
                if not (systVar in ObsCorrHistos) : continue

                avgX_i, _, cXY_i, _ = analyzeCorrelationOfMoments(ObsCorrHistos[systVar],binsOfInterest,False)
                for i in xrange(0,avgX_i.GetNoElements()):
                    avgX_i[i]=avgX_i[i]-avgX[i]
                    for j in xrange(0,avgX_i.GetNoElements()):
                        if cXY[i][j]==0 : continue
                        cXY_i[i][j]=cXY_i[i][j]-cXY[i][j]
                uncX[title].append(avgX_i)
                cXYstab[title].append(cXY_i)

        #save for calibration
        momentCalibration[mass]=(avgX,uncX,avgX_gen,uncX_gen,cXY,cXYstab)

    #calibrate individually the measurements 
    #(only stat unc taken into account, total experimental uncertainties will be shown for reference)
    mtopCalib={}
    idx=0
    for title,name in OBSERVABLES:
        offset,slope=showMomentCalibration(momentCalibration,idx,title,opt.output)
        mtopCalib[idx]=(offset,slope)
        idx+=1
    
    #add theory uncertainties (only available for 172.5 GeV, assume it holds for other mass points)
    modelUncs={}
    for syst in FILESYSTS:
        title=syst[0]
        subsources=syst[1]
        reference=syst[2]
        name=syst[3]

        modelUncs[title]=[]
        for systVar in subsources:
            avgX_i = avgXmodelVars[systVar]
            referenceX=momentCalibration[172.5][0]
            if reference!='nominal': referenceX=avgXmodelVars[reference]

            #take the difference to the reference
            for i in xrange(0,avgX_i.GetNoElements()): avgX_i[i]=avgX_i[i]-referenceX[i]

            modelUncs[title].append(avgX_i)


    #calibrate combination
    for mass in momentCalibration:
        runCombinationDataCard(mass=mass,
                               avgX=momentCalibration[mass][0],
                               uncX=momentCalibration[mass][1],
                               modelUncs=modelUncs,
                               cXY=momentCalibration[mass][4],
                               mtopCalib=mtopCalib,
                               outDir=opt.output)
        if mass!=172.5 : continue
        printMomentTable(mass=mass,
                         avgX=momentCalibration[mass][0],
                         uncX=momentCalibration[mass][1],
                         modelUncs=modelUncs,
                         cXY=momentCalibration[mass][4],
                         mtopCalib=mtopCalib,
                         outDir=opt.output)



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
        for ext in ['png','pdf']:
            c.SaveAs('%s/%s.%s'%(outDir,name,ext))



"""
"""
def showMomentCalibration(momentCalibration,idx,title,outDir):
    c=ROOT.TCanvas('c','c',500,500)
    grStat=ROOT.TGraphErrors()
    grStat.SetName('stat')
    grStat.SetMarkerStyle(20)
    grTotal=ROOT.TGraphErrors()
    grTotal.SetName('total')
    grTotal.SetMarkerStyle(1)
    grGen=ROOT.TGraphErrors()
    grGen.SetMarkerStyle(24)
    grGen.SetMarkerColor(ROOT.kGray)
    grGen.SetLineColor(ROOT.kGray)
    for mass in momentCalibration:
        np=grStat.GetN()

        grGen.SetPoint(np,mass,momentCalibration[mass][2][idx])
        grGen.SetPointError(np,0,momentCalibration[mass][3]['Stat.'][0][idx])

        avgX=momentCalibration[mass][0][idx]
        uncX=momentCalibration[mass][1]
        grStat.SetPoint(np,mass,avgX)
        grStat.SetPointError(np,0,uncX['Stat.'][0][idx])

        grTotal.SetPoint(np,mass,avgX)
        totalUnc=0.
        for systVar in uncX:
            if systVar=='Top p_{t}': continue
            maxDiff=0
            for diff in uncX[systVar]:
                diffVal=diff[idx]
                maxDiff=ROOT.TMath.Max(maxDiff,diffVal)
            totalUnc+=maxDiff**2
        grTotal.SetPointError(np,0,ROOT.TMath.Sqrt(totalUnc))


    grTotal.Draw('a5')
    grTotal.GetXaxis().SetTitle('Mass [GeV]')
    grTotal.GetYaxis().SetTitle(title)

    grGen.Draw('p')
    grGen.Fit('pol1','MQ+','same')
    pol1_gen=grGen.GetFunction('pol1')
    pol1_gen.SetLineColor(ROOT.kGray)

    grStat.Draw('p')
    grStat.Fit('pol1','MQ+','same')
    pol1=grStat.GetFunction('pol1')

    txt=ROOT.TLatex()
    txt.SetNDC(True)
    txt.SetTextFont(42)
    txt.SetTextSize(0.035)
    txt.SetTextAlign(12)
    txt.DrawLatex(0.18,0.95,'#bf{CMS} #it{preliminary}')
    txt.DrawLatex(0.75,0.95,'19.7 fb^{-1} (8 TeV)')
    offset,slope=pol1.GetParameter(0),pol1.GetParameter(1)
    txt.DrawLatex(0.2,0.85,'#scale[0.8]{Rec. (%s) + (%s) x m_{top}}'%(toROOTRounded(pol1.GetParameter(0),pol1.GetParError(0)),
                                                                      toROOTRounded(pol1.GetParameter(1),pol1.GetParError(1))))
    txt.DrawLatex(0.2,0.8,'#scale[0.8]{Gen. (%s) + (%s) x m_{top}}'%(toROOTRounded(pol1_gen.GetParameter(0),pol1_gen.GetParError(0)),
                                                                     toROOTRounded(pol1_gen.GetParameter(1),pol1_gen.GetParError(1))))
    
    c.Modified()
    c.Update()
    for ext in ['png','pdf']:
        c.SaveAs('%s/momcalib_%d.%s'%(outDir,idx,ext))

    return offset,slope
        

"""
steer
"""
def main():
	usage = 'usage: %prog [options]'
	parser = optparse.OptionParser(usage)
	parser.add_option('-i', '--input',
                          dest='input',   
                          default='unfoldResults/moments',
                          help='input directory with the files [default: %default]')
	parser.add_option('-o', '--output',
                          dest='output', 
                          default='unfoldResults/plots',
                          help='Output directory [default: %default]')
	(opt, args) = parser.parse_args()

        ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
	ROOT.AutoLibraryLoader.enable()
        setTDRStyle()
        ROOT.gROOT.SetBatch(True)
        ROOT.gStyle.SetOptTitle(0)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptFit(0)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetPaintTextFormat('4.2f') 
	os.system('mkdir -p %s' % opt.output)

        prepareCalibration(opt)
        

if __name__ == "__main__":
	sys.exit(main())
