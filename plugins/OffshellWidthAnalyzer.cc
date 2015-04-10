// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDFilter.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
//
// class declaration
//

#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/JetReco/interface/GenJetCollection.h"
#include "DataFormats/JetReco/interface/GenJet.h"
#include "DataFormats/Math/interface/deltaR.h"

#include <TTree.h>
#include <TH1F.h>

#include <algorithm>

bool sortCandidatesByPt(const reco::Candidate *a, const reco::Candidate *b)  { return a->pt()>b->pt(); }

class OffshellWidthAnalyzer : public edm::EDFilter 
{
public:
  explicit OffshellWidthAnalyzer(const edm::ParameterSet&);
  ~OffshellWidthAnalyzer();
  
  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  
private:
  virtual void beginJob() ;
  virtual bool filter( edm::Event & , const edm::EventSetup & );
  virtual void endJob() ;
  
  virtual void beginRun(edm::Run const&, edm::EventSetup const&);
  virtual void endRun(edm::Run const&, edm::EventSetup const&);
  virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
  virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

  TTree *ntuple;
  float l1id,l1pt,l1eta,l1phi,l1mass,l2id,l2pt,l2eta,l2phi,l2mass;
  int nj;
  int jflav[100],jmatch[100];
  float jpt[100],jeta[100],jphi[100],jmass[100];
  int ng,gid[100];
  float gpt[100],geta[100],gphi[100],gmass[100];
  TH1F *countH;
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
OffshellWidthAnalyzer::OffshellWidthAnalyzer(const edm::ParameterSet& iConfig)
{
   //now do what ever initialization is needed
}


OffshellWidthAnalyzer::~OffshellWidthAnalyzer()
{
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)
}


//
// member functions
//

// ------------ method called for each event  ------------
bool OffshellWidthAnalyzer::filter( edm::Event &iEvent , const edm::EventSetup &iSetup )
{
   using namespace std;
   using namespace edm;

   //count generated events
   countH->Fill(0);

   //
   // gen particles
   //
   edm::Handle< std::vector<reco::GenParticle> > genParticles;
   iEvent.getByLabel("genParticles", genParticles);
   if(!genParticles.isValid())     cerr << "  WARNING: genParticles is not valid! " << endl;
   std::vector<const reco::Candidate *> outgoingLeptons, finalstatePartons, hardProcW, hardProcB, finalStateB, hardProcLeptons;
   for(size_t i=0; i<genParticles->size(); i++)
     {
       const reco::GenParticle &genParticle=genParticles->at(i);
       int status=genParticle.status();
       int pid=genParticle.pdgId();
       bool isLepton(abs(pid)==11||abs(pid)==13);
       bool isParton(abs(pid)<6 || abs(pid)==21);
       if(status==3)
	 {
	   if(abs(pid)==5)  { hardProcB.push_back(&genParticle); finalStateB.push_back(&genParticle); }
	   if(abs(pid)==23) { hardProcW.push_back(&genParticle); }
	   if(isLepton)     { hardProcLeptons.push_back(&genParticle); }
	 }
       if(status==2 && isParton)
	 {
	   finalstatePartons.push_back(&genParticle);
	 }
       if(status==1 && isLepton) 
	 {
	   outgoingLeptons.push_back(&genParticle);
	 } 
     }

   //require two leptons
   if(outgoingLeptons.size()<2) return false;
   sort(outgoingLeptons.begin(),outgoingLeptons.end(),sortCandidatesByPt);

   //require emu
   int leadId(outgoingLeptons[0]->pdgId()), trailerId(outgoingLeptons[1]->pdgId());
   int ch(leadId*trailerId);
   if(ch!=-11*13) return false;

   //require in fiducial volume
   bool inFiducialVol(true);
   for(size_t i=0; i<2; i++) inFiducialVol &= (outgoingLeptons[i]->pt()>20 && fabs(outgoingLeptons[i]->eta())<2.4);
   if(!inFiducialVol) return false;

   //
   // gen jets
   //
   edm::Handle< std::vector<reco::GenJet> > genJets;
   iEvent.getByLabel("ak5GenJets", genJets);
   std::vector< std::pair<const reco::GenJet *, std::pair<const reco::Candidate *,const reco::Candidate *> > > selJets;
   for(std::vector<reco::GenJet>::const_iterator genJet=genJets->begin(); genJet!=genJets->end(); genJet++)
     {
       if(genJet->pt()<25 || fabs(genJet->eta())>2.4) continue;
       
       //require both hadronic and e.m. energy
       if(genJet->hadEnergy()==0.01 || genJet->emEnergy()<0.01) continue;
       
       //more than one constituent
       if(genJet->getGenConstituents().size()<2) continue;
 
       //require to be away from leptons
       bool matchesLepton(false);
       for(size_t i=0; i<2; i++)
	 {
	   float dR=deltaR(*genJet,*(outgoingLeptons[i]));
	   matchesLepton |= (dR<0.4);
	 }
       if(matchesLepton) continue;

       //flavor match
       const reco::Candidate *flavorMatch=0;
       for(size_t i=0; i<finalstatePartons.size(); i++)
	 {
	   float dR=deltaR(*genJet,*(finalstatePartons[i]));
	   if(dR>0.4) continue;
	   if(flavorMatch==0) flavorMatch=finalstatePartons[i];
	   float dPt=fabs(finalstatePartons[i]->pt()-genJet->pt());
	   float curDpt=fabs(flavorMatch->pt()-genJet->pt());
	   if(curDpt<dPt) continue;
	   flavorMatch=finalstatePartons[i];
	 }
       
       //hard proc match
       const reco::Candidate *bMatch=0;
       for(size_t i=0; i<hardProcB.size(); i++)
	 {
	   float dR_is=deltaR(*(hardProcB[i]),*genJet);
	   float dR_fs=deltaR(*(finalStateB[i]),*genJet);
	   if(dR_is>0.4 && dR_fs>0.4) continue;
	   bMatch=hardProcB[i];
	   break;
	 }
       std::pair<const reco::Candidate *,const reco::Candidate *> match(flavorMatch,bMatch);
       selJets.push_back(
			 std::pair<const reco::GenJet *, std::pair<const reco::Candidate *,const reco::Candidate *> >( &*(genJet), match)
			 );
     }
   
   if(selJets.size()<2) return false;

   //save summary to tuple
   ng=0;
   for(size_t i=0; i<hardProcW.size(); i++,ng++)
     {
       gid[ng]=hardProcW[i]->pdgId();
       gpt[ng]=hardProcW[i]->pt();
       geta[ng]=hardProcW[i]->eta();
       gphi[ng]=hardProcW[i]->phi();
       gmass[ng]=hardProcW[i]->mass();
     }  
   for(size_t i=0; i<hardProcB.size(); i++,ng++)
     {
       gid[ng]=hardProcB[i]->pdgId();
       gpt[ng]=hardProcB[i]->pt();
       geta[ng]=hardProcB[i]->eta();
       gphi[ng]=hardProcB[i]->phi();
       gmass[ng]=hardProcB[i]->mass();
     }  
   l1id=outgoingLeptons[0]->pdgId(); l1pt=outgoingLeptons[0]->pt(); l1eta=outgoingLeptons[0]->eta(); l1phi=outgoingLeptons[0]->phi(); l1mass=outgoingLeptons[0]->mass();
   l2id=outgoingLeptons[1]->pdgId(); l2pt=outgoingLeptons[1]->pt(); l2eta=outgoingLeptons[1]->eta(); l2phi=outgoingLeptons[1]->phi(); l2mass=outgoingLeptons[1]->mass();
   nj=selJets.size();
   for(size_t i=0; i<selJets.size(); i++)
     {
       jflav[i]=(selJets[i].second.first ? selJets[i].second.first->pdgId() : 0);
       jmatch[i]=(selJets[i].second.second ? selJets[i].second.second->pdgId() : 0);
       jpt[i]=selJets[i].first->pt();
       jeta[i]=selJets[i].first->eta();
       jphi[i]=selJets[i].first->phi();
       jmass[i]=selJets[i].first->mass();
     }
   ntuple->Fill();

   bool debug(false);
   if(debug)
     {
       cout << "[Leptons] \t" 
	    << outgoingLeptons[0]->pdgId() << " (" << outgoingLeptons[0]->pt() << "," << outgoingLeptons[0]->eta() << ") "
	    << outgoingLeptons[1]->pdgId() << " (" << outgoingLeptons[1]->pt() << "," << outgoingLeptons[1]->eta() << ") "
	    << endl << "[Jets]    \t"
	    << endl;
       for(size_t i=0; i<selJets.size(); i++)
	 {
	   if(selJets[i].second.first) cout << selJets[i].second.first->pdgId() << " ";
	   else                        cout << "- ";
	   if(selJets[i].second.second) cout << selJets[i].second.second->pdgId() << " ";
	   else                        cout << "- ";
	   cout << " ("<< selJets[i].first->pt() << "," << selJets[i].first->eta() << ") "; 
	 }
       cout << endl;
     }


   /*


   //compute acceptance
   bool passLeptons(abs(ch)==11*13);
   bool passOS(ch<0);

   if(!passLeptons || !passOS || jets.size()<2)  return false;
   */

   return true;
}


// ------------ method called once each job just before starting event loop  ------------
void OffshellWidthAnalyzer::beginJob()
{
  //book the histograms
  edm::Service<TFileService> fs;
  ntuple=fs->make<TTree>("event","event");
  ntuple->Branch("l1id",   &l1id,    "l1id/I");
  ntuple->Branch("l1pt",   &l1pt,    "l1pt/F");
  ntuple->Branch("l1eta",  &l1eta,   "l1eta/F");
  ntuple->Branch("l1phi",  &l1phi,   "l1phi/F");
  ntuple->Branch("l1mass", &l1mass,  "l1mass/F");
  ntuple->Branch("l2id",   &l2id,    "l2id/I");
  ntuple->Branch("l2pt",   &l2pt,    "l2pt/F");
  ntuple->Branch("l2eta",  &l2eta,   "l2eta/F");
  ntuple->Branch("l2phi",  &l2phi,   "l2phi/F");
  ntuple->Branch("l2mass", &l2mass,  "l2mass/F");
  ntuple->Branch("nj",    &nj,       "nj/I");
  ntuple->Branch("jflav",  jflav,    "jflav[nj]/I");
  ntuple->Branch("jmatch", jmatch,   "jmatch[nj]/I");
  ntuple->Branch("jpt",    jpt,      "jpt[nj]/F");
  ntuple->Branch("jeta",   jeta,     "jeta[nj]/F");
  ntuple->Branch("jphi",   jphi,     "jphi[nj]/F");
  ntuple->Branch("jmass",  jmass,    "jmass[nj]/F");
  ntuple->Branch("ng",    &nj,       "ng/I");
  ntuple->Branch("gid",    gid,      "gid[ng]/I");
  ntuple->Branch("gpt",    gpt,      "gpt[ng]/F");
  ntuple->Branch("geta",   geta,     "geta[ng]/F");
  ntuple->Branch("gphi",   gphi,     "gphi[ng]/F");
  ntuple->Branch("gmass",  gmass,    "gmass[ng]/F");
  countH=fs->make<TH1F>("count","",1,0,1);
}


// ------------ method called once each job just after ending the event loop  ------------
void 
OffshellWidthAnalyzer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
OffshellWidthAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
OffshellWidthAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
OffshellWidthAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
OffshellWidthAnalyzer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
OffshellWidthAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(OffshellWidthAnalyzer);
