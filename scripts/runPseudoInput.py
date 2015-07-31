#! /usr/bin/env python

import sys
import os
import json
import pickle
import ROOT

sys.path.append('/afs/cern.ch/cms/caf/python/')
from cmsIO import cmsFile

"""
Create the histograms for the input for the pseudo data fit.  Each histogram has bkg + ttbar (for some mass) + singlet (for some mass or systematic).
"""
def makePseudoInputPlots(outDir):

    masshistos = {}

    tags = ['t','tt']
    channels = ['e2j','e3j','m2j','m3j']
    channels1 = ['e2j','e3j','mu2j','mu3j']
    masses = ['163','166','169','171','172','173','175','178','181']
    combinations = ['cor','wro','inc']

    rootfile_nominal = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')
    rootfile_massscans = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_mass_scans/plotter.root')

    for tag in tags:
        for mass in masses:
            for ch in channels:
                for comb in combinations:
                    masshistos[(tag,ch,mass,comb)] = None

    #Gather the mass scan signal and ttbar
    for key in rootfile_massscans.GetListOfKeys():

        name = key.GetName()
        rootfile_massscans.cd(name)

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
            hist_name = histo.GetName()
            ROOT.gDirectory.GetObject(hist_name, hist)
            hist.SetTitle('')
            if masshistos[(tag,ch,mass,comb)] == None:
                masshistos[(tag,ch,mass,comb)] = hist
            else:
                masshistos[(tag,ch,mass,comb)].Add(hist)

        if masshistos[(tag,ch,mass,comb)] != None:
            masshistos[(tag,ch,mass,comb)].SetFillColor(0)

    #Gather the nominal signal and ttbar
    for key in rootfile_nominal.GetListOfKeys():

        name = key.GetName()
        rootfile_nominal.cd(name)

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
            hist_name = histo.GetName()
            hist = ROOT.TH1F()
            ROOT.gDirectory.GetObject(hist_name,hist)
            hist.SetTitle('')
            if masshistos[(tag,ch,mass,comb)] == None:
                masshistos[(tag,ch,mass,comb)] = hist
            else:
                masshistos[(tag,ch,mass,comb)].Add(hist)

        if masshistos[(tag,ch,mass,comb)] != None:
            masshistos[(tag,ch,mass,comb)].SetFillColor(0)

    #Gather bkg histos
    bkghistos = {}
    
    for key in os.listdir('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/bkg_templates/'):
        
        rootfile = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/ratio_plots/bkg_templates/'+key)

        for histo in ROOT.gDirectory.GetListOfKeys():
            
            hist_name = histo.GetName()
            hist = ROOT.TH1F()
            ROOT.gDirectory.GetObject(hist_name,hist)
            hist.SetFillColor(0)
            bkghistos[key] = hist

    #Gather syst histos
    systhistos = {}

    weight_opts = ['nominal','puup','pudn','lepselup','lepseldn','umetup','umetdn','toppt','topptup','bfrag','bfragup','bfragdn','bfragp11','bfragpete','bfraglund','jesup','jesdn','jerup','jerdn','btagup','btagdn','lesup','lesdn','bfnuup','bfnudn']
    systs = ['scaledown','scaleup','matchingdown','matchingup','TuneP11mpiHi','TuneP11noCR','TuneP11','TuneP11TeV','widthx5','mcatnlo','Z2Star']

    for weight in weight_opts:
        for ch in channels1:
            systhistos[weight+'_'+ch] = None

    for weight in weight_opts:
        for tag in channels1:
            rootfile_nominal.cd('SVLMass_'+weight+'_'+tag)
            for key in ROOT.gDirectory.GetListOfKeys():
                name = key.GetName()
                hist = ROOT.TH1F()
                ROOT.gDirectory.GetObject(name,hist)
                if systhistos[weight+'_'+tag] == None:
                    systhistos[weight+'_'+tag] = hist
                else:
                    systhistos[weight+'_'+tag].Add(hist)
            systhistos[weight+'_'+tag].SetFillColor(0)

    for key in os.listdir('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/rootfiles_syst/'):

        if 'TT' in key: continue
        rootfile = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/rootfiles_syst/'+key)

        process = ''
        syst_cur = ''
        for syst in systs:
            if (syst in key) and (len(syst) > len(syst_cur)):
                syst_cur = syst
        if 'SemiLep' in key:
            syst_cur = 'SemiLep_'+syst_cur
        if 'SingleT' in key:
            process = 'SingleT'
        if 'TTJets' in key:
            process = 'TT'

        hist = ROOT.TH1F()

        for tag in channels1:
            ROOT.gDirectory.GetObject('SVLMass_'+tag,hist)
            systhistos[process+'_'+syst_cur+'_'+tag] = hist
        systhistos[process+'_'+syst_cur+'_'+tag].SetFillColor(0)

    #Make the plots - masshistos
    for tag in channels:
        tag1 = ''
        if 'e' in tag:
            tag1 = tag
        elif '2' in tag:
            tag1 = 'mu2j'
        else:
            tag1 = 'mu3j'
        for mass in masses:
            
            bkg_histo = bkghistos['QCD_template_'+tag1+'.root']
            bkg_histo.Add(bkghistos['WJets_template_'+tag1+'.root'])
            
            ttbar_histo = masshistos[('tt',tag,mass,'inc')]
            if ttbar_histo == None: continue
            sig_histo = masshistos[('t',tag,mass,'cor')]
            if sig_histo == None: continue
            sig_histo.Add(masshistos[('t',tag,mass,'wro')])
            
            bkg_histo.SetFillColor(ROOT.kBlue)
            ttbar_histo.SetFillColor(ROOT.kGray)
            sig_histo.SetFillColor(ROOT.kRed)
            
            total_hist = bkg_histo
            total_hist.Add(ttbar_histo)
            total_hist.Add(sig_histo)
            
            total_stack = ROOT.THStack()
            total_stack.Add(bkg_histo)
            total_stack.Add(ttbar_histo)
            total_stack.Add(sig_histo)

            total_stack.SaveAs(outDir+'stack_mass_check_'+mass+'_'+tag+'.root')
            total_hist.SaveAs(outDir+'mass_check_'+mass+'_'+tag+'.root')

        #Make the plots - systs
        for key in systhistos.keys():
            if 'TT' in key: continue
            bkg_histo = bkghistos['QCD_template_'+tag1+'.root']
            bkg_histo.Add(bkghistos['WJets_template_'+tag1+'.root'])

            ttbar_histo = ROOT.TH1F()
            if 'e' in tag:
                ttbar_histo = bkghistos['ttbar_template_e.root']
            else:
                ttbar_histo = bkghistos['ttbar_template_mu.root']

            sig_histo = systhistos[key]
            
            bkg_histo.SetFillColor(ROOT.kBlue)
            ttbar_histo.SetFillColor(ROOT.kGray)
            sig_histo.SetFillColor(ROOT.kRed)

            total_stack = ROOT.THStack()
            total_stack.Add(bkg_histo)
            total_stack.Add(ttbar_histo)
            total_stack.Add(sig_histo)

            total_hist = bkg_histo
            total_hist.Add(ttbar_histo)
            total_hist.Add(sig_histo)

            total_stack.SaveAs(outDir+'stack_syst_'+key+'_'+tag+'.root')
            total_hist.SaveAs(outDir+'syst_'+key+'_'+tag+'.root')


"""
Main function
"""
def main():
    makePseudoInputPlots('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/pseudo_inputs/')

main()
