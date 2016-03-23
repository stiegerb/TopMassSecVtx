#include "UserCode/TopMassSecVtx/interface/UEAnalysis.h"

using namespace std;

//
UEAnalysis::UEAnalysis(SmartSelectionMonitor &mon)
  : mon_(&mon)
{
  Double_t ptttaxis[]={0,10.,20.,25.,30.,40.,55.,70.,90.,135.,500.};
  Int_t nptttBins=sizeof(ptttaxis)/sizeof(Double_t)-1;

  mon_->addHistogram( new TH1F("ptttbar",";t#bar{t} transverse momentum [GeV];Events",nptttBins,ptttaxis));
  mon_->addHistogram( new TH2F("phiresponse",";Generated #phi(t#bar{t}) [rad]; #Delta #phi(t#bar{t}) [rad];Events",50,0,3.4,50,0,3.4) );
  mon_->addHistogram( new TH2F("phivspt",";Generated t#bar{t} transverse momentum [GeV]; #Delta #phi(t#bar{t}) [rad];Events",nptttBins,ptttaxis,50,0.,3.4) );
  mon_->addHistogram( new TH2F("ptresponse",";Generated p_{T}(t#bar{t}) [GeV]; #Delta p_{T}(t#bar{t}) [GeV]; Events",nptttBins,ptttaxis,50,0.,50.) );

  //soft hadronic activity
  TH1 *hsoft_inc=  mon_->addHistogram( new TH1F("nextrajetsinc",";Extra jet multiplicity;Events",6,0,6));
  for(int ibin=1; ibin<=hsoft_inc->GetXaxis()->GetNbins(); ibin++){
    TString label("="); if(ibin==hsoft_inc->GetXaxis()->GetNbins()) label="#geq"; label += (ibin-1);
    hsoft_inc->GetXaxis()->SetBinLabel(ibin,label);  
  }
}

//
void UEAnalysis::attachToDir(TDirectory *outDir)
{
  //summary ntuple
  summaryTuple_ = new TTree("ue","ue");
  summaryTuple_->SetDirectory(outDir);
  summaryTuple_->SetAutoSave(500000);
  createUEAnalysisSummary(summaryTuple_,ue_);
}


//
void UEAnalysis::analyze(std::vector<data::PhysicsObject_t *> &leptons,
			 std::vector<data::PhysicsObject_t *> &jets,
			 LorentzVector &met,
			 data::PhysicsObjectCollection_t &pf,
			 data::PhysicsObjectCollection_t &gen,
			 int nvtx,
			 float weight)
{
  float minPFpt(0.5), maxPFeta(2.1);
  //float acceptance( 2*TMath::Pi() * maxPFeta );

  //check the event category
  int lid1(leptons[0]->get("id")), lid2(leptons[1]->get("id"));
  std::vector<TString> ch;
  int chIdx(abs(lid1)*abs(lid2));
  if     (chIdx==11*11 || chIdx==13*13) ch.push_back("ll");
  else if(chIdx==11*13) ch.push_back("emu");
  else return;
  ch.push_back("");

  //ttbar system reconstructed
  LorentzVector htlep=*(leptons[0])+*(leptons[1])+*(jets[0])+*(jets[1]);
  LorentzVector rec_ttbar=htlep+met;

  //add category depending on the number of extra jets
  int nGenExtraJets(0), nExtraJets(0), nJets(2);
  for(size_t ijet=2; ijet<jets.size(); ijet++){
    
    //gen-level
    const data::PhysicsObject_t &genJet=jets[ijet]->getObject("genJet");
    if(genJet.pt()>20 && fabs(genJet.eta())<2.5) nGenExtraJets++;
    
    //reco-level
    if(fabs(jets[ijet]->eta())>2.5 ) continue;
    if(jets[ijet]->pt()>=30) nJets++;
    if(jets[ijet]->pt()<20) continue;
    nExtraJets++;
  }
  if(nExtraJets==0) ch.push_back( ch[0]+"eq0j" );
  if(nExtraJets==1) ch.push_back( ch[0]+"eq1j" );
  if(nExtraJets>1)  ch.push_back( ch[0]+"geq2j" );
  mon_->fillHisto("nextrajetsinc",      ch,nExtraJets,        weight);
  
  //
  //generator level kinematics
  //
  LorentzVector top,antitop;
  LorentzVector chLepton,antiChLepton;
  LorentzVector bquark,antibquark;
  LorentzVector genMet(0,0,0,0);
  for(size_t igen=0; igen<gen.size(); igen++)
    {
      if(gen[igen].get("status")!=3) continue;
      if(gen[igen].get("id")==6)  top=gen[igen];
      if(gen[igen].get("id")==-6) antitop=gen[igen];
      if(gen[igen].get("id")==5)  bquark=gen[igen];
      if(gen[igen].get("id")==-5) antibquark=gen[igen];
      if(gen[igen].get("id")==11||gen[igen].get("id")==13)   chLepton=gen[igen];
      if(gen[igen].get("id")==-11||gen[igen].get("id")==-13) antiChLepton=gen[igen];
      if(fabs(gen[igen].get("id"))==12||fabs(gen[igen].get("id"))==14||fabs(gen[igen].get("id"))==16) genMet+=gen[igen];
    }
  LorentzVector gen_ttbar=top+antitop;

  //
  //reconstructed level kinematics
  //
  float const_rec_ttbar_pt( rec_ttbar.pt()>500 ? 500. : rec_ttbar.pt() );
  Int_t ptbin(mon_->getHisto("ptttbar","emu")->GetXaxis()->FindBin(const_rec_ttbar_pt) );
  float ptbinWidth(mon_->getHisto("ptttbar","emu")->GetXaxis()->GetBinWidth(ptbin));
  mon_->fillHisto("ptttbar",  ch, const_rec_ttbar_pt, weight/ptbinWidth);
  if(gen_ttbar.pt()>0)
    {
      mon_->fillHisto("phiresponse",  ch, fabs(gen_ttbar.phi()), fabs(deltaPhi(rec_ttbar.phi(),gen_ttbar.phi())), weight);
      mon_->fillHisto("phivspt",      ch, gen_ttbar.pt(),        fabs(deltaPhi(rec_ttbar.phi(),gen_ttbar.phi())), weight/ptbinWidth);
      mon_->fillHisto("ptresponse",   ch, gen_ttbar.pt(),        fabs(rec_ttbar.pt()-gen_ttbar.pt()),             weight/ptbinWidth);
    }

  //
  //gen level counting
  //
  std::vector<std::pair<float,LorentzVector> > genAccP4;
  for(size_t igen=0; igen<gen.size(); igen++)
    {
      if(gen[igen].get("status") !=1 || gen[igen].get("charge")==0) continue;

      //do not consider if matching the leptons or the charged pf candidates associated to the b-tagged jets
      if( fabs(deltaR(gen[igen],chLepton))<0.1 )     continue;
      if( fabs(deltaPhi(gen[igen],antiChLepton))<0.1 ) continue;
      bool belongsToTagJet(false);
      for(size_t ijet=0; (ijet<2 && !belongsToTagJet); ijet++)
	{
	  size_t pfstart=jets[ijet]->get("pfstart");
	  size_t pfend=jets[ijet]->get("pfend");
	  for(size_t ipfn=pfstart; ipfn<=pfend; ipfn++)
	    {
	      if( fabs(deltaR(gen[igen],pf[ipfn]))>0.1 ) continue;
	      belongsToTagJet=true;
	      break;
	    }
	}
      if(belongsToTagJet) continue;

      //check if in acceptance
      if(gen[igen].pt()<minPFpt || fabs(gen[igen].eta())>maxPFeta) continue;
      float dphi=fabs(deltaPhi(gen[igen].phi(),gen_ttbar.phi())*180/TMath::Pi());
      genAccP4.push_back( std::pair<float,LorentzVector>(dphi,gen[igen]) );
    }
      
  
  
  //
  //rec level counting
  //
  std::vector<std::pair<float,LorentzVector> > recAccP4;  
  std::vector<int> recAccMatches;
  for(size_t ipfn=0; ipfn<pf.size(); ipfn++)
    {
      if(pf[ipfn].get("charge")==0) continue;
      
      //remove if it belongs to a tag jet
      bool belongsToTagJet(false);
      for(size_t ijet=0; ijet<2; ijet++)
	{
	  size_t pfstart=jets[ijet]->get("pfstart");
	  size_t pfend=jets[ijet]->get("pfend");
	  if(ipfn>=pfstart && ipfn<=pfend) belongsToTagJet=true;
	}
      if(belongsToTagJet) continue;
      
      //fiducial cut
      if(pf[ipfn].pt()<minPFpt || fabs(pf[ipfn].eta())>maxPFeta) continue;

      //remove if matching a selected lepton
      double minDRpfl(9999.);
      for(size_t ilep=0; ilep<2; ilep++)
	minDRpfl = TMath::Min( minDRpfl, deltaR(pf[ipfn],*(leptons[ilep]) ) );
      if(minDRpfl<0.05) continue;

      //float dz(pf[ipfn].getVal("dz")),   d0(pf[ipfn].getVal("d0"));
      float sdz(pf[ipfn].getVal("sdz")), sd0(pf[ipfn].getVal("sd0"));
      if(fabs(sdz)>10 || fabs(sd0)>10) continue;

      int nMatch(-1);
      for(size_t igen=0; igen<genAccP4.size(); igen++)
	{
	  float dR=deltaR(genAccP4[igen].second,pf[ipfn]);
	  if(dR>0.1) continue;
	  nMatch=igen;
	  break;
	}
      recAccMatches.push_back(nMatch);
      float dphi=deltaPhi(pf[ipfn].phi(),rec_ttbar.phi())*180/TMath::Pi();
      recAccP4.push_back( std::pair<float,LorentzVector>(dphi,pf[ipfn]) );
    }

  //summary
  ue_.ch=chIdx;
  ue_.weight=weight;
  ue_.normWeight=1.0;
  ue_.gen_ptttbar=gen_ttbar.pt();
  ue_.gen_phittbar=gen_ttbar.phi();
  ue_.rec_ptttbar=rec_ttbar.pt();
  ue_.rec_phittbar=rec_ttbar.phi();
  ue_.njets=nJets;
  ue_.gen_nextrajets=nGenExtraJets;
  ue_.rec_nextrajets=nExtraJets;
  ue_.leadpt=leptons[0]->pt();
  ue_.trailerpt=leptons[1]->pt();
  ue_.st=leptons[0]->pt()+leptons[1]->pt();
  LorentzVector dil=*(leptons[0])+*(leptons[1]);
  ue_.sumpt=dil.pt();


  //reset counters before filling
  for(int ireg=0; ireg<4; ireg++)
    for(int jreg=0; jreg<4; jreg++)
      {
	ue_.gen_nch[ireg][jreg]=0; 	ue_.rec_nch[ireg][jreg]=0;
	ue_.gen_ptflux[ireg][jreg]=0;   ue_.rec_ptflux[ireg][jreg]=0;
	ue_.gen_avgpt[ireg][jreg]=0;    ue_.rec_avgpt[ireg][jreg]=0;
      }

  for(size_t ipf=0; ipf<recAccP4.size(); ipf++)
    {
      float rec_dphi( fabs(recAccP4[ipf].first) );
      int ireg=1;
      if(rec_dphi>60 && rec_dphi<120) ireg=2;
      if(rec_dphi>120) ireg=3;

      int jreg=0;
      if( recAccMatches[ipf]>=0 ) 
	{
	  float gen_dphi=genAccP4[ recAccMatches[ipf] ].first;
	  jreg=1;
	  if(gen_dphi>60 && gen_dphi<120) jreg=2;
	  if(gen_dphi>120) jreg=3;

	  ue_.gen_nch[ireg][jreg]    += 1;
	  ue_.gen_ptflux[ireg][jreg] += genAccP4[ recAccMatches[ipf] ].second.pt();
	}

      ue_.rec_nch[ireg][jreg] +=1;       
      ue_.rec_ptflux[ireg][jreg]  += recAccP4[ipf].second.pt();
    }
  
  //take into account inefficiencies
  for(int igen=0; igen<(int)genAccP4.size(); igen++)
    {
      if( std::find(recAccMatches.begin(), recAccMatches.end(), igen) != recAccMatches.end() ) continue;
      
      int ireg=0;
   
      float gen_dphi=genAccP4[ igen ].first;
      int jreg=1;
      if(gen_dphi>60 && gen_dphi<120) jreg=2;
      if(gen_dphi>120) jreg=3;

      ue_.gen_nch[ireg][jreg]    += 1;
      ue_.gen_ptflux[ireg][jreg] += genAccP4[igen].second.pt();      
    }

  //finalize
  for(int ireg=0; ireg<4; ireg++)
    for(int jreg=0; jreg<4; jreg++)
      {
	if(ue_.gen_nch[ireg][jreg]>0) 	ue_.gen_avgpt[ireg][jreg]=ue_.gen_ptflux[ireg][jreg]/ue_.gen_nch[ireg][jreg];
	if(ue_.rec_nch[ireg][jreg]>0) 	ue_.rec_avgpt[ireg][jreg]=ue_.rec_ptflux[ireg][jreg]/ue_.rec_nch[ireg][jreg];	
	/*
	cout << "(" << ireg << "," << jreg << ")" 
	     << " ch=" << ue_.gen_nch[ireg][jreg] << "/" << ue_.rec_nch[ireg][jreg]
	     << " pt=" << ue_.gen_ptflux[ireg][jreg] << "/" << ue_.rec_ptflux[ireg][jreg]
	     << endl;
	*/
      }
}
