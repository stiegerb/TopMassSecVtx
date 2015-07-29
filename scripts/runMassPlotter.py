#! /usr/bin/env python

import sys
import os
import json
import pickle
import ROOT
from UserCode.TopMassSecVtx.PlotUtils import RatioPlot

sys.path.append('/afs/cern.ch/cms/caf/python/')
from cmsIO import cmsFile

"""
Create the mass scan plots. - possible bug?
"""
def makeMassScanPlots(outDir):

    #Get the required files
    masshistos = {}

    #Files are of form tag_ch_mass_comb
    tags = ['t','tt']#,'bg']
    channels = ['e2j','e3j','m2j','m3j']

    #Masses are given as whole numbers; 0.5 added later
    masses = ['163','166','169','171','172','173','175','178','181']
    combinations = ['cor','wro','inc']#,'unm']
    colors = {
        '163':ROOT.kGray,
        '166':ROOT.kAzure+5,
        '169':ROOT.kOrange-3,
        '171':ROOT.kOrange+9,
        '173':ROOT.kGray+2,
        '175':ROOT.kSpring-5,
        '178':ROOT.kBlue+2,
        '181':ROOT.kTeal-9,
        '172':ROOT.kMagenta-2
        }

    #Rootfile1 is for the mass scans; rootfile2 is for the base case (172.5)
    rootfile1 = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_mass_scans/plotter.root')
    rootfile2 = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    #Define every possible combination of the plots
    for tag in tags:
        for mass in masses:
            for ch in channels:
                for comb in combinations:
                    masshistos[(tag,ch,mass,comb)]=None

    #Fill masshistos with plots from the mass scans
    for key in rootfile1.GetListOfKeys():

        name = key.GetName()
        rootfile1.cd(name)

        tag = ''
        ch = ''
        comb = ''
        mass = ''

        for t in tags:
            if (t+'_') in name:
                tag = t
        if tag == '': continue

        for c in channels:
            if (c+'_') in name:
                ch = c
        if ch == '': continue

        for c in combinations:
            if (c) in name:
                comb = c
        if comb == '': continue

        for m in masses:
            if m in name:
                mass = m
        if mass == '': continue

        hist = ROOT.TH1F()
        
        for histo in ROOT.gDirectory.GetListOfKeys():
            histo1 = histo.GetName()
            if masshistos[(tag,ch,mass,comb)] == None:
                ROOT.gDirectory.GetObject(histo1,hist)
                hist.SetTitle('')
                masshistos[(tag,ch,mass,comb)] = hist
            else:
                ROOT.gDirectory.GetObject(histo1,hist)
                hist.SetTitle('')
                masshistos[(tag,ch,mass,comb)].Add(hist)
                print('Added for '+tag+' '+ch+' '+mass+' '+comb+'\n')
                        
        if masshistos[(tag,ch,mass,comb)]!=None:
            masshistos[(tag,ch,mass,comb)].SetLineColor(colors[mass])
            masshistos[(tag,ch,mass,comb)].SetFillColor(0)

    #Fill masshistos for the base case
    for key in rootfile2.GetListOfKeys():

        name = key.GetName()
        rootfile2.cd(name)

        tag = ''
        ch = ''
        comb = ''
        mass = ''

        for t in tags:
            if (t+'_') in name:
                tag = t
        if tag == '': continue

        for c in channels:
            if (c+'_') in name:
                ch = c
        if ch == '': continue

        for c in combinations:
            if (c) in name:
                comb = c
        if comb == '': continue

        for m in masses:
            if m in name:
                mass = m
        if mass == '': continue

        hist = ROOT.TH1F()

        for histo in ROOT.gDirectory.GetListOfKeys():
            histo1 = histo.GetName()
            if masshistos[(tag,ch,mass,comb)] == None:
                ROOT.gDirectory.GetObject(histo1,hist)
                hist.SetTitle('')
                masshistos[(tag,ch,mass,comb)] = hist
            else:
                ROOT.gDirectory.GetObject(histo1,hist)
                hist.SetTitle('')
                masshistos[(tag,ch,mass,comb)].Add(hist)
                print('Added for '+tag+' '+ch+' '+mass+' '+comb+'\n')

        if masshistos[(tag,ch,mass,comb)]!=None:
            masshistos[(tag,ch,mass,comb)].SetFillColor(0)
            masshistos[(tag,ch,mass,comb)].SetLineColor(colors[mass])

    #Make the ratio plots for single top
    for chan in channels:
        for comb in ['cor','wro']:
            ratplot = RatioPlot('ratioplot')
            ratplot.normalized = False
            ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
            ratplot.ratiorange = (0.5, 1.5)
            
            reference = masshistos[('t',chan,'172',comb)]
            ratplot.reference = reference
            for mass in masses:
                legentry = 'm_{t} = %5.1f GeV' % (float(mass)+0.5)
                try:
                    histo = masshistos[('t',chan,mass,comb)]
                    ratplot.add(histo, legentry)
                except KeyError: pass
                except AttributeError: pass
            
            ratplot.tag = comb+' combinations'
            ratplot.subtag = '%s %s' % ('t', chan)
            ratplot.show("massscan_%s_%s_%s_tot"%('t',chan,comb), outDir)

    #Make the ratio plots for single top combined
    for chan in channels:
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
        ratplot.ratiorange = (0.5, 1.5)
        
        reference = masshistos[('t',chan,'172','cor')]
        reference.Add(masshistos[('t',chan,'172','wro')])
        ratplot.reference = reference
        for mass in masses:
            legentry = 'm_{t} = %5.1f GeV' % (float(mass)+0.5)
            try:
                histo = masshistos[('t',chan,mass,'cor')]
                histo.Add(masshistos[('t',chan,mass,'wro')])
                ratplot.add(histo, legentry)
            except KeyError: pass
            except AttributeError: pass
            
        ratplot.tag = 'All combinations'
        ratplot.subtag = '%s %s' % ('t', chan)
        ratplot.show("massscan_%s_%s_tot"%('t',chan), outDir)

    #Make the ratio plots for ttbar
    for chan in channels:
        ratplot.reset()
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
        ratplot.ratiorange = (0.5, 1.5)
        
        reference = masshistos[('tt',chan,'172','inc')]
        ratplot.reference = reference
        print ratplot.reference 
        
        for mass in masses:
            legentry = 'm_{t} = %5.1f GeV' % (float(mass)+0.5)
            try:
                histo = masshistos[('tt',chan,mass,'inc')]
                ratplot.add(histo, legentry)
            except KeyError: pass
            except AttributeError: pass
            
        ratplot.tag = 'All combinations'
        ratplot.subtag = '%s %s' % ('tt', chan)
        ratplot.show("massscan_%s_%s_unm_tot"%('tt',chan), outDir)

"""
Make ttbar comparison plots. norm option makes the histograms normalized to 1.
"""
def makeTTbarPlots(outDir,norm=None):

    #Open the rootfile - working with 172.5 GeV
    rootfile = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    tags = ['e2j','e3j','mu2j','mu3j']

    histos = {}

    #Fill histos directory with svlmass plots for ttbar with -0.05 <= BDT <= 0.11
    for tag in tags:
        rootfile.cd('SVLMassWJets_'+tag)
        hist = ROOT.TH1F()

        ROOT.gDirectory.GetObject('MC8TeV_TTJets_MSDecays_172v5_SVLMassWJets_'+tag,hist)
        hist.SetFillColor(0)
        hist.SetTitle('')
        if norm=='norm':
            hist.Scale(1/hist.Integral())
        hist.Rebin()
        histos[tag+'_BDT']=hist
        hist1 = ROOT.TH1F()
        foundone = False
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' in name) and ('Graph' not in name):
                if foundone==False:
                    ROOT.gDirectory.GetObject(name,hist1)
                    foundone=True
                else:
                    hist2 = ROOT.TH1F()
                    ROOT.gDirectory.GetObject(name,hist2)
                    hist1.Add(hist2)
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' not in name) and ('MSDecays' not in name):
                hist2 = ROOT.TH1F()
                ROOT.gDirectory.GetObject(name,hist2)
                hist1.Add(hist2,-1)
        hist1.Rebin()
        hist1.SetFillColor(0)
        if norm=='norm':
            hist1.Scale(1/hist1.Integral())
        histos[tag+'_data_BDT']=hist1

    #Fill histos directory with svlmass plots for ttbar with nominal cuts
    for tag in tags:
        rootfile.cd('SVLMass_'+tag)
        hist = ROOT.TH1F()

        ROOT.gDirectory.GetObject('MC8TeV_TTJets_MSDecays_172v5_SVLMass_'+tag,hist)
        hist.SetFillColor(0)
        hist.SetTitle('')
        if norm=='norm':
            hist.Scale(1/hist.Integral())
        hist.Rebin()
        histos[tag]=hist
        hist1 = ROOT.TH1F()
        foundone = False
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' in name) and ('Graph' not in name):
                if foundone==False:
                    ROOT.gDirectory.GetObject(name,hist1)
                    foundone=True
                else:
                    hist2 = ROOT.TH1F()
                    ROOT.gDirectory.GetObject(name,hist2)
                    hist1.Add(hist2)
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' not in name) and ('MSDecays' not in name):
                hist2 = ROOT.TH1F()
                ROOT.gDirectory.GetObject(name,hist2)
                hist1.Add(hist2,-1)
        hist1.Rebin()
        hist1.SetFillColor(0)
        if norm=='norm':
            hist1.Scale(1/hist1.Integral())
        histos[tag+'_data']=hist1

    #Create ttbar electron plot (nominal vs 3jets with inverted BDT)
    ratplot = RatioPlot('ratioplot')
    ratplot.normalized = False
    ratplot.ratiotitle = 'Ratio wrt 3 jets'
    ratplot.ratiorange = (0.5,1.5)

    reference = histos['e3j_BDT']
    ratplot.reference = reference

    legentry = 'ttbar e2j'
    hist = histos['e2j']
    ratplot.add(hist,legentry)
    legentry = 'ttbar e3j'
    hist = histos['e3j_BDT']
    ratplot.add(hist,legentry)
    legentry = 'Data e3j'
    hist = histos['e3j_data_BDT']
    ratplot.add(hist,legentry)

    ratplot.tag = 'TTbar electrons'
    ratplot.subtag = 'tt'
    if norm=='norm':
        ratplot.show('tt_e_compare_normalized',outDir)
    else:
        ratplot.show('tt_e_compare',outDir)

    #Create ttbar muon plot (2jets vs 3jets)
    ratplot.reset()
    ratplot = RatioPlot('ratioplot')
    ratplot.normalized = False
    ratplot.ratiotitle = 'Ratio wrt 3 jets'
    ratplot.ratiorange = (0.5,1.5)

    reference = histos['mu3j_BDT']
    ratplot.reference = reference

    legentry = 'ttbar mu2j'
    hist = histos['mu2j']
    ratplot.add(hist,legentry)
    legentry = 'ttbar mu3j'
    hist = histos['mu3j_BDT']
    ratplot.add(hist,legentry)
    legentry = 'Data mu3j'
    hist = histos['mu3j_data_BDT']
    ratplot.add(hist,legentry)

    ratplot.tag = 'TTbar muons'
    ratplot.subtag = 'tt'
    if norm=='norm':
        ratplot.show('tt_mu_compare_normalized',outDir)
    else:
        ratplot.show('tt_mu_compare',outDir)

"""
Make QCD comparison plots.
"""
def makeQCDPlots(outDir, norm=None):

    #Open rootfile
    rootfile = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    tags = ['e2j','e3j','mu2j','mu3j']
    histos = {}

    #runPlotter may save the QCD histogram as any of these names
    possibilities = ['QCDMuPt20toInf','QCDPt170to250','QCDPt250to350','QCDPt30to80','QCDPt350toInf','QCDPt80to170']

    #Fill the histos dictionary
    for tag in tags:
        rootfile.cd('SVLMassQCD_'+tag)
        hist1 = ROOT.TH1F()
        hist2 = ROOT.TH1F()

        #For the QCD optimized plots
        for p in possibilities:
            try:
                ROOT.gDirectory.GetObject('MC8TeV_'+p+'_SVLMassQCD_'+tag,hist1)
                hist1.SetFillColor(0)
                hist1.SetTitle('')
                if norm=='norm':
                    hist1.Scale(1/hist1.Integral())
                hist1.Rebin()
                histos[tag+'QCD']=hist1
            except LookupError: pass

        #For the standard analysis plots
        rootfile.cd('SVLMass_'+tag)
        for p in possibilities:
            try:
                ROOT.gDirectory.GetObject('MC8TeV_'+p+'_SVLMass_'+tag,hist2)
                hist2.SetFillColor(0)
                hist2.SetTitle('')
                if norm=='norm':
                    hist2.Scale(1/hist2.Integral())
                hist2.Rebin()
                histos[tag]=hist2
            except LookupError: pass

        hist1 = ROOT.TH1F()
        foundone = False
        rootfile.cd('SVLMassQCD_'+tag)
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' in name) and ('Graph' not in name):
                if foundone==False:
                    ROOT.gDirectory.GetObject(name,hist1)
                    foundone=True
                else:
                    hist2 = ROOT.TH1F()
                    ROOT.gDirectory.GetObject(name,hist2)
                    hist1.Add(hist2)
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' not in name) and ('QCD' not in name):
                hist2 = ROOT.TH1F()
                ROOT.gDirectory.GetObject(name,hist2)
                hist1.Add(hist2,-1)
        hist1.Rebin()
        hist1.SetFillColor(0)
        if norm=='norm':
            hist1.Scale(1/hist1.Integral())
        histos[tag+'_data']=hist1

    ratplot = RatioPlot('ratioplot')

    #Make the ratio plots
    for tag in tags:
        ratplot.reset()
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = 'Ratio wrt Inverse EvCat Selection'
        ratplot.ratiorange = (0.5,1.5)
        
        reference = histos[tag+'QCD']
        ratplot.reference = reference
        
        legentry = 'Full cuts ' + tag
        hist = histos[tag]
        ratplot.add(hist,legentry)
        legentry = 'QCD Cuts '+ tag
        hist = histos[tag+'QCD']
        ratplot.add(hist,legentry)
        legentry = 'Data '+tag
        hist = histos[tag+'_data']
        ratplot.add(hist,legentry)

        ratplot.tag = 'QCD '+tag
        ratplot.subtag = 'qcd'
        if norm=='norm':
            ratplot.show('qcd_'+tag+'_compare_normalized',outDir)
        else:
            ratplot.show('qcd_'+tag+'_compare',outDir)


"""
Make W+Jets comparison plots.
"""
def makeWJetsPlots(outDir,norm=None):

    #Open the rootfile
    rootfile = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    tags = ['e2j','e3j','mu2j','mu3j']
    histos = {}

    #runPlotter may save the WJets plot as any of these
    possibilities = ['WJets','W1Jets','W2Jets','W3Jets','W4Jets']

    #Fill the histos dictionary
    for tag in tags:
        rootfile.cd('SVLMassWJets_'+tag)
        hist1 = ROOT.TH1F()
        hist2 = ROOT.TH1F()

        #For the WJets optimized plots
        for p in possibilities:
            try:
                ROOT.gDirectory.GetObject('MC8TeV_'+p+'_SVLMassWJets_'+tag,hist1)
                hist1.SetFillColor(0)
                hist1.SetTitle('')
                if norm=='norm':
                    hist1.Scale(1/hist1.Integral())
                hist1.Rebin()
                histos[tag+'WJets']=hist1
            except LookupError: pass

        #For the standard analysis plots
        rootfile.cd('SVLMass_'+tag)
        for p in possibilities:
            try:
                ROOT.gDirectory.GetObject('MC8TeV_'+p+'_SVLMass_'+tag,hist2)
                hist2.SetFillColor(0)
                hist2.SetTitle('')
                if norm=='norm':
                    hist2.Scale(1/hist2.Integral())
                hist2.Rebin()
                histos[tag]=hist2
            except LookupError: pass

        hist1 = ROOT.TH1F()
        foundone = False
        rootfile.cd('SVLMassWJets_'+tag)
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' in name) and ('Graph' not in name):
                if foundone==False:
                    ROOT.gDirectory.GetObject(name,hist1)
                    foundone=True
                else:
                    hist2 = ROOT.TH1F()
                    ROOT.gDirectory.GetObject(name,hist2)
                    hist1.Add(hist2)
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if ('Data' not in name): 
                good = True
                for item in possibilities:
                    if item in name:
                        good=False
                if good:
                    hist2 = ROOT.TH1F()
                    ROOT.gDirectory.GetObject(name,hist2)
                    hist1.Add(hist2,-1)
        hist1.Rebin()
        hist1.SetFillColor(0)
        if norm=='norm':
            hist1.Scale(1/hist1.Integral())
        histos[tag+'_data']=hist1

    ratplot = RatioPlot('ratioplot')

    #Make the ratio plots
    for tag in tags:
        ratplot.reset()
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = 'Ratio wrt Inverse BDT Cut'
        ratplot.ratiorange = (0.5,1.5)
        
        reference = histos[tag+'WJets']
        ratplot.reference = reference
        
        legentry = 'Full cuts ' + tag
        hist = histos[tag]
        ratplot.add(hist,legentry)
        legentry = 'WJets Cuts '+ tag
        hist = histos[tag+'WJets']
        ratplot.add(hist,legentry)
        legentry = 'Data '+tag
        hist = histos[tag+'_data']
        ratplot.add(hist,legentry)

        ratplot.tag = 'WJets '+tag
        ratplot.subtag = 'wjets'
        if norm=='norm':
            ratplot.show('wjets_'+tag+'_compare_normalized',outDir)
        else:
            ratplot.show('wjets_'+tag+'_compare',outDir)

"""
Make plots for systematics.
"""
def makeSystPlots(outDir):
    
    #Open the root file with the reweighted events
    rootfile1 = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    #List of reweightings
    weight_opts = ['nominal','puup','pudn','lepselup','lepseldn','umetup','umetdn','toppt','topptup','bfrag','bfragup','bfragdn','bfragp11','bfragpete','bfraglund','jesup','jesdn','jerup','jerdn','btagup','btagdn','lesup','lesdn','bfnuup','bfnudn']

    tags = ['e2j','e3j','mu2j','mu3j']

    #histos for reweightings; histos1 for syst files
    histos = {}
    histos1 = {}

    for weight in weight_opts:
        for tag in tags:
            histos[weight+'_'+tag]=None

    #Fill histos with reweighted signal files
    for weight in weight_opts:
        for tag in tags:
            rootfile1.cd('SVLMass_'+weight+'_'+tag)
            for key in ROOT.gDirectory.GetListOfKeys():
                name = key.GetName()
                hist = ROOT.TH1F()
                ROOT.gDirectory.GetObject(name,hist)
                if histos[weight+'_'+tag]==None:
                    histos[weight+'_'+tag]=hist
                else:
                    histos[weight+'_'+tag].Add(hist)
            histos[weight+'_'+tag].SetFillColor(0)
    
    #List of systematics files
    systs = ['scaledown','scaleup','matchingdown','matchingup','TuneP11mpiHi','TuneP11noCR','TuneP11','TuneP11TeV','widthx5','mcatnlo','Z2Star']

    #Fill histos1 with systematics files
    for key in os.listdir('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/rootfiles_syst/'):
        rootfile2 = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/rootfiles_syst/'+key)
        process = ''
        syst_cur=''
        for syst in systs:
            if syst in key:
                syst_cur = syst
        if 'SemiLep' in key:
            syst_cur = 'SemiLep_'+syst_cur
        if 'SingleT' in key:
            process = 'SingleT'
        if 'TTJets' in key:
            process = 'TT'

        hist = ROOT.TH1F()

        for tag in tags:
            ROOT.gDirectory.GetObject('SVLMass_'+tag,hist)
            histos1[process+'_'+syst_cur+'_'+tag]=hist
        histos1[process+'_'+syst_cur+'_'+tag].SetFillColor(0)

    #Create the ratio plots
    for tag in tags:
        #First for the reweighted signal
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = 'Ratio wrt Nominal Reweighting'
        ratplot.ratiorange = (0.5,1.5)
        
        reference = histos['nominal_'+tag]
        ratplot.reference = reference
        
        for key in histos.keys():
            if tag in key:
                legentry = key
                hist = histos[key]
                ratplot.add(hist,legentry)

        ratplot.tag = 'Reweighting '+tag
        ratplot.subtag = 'syst'
        ratplot.show('syst_'+tag+'_compare_reweight',outDir)
        ratplot.reset()

        #Then for single top systematics
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = 'Ratio wrt Nominal Systematics SingleT'
        ratplot.ratiorange = (0.5,1.5)
        
        reference = histos['nominal_'+tag]
        ratplot.reference = reference
        
        legentry = 'nominal_'+tag
        hist = histos['nominal_'+tag]
        ratplot.add(hist,legentry)
        for key in histos1.keys():
            if tag in key:
                if 'SingleT' in key:
                    legentry = key
                    hist = histos1[key]
                    ratplot.add(hist,legentry)

        ratplot.tag = 'Systematics SingleT '+tag
        ratplot.subtag = 'syst_singlet'
        ratplot.show('syst_'+tag+'_compare_syst_singlet',outDir)
        ratplot.reset()

        #Finally for ttbar systematics
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = 'Ratio wrt Nominal Systematics TTbar'
        ratplot.ratiorange = (0.5,1.5)
        
        rootfile1.cd('SVLMass_'+tag)
        ttbar_hist = ROOT.TH1F()
        for key in ROOT.gDirectory.GetListOfKeys():
            name = key.GetName()
            if 'MSDecays' in name:
                ROOT.gDirectory.GetObject(name,ttbar_hist)
        ttbar_hist.SetFillColor(0)
        reference = ttbar_hist
        ratplot.reference = reference
        
        legentry = 'nominal_'+tag
        hist = ttbar_hist
        ratplot.add(hist,legentry)
        for key in histos1.keys():
            if tag in key:
                if 'TT' in key:
                    legentry = key
                    hist = histos1[key]
                    ratplot.add(hist,legentry)

        ratplot.tag = 'Systematics TTbar '+tag
        ratplot.subtag = 'syst_ttbar'
        ratplot.show('syst_'+tag+'_compare_syst_ttbar',outDir)
        ratplot.reset()



"""
Main function
"""
def main():
    makeMassScanPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/')
    makeTTbarPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/','norm')
    makeWJetsPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/','norm')
    makeQCDPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/','norm')
    makeSystPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/')

main()
