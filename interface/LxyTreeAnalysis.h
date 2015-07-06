#ifndef LxyTreeAnalysis_h
#define LxyTreeAnalysis_h

#include "UserCode/TopMassSecVtx/interface/BtagUncertaintyComputer.h"

#include "TSystem.h"
#include "TGraphErrors.h"
#include <TFile.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TRandom2.h>
#include <TString.h>
#include <TVectorD.h>
#include <TTreeFormula.h>
#include <TLorentzVector.h>

#include <iostream>
#include "UserCode/TopMassSecVtx/interface/PDFInfo.h"
#include "UserCode/TopMassSecVtx/interface/LxyTreeAnalysisBase.h"

// Plot class defined here
#include "UserCode/TopMassSecVtx/interface/SVLInfoTreeAnalysis.h"

class LxyTreeAnalysis : public LxyTreeAnalysisBase {
public:
    LxyTreeAnalysis(TTree *tree=0,TString weightsDir=""):LxyTreeAnalysisBase(tree) {
        fMaxevents = -1;
        fProcessNorm = 1.0;
        //b-tag efficiencies read b-tag efficiency map
        if(weightsDir!="")
        {
            TString btagEffCorrUrl(weightsDir);
            btagEffCorrUrl += "/btagEff.root";
            gSystem->ExpandPathName(btagEffCorrUrl);
            TFile *btagF=TFile::Open(btagEffCorrUrl);
            if(btagF!=0 && !btagF->IsZombie())
            {
                TList *dirs=btagF->GetListOfKeys();
                for(int itagger=0; itagger<dirs->GetEntries(); itagger++)
                {
                    TString iDir(dirs->At(itagger)->GetName());
                    btagEffCorr_[ std::pair<TString,TString>(iDir,"b") ]
                        = std::pair<TGraphErrors *,TGraphErrors *>( (TGraphErrors *) btagF->Get(iDir+"/beff"),(TGraphErrors *) btagF->Get(iDir+"/sfb") );
                    btagEffCorr_[ std::pair<TString,TString>(iDir,"c") ]
                        = std::pair<TGraphErrors *,TGraphErrors *>( (TGraphErrors *) btagF->Get(iDir+"/ceff"),(TGraphErrors *) btagF->Get(iDir+"/sfc") );
                    btagEffCorr_[ std::pair<TString,TString>(iDir,"udsg") ]
                        = std::pair<TGraphErrors *,TGraphErrors *>( (TGraphErrors *) btagF->Get(iDir+"/udsgeff"),(TGraphErrors *) btagF->Get(iDir+"/sfudsg") );
                }
            }
            // std::cout << btagEffCorr_.size() << " b-tag correction factors have been read" << std::endl;
        }
    }
    virtual ~LxyTreeAnalysis() {}
    virtual void RunJob(TString);
    virtual void Begin(TFile*);
    virtual void End(TFile*);
    virtual void Loop();
    virtual void BookDileptonTree();
    virtual void ResetDileptonTree();
    virtual void BookHistos();
    virtual void BookCharmHistos();
    virtual void BookSVLHistos();
    virtual void WriteHistos();
    TLorentzVector RotateLepton(TLorentzVector &origLep,std::vector<TLorentzVector> &isoObjects);
    virtual void BookCharmTree();
    virtual void ResetCharmTree();
    virtual void FillCharmTree(int type, int jetindex,
                               int trackind1, float mass1,
                               int trackind2, float mass2);
    virtual void FillCharmTree(int type, int jetindex,
                               int trackind1, float mass1,
                               int trackind2, float mass2,
                               int trackind3, float mass3);
    virtual void FillCharmTree(int type, int jind,
                               TLorentzVector p_cand, TLorentzVector p_jet,
                               float hardpt=-88.88, float softpt=-88.88);
    virtual void FillCharmTree(int type, int jind,
                               float candmass,
                               TLorentzVector p_cand, TLorentzVector p_jet,
                               float hardpt=-88.88, float softpt=-88.88);

    virtual void BookSVLTree();
    virtual void ResetSVLTree();

    virtual void analyze();
    virtual bool selectEvent();
    virtual bool selectSVLEvent(bool &passBtagNom, bool &passBtagUp, bool &passBtagDown,
                                bool &passMETNom, bool &passMETUp, bool &passMETDown);
    virtual bool selectDYControlEvent();
    virtual int firstTrackIndex(int jetindex);
    void fillJPsiHists(int jetindex);
    void fillD0Hists(int jetindex);
    void fillDpmHists(int jetindex);

    inline virtual void setMaxEvents(Long64_t max) {
        fMaxevents = max;
    }
    inline virtual void setProcessNormalization(Float_t norm) {
        fProcessNorm = norm;
    }

    virtual Bool_t Notify() {
        // Called when a new tree is loaded in the chain
        // std::cout << "New tree (" << fCurrent
        //           << ") from "
        //           << fChain->GetCurrentFile()->GetName() << std::endl;
        for (size_t i = 0; i < fPlotList.size(); ++i) {
            fPlotList[i]->SetTree(fChain->GetTree());
            fPlotList[i]->Notify();
        }
        return kTRUE;
    }

    /////////////////////////////////////////////
    // Plot class interface:
    virtual void AddPlot(TString name, TString var, TString sel,
                         Int_t nbins, Float_t minx, Float_t maxx,
                         TString axistitle) {
        // Add a plot through the external interface
        Plot *plot = new Plot(name, var, sel, nbins, minx, maxx, axistitle, fChain);
        fPlotList.push_back(plot);
    }

    virtual void ListPlots() {
        for (size_t i = 0; i < fPlotList.size(); ++i) {
            fPlotList[i]->Print();
        }
    }

    virtual void FillPlots() {
        for (size_t i = 0; i < fPlotList.size(); ++i) {
            fPlotList[i]->Fill();
        }
    }

    virtual void WritePlots() {
        for (size_t i = 0; i < fPlotList.size(); ++i) {
            fPlotList[i]->fHisto->Write(fPlotList[i]->fHisto->GetName());
            delete fPlotList[i];
        }
    }


    /////////////////////////////////////////////
    PDFInfo *fPDFInfo;

    std::vector<Plot*> fPlotList;
    Long64_t fMaxevents;
    Float_t fProcessNorm;

    std::vector<TH1*> fHistos;

    // Charm resonance histos
    TH1D *fHMJPsi, *fHMJPsimu, *fHMJPsie, *fHMJPsiK;
    TH1D *fHMD0Incl5TrkDR;
    TH1D *fHMD0Incl3Trk;
    TH1D *fHMD0mu, *fHMD0e, *fHMD0lep;
    TH1D *fHMDsm;
    TH1D *fHDMDsmD0, *fHDMDsmD0loose;
    TH1D *fHMDpm, *fHMDpmZO;
    TH1D *fHMDpme, *fHMDpmmu, *fHMDpmlep;

    TTree *fCharmInfoTree;
    Int_t   fTCharmEvCat, fTCandType; // J/Psi = 443, D0 = 421, D+ = 411
    Float_t fTCandMass, fTCandPt, fTCandPz, fTCandEta;
    Float_t fTHardTkPt, fTSoftTkPt;
    Float_t fTCandPtRel, fTCandDeltaR;
    Float_t fTJetPt, fTJetEta, fTSumPtCharged, fTJetPz, fTSumPzCharged;

    // Lepton Secondary Vertex:
    TH1D *fHNJets, *fHNJets_e, *fHNJets_m, *fHNJets_ee, *fHNJets_mm, *fHNJets_em;
    TH1D *fHNSVJets, *fHNSVJets_e, *fHNSVJets_m, *fHNSVJets_ee, *fHNSVJets_mm, *fHNSVJets_em;
    TH1D *fHNbJets, *fHNbJets_e, *fHNbJets_m, *fHNbJets_ee, *fHNbJets_mm, *fHNbJets_em;
    TH1D *fHMET, *fHMET_e, *fHMET_m, *fHMET_ee, *fHMET_mm, *fHMET_em;

    TH1D *fHMjj, *fHMjj_e, *fHMjj_m;
    TH1D *fHMjj_ch, *fHMjj_e_ch, *fHMjj_m_ch;
    TH1D *fHMT, *fHMT_e, *fHMT_m;

    // Drell-Yan control region
    TH1D *fHDY_mll_ee, *fHDY_mll_mm, *fHDY_met_ee, *fHDY_met_mm;

    TTree *fSVLInfoTree;
    Int_t fTEvent, fTRun, fTLumi, fTNPVtx, fTNCombs, fTEvCat;
    Int_t fTNJets, fTNBTags;
    Float_t fTMET,fTMT;
    Float_t fTWeight[11], fTJESWeight[5], fTMETWeight[3], fTBtagWeight[3], fTXSWeight;
    Float_t fTSVLMass, fTSVLMass_sf[2], fTSVLDeltaR, fTSVLMass_rot, fTSVLDeltaR_rot;
    Float_t fTLPt, fTSVMass, fTSVPt, fTSVLxy, fTSVLxySig, fTJPt, fTJEta, fMjj,fTSVPtChFrac, fTSVPzChFrac,fTSVProjFrac,fTSVPtRel;
    Float_t fTFJPt, fTFJEta;
    Float_t fTSVBfragWeight[6];
    Float_t fPDFWeight[100];
    Int_t fTBHadNeutrino,fTBHadId;
    Int_t fTSVLMinMassRank, fTSVLCombRank, fTSVLDeltaRRank, fTSVLMinMassRank_rot, fTSVLDeltaRRank_rot;
    Int_t fTSVNtrk, fTCombCat, fTCombInfo;
    Int_t fTJFlav;
    Float_t fTGenMlb, fTGenTopPt;

    //Dilepton specific
    TTree *fDileptonInfoTree;
    Float_t fLpPt,fLmPt,fLpEta,fLmEta,fLpPhi,fLmPhi,fLmId,fLpId;
    Float_t fGenLpPt,fGenLmPt,fGenLpEta,fGenLmEta,fGenLpPhi,fGenLmPhi,fGenLpId,fGenLmId;

    TRandom2 rndGen_;
    BTagSFUtil btsfutil_;
    std::map<std::pair<TString,TString>, std::pair<TGraphErrors *,TGraphErrors *> > btagEffCorr_;
};
#endif

