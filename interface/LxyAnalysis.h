#ifndef _lxyanalysis_
#define _lxyanalysis_

#include "UserCode/llvv_fwk/interface/SmartSelectionMonitor.h"
#include "UserCode/llvv_fwk/interface/DataEventSummaryHandler.h"

struct BeautyEvent_t
{
  Int_t run, lumi, event, evcat, nvtx;
  Float_t rho;
  Int_t nw;
  Float_t w[50];
  Int_t nl,lid[50],glid[50];
  Float_t lpt[50],leta[50],lphi[50];
  Float_t glpt[50],gleta[50],glphi[50];
  Int_t nj,jflav[50];
  Float_t jpt[50],jeta[50],jphi[50],jcsv[50],jarea[50],jtoraw[50];
  Float_t gjpt[50],gjeta[50],gjphi[50];
  Int_t bid[50],bhadid[50];
  Float_t svpt[50],sveta[50],svphi[50],svmass[50],svntk[50],svlxy[50],svlxyerr[50];
  Float_t bpt[50],beta[50],bphi[50];
  Float_t bhadpt[50],bhadeta[50],bhadphi[50],bhadmass[50],bhadlxy[50];
  Int_t tid[50];
  Float_t tpt[50],teta[50],tphi[50],tmass[50];
  Int_t npf,pfid[500],pfjetidx[500];
  Float_t pfpt[500],pfeta[500],pfphi[500];
  Float_t metpt,metphi;
};

class LxyAnalysis
{

public:
  LxyAnalysis();

  void attachToDir(TDirectory *outDir);

  bool analyze(Int_t run, Int_t event, Int_t lumi,
	       Int_t nvtx, Float_t rho,
	       std::vector<Float_t> weights,
	       Int_t evCat,
	       std::vector<data::PhysicsObject_t *> &leptons,
	       std::vector<data::PhysicsObject_t *> &jets,
	       LorentzVector &met,
	       data::PhysicsObjectCollection_t &pf,
	       data::PhysicsObjectCollection_t &mctruth);

private:

  void resetBeautyEvent();

  TTree *outT_;
  BeautyEvent_t bev_;
  TDirectory *outDir_;

};

#endif
