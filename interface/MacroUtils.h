#ifndef macroutils_h
#define macroutils_h

#include "DataFormats/FWLite/interface/Handle.h"
#include "DataFormats/FWLite/interface/Event.h"
#include "DataFormats/FWLite/interface/ChainEvent.h"
#include "DataFormats/Common/interface/MergeableCounter.h"

#include "FWCore/FWLite/interface/AutoLibraryLoader.h"
#include "FWCore/PythonParameterSet/interface/MakeParameterSets.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "PhysicsTools/Utilities/interface/LumiReWeighting.h"

#include "DataFormats/Math/interface/deltaPhi.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/IPTools/interface/IPTools.h"

#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"

#include <vector>
#include "TVector3.h"
#include "TMath.h"
#include "TGraph.h"
#include <Math/VectorUtil.h>

#include "Math/LorentzVector.h"
typedef ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > LorentzVector;

namespace utils
{
  namespace cmssw
  {
    //retrieve last state before decay
    const reco::Candidate *getGeneratorFinalStateFor(const reco::Candidate *p);

    //check pdg id code for b-flavored hadrons
    bool isBhadron(int pdgId);

    //get impact parameter for a track
    template<class T>
    std::pair<bool,Measurement1D> getImpactParameter(const T &trkRef, reco::VertexRef &vtx, const edm::EventSetup &iSetup, bool is3d=true)
      {
	edm::ESHandle<TransientTrackBuilder> trackBuilder;
	iSetup.get<TransientTrackRecord>().get("TransientTrackBuilder", trackBuilder);
	reco::TransientTrack tt = trackBuilder->build(trkRef.get());
	if(is3d) return IPTools::absoluteImpactParameter3D(tt, *vtx);
	else     return IPTools::absoluteTransverseImpactParameter(tt, *vtx);
      }

    //
    template<class T>
    float getArcCos(T &a,T &b)
      {
	TVector3 mom1(a.px(),a.py(),a.pz());
	TVector3 mom2(b.px(),b.py(),b.pz());
	float cosine = mom1.Dot(mom2)/(mom1.Mag()*mom2.Mag());
	float arcCosine = acos(cosine);
	return arcCosine;
      }

    template<class T>
    float getMT(T &visible, T &invisible, bool setSameMass=false)
    {
      float mt(-1);
      if(setSameMass){
	T sum=visible+invisible;
	mt= TMath::Power(TMath::Sqrt(TMath::Power(visible.pt(),2)+pow(visible.mass(),2))+TMath::Sqrt(TMath::Power(invisible.pt(),2)+pow(visible.mass(),2)),2);
	mt-=TMath::Power(sum.pt(),2);
	mt=TMath::Sqrt(mt);
      }else{
	double dphi=fabs(deltaPhi(invisible.phi(),visible.phi()));
	mt=TMath::Sqrt(2*invisible.pt()*visible.pt()*(1-TMath::Cos(dphi)));
      }
      return mt;
    }

    template<class T1, class T2>
    float getMT(T1 &orig_visible, T2 &orig_invisible, bool setSameMass=false)
    {
      float mt(-1);
      LorentzVector visible(orig_visible.Px(),orig_visible.Py(),orig_visible.Pz(),orig_visible.E());
      LorentzVector invisible(orig_invisible.Px(),orig_invisible.Py(),orig_invisible.Pz(),orig_invisible.E());
      if(setSameMass){
	LorentzVector sum=visible+invisible;
	mt= TMath::Power(TMath::Sqrt(TMath::Power(visible.pt(),2)+pow(visible.mass(),2))+TMath::Sqrt(TMath::Power(invisible.pt(),2)+pow(visible.mass(),2)),2);
	mt-=TMath::Power(sum.pt(),2);
	mt=TMath::Sqrt(mt);
      }else{
	double dphi=fabs(deltaPhi(invisible.phi(),visible.phi()));
	mt=TMath::Sqrt(2*invisible.pt()*visible.pt()*(1-TMath::Cos(dphi)));
      }
      return mt;
    }

    std::vector<float> smearJER(float pt, float eta, float genPt);
    std::vector<float> smearJES(float pt, float eta, JetCorrectionUncertainty *jecUnc);

    typedef std::vector<TGraph *> PuShifter_t;
    enum PuShifterTypes {PUDOWN,PUUP};
    utils::cmssw::PuShifter_t getPUshifters(std::vector< float > &Lumi_distr, float puUnc);

    Float_t getEffectiveArea(int id, float eta,int cone=3,TString isoSum="");

    // cf. AN-14-145
    Float_t getElectronEnergyScale(float pt, float eta);
    
    // Single muon trigger efficiency
    void getSingleMuTrigEff(const double&, const double&, double& );

    //cf. https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JetEnCorFWLite
    FactorizedJetCorrector *getJetCorrector(TString baseDir, bool isMC);
  }
}

// CODE FOR DUPLICATE EVENTS CHECKING
namespace __gnu_cxx{
  template<> struct hash< std::string >{
    size_t operator()( const std::string& x ) const{ return hash< const char* >()( x.c_str() );  }
  };
}

class DuplicatesChecker{
 private :
  typedef __gnu_cxx::hash_map<std::string, bool > RunEventHashMap;
  RunEventHashMap map;
 public :
  DuplicatesChecker(){}
  ~DuplicatesChecker(){}
  void Clear(){map.clear();}
  bool isDuplicate(unsigned int Run, unsigned int Lumi, unsigned int Event){
    char tmp[255];sprintf(tmp,"%i_%i_%i",Run,Lumi,Event);
    RunEventHashMap::iterator it = map.find(tmp);
    if(it==map.end()){
      map[tmp] = true;
      return false;
    }
    return true;
  }
  bool isDuplicate(unsigned int Run, unsigned int Lumi, unsigned int Event,unsigned int cat){
    char tmp[255];sprintf(tmp,"%i_%i_%i_%i",Run,Lumi,Event,cat);
    RunEventHashMap::iterator it = map.find(tmp);
    if(it==map.end()){
      map[tmp] = true;
      return false;
    }
    return true;
  }
};

#endif
