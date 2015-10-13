#!/usr/bin/env python

import ROOT

def readMFCMDistributionsFrom(dists,file,tag):

    file = open(file, "r")

    histos={}
    lines=file.readlines()
    for il in xrange(0,len(lines)):
        line=lines[il]
        try:
            header=line.split()[0]
            
            for dist,subdists in dists:

                if not header in subdists: continue
                print header,'to be added to',dist,' with tag=',tag

                if not dist in histos:
                    histos[dist]=ROOT.TH1F('dist_'+tag,tag+';M(l,b) [GeV];d#sigma/dM(l,b) [pb/GeV]',80,0,400)
                    histos[dist].SetDirectory(0)
                
                for ill in xrange(il+1,len(lines)):
                    vals=lines[ill].split()
                    if len(vals)!=3 : break
                    xbin=histos[dist].GetXaxis().FindBin( float(vals[0]) )
                    histos[dist].SetBinContent(xbin,float(vals[1]))
                    histos[dist].SetBinError(xbin,float(vals[2]))
        except:
            pass

    return histos
    
def getMCFMdists(allHistos):
    MCFMfiles=[
        ('MCFM NLO (prod)',       'tt_bbl_tota_CT10.00_172_172_test.dat'),
        ('MCFM NLO (prod+decay)', 'tt_bbl_todk_CT10.00_172_172_test.dat'),
        ('MCFM LO',               'tt_bbl_lord_CT10.00_172_172_test.dat'),
        ]
    MCFMdists=[
        ('correct combinations',['m(l+,b)','m(l-,bb)']),
        ('wrong combinations',['m(l,bb)','m(l-,b)'])
        ]
    for tag,file in MCFMfiles:
        histos=readMFCMDistributionsFrom(dists=MCFMdists,file=file,tag=tag)
        for h in histos:
            if not h in allHistos:
                allHistos[h]=[]
                allHistos[h+'_norm']=[]
            allHistos[h].append(histos[h])
            allHistos[h+'_norm'].append(histos[h].Clone(histos[h].GetName()+'_norm'))
            allHistos[h+'_norm'][-1].Scale(1./ allHistos[h+'_norm'][-1].Integral())
            allHistos[h+'_norm'][-1].GetYaxis().SetTitle( '1/#sigma ' + allHistos[h+'_norm'][-1].GetYaxis().GetTitle().replace('pb/GeV','GeV^{-1}' ) )

def addOtherDistsFrom(allHistos,otherFiles):
    for tag,url,xsec in otherFiles:
        print 'Adding ',tag,url,xsec
        fIn=ROOT.TFile.Open(url)
        tree=fIn.Get('accAnalyzer/genev')
        totalEntries=tree.GetEntriesFast()

        for h in allHistos:
            if '_norm' in h : continue
            allHistos[h].append( allHistos[h][0].Clone(allHistos[h][0].GetName()+'_'+tag) )
            allHistos[h][-1].Reset('ICE')
            allHistos[h][-1].SetDirectory(0)
            allHistos[h][-1].SetTitle(tag)
            allHistos[h][-1].Sumw2()

        iniEvents=float(fIn.Get('accAnalyzer/cutflow').GetBinContent(1))

        for i in xrange(0,totalEntries):
            tree.GetEntry(i)

            #choose two leptons
            leptons={}
            for il in xrange(0,ROOT.TMath.Min(tree.nl,2)):
                if ROOT.TMath.Abs(tree.lid[il])!=11 and ROOT.TMath.Abs(tree.lid[il])!=13 : continue
                lid=11
                if tree.lid[il]<0 : lid=-11
                if tree.lpt[il]<20 or ROOT.TMath.Abs(tree.leta[il])>2.5 : continue
                leptons[lid]=ROOT.TLorentzVector()
                leptons[lid].SetPtEtaPhiM(tree.lpt[il],tree.leta[il],tree.lphi[il],tree.lmass[il])
            if len(leptons)!=2 : continue

            bjets={}
            for ij in xrange(0,tree.nj):

                #consider only b-jets
                if ROOT.TMath.Abs(tree.jflav[ij])!=5: continue
                if tree.jflav[ij] in bjets : continue
                
                #cross-clean with leptons
                p4=ROOT.TLorentzVector()
                p4.SetPtEtaPhiM(tree.jpt[ij],tree.jeta[ij],tree.jphi[ij],tree.jmass[ij])            
                if p4.DeltaR( leptons[-11])<0.5 or p4.DeltaR(leptons[11])<0.5 : continue

                #require in fiducial region
                if tree.bpt[ij]<5 or ROOT.TMath.Abs(tree.beta[ij])>2.5 : continue
                #if tree.bpt[ij]<30 or ROOT.TMath.Abs(tree.beta[ij])>2.5 : continue
                bjets[tree.jflav[ij]]=ROOT.TLorentzVector()
                bjets[tree.jflav[ij]].SetPtEtaPhiM(tree.bpt[ij],tree.beta[ij],tree.bphi[ij],tree.bmass[ij])

            if len(bjets)!=2 : continue
            
            weight=0.25*1.0e3*xsec/(iniEvents*allHistos[h+'_norm'][-1].GetBinWidth(1))
            allHistos['correct combinations'][-1].Fill( (bjets[-5]+leptons[11]).M(),weight )
            allHistos['correct combinations'][-1].Fill( (bjets[5]+leptons[-11]).M(),weight )
            allHistos['wrong combinations'][-1].Fill( (bjets[-5]+leptons[-11]).M(),weight )
            allHistos['wrong combinations'][-1].Fill( (bjets[5]+leptons[11]).M(),weight )

        for h in allHistos:
            if '_norm' in h : continue
            allHistos[h+'_norm'].append(allHistos[h][-1].Clone(allHistos[h][-1].GetName()+'_norm'))
            allHistos[h+'_norm'][-1].Scale(1./ allHistos[h+'_norm'][-1].Integral())
            allHistos[h+'_norm'][-1].GetYaxis().SetTitle( '1/#sigma ' + allHistos[h+'_norm'][-1].GetYaxis().GetTitle().replace('pb/GeV','GeV^{-1}' ) )

    return allHistos
            



allHistos={}
getMCFMdists(allHistos)
otherFiles=[('MadGraph+Pythia6','AcceptanceAnalysis_MadGraphPythia6.root',245.8),
            ('Powheg+Pythia6','AcceptanceAnalysis_PowhegPythia6.root',245.8)
            ]
addOtherDistsFrom(allHistos,otherFiles)

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

c=ROOT.TCanvas('c','c',500,500)
c.SetTopMargin(0.0)
c.SetLeftMargin(0.0)
c.SetBottomMargin(0.0)
c.SetRightMargin(0.0)

p1=ROOT.TPad('p1','p1',0,0,1.0,0.8)
p1.SetTopMargin(0.01)
p1.SetLeftMargin(0.12)
p1.SetBottomMargin(0.1)
p1.SetRightMargin(0.05)
p1.Draw()

c.cd()
p2=ROOT.TPad('p2','p2',0,0.8,1.0,1.0)
p2.SetTopMargin(0.05)
p2.SetLeftMargin(0.12)
p2.SetBottomMargin(0.01)
p2.SetRightMargin(0.05)
p2.Draw()
c.cd()

colors=[1,ROOT.kAzure-3,ROOT.kRed+2,ROOT.kGreen+2,ROOT.kGray]
for plot in allHistos:

    p1.Clear()
    leg=ROOT.TLegend(0.55,0.75,0.95,0.95)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    leg.SetBorderSize(0)
    drawOpt='e1'

    ih=0
    ratioPlots=[]
    for h in allHistos[plot]:
        h.Draw(drawOpt)
        
        h.SetMarkerColor(colors[ih])
        h.SetLineColor(colors[ih])
        h.SetMarkerStyle(20+ih*3)

        if ih>0:
            ratioPlots.append(h.Clone(h.GetName()+'_ratio'))
            ratioPlots[-1].Divide(allHistos[plot][0])
            ratioPlots[-1].GetYaxis().SetTitle('#splitline{ratio to}{#scale[0.8]{%s}}' % allHistos[plot][0].GetTitle())
        
        ih=ih+1
        if drawOpt=='e1':
            h.GetYaxis().SetTitleOffset(1.1)
            #h.GetYaxis().SetRangeUser(0.01,h.GetYaxis().GetXmax()*1.5)
            h.GetXaxis().SetRangeUser(0,300)
        leg.AddEntry(h,h.GetTitle(),'lp')
        drawOpt='e1same'
    
    leg.Draw()

    txt=ROOT.TLatex()
    txt.SetTextFont(42)
    txt.SetTextSize(0.035)
    txt.SetNDC()
    txt.DrawLatex(0.15,0.9,'#splitline{#bf{CMS} simulation}{#scale[0.8]{#it{%s}}}'%plot.replace('_norm', '(normalized)'))

    p2.cd()
    p2.SetGridy()
    drawOpt='e1'
    for h in ratioPlots:
        h.Draw(drawOpt)
        h.GetYaxis().SetRangeUser(0.42,1.76)
        h.GetYaxis().SetTitleSize(0.15)
        h.GetYaxis().SetTitleOffset(0.3)
        h.GetYaxis().SetLabelSize(0.13)
        h.GetYaxis().SetNdivisions(5)
        h.GetXaxis().SetRangeUser(0,300)
        drawOpt='e1same'

    c.Modified()
    c.Update()
    outputName=plot.replace(' ','_')
    c.SaveAs(outputName+'.pdf')
    c.SaveAs(outputName+'.png')

    fOut=ROOT.TFile.Open(outputName+'.root','RECREATE')
    for h in ratioPlots: h.Write()
    fOut.Close()

