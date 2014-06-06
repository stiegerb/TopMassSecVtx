#ifndef _lxyanalysis_
#define _lxyanalysis_

#include "UserCode/llvv_fwk/interface/SmartSelectionMonitor.h"
#include "UserCode/llvv_fwk/interface/DataEventSummaryHandler.h"

struct BeautyEvent_t
{
  Int_t run, lumi, event, evcat, nvtx;
  Int_t nw;
  Float_t w[50];
  Int_t nl,lid[50];
  Float_t lpt[50],leta[50],lphi[50];
  Int_t nj,jflav[50];
  Float_t jpt[50],jeta[50],jphi[50];
  Int_t bid,bhadid;
  Float_t svpt,sveta,svphi,svmass,svntk,svlxy,svlxyerr;
  Float_t bpt,beta,bphi;
  Float_t bhadpt,bhadeta,bhadphi,bhadmass,bhadlxy;
  Int_t npf,pfid[50];
  Float_t pfpt[50],pfeta[50],pfphi[50];
  Float_t metpt,metphi;
};
  
class LxyAnalysis
{

public:
  LxyAnalysis();

  void attachToDir(TDirectory *outDir);

  void analyze(Int_t run, Int_t event, Int_t lumi,
	       Int_t nvtx, std::vector<Float_t> weights,
	       Int_t evCat,
	       data::PhysicsObjectCollection_t &leptons, 
	       data::PhysicsObjectCollection_t &jets,
	       LorentzVector &met, 
	       data::PhysicsObjectCollection_t &pf,
	       data::PhysicsObjectCollection_t &mctruth);

  inline void finalize() { 
    if(outDir_ && outT_) 
      { 
	std::cout << "Preparing to write" << outDir_->GetName() << std::endl;
	outDir_->cd(); 
	outT_->Write(); 
	std::cout << "All done here" << std::endl;
      } 
  }

private:

  void resetBeautyEvent();

  TTree *outT_;
  BeautyEvent_t bev_;
  TDirectory *outDir_;

};

#endif
