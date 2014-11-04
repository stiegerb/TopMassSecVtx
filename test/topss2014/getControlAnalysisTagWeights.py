import ROOT
import os

from UserCode.TopMassSecVtx.CMS_lumi import *
from UserCode.TopMassSecVtx.PlotUtils import *
from UserCode.TopMassSecVtx.rounding import *

setTDRStyle()


samples=['qcd','z','w','photon']
dir="%s/public/html/TopMassSecVtx"%(os.environ.get('HOME'))

tagPtGr=[]
for s in samples :
    url='%s/%s_samples_plots/plotter.root'%(dir,s)
    fIn=ROOT.TFile.Open(url)
    
    for plotDirName in ['all_tagpt','all_probeflav','svx_probeflav']:
        plotDir=fIn.Get(plotDirName)

        totalMC=None
        data=None
        for key in plotDir.GetListOfKeys():
            hname=key.GetName()
            h=fIn.Get('%s/%s'%(plotDirName,hname))
            if hname.find('MC')>=0 :
                if totalMC is None:
                    totalMC=h.Clone(plotDirName+'_totalmc')
                    totalMC.Reset('ICE')
                totalMC.Add(h)
            elif hname.find('Data')>=0:
                data=h.Clone(plotDirName+'_data')
        
        #derive the weights to reweight MC to match the tag pT spectrum
        if plotDirName.find('tagpt')>=0 :
            data.Scale(1./data.Integral())
            totalMC.Scale(1./totalMC.Integral())
            ratio=data.Clone(s)
            ratio.Divide(totalMC)
            tagPtGr.append( ROOT.TGraphErrors(ratio) )
            tagPtGr[ len(tagPtGr)-1 ].SetName(s)

        #build the flavour composition pie
        if plotDirName.find('probeflav')>=0 :
            nbins=totalMC.GetXaxis().GetNbins()
            flavorH=ROOT.TH1F('expflav',';Jet flavour;% expected',nbins-1,0,nbins-1)
            flavorH.SetFillColor(ROOT.kGray)

            print '********************'
            print s,plotDirName
            totalJetsData=data.GetBinContent(1)
            totalJets=totalMC.GetBinContent(1)
            for i in xrange(2,nbins+1):
                frac=totalMC.GetBinContent(i)/totalJets
                fracErr=totalMC.GetBinError(i)/totalJets
                flavorH.GetXaxis().SetBinLabel(i-1,totalMC.GetXaxis().GetBinLabel(i))
                flavorH.SetBinContent(i-1,frac)
                flavorH.SetBinError(i-1,fracErr)
                print totalMC.GetXaxis().GetBinLabel(i),' ',toLatexRounded(totalJetsData*frac,totalJetsData*fracErr)
            
            canvas=ROOT.TCanvas('c','c',500,500)
            flavorPie=ROOT.TPie(flavorH)
            flavorPie.SetRadius(.35)
            flavorPie.SetLabelFormat('#splitline{#scale[0.7]{%txt}}{%perc}')
            flavorPie.Draw()
            CMS_lumi(canvas,2,0)

            txt=ROOT.TPaveText(0.18,0.87,0.22,0.92,'brNDC')
            txt.SetBorderSize(0)
            txt.SetTextAlign(12)
            txt.SetFillStyle(0)
            txt.SetTextFont(42)
            txt.SetTextSize(0.03)
            txt.AddText(s + ' events')
            txt.Draw()

            canvas.Modified()
            canvas.Update()
    
            raw_input()
            for ext in ['png','pdf'] : canvas.SaveAs('%s_%s.%s'%(plotDirName,s,ext))
    fIn.Close()
            
#save weights into file                       
fOut=ROOT.TFile('ControlTagPtWeights.root','RECREATE')
for gr in tagPtGr : gr.Write()
fOut.Close()
