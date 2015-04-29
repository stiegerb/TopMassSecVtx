#include "FWCore/Utilities/interface/EDMException.h"
#include "DataFormats/JetReco/interface/GenJet.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/Common/interface/View.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include <memory>
#include <string>
#include <iostream>
#include "TH1.h"
#include "TH2.h"
#include "TFile.h"
#include "TString.h"
#include "TVector2.h"
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
  hists["genBHadronNuDecay"]     = fs->make<TH1F>("genBHadronNuDecay", "genBHadronNuDecay", 2, 0, 2);
  hists["genBHadronPtFraction"]  = fs->make<TH1F>("genBHadronPtFraction", "genBHadronPtFraction", 100, 0, 2);
}

//
void FragmentationAnalyzer::analyze(const edm::Event& evt, const edm::EventSetup& setup)
{  
  edm::Handle<std::vector< reco::GenJet > > genJets;
  evt.getByLabel(genJets_, genJets);
  
  //////////////////////////////////////////////////////////////////////////
  // GENPARTICLES
  ////////////////////////////////////////////////////////////////////////
  
  edm::Handle<reco::GenParticleCollection> genParticles;
  evt.getByLabel("genParticles", genParticles);
  for(size_t i = 0; i < genParticles->size(); ++ i) 
    {
      const reco::GenParticle & p = (*genParticles)[i];
      if (p.pt() == 0) continue;
      
      int id = p.pdgId();
      if (!IS_BHADRON_PDGID(id)) continue;
      
      int n = p.numberOfDaughters();
      
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
      
      // Weakly decaying B hadron
      if (!hasBDaughter) 
	{
	  hists.find("genBHadronNuDecay")->second->Fill( hasNuDaughter );
	  
	  // Fragmentation distribution
	  for (std::vector< reco::GenJet >::const_iterator ijet = genJets->begin(); ijet != genJets->end(); ++ijet) 
	    {
	      if (p.pt() == 0 || ijet->pt() == 0) continue;
	      double deta = p.eta() - ijet->eta();
	      double dphi = TVector2::Phi_mpi_pi(p.phi() - ijet->phi());
	      double dr   = sqrt( deta*deta + dphi*dphi );
	      
	      // Simple dR match of hadron and GenJet
	      if (dr < 0.5) 
		{
		  double xb = p.pt()/ijet->pt();
		  hists.find("genBHadronPtFraction")->second->Fill(xb);
		  break;
		}
	    }
	}
    }
}


DEFINE_FWK_MODULE(FragmentationAnalyzer);
