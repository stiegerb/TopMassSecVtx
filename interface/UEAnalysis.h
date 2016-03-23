#ifndef _ueanalysis_
#define _ueanalysis_

#include "UserCode/TopMassSecVtx/interface/SmartSelectionMonitor.h"
#include "UserCode/TopMassSecVtx/interface/DataEventSummaryHandler.h"
#include "UserCode/TopMassSecVtx/interface/UEAnalysisSummary.h"

#include <vector>

#include "TString.h"
#include "TNtuple.h"

class UEAnalysis
{

public:
  UEAnalysis(SmartSelectionMonitor &mon);

  void analyze(std::vector<data::PhysicsObject_t *> &leptons,
	       std::vector<data::PhysicsObject_t *> &jets,
	       LorentzVector &met, 
	       data::PhysicsObjectCollection_t &pf,
	       data::PhysicsObjectCollection_t &mctruth,
	       int nvtx,
	       float weight);

  void fillSummaryTuple(float evWeight) { ue_.normWeight=evWeight; summaryTuple_->Fill(); }
  void attachToDir(TDirectory *outDir);
  TTree *getSummaryTuple()            { return summaryTuple_; }

  ~UEAnalysis() { }
  
private:

  UEAnalysisSummary_t ue_;
  SmartSelectionMonitor *mon_;
  std::vector<TString> ueReg_;
  TTree *summaryTuple_;
};

#endif
