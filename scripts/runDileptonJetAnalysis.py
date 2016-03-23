#! /usr/bin/env python
import ROOT
import utils
from array import array
import optparse
import numpy as np
import os,sys
from UserCode.TopMassSecVtx.storeTools_cff import fillFromStore
from makeSVLMassHistos import getMassTrees
import re

"""
Loop over a tree and fill histograms
"""
def runJetAnalysis(fileName,outFileName,mode):
    
    isData = True if 'Data' in outFileName else False
    print '...analysing ',fileName,' file names isData=',isData,' output in',outFileName

    #create list of systematic variations
    systVars=['nominal']

    #include other uncertainties for signal only
    pdfIdx={}
    if 'MC8TeV_TTJets_MSDecays_172v5' in fileName:
        
        systVars += ['puup','pudn',
                     'lepselup','lepseldn', 'lesup','lesdn',
                     'toppt',
                     'jesup', 'jesdn',  'jerup',    'jerdn',
                     'btagup','btagdn', 'mistagup', 'mistagdn']

        for idx in xrange(0,52) : 
            key='pdf%d'%idx
            systVars.append(key)
            pdfIdx[key]=idx

    #create histogram
    ptllbins = [10,28.89,40.52,50.18,58.99,67.74,76.90,87.47,101.13,125]
    baseHisto=ROOT.TH2D('ptllvsnjets',';Dilepton transverse momentum [GeV];Jet multiplicity;Events',
                        len(ptllbins)-1,array('d',ptllbins),
                        10,0,10)
    histos={}
    for var in systVars:
        histos[var]=baseHisto.Clone('ptllvsnjets_%s'%var)
        histos[var].SetDirectory(0)
        histos[var].Sumw2()
    baseHisto.Delete()

    #open file
    tree=ROOT.TChain('DileptonInfo')
    tree.AddFile(fileName)

    #loop over events in the tree and fill histos
    totalEntries=tree.GetEntries()
    for i in xrange(0,totalEntries):

        tree.GetEntry(i)

        if i%100==0 : sys.stdout.write('\r [ %d/100 ] done' %(int(float(100.*i)/float(totalEntries))) )

        #select only emu events
        if tree.EvCat != -11*13 : continue
        
        #extra jet counting
        njets=ROOT.TMath.Min(tree.NJets-ROOT.TMath.Min(tree.NbJets,2),10)
        if tree.NJets<2 and mode==1 : continue

        #loop over variations
        for var in systVars:
            if isData and var!='nominal' : continue

            #base weight: BR fix for ttbar x pileup x lepton selection x xsec weight
            weight = 1.0
            if not isData:
                if var=='nominal'   : 
                    weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[0]*tree.JESWeight[0]
                elif var=='puup'    : weight = tree.Weight[0]*tree.Weight[2]*tree.Weight[4]*tree.BtagWeight[0]*tree.JESWeight[0]
                elif var=='pudn'    : weight = tree.Weight[0]*tree.Weight[3]*tree.Weight[4]*tree.BtagWeight[0]*tree.JESWeight[0]
                elif var=='lepselup': weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[5]*tree.BtagWeight[0]*tree.JESWeight[0]
                elif var=='lepseldn': weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[6]*tree.BtagWeight[0]*tree.JESWeight[0]
                elif var=='jesup'   : weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[0]*tree.JESWeight[1]
                elif var=='jesdn'   : weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[0]*tree.JESWeight[2]
                elif var=='jerup'   : weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[0]*tree.JESWeight[3]
                elif var=='jerdn'   : weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[0]*tree.JESWeight[4]
                elif var=='btagup'  : weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[1]*tree.JESWeight[0]
                elif var=='btagdn'  : weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[2]*tree.JESWeight[0]
                elif var=='mistagup': weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[3]*tree.JESWeight[0]
                elif var=='mistagdn': weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[4]*tree.JESWeight[0]
                elif var=='toppt'   : weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[0]*tree.JESWeight[0]*tree.Weight[10]
                elif 'pdf' in var :   
                    weight = tree.Weight[0]*tree.Weight[1]*tree.Weight[4]*tree.BtagWeight[0]*tree.JESWeight[0]*tree.PDFWeights[ pdfIdx[var] ]
                
            #positive lepton
            lp=ROOT.TLorentzVector()
            lp.SetPtEtaPhiM(tree.LpPt,tree.LpEta,tree.LpPhi,0.)
            if var=='lesup' : lp*=(1+tree.LpScale)
            if var=='lesdn' : lp*=(1-tree.LpScale)

            #negative lepton
            lm=ROOT.TLorentzVector()
            lm.SetPtEtaPhiM(tree.LmPt,tree.LmEta,tree.LmPhi,0.)       
            if var=='lesup' : lm*=(1+tree.LmScale)
            if var=='lesdn' : lm*=(1-tree.LmScale)

            #charged lepton pair - pt
            ll=ROOT.TLorentzVector()
            ll = lp + lm

            #fill hsistos
            histos[var].Fill(ll.Pt(),njets,weight)

    #save results
    fOut=ROOT.TFile.Open(outFileName,'RECREATE')
    for var in histos: histos[var].Write()
    fOut.Close()

 
"""
Wrapper for when the analysis is run in parallel
Also creates histograms, get quantiles from just one file and re run histograms
"""
def runJetAnalysisPacked(args):
    try:
        fileNames,outFileName,mode=args
        runJetAnalysis(fileNames,outFileName,mode)
    except : # ReferenceError:
        print 50*'<'
        print "  Problem with", fileNames, "continuing without"
        print 50*'<'
        return False
    
"""
Create summary distributions to unfold
"""
def createJetAnalysisTasks(opt):

    onlyList=opt.only.split('v')

    #########################
    ## Multiple files
    ## First collect all the files
    file_list = []

    ## Local directory
    if os.path.isdir(opt.input):
        for file_path in os.listdir(opt.input):
            if file_path.endswith('.root'):
                file_list.append(os.path.join(opt.input,file_path))

    ## Directory on eos
    elif opt.input.startswith('/store/'):
        file_list = getEOSlslist(opt.input)

    #list of files to analyse
    tasklist=[]
    for filename in file_list:
        baseFileName=os.path.basename(filename)      
        tag,ext=os.path.splitext(baseFileName)
        splitNb=re.search(r'\d+$',tag)
        if splitNb:
            postfix='_'+splitNb.group()
            tag=tag[:-len(postfix)]
        if len(onlyList)>0:
            processThis=False
            for filtTag in onlyList:
                if filtTag in tag:
                    processThis=True
            if not processThis : continue
        tasklist.append((filename,'%s/%s'%(opt.output,baseFileName),opt.mode))

    #loop over tasks
    if opt.jobs>1:
        print ' Submitting jobs in %d threads' % opt.jobs
        import multiprocessing as MP
        pool = MP.Pool(opt.jobs)
        pool.map(runJetAnalysisPacked,tasklist)
    else:
        for fileNames,outFileName,mode in tasklist:
            runJetAnalysis(fileNames,outFileName,mode)

"""
steer
"""
def main():
	usage = 'usage: %prog [options]'
	parser = optparse.OptionParser(usage)
	parser.add_option('-i', '--input',
                          dest='input',   
                          default='/afs/cern.ch/user/p/psilva/public/Dileptons2012',
                          help='input directory with the files [default: %default]')
	parser.add_option('--jobs',
                          dest='jobs', 
                          default=1,
                          type=int,
                          help='# of jobs to process in parallel the trees [default: %default]')
        parser.add_option('--mode',
                          dest='mode', 
                          default=0,
                          type=int,
                          help='running mode [default: %default]')
	parser.add_option('--only',
                          dest='only', 
                          default='',
                          type='string',
                          help='csv list of tags to process')
	parser.add_option('-o', '--output',
                          dest='output', 
                          default='jetAnalysis',
                          help='Output directory [default: %default]')
	(opt, args) = parser.parse_args()

        ROOT.gSystem.Load("libUserCodeTopMassSecVtx")
	ROOT.AutoLibraryLoader.enable()
	os.system('mkdir -p %s' % opt.output)

        createJetAnalysisTasks(opt)
        

if __name__ == "__main__":
	sys.exit(main())
