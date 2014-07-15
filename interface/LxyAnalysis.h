#ifndef _lxyanalysis_
#define _lxyanalysis_

#include "UserCode/llvv_fwk/interface/SmartSelectionMonitor.h"
#include "UserCode/llvv_fwk/interface/DataEventSummaryHandler.h"



struct BeautyEvent_t
{
	static const unsigned gMaxNWeights = 50;
	static const unsigned gMaxNLeps = 5;
	static const unsigned gMaxNJets = 50;
	static const unsigned gMaxNSV = 50;
	static const unsigned gMaxNPFCands = 500;

	Int_t run, lumi, event, evcat, gevcat, nvtx;
	Float_t rho;
	// Weights
	Int_t nw;
	Float_t w[gMaxNWeights];
	// Leptons / GenLeptons
	Int_t nl,lid[gMaxNLeps],glid[gMaxNLeps];
	Float_t lpt[gMaxNLeps],leta[gMaxNLeps],lphi[gMaxNLeps];
	Float_t glpt[gMaxNLeps],gleta[gMaxNLeps],glphi[gMaxNLeps];
	// Jets
	Int_t nj,jflav[gMaxNJets];
	Float_t jpt[gMaxNJets],jeta[gMaxNJets],jphi[gMaxNJets];
	Float_t gjpt[gMaxNJets],gjeta[gMaxNJets],gjphi[gMaxNJets];
	Float_t jcsv[gMaxNJets],jarea[gMaxNJets];
	Float_t jtoraw[gMaxNJets],jjesup[gMaxNJets],jjesdn[gMaxNJets];
	// Sec.Vertices
	Float_t svpt[gMaxNSV],sveta[gMaxNSV],svphi[gMaxNSV];
	Float_t svmass[gMaxNSV],svntk[gMaxNSV],svlxy[gMaxNSV],svlxyerr[gMaxNSV];
	// Gen Bhadrons
	Int_t bid[gMaxNSV],bhadid[gMaxNSV];
	Float_t bpt[gMaxNSV],beta[gMaxNSV],bphi[gMaxNSV];
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

	bool analyze(Int_t run, Int_t event, Int_t lumi,
				 Int_t nvtx, Float_t rho,
				 std::vector<Float_t> weights,
				 Int_t evCat, Int_t gevCat,
				 std::vector<data::PhysicsObject_t *> &leptons,
				 std::vector<data::PhysicsObject_t *> &jets,
				 std::vector<LorentzVector> &mets,
				 data::PhysicsObjectCollection_t &pf,
				 data::PhysicsObjectCollection_t &mctruth);

private:

	void resetBeautyEvent();

	TTree *outT_;
	BeautyEvent_t bev_;
	TDirectory *outDir_;

};

#endif
