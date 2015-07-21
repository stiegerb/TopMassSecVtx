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
Create the mass scan plots.
"""
def main(outDir):

    #Get the required files
    masshistos = {}

    tags = ['t','tt']#,'bg']
    channels = ['e2j','e3j','m2j','m3j']
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
    prefixes = [
        'MC8TeV_SingleT_t_',
        'MC8TeV_SingleTbar_t_',
        'MC8TeV_SingleT_tW_',
        'MC8TeV_SingleTbar_tW_',
        'MC8TeV_SingleT_s_',
        'MC8TeV_SingleTbar_s_',
        'MC8TeV_WW_',
        'MC8TeV_DYJetsToLL_50toInf_',
        'MC8TeV_DY1JetsToLL_50toInf_',
        'MC8TeV_DY2JetsToLL_50toInf_',
        'MC8TeV_DY3JetsToLL_50toInf_',
        'MC8TeV_DY4JetsToLL_50toInf_',
        'MC8TeV_QCDPt170to250_',
        'MC8TeV_QCDPt250to350_',
        'MC8TeV_QCDPt30to80_',
        'MC8TeV_QCDPt350toInf_',
        'MC8TeV_QCDPt80to170_',
        'MC8TeVMuPt20toInf_',
        'MC8TeV_TT_AUET2_powheg_herwig_',
        'MC8TeV_TTJets_MSDecays_172v5_',
        'MC8TeV_TTJets_MSDecays_',
        'MC8TeV_TTWJets_',
        'MC8TeV_TTZJets_',
        'MC8TeV_W1Jets_',
        'MC8TeV_W2Jets_',
        'MC8TeV_W3Jets_',
        'MC8TeV_W4Jets_',
        'MC8TeV_WJets_',
        'MC8TeV_WZ_',
        'MC8TeV_ZZ_',
        'MC8TeV_TTJets_'
        ]
    rootfile1 = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_mass_scans/plotter.root')
    rootfile2 = ROOT.TFile.Open('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_base/plotter.root')

    for tag in tags:
        for ch in channels:
            for mass in masses:
                for comb in combinations:
                    name = tag+'_'+ch+'_'+mass+'_'+comb
                    rootfile1.cd(name)
                    hist = ROOT.TH1F()
                    foundone = False
                    masshistos[(tag,ch,mass,comb)] = None
                    for pre in prefixes:
                        try:
                            if masshistos[(tag,ch,mass,comb)] == None:
                                ROOT.gDirectory.GetObject(pre+mass+'v5_'+name,hist)
                                masshistos[(tag,ch,mass,comb)] = hist
                            else:
                                ROOT.gDirectory.GetObject(pre+mass+'v5_'+name,hist)
                                masshistos[(tag,ch,mass,comb)].Add(hist)
                            foundone = True
                        except LookupError:
                            pass
                    if foundone == False:
                        rootfile2.cd(name)
                        print(name)
                        for pre in prefixes:
                            try:
                                if masshistos[(tag,ch,mass,comb)] == None:
                                    ROOT.gDirectory.GetObject(pre+name,hist)
                                    masshistos[(tag,ch,mass,comb)] = hist
                                else:
                                    ROOT.gDirectory.GetObject(pre+name,hist)
                                    masshistos[(tag,ch,mass,comb)].Add(hist)
                                foundone = True
                            except LookupError:
                                pass
                    if masshistos[(tag,ch,mass,comb)] != None:
                        print('FOUND:' +tag+' '+ch+' '+mass+' '+comb)
                        masshistos[(tag,ch,mass,comb)].SetLineColor(colors[mass])
                        masshistos[(tag,ch,mass,comb)].SetFillColor(0)
                        masshistos[(tag,ch,mass,comb)].SetFillStyle(0)
                    else:
                        del masshistos[(tag,ch,mass,comb)]

                    
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
            
            ratplot.tag = 'All combinations'
            ratplot.subtag = '%s %s' % ('t', chan)
            ratplot.show("massscan_%s_%s_%s_tot"%('t',chan,comb), outDir)

    for chan in channels:
        #Original Code
        ratplot = RatioPlot('ratioplot')
        ratplot.normalized = False
        ratplot.ratiotitle = "Ratio wrt 172.5 GeV"
        ratplot.ratiorange = (0.0, 2.0)
        
        reference = masshistos[('tt',chan,'172','inc')]
        ratplot.reference = reference
        
        for mass in masses:
            legentry = 'm_{t} = %5.1f GeV' % (float(mass)+0.5)
            try:
                histo = masshistos[('tt',chan,mass,'inc')]
                ratplot.add(histo, legentry)
            except KeyError: pass
                # print "Can't find ", (tag,chan,mass,'tot')
            
            
        ratplot.tag = 'All combinations'
        ratplot.subtag = '%s %s' % ('tt', chan)
        ratplot.show("massscan_%s_%s_unm_tot"%('tt',chan), outDir)

main('/afs/cern.ch/user/e/edrueke/edrueke/top_lxy/CMSSW_5_3_22/src/UserCode/TopMassSecVtx/singleTop/plots_mass_scans/mass_scans/')
