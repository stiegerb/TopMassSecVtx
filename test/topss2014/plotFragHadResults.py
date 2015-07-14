import ROOT

from UserCode.TopMassSecVtx.PlotUtils import *

import pickle
cachefile = open('.svlfraghadhistos.pck', 'r')
histos=pickle.load(cachefile)
cachefile.close()

setTDRStyle()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)
ROOT.gROOT.SetBatch(True)

c=ROOT.TCanvas('c','c',500,500)
c.SetRightMargin(0)
c.SetLeftMargin(0)
c.SetTopMargin(0)
c.SetBottomMargin(0)

p1 = ROOT.TPad('p1','p1',0.0,0.85,1.0,0.0)
p1.Draw()
c.cd()
p2 = ROOT.TPad('p2','p2',0.0,0.85,1.0,1.0)
p2.Draw()

for tag in histos['Z2star']:
    
    p1.cd()
    p1.Clear()
    p1.SetRightMargin(0.05)
    p1.SetLeftMargin(0.12)
    p1.SetTopMargin(0.008)
    p1.SetBottomMargin(0.15)
    p1.SetGridx(True)
    drawOpt='hist'
    pulls=[]
    refH=None
    hctr=0
    for model in histos:
        if not model in ['Z2star','Z2starLEP'] : continue
        #if not model in ['Z2starLEP','Z2starLEP_peterson','Z2starLEP_lund']: continue
        #if not model in ['Z2starLEP','Z2star']:continue
        #if not model in ['Cluster','Lund']: continue
        if not 'Bpt_jpt' in histos[model][tag].GetName() and not 'Btype' in histos[model][tag].GetName() :
            histos[model][tag].Rebin(4)
        total=histos[model][tag].Integral()
        if total==0: continue
        hctr+=1
        histos[model][tag].SetLineColor(hctr)
        histos[model][tag].Scale(1./total)
        histos[model][tag].Draw(drawOpt)
        drawOpt='histsame'
        histos[model][tag].GetYaxis().SetTitle('PDF')
        histos[model][tag].SetFillStyle(0)
	histos[model][tag].GetYaxis().SetLabelSize(0.04)
	histos[model][tag].GetYaxis().SetTitleSize(0.05)
	histos[model][tag].GetXaxis().SetTitleOffset(1.3)
	histos[model][tag].GetXaxis().SetLabelSize(0.04)
	histos[model][tag].GetXaxis().SetTitleSize(0.05)
	histos[model][tag].GetXaxis().SetTitleOffset(0.8)

        if refH is None:
            refH=histos[model][tag]
        else:
            pulls.append( histos[model][tag].Clone( histos[model][tag].GetName()+'_pull') )
            pulls[-1].SetDirectory(0)
            pulls[-1].Divide(refH)
            chi2=refH.Chi2Test(histos[model][tag],'WW CHI2/NDF')
            title='#splitline{%s}{#scale[0.8]{#chi^{2}/ndf:%3.2f}}'%(histos[model][tag].GetTitle(),chi2)
            #pval=refH.Chi2Test(histos[model][tag],'WW')
            #title='#splitline{%s}{#scale[0.8]{p-val:%3.2f}}'%(histos[model][tag].GetTitle(),pval)
            title=title.replace('star','*')
            title=title.replace('LEP_','LEP')
            histos[model][tag].SetTitle(title)
#            pulls[-1].Add(refH,-1)
#            for xbin in xrange(1,pulls[-1].GetXaxis().GetNbins()):
#                refUnc=refH.GetBinError(xbin)
#                if refUnc>0:
#                    diff=pulls[-1].GetBinContent(xbin)
#                    diffUnc=pulls[-1].GetBinError(xbin)
#                    pulls[-1].SetBinContent(xbin,diff/refUnc)
#                    pulls[-1].SetBinError(xbin,diffUnc/refUnc)
#                else:
#                    pulls[-1].SetBinContent(xbin,0)
#                    pulls[-1].SetBinError(xbin,0)
#            pulls[-1].SetMarkerStyle(20)
            pulls[-1].SetMarkerColor(pulls[-1].GetLineColor())
        drawOpt='histsame'
    if drawOpt=='hist' : continue
    leg=p1.BuildLegend(0.5,0.5,0.95,0.95)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.04)
    leg.SetTextAlign(12)
    leg.SetTextFont(42)
    cat='inclusive'
    if 'Bpm' in tag : cat='B^{#pm}'
    if 'B0' in tag : cat='B^{0}'
    if 'Bs' in tag : cat='B_{s}'
    if 'Others' in tag : cat='Others'
    leg.SetHeader("#splitline{#bf{Pythia} #it{simulation} (8 TeV)}{#it{%s}}"%cat)
    #leg.SetHeader("#splitline{#bf{Sherpa} #it{simulation} (8 TeV)}{#it{%s}}"%cat)
    leg.Draw()

    p2.cd()
    p2.SetBottomMargin(0.005)
    p2.SetRightMargin(0.05)
    p2.SetLeftMargin(0.12)
    p2.SetTopMargin(0.05)
    p2.SetGridx(True)
    p2.SetGridy(True)
    drawOpt=''
    for p in pulls:
        p.Draw(drawOpt)
        drawOpt='same'        
        #p.GetYaxis().SetTitle("Pull")
        p.SetMarkerStyle(20)
        p.SetMarkerColor(p.GetLineColor())
        p.GetYaxis().SetTitle("Ratio")
	p.GetYaxis().SetTitleSize(0.3)
	p.GetYaxis().SetLabelSize(0.2)
	p.GetXaxis().SetTitleSize(0)
	p.GetXaxis().SetLabelSize(0)
	p.GetYaxis().SetTitleOffset(0.15)
	p.GetYaxis().SetNdivisions(4)
	#p.GetYaxis().SetRangeUser(-8.1,8.1)
	p.GetYaxis().SetRangeUser(0.75,1.25)
	p.GetXaxis().SetTitleOffset(0.8)

    c.cd()
    c.Modified()
    c.Update()
    c.SaveAs('%s.png'%tag)
    c.SaveAs('%s.pdf'%tag)
    if tag=='Btype':
        fOut=ROOT.TFile.Open('BtypeWeights.root','RECREATE')
        for p in pulls: p.Write()
        fOut.Close()

p1.Delete()
p2.Delete()
c.Delete()
            
