import ROOT
from array import array
from UserCode.TopMassSecVtx.PlotUtils import printProgress

##### EXPAND PER B-FLAVOR B+/- B0  BS Lambda

fragBins=[0,    0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45,
          0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95,
          1.0,  1.2,  1.40, 2.0]
baseHistos={
    'mlB':ROOT.TH1F('mlB',';M(B,l) [GeV];Pairs',100,0,250),
    'mlj':ROOT.TH1F('mlj',';M(j,l) [GeV];Pairs',100,0,250),
    'Bpt':ROOT.TH1F('Bpt',';Transverse momentum [GeV];B-hadrons',100,0,250),
    'Bpt_jpt':ROOT.TH1F('Bpt_jpt',';p_{T}(B)/p_{T}(jet);Jets',len(fragBins)-1,array('f',fragBins)),
    'jpt':ROOT.TH1F('jpt',';Transverse momentum [GeV];Jets',100,0,250),
    'jeta':ROOT.TH1F('jeta',';Pseudo-rapidity;Jets',100,0,2.6),
    'lpt':ROOT.TH1F('lpt',';Transverse momentum [GeV];Leptons',100,0,250),
    'leta':ROOT.TH1F('leta',';Pseudo-rapidity;Leptons',100,0,2.6)
    }


histos={}
fragH={}
fragWgt={}
for model in ['Z2starLEP','Z2star'] : #,'Z2starLEP_lund','Z2starLEP_peterson','Cluster','Lund']:
    fIn=ROOT.TFile.Open('FragmentationDist_%s.root'%model)
    tree=fIn.Get('fragAnalyzer/FragTree')

    histos[model]={}
    fragH[model]={}
    fragWgt[model]={}
    for bid in ['inc','Bpm', 'B0','Bs', 'Others']:

        cond=''
        if bid=='Bpm'    : cond='abs(Bid)==521'
        if bid=='B0'     : cond='abs(Bid)==511 || abs(Bid)==513'
        if bid=='Bs'     : cond='abs(Bid)==531'
        if bid=='Others' : cond='abs(Bid)!=521 && abs(Bid)!=511 && abs(Bid)!=531'

        frag=ROOT.TH1F('frag','',len(fragBins)-1,array('f',fragBins))
        tree.Draw('Bpt/Bjpt >> frag',cond,'goff')
        frag.Scale(1./frag.Integral())
        fragH[model][bid]=frag.Clone('frag_%s_%s' % (model,bid) )
        fragH[model][bid].SetDirectory(0)

        target=fragH['Z2starLEP'][bid].Clone('target')
        target.Divide(frag)
        fragWgt[model][bid]=target.Clone('target_%s_%s' %(model,bid) )
        fragWgt[model][bid].SetDirectory(0)

        frag.Delete()
        target.Delete()

        for key in baseHistos:

            if key.find('l')==0 and bid!='inc' : continue

            tag='%s%s'%(key,bid)
            ic=len(histos)
            histos[model][tag]=baseHistos[key].Clone('%s_%s'%(tag,model))
            histos[model][tag].Sumw2()
            histos[model][tag].SetDirectory(0)
            histos[model][tag].SetTitle('%s'%model)
            histos[model][tag].SetLineColor(ic)
            histos[model][tag].SetMarkerColor(ic)

            histos[model][tag+'_wgt']=histos[model][tag].Clone('%s_wgt_%s'%(tag,model))
            histos[model][tag+'_wgt'].SetDirectory(0)
            histos[model][tag+'_wgt'].SetTitle('%s (Z2*LEP)'%model)
            
    histos[model]['Btype']=ROOT.TH1F('Btype',';B-hadron type;B-hadrons',4,0,4)
    histos[model]['Btype'].GetXaxis().SetBinLabel(1,'B^{0}')
    histos[model]['Btype'].GetXaxis().SetBinLabel(2,'B^{#pm}')
    histos[model]['Btype'].GetXaxis().SetBinLabel(3,'B_{s}')
    histos[model]['Btype'].GetXaxis().SetBinLabel(4,'Others')
    histos[model]['Btype'].SetTitle('%s'%model)
    histos[model]['Btype'].Sumw2()
    histos[model]['Btype'].SetDirectory(0)
    histos[model]['Btype_wgt']=histos[model]['Btype'].Clone('Btype_wgt')
    histos[model]['Btype_wgt'].SetDirectory(0)

    totalEntries=tree.GetEntriesFast()
    for i in xrange(0,totalEntries):
        tree.GetEntry(i)
        printProgress(i,totalEntries)
        
        for ib in xrange(0,tree.nB):

            bid,bidCtr='Others',3
            if ROOT.TMath.Abs(tree.Bid[ib])==511   : bid,bidCtr='B0',0
            elif ROOT.TMath.Abs(tree.Bid[ib])==521 : bid,bidCtr='Bpm',1
            elif ROOT.TMath.Abs(tree.Bid[ib])==531 : bid,bidCtr='Bs',2

            ptratio = tree.Bpt[ib]/tree.Bjpt[ib]
            
            if ptratio>fragWgt[model][bid].GetXaxis().GetXmax() : continue
            bwgt=fragWgt[model][bid].GetBinContent( fragWgt[model][bid].GetXaxis().FindBin(ptratio) )
            histos[model]['Btype'].Fill(bidCtr)
            histos[model]['Btype_wgt'].Fill(bidCtr,bwgt)
            for bkey in ['inc',bid]:
                histos[model]['jpt%s'%bkey].Fill(tree.Bjpt[ib])
                histos[model]['jpt%s_wgt'%bkey].Fill(tree.Bjpt[ib],bwgt)
                histos[model]['jeta%s'%bkey].Fill(ROOT.TMath.Abs(tree.Bjeta[ib]))
                histos[model]['jeta%s_wgt'%bkey].Fill(ROOT.TMath.Abs(tree.Bjeta[ib]),bwgt)
                histos[model]['Bpt%s'%bkey].Fill(tree.Bpt[ib])
                histos[model]['Bpt%s_wgt'%bkey].Fill(tree.Bpt[ib],bwgt)
                histos[model]['Bpt_jpt%s'%bkey].Fill(ptratio)
                histos[model]['Bpt_jpt%s_wgt'%bkey].Fill(ptratio,bwgt)
        
            bhadp4=ROOT.TLorentzVector(0,0,0,0)
            bhadp4.SetPtEtaPhiM(tree.Bpt[ib],tree.Beta[ib],tree.Bphi[ib],tree.Bm[ib])
            bjp4=ROOT.TLorentzVector(0,0,0,0)
            bjp4.SetPtEtaPhiM(tree.Bjpt[ib],tree.Bjeta[ib],tree.Bjphi[ib],tree.Bjm[ib])

            for il in xrange(0,tree.nL):
                lp4=ROOT.TLorentzVector(0,0,0,0)
                lp4.SetPtEtaPhiM(tree.Lpt[il],tree.Leta[il],tree.Lphi[il],tree.Lm[il])
        
                mlB=(bhadp4+lp4).M()
                mlj=(bjp4+lp4).M()
                for bkey in ['inc',bid]:
                    histos[model]['mlB%s'%bkey].Fill(mlB)
                    histos[model]['mlB%s_wgt'%bkey].Fill(mlB,bwgt)
                    histos[model]['mlj%s'%bkey].Fill(mlj)
                    histos[model]['mlj%s_wgt'%bkey].Fill(mlj,bwgt)
                    
                    if ib!=0 or bkey!='inc': continue
                    histos[model]['lpt%s'%bkey].Fill(tree.Lpt[il])
                    histos[model]['lpt%s_wgt'%bkey].Fill(tree.Lpt[il],bwgt)
                    histos[model]['leta%s'%bkey].Fill(ROOT.TMath.Abs(tree.Leta[il]))
                    histos[model]['leta%s_wgt'%bkey].Fill(ROOT.TMath.Abs(tree.Leta[il]),bwgt)


import pickle
cachefile = open(".svlfraghadhistos.pck", 'w')
pickle.dump(histos, cachefile, pickle.HIGHEST_PROTOCOL)
pickle.dump(fragWgt, cachefile, pickle.HIGHEST_PROTOCOL)
cachefile.close()
print 'Wrote .svlfraghadhistos.pck with all the fraghad histos'

#c=ROOT.TCanvas('c','c',500,500)
#ROOT.gStyle.SetOptStat(0)
#ROOT.gStyle.SetOptTitle(0)
#for tag in histos['Cluster']:
#    c.Clear()
#    drawOpt='hist'
#    for model in histos:
#        histos[model][tag].Draw(drawOpt)
#        drawOpt='histsame'
#    c.BuildLegend()
#    c.Modified()
#    c.Update()
#    raw_input(tag)
#            
