import ROOT

"""
"""
def showHistosFor(distName,tags):

    allHistos=[]
    for name,title,_ in tags:
        fIn=ROOT.TFile.Open('FragmentationDist_%s.root'%name)
        print fIn
        allHistos.append( fIn.Get("fragAnalyzer/%s"%distName) )
        allHistos[-1].SetDirectory(0)
        allHistos[-1].SetName(name)
        allHistos[-1].SetTitle(title)
        fIn.Close()

    c=ROOT.TCanvas('c','c',500,800)
    for ybin in xrange(1,allHistos[0].GetYaxis().GetNbins()+1):
        c.Clear()
        c.Divide(1,2)

        ref=None
        allProjs=[]
        allPulls=[]
        p=c.cd(1)
        p.SetLeftMargin(0.15)
        p.SetRightMargin(0.05)
        p.SetTopMargin(0.05)
        p.SetBottomMargin(0.12)
        for i in xrange(0,len(allHistos)):
            proj=allHistos[i].ProjectionX('%s_%d_%d'%(allHistos[i].GetName(),ybin,i),ybin,ybin)
            if 'ml' in distName : proj.Rebin(4)
            allProjs.append(proj)
            proj.Scale(1./proj.Integral())
            proj.SetLineColor(tags[i][2])
            proj.SetLineWidth(2)
            drawOpt='hist' if i==0 else 'histsame'
            proj.Draw(drawOpt)
            if 'ml' in distName : proj.GetXaxis().SetRangeUser(0,300)
            proj.GetYaxis().SetTitle('PDF')
            proj.GetYaxis().SetTitleSize(0.06)
            proj.GetXaxis().SetTitleSize(0.06)
            proj.GetYaxis().SetLabelSize(0.06)
            proj.GetXaxis().SetLabelSize(0.06)
            proj.GetXaxis().SetTitleOffset(0.9)
            
            if ref is None: ref=proj.Clone()
            allPulls.append(proj.Clone(proj.GetName()+'_pull'))
            allPulls[-1].SetDirectory(0)
            allPulls[-1].Divide(ref)
        
        leg=p.BuildLegend(0.6,0.7,0.9,0.95)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetTextFont(42)
        leg.SetTextSize(0.05)
        leg.SetHeader('#bf{CMS} #it{simulation}')

        p=c.cd(2)
        p.SetLeftMargin(0.15)
        p.SetRightMargin(0.05)
        p.SetTopMargin(0.05)
        p.SetBottomMargin(0.12)
        for i in xrange(0,len(allPulls)):
            drawOpt='e2' if i==0 else 'same'
            if i==0:
                allPulls[i].SetFillStyle(3001)
                allPulls[i].SetFillColor(tags[i][2])
            else:
                allPulls[i].SetMarkerStyle(20+i)
                allPulls[i].SetMarkerColor(tags[i][2])
            allPulls[i].Draw(drawOpt)
            allPulls[i].GetYaxis().SetTitle('Ratio')
            allPulls[i].GetYaxis().SetRangeUser(0.8,1.2)
            if 'ml' in distName : allPulls[i].GetXaxis().SetRangeUser(0,200)
            if 'ntrk' in distName : allPulls[i].GetYaxis().SetRangeUser(0.5,2.0)
        c.Modified()
        c.Update()
        c.SaveAs('%s_%d.png'%(distName,ybin))
        c.SaveAs('%s_%d.pdf'%(distName,ybin))
        
        for h in allProjs: h.Delete()
        for h in allPulls: h.Delete()

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)
tags=[
    ('Lund','String (SHERPA)',ROOT.kBlack),
    ('Cluster','Cluster (SHERPA)',ROOT.kAzure+7),
    ('Z2star','String (PYTHIA)',ROOT.kGreen-3)
    ]
for distName in ['mlB','mlBmatched','mlbjet','ntrk']:
    showHistosFor(distName=distName,tags=tags)

