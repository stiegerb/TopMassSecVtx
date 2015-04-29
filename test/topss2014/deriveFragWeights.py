import ROOT

fIn=ROOT.TFile.Open('BfragWeights.root')

Z2starLEP=fIn.Get('genBHadronPtFraction;1').Clone('Z2starLEP')
Z2starLEP.SetTitle('Z2starLEP')
Z2starLEP.SetDirectory(0)

Z2star_rbLEP=fIn.Get('genBHadronPtFraction;2').Clone('Z2star_rbLEP')
Z2star_rbLEP.SetDirectory(0)

Z2star_rbLEPhard=fIn.Get('genBHadronPtFraction;3').Clone('Z2star_rbLEPhard')
Z2star_rbLEPhard.SetDirectory(0)

Z2star_rbLEPsoft=fIn.Get('genBHadronPtFraction;4').Clone('Z2star_rbLEPsoft')
Z2star_rbLEPsoft.SetDirectory(0)

fIn.Close()

allHistos=[Z2starLEP,Z2star_rbLEP,Z2star_rbLEPhard,Z2star_rbLEPsoft]

for tune in ['P11','Z2starLEP_peterson','Z2starLEP_lund']:
    fIn=ROOT.TFile.Open('FragmentationDist_%s.root'%tune)
    allHistos.append( fIn.Get('fragAnalyzer/genBHadronPtFraction').Clone(tune) )
    allHistos[-1].SetDirectory(0)
    allHistos[-1].SetTitle(tune)
    fIn.Close()

for h in allHistos:
    h.Sumw2()
    h.Scale(1./h.Integral())

ratioGr=[]
for h in allHistos:
    ratio=h.Clone('ratio')
    ratio.Divide(Z2starLEP)
    ratioGr.append( ROOT.TGraphErrors(ratio) )
    ratioGr[-1].SetName(h.GetName()+'_weight')    
    ratio.Delete()

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

c=ROOT.TCanvas('c','c',500,500)
c.SetRightMargin(0.05)
c.SetTopMargin(0.05)
c.SetLeftMargin(0.12)
c.SetBottomMargin(0.1)
colors=[ROOT.kBlack,ROOT.kMagenta, ROOT.kMagenta+2, ROOT.kMagenta-9,ROOT.kRed+1,ROOT.kAzure+7, ROOT.kBlue-7]
for i in xrange(0,len(allHistos)):
    title=allHistos[i].GetTitle()
    title=title.replace('star','*')
    title=title.replace('_',' ')
    allHistos[i].SetTitle(title)
    drawOpt='hist' if i==0 else 'histsame'
    allHistos[i].SetLineColor(colors[i])
    allHistos[i].SetMarkerColor(colors[i])
    allHistos[i].Draw(drawOpt)
    allHistos[i].GetYaxis().SetRangeUser(0,0.1)
    allHistos[i].GetXaxis().SetTitle("p_{T}(B)/p_{T}(AK5 jet)")
    allHistos[i].GetYaxis().SetTitle('PDF')
leg=c.BuildLegend()
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetBorderSize(0)
leg.SetNColumns(2)
c.Modified()
c.Update()
raw_input()
c.SaveAs('fragfunctions.pdf')

c.Clear()
for i in xrange(0,len(ratioGr)):
    title=allHistos[i].GetTitle()
    ratioGr[i].SetTitle(title)
    drawOpt='a3' if i==0 else 'cx'
    ratioGr[i].SetLineColor(colors[i])
    ratioGr[i].SetMarkerColor(colors[i])
    if i==0:
        ratioGr[i].SetFillStyle(3001)
        ratioGr[i].SetFillColor(ROOT.kGray)
    ratioGr[i].Draw(drawOpt)
    ratioGr[i].GetYaxis().SetRangeUser(0.4,2.5)
    ratioGr[i].GetXaxis().SetTitle("p_{T}(B)/p_{T}(AK5 jet)")
    ratioGr[i].GetYaxis().SetTitle('Ratio to Z2* LEP')
leg=c.BuildLegend()
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetBorderSize(0)
leg.SetNColumns(2)
raw_input()
c.SaveAs('fragweights.pdf')

    
fOut=ROOT.TFile.Open('FinalBfragWeights.root','RECREATE')
for h in allHistos : h.Write()
for gr in ratioGr: gr.Write()
fOut.Close()

