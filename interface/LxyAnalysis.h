#ifndef _lxyanalysis_
#define _lxyanalysis_

#include "UserCode/TopMassSecVtx/interface/SmartSelectionMonitor.h"
#include "UserCode/TopMassSecVtx/interface/DataEventSummaryHandler.h"



struct BeautyEvent_t
{
  static const unsigned gMaxNWeights = 50;
  static const unsigned gMaxNLeps = 5;
  static const unsigned gMaxNJets = 50;
  static const unsigned gMaxNSV = 50;
  static const unsigned gMaxNPFCands = 1000;

  Int_t run, lumi, event, evcat, gevcat, nvtx, ngenTruepu;
  Float_t rho, instLumi;
  // Weights
  Int_t nw;
  Float_t w[gMaxNWeights];
  //gen level information for PDF stuff
  Float_t qscale, x1,x2;
  Int_t id1, id2;
  // Leptons / GenLeptons
  Int_t nl,lid[gMaxNLeps],glid[gMaxNLeps];
  Float_t lpt[gMaxNLeps],leta[gMaxNLeps],lphi[gMaxNLeps];
  Float_t glpt[gMaxNLeps],gleta[gMaxNLeps],glphi[gMaxNLeps];
  // Jets
  Int_t nj,jflav[gMaxNJets];
  Float_t jpt[gMaxNJets],jeta[gMaxNJets],jphi[gMaxNJets];
  Float_t gjpt[gMaxNJets],gjeta[gMaxNJets],gjphi[gMaxNJets];
  Float_t jcsv[gMaxNJets],jarea[gMaxNJets];
  Float_t jtoraw[gMaxNJets],jjesup[gMaxNJets][26],jjesdn[gMaxNJets][26];
  Float_t jbhadmatchdr[gMaxNJets];
  // Sec.Vertices
  Float_t svpt[gMaxNSV],sveta[gMaxNSV],svphi[gMaxNSV];
  Float_t svmass[gMaxNSV],svntk[gMaxNSV],svlxy[gMaxNSV],svlxyerr[gMaxNSV];
  // Gen Bhadrons
  Int_t bid[gMaxNSV],bhadid[gMaxNSV], bhadneutrino[gMaxNSV];
  Float_t bpt[gMaxNSV],beta[gMaxNSV],bphi[gMaxNSV],bwgt[gMaxNSV][3];
  Float_t bhadpt[gMaxNSV],bhadeta[gMaxNSV],bhadphi[gMaxNSV];
  Float_t bhadmass[gMaxNSV],bhadlxy[gMaxNSV];
  // Gen Top
  Int_t tid[gMaxNSV];
  Float_t tpt[gMaxNSV],teta[gMaxNSV],tphi[gMaxNSV],tmass[gMaxNSV];
  // PF Candidates
  Int_t npf,npfb1,pfid[gMaxNPFCands],pfjetidx[gMaxNPFCands];
  Float_t pfpt[gMaxNPFCands],pfeta[gMaxNPFCands],pfphi[gMaxNPFCands];
  // MET
  Float_t metpt, metphi;
  // MET Variations:
  // 0 = jerup  1 = jerdown  2 = jesup 3 = jesdown
  // 4 = umetup 5 = umetdown 6 = lesup 7 = lesdown
  Float_t metvar[8];
};

class LxyAnalysis
{
 public:
  LxyAnalysis();
  void attachToDir(TDirectory *outDir);
  inline BeautyEvent_t &getBeautyEvent(){ return bev_; }
  void analyze(std::vector<data::PhysicsObject_t *> &leptons, std::vector<data::PhysicsObject_t *> &jets, std::vector<LorentzVector> &mets, data::PhysicsObjectCollection_t &pf, data::PhysicsObjectCollection_t &mctruth);
  void save();
  void resetBeautyEvent();
 private:
  TTree *outT_;
  BeautyEvent_t bev_;
  TDirectory *outDir_;
};

#endif
