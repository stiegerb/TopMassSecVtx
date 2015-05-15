#include "FWCore/Utilities/interface/EDMException.h"
#include "DataFormats/JetReco/interface/GenJet.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/Common/interface/View.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "UserCode/TopMassSecVtx/interface/MacroUtils.h"
#include <memory>
#include <string>
#include <iostream>
#include "TH1.h"
#include "TH2.h"
#include "TFile.h"
#include "TString.h"
#include "TVector2.h"
#include "TTree.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"


#define IS_BHADRON_PDGID(id) ( ((abs(id)/100)%10 == 5) || (abs(id) >= 5000 && abs(id) <= 5999) )
#define IS_NEUTRINO_PDGID(id) ( (abs(id) == 12) || (abs(id) == 14) || (abs(id) == 16) )


class FragmentationAnalyzer : public edm::EDAnalyzer {

 public:
  FragmentationAnalyzer(const edm::ParameterSet&);
  virtual void analyze(const edm::Event&, const edm::EventSetup&);
  
 private:
  edm::InputTag genJets_;
  std::map<std::string, TH1F*> hists;
  TTree *ntuple_;
  Int_t nB_,nL_, Bid_[100], Bntk_[100], Lid_[100];
  Float_t Bpt_[100],  Beta_[100],  Bphi_[100],   Bm_[100];
  Float_t Bjpt_[100], Bjeta_[100], Bjphi_[100],  Bjm_[100];
  Float_t Bsvpt_[100],Bsveta_[100],Bsvphi_[100], Bsvm_[100];
  Float_t Lpt_[100],  Leta_[100],  Lphi_[100],   Lm_[100];
};

FragmentationAnalyzer::FragmentationAnalyzer(const edm::ParameterSet& cfg) : 
  genJets_(cfg.getParameter<edm::InputTag>("genJets"))
{
  
  // load TFile Service
  edm::Service<TFileService> fs;
  if( !fs )
    {
      throw edm::Exception( edm::errors::Configuration,"TFile Service is not registered in cfg file");
    }
  hists["genBHadronNuDecay"]     = fs->make<TH1F>("genBHadronNuDecay",    "genBHadronNuDecay", 2, 0, 2);
  hists["genBHadronPtFraction"]  = fs->make<TH1F>("genBHadronPtFraction", "genBHadronPtFraction", 100, 0, 2);
  for(std::map<std::string, TH1F*>::iterator it=hists.begin(); it != hists.end(); it++) it->second->Sumw2();
  
  //summary tree
  ntuple_ = fs->make<TTree>("FragTree","FragTree");
  ntuple_->Branch("nB",    &nB_,    "nB/I");
  ntuple_->Branch("Bid",    Bid_,   "Bid[nB]/I");
  ntuple_->Branch("Bntk",   Bntk_,  "Bntk[nB]/I");
  ntuple_->Branch("Bpt",    Bpt_,   "Bpt[nB]/F");
  ntuple_->Branch("Beta",   Beta_,  "Beta[nB]/F");
  ntuple_->Branch("Bphi",   Bphi_,  "Bphi[nB]/F");
  ntuple_->Branch("Bm",     Bm_,    "Bm[nB]/F");
  ntuple_->Branch("Bjpt",   Bjpt_,  "Bjpt[nB]/F");
  ntuple_->Branch("Bjeta",  Bjeta_, "Bjeta[nB]/F");
  ntuple_->Branch("Bjphi",  Bjphi_, "Bjphi[nB]/F");
  ntuple_->Branch("Bjm",    Bjm_,   "Bjm[nB]/F");
  ntuple_->Branch("Bsvpt",  Bsvpt_, "Bsvpt[nB]/F");
  ntuple_->Branch("Bsveta", Bsveta_,"Bsveta[nB]/F");
  ntuple_->Branch("Bsvphi", Bsvphi_,"Bsvphi[nB]/F");
  ntuple_->Branch("Bsvm",   Bsvm_,  "Bsvm[nB]/F");
  ntuple_->Branch("nL",    &nL_,    "nL/I");
  ntuple_->Branch("Lid",    Lid_,   "Lid[nL]/I");
  ntuple_->Branch("Lpt",    Lpt_,   "Lpt[nL]/F");
  ntuple_->Branch("Leta",   Leta_,  "Leta[nL]/F");
  ntuple_->Branch("Lphi",   Lphi_,  "Lphi[nL]/F");
  ntuple_->Branch("Lm",     Lm_,    "Lm[nL]/F");
}

//
void FragmentationAnalyzer::analyze(const edm::Event& evt, const edm::EventSetup& setup)
{  
  std::vector<int> leptons,bHadrons;

  //gen jets
  edm::Handle<std::vector< reco::GenJet > > genJets;
  evt.getByLabel(genJets_, genJets);
  
  //gen particles
  edm::Handle<reco::GenParticleCollection> genParticles;
  evt.getByLabel("genParticles", genParticles);
  for(size_t i = 0; i < genParticles->size(); ++ i) 
    {
      const reco::GenParticle & p = (*genParticles)[i];
      const reco::Candidate *mother=p.mother();
      int id = p.pdgId();
      if (p.pt() == 0) continue;

      //iso leptons
      if(abs(id)==11 || abs(id)==13)
	{ 
	  if(p.pt()<20 || fabs(p.eta())>2.5 || mother==0 || abs(mother->pdgId())!=24) continue;
	  leptons.push_back(i); 
	}      

      //B hadrons
      if (!IS_BHADRON_PDGID(id)) continue;
      
      int n = p.numberOfDaughters();
      if(n<2) continue;
      
      bool hasBDaughter = false;
      bool hasNuDaughter = false;
      for(int j = 0; j < n; ++j) 
	{
	  const reco::Candidate * d = p.daughter( j );
	  int dauId = d->pdgId();
	  if (IS_BHADRON_PDGID(dauId)) 
	    {
	      hasBDaughter = true;
	      break;
	    }
	  if (IS_NEUTRINO_PDGID(dauId)) hasNuDaughter = true;
	}
      if(hasBDaughter) continue;
      
      bHadrons.push_back(i);

      // Weakly decaying B hadron
      hists.find("genBHadronNuDecay")->second->Fill( hasNuDaughter );
      
      // Fragmentation distribution
      for (std::vector< reco::GenJet >::const_iterator ijet = genJets->begin(); 
	   ijet != genJets->end(); 
	   ++ijet)
	{
	  if (p.pt() == 0 || ijet->pt() == 0) continue;
	  double dr   = deltaR(p,*ijet);
	  
	  // Simple dR match of hadron and GenJet
	  if (dr < 0.5) 
	    {
	      double xb = p.pt()/ijet->pt();
	      hists.find("genBHadronPtFraction")->second->Fill(xb);	      
	      break;
	    }
	}
    }

  if(bHadrons.size()==0) return;

  //for b-hadron studies
  nB_=0;
  for (std::vector< reco::GenJet >::const_iterator ijet = genJets->begin();
       ijet != genJets->end();
       ++ijet)
    {
      //fiducial cuts
      if(ijet->pt()<20) continue;
      if(fabs(ijet->eta())>2.5) continue;

      //quality cuts
      if(ijet->hadEnergy()/ijet->energy()<0.05) continue; 
      if(ijet->emEnergy()/ijet->energy()>0.95)  continue; 
      if(ijet->getGenConstituents().size()<2)   continue;
	
      //check if a B hadron can be matched
      bool isBjet(false);
      for(int k=bHadrons.size()-1; k>=0; --k)
	{
	  const reco::GenParticle & bhad = (*genParticles)[ bHadrons[k] ];
	  float dR=deltaR(bhad,*ijet);
	  if(dR>0.5) continue;

	  Bid_[nB_]  = bhad.pdgId();
	  Bpt_[nB_]  = bhad.pt();
	  Beta_[nB_] = bhad.eta();      
	  Bphi_[nB_] = bhad.phi();
	  Bm_[nB_]   = bhad.mass();
	  Bntk_[nB_] = 0;
	  LorentzVector svP4(0,0,0,0);
	  for(size_t j = 0; j < bhad.numberOfDaughters(); ++j) 
	    {
	      const reco::Candidate * d = bhad.daughter(j);
	      if(d==0) continue;
	      if(d->charge()==0) continue;
	      svP4 += d->p4();
	      Bntk_[nB_] += (d->charge()!=0);
	    }
	  Bsvpt_[nB_]=svP4.pt();
	  Bsveta_[nB_]=svP4.eta();
	  Bsvphi_[nB_]=svP4.phi();
	  Bsvm_[nB_]=svP4.mass();
	  isBjet=true;
	  break;
	}
      if(!isBjet) continue;

      Bjpt_[nB_]  = ijet->pt();
      Bjeta_[nB_] = ijet->eta();
      Bjphi_[nB_] = ijet->phi();
      Bjm_[nB_]   = ijet->mass();
      nB_++;
    }
  
  //leptons from W may be from semileptonic hadron decays (at least in Sherpa)
  nL_=0;
  for(size_t ilep=0; ilep<leptons.size(); ilep++)
    {
      const reco::GenParticle & lep = (*genParticles)[ leptons[ilep] ];
      float minDR(9999.);
      for(size_t ib=0; ib<bHadrons.size(); ib++)
	{
	  const reco::GenParticle & bhad = (*genParticles)[ bHadrons[ib] ];
          float dR=deltaR(lep,bhad);
	  if(minDR<dR) minDR=dR;
	}
      if(minDR<0.5) continue;
      Lid_[nL_]  = lep.pdgId();
      Lpt_[nL_]  = lep.pt();
      Leta_[nL_] = lep.eta();
      Lphi_[nL_] = lep.phi();
      Lm_[nL_]   = lep.mass();
      nL_++;
    }
  
  //fill ntuple
  if(nL_ && nB_) ntuple_->Fill();
}


DEFINE_FWK_MODULE(FragmentationAnalyzer);
