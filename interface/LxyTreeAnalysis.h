#ifndef LxyTreeAnalysis_h
#define LxyTreeAnalysis_h

#include <TFile.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TString.h>
#include <TTreeFormula.h>
#include <TLorentzVector.h>

#include <iostream>

#include "UserCode/TopMassSecVtx/interface/LxyTreeAnalysisBase.h"

class Plot {
public:
    Plot() {};
    Plot(TString name, TString var, TString selection,
         Int_t nbins, Float_t minx, Float_t maxx, TTree *tree=0) {
        fName = name;
        fHisto = new TH1D(name, name, nbins, minx, maxx);
        fHisto->Sumw2();
        fHisto->SetXTitle(var);
        fVariable  = new TTreeFormula("Variable", var, tree);
        fSelection = new TTreeFormula("Formula", selection, tree);
    };

    virtual ~Plot() {
        fHisto->Delete();
        fVariable->Delete();
        fSelection->Delete();
    };

    virtual void Fill() {
        float weight = fSelection->EvalInstance();
        if( weight == 0. ) return;
        float var = fVariable->EvalInstance();
        fHisto->Fill(var, weight);
    }

    virtual void Print() {
        std::cout << "fName=" << fName.Data()
                  << " fBranchName=\"" << fVariable->GetExpFormula().Data()
                  << "\" fSelection=\"" << fSelection->GetExpFormula().Data()
                  << "\"" << std::endl;
    };

    virtual void SetTree(TTree *tree) {
        fSelection->SetTree(tree);
        fVariable->SetTree(tree);
    }

    virtual void Notify() {
        fSelection->Notify();
        fVariable->Notify();
    }

    TString fName;
    TH1D *fHisto;
    TTreeFormula *fSelection;
    TTreeFormula *fVariable;
private:
};

class LxyTreeAnalysis : public LxyTreeAnalysisBase {
public:
    LxyTreeAnalysis(TTree *tree=0):LxyTreeAnalysisBase(tree) {
        fMaxevents = -1;
    }
    virtual ~LxyTreeAnalysis() {}
    virtual void RunJob(TString);
    virtual void Begin(TFile*);
    virtual void End(TFile*);
    virtual void Loop();

    virtual void BookHistos();
    virtual void WriteHistos();

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
                               TLorentzVector p_cand, TLorentzVector p_jet);

    virtual void analyze();
    virtual bool selectEvent();
    virtual int firstTrackIndex(int jetindex);
    void fillJPsiHists(int jetindex);
    void fillD0Hists(int jetindex);
    void fillDpmHists(int jetindex);

    inline virtual void setMaxEvents(Long64_t max) {
        fMaxevents = max;
    }

    /////////////////////////////////////////////
    // LxyTreeAnalysis interface:
    virtual void AddPlot(TString name, TString var, TString sel,
                         Int_t nbins, Float_t minx, Float_t maxx) {
        // Add a plot through the external interface
        Plot *plot = new Plot(name, var, sel, nbins, minx, maxx, fChain);
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
                        Int_t nbins, Float_t minx, Float_t maxx){
      // Add a plot through the external interface
      Plot *plot = new Plot(name, var, sel, nbins, minx, maxx, fChain);
      fPlotList.push_back(plot);
   }

   virtual void ListPlots(){
      for (size_t i = 0; i < fPlotList.size(); ++i){
         fPlotList[i]->Print();
      }
   }

   virtual void FillPlots(){
      for (size_t i = 0; i < fPlotList.size(); ++i){
         fPlotList[i]->Fill();
      }
   }

   virtual void WritePlots(){
      for (size_t i = 0; i < fPlotList.size(); ++i){
         fPlotList[i]->fHisto->Write(fPlotList[i]->fHisto->GetName());
         delete fPlotList[i];
      }
   }

    /////////////////////////////////////////////
    std::vector<Plot*> fPlotList;
    Long64_t fMaxevents;

    std::vector<TH1*> fHistos;

    // Charm resonance histos
    TH1D *fHMJPsi, *fHMJPsimu, *fHMJPsie, *fHMJPsiK;
    TH1D *fHMD0Incl5TrkDR;
    TH1D *fHMD0Incl3Trk;
    TH1D *fHMD0mu, *fHMD0e, *fHMD0lep;
    TH1D *fHMDs2010lep;
    TH1D *fHDMDs2010D0lep;
    TH1D *fHMDpm, *fHMDpmZO;
    TH1D *fHMDpme, *fHMDpmmu, *fHMDpmlep;

    TTree *fCharmInfoTree;
    Int_t   fTCandType; // J/Psi = 443, D0 = 421, D+ = 411
    Float_t fTCandMass, fTCandPt, fTCandPz, fTCandEta;
    Float_t fTCandPtRel, fTCandDeltaR;
    Float_t fTJetPt, fTJetEta, fTSumPtCharged, fTJetPz, fTSumPzCharged;

    // Lepton - secondary vertex histos
// cut
   TH1D *fHmlsv_emu_deltar_cut;
   TH1D *fHmlsv_emu_deltar_cut_flow;
   TH1D *fHmlsv_emu_deltar_cut_correct;
   TH1D *fHmlsv_emu_deltar_cut_wrong;

   TH1D *fHmlsv_emu_deltar_cut_ntr2;
   TH1D *fHmlsv_emu_deltar_cut_ntr2_correct;
   TH1D *fHmlsv_emu_deltar_cut_ntr2_wrong;

   TH1D *fHmlsv_emu_deltar_cut_ntr3;
   TH1D *fHmlsv_emu_deltar_cut_ntr3_correct;
   TH1D *fHmlsv_emu_deltar_cut_ntr3_wrong;

   TH1D *fHmlsv_emu_deltar_cut_ntr4;
   TH1D *fHmlsv_emu_deltar_cut_ntr4_correct;
   TH1D *fHmlsv_emu_deltar_cut_ntr4_wrong;

//invm using deltar
   TH1D *fHdeltar_lsv_emu_deltar_cut;
   TH1D *fHdeltar_lsv_emu_deltar_cut_correct;
   TH1D *fHdeltar_lsv_emu_deltar_cut_wrong;

   TH1D *fHmlsv_emu_deltar;
   TH1D *fHmlsv_emu_deltar_correct;
   TH1D *fHmlsv_emu_deltar_wrong;

   TH1D *fHmlsv_emu_deltar_ntr2;
   TH1D *fHmlsv_emu_deltar_ntr2_correct;
   TH1D *fHmlsv_emu_deltar_ntr2_wrong;

   TH1D *fHmlsv_emu_deltar_ntr3;
   TH1D *fHmlsv_emu_deltar_ntr3_correct;
   TH1D *fHmlsv_emu_deltar_ntr3_wrong;

   TH1D *fHmlsv_emu_deltar_ntr4;
   TH1D *fHmlsv_emu_deltar_ntr4_correct;
   TH1D *fHmlsv_emu_deltar_ntr4_wrong;

//minmass

   TH1D *fHmlsv_emu_minmass;
   TH1D *fHmlsv_emu_minmass_flow;
   TH1D *fHmlsv_emu_minmass_correct;
   TH1D *fHmlsv_emu_minmass_wrong;

   TH1D *fHmlsv_emu_minmass_ntr2;
   TH1D *fHmlsv_emu_minmass_ntr2_correct;
   TH1D *fHmlsv_emu_minmass_ntr2_wrong;

   TH1D *fHmlsv_emu_minmass_ntr3;
   TH1D *fHmlsv_emu_minmass_ntr3_correct;
   TH1D *fHmlsv_emu_minmass_ntr3_wrong;

   TH1D *fHmlsv_emu_minmass_ntr4;
   TH1D *fHmlsv_emu_minmass_ntr4_correct;
   TH1D *fHmlsv_emu_minmass_ntr4_wrong;

   TH1D *fHmlsv_emu_deltar_cut_correct_topweight;
   TH1D *fHmlsv_emu_deltar_cut_correct_topweight_up;
   TH1D *fHmlsv_emu_deltar_cut_wrong_topweight;
   TH1D *fHmlsv_emu_deltar_cut_wrong_topweight_up;

   TH1D *fHmlsv_emu_minmass_correct_topweight;
   TH1D *fHmlsv_emu_minmass_correct_topweight_up;
   TH1D *fHmlsv_emu_minmass_wrong_topweight;
   TH1D *fHmlsv_emu_minmass_wrong_topweight_up;

   TH1D *fHmlsv_emu_minmass_correct_nvtx_1bin;
   TH1D *fHmlsv_emu_minmass_correct_nvtx_2bin;
   TH1D *fHmlsv_emu_minmass_correct_nvtx_3bin;
   TH1D *fHmlsv_emu_minmass_correct_nvtx_4bin;

   TH1D *fHmlsv_emu_minmass_wrong_nvtx_1bin;
   TH1D *fHmlsv_emu_minmass_wrong_nvtx_2bin;
   TH1D *fHmlsv_emu_minmass_wrong_nvtx_3bin;
   TH1D *fHmlsv_emu_minmass_wrong_nvtx_4bin;
   TH1D *fHsvntk;

// pratio

   TH1D *fHsecbhad_pratio_emu;
   TH1D *fHsecbhad_pratio_emu_ntr2;
   TH1D *fHsecbhad_pratio_emu_ntr3;
   TH1D *fHsecbhad_pratio_emu_ntr4;
   TH1D *fHsecbhad_pratio_emu_ntr5;
   TH1D *fHsecbhad_pratio_emu_ntr6;
   TH1D *fHsecbhad_pratio_emu_ntr7;
   TH1D *fHsecbhad_pratio_emu_ntr8;
   TH1D *fHsecbhad_pratio_emu_ntr9;
   TH1D *fHsecbhad_pratio_emu_ntr10;
   TH1D *fHsecbhad_pratio_emu_ntr11;
   TH1D *fHsecbhad_pratio_emu_ntr12;
   TH1D *fHsecbhad_pratio_emu_ntr13;
   TH1D *fHsecbhad_pratio_emu_ntr14;
   TH1D *fHsecbhad_pratio_emu_ntr15;

   TH1D *fHsecbhad_deltar_emu;
   TH1D *fHsecbhad_deltar_emu_ntr2;
   TH1D *fHsecbhad_deltar_emu_ntr3;
   TH1D *fHsecbhad_deltar_emu_ntr4;
   TH1D *fHsecbhad_deltar_emu_ntr5;
   TH1D *fHsecbhad_deltar_emu_ntr6;
   TH1D *fHsecbhad_deltar_emu_ntr7;
   TH1D *fHsecbhad_deltar_emu_ntr8;
   TH1D *fHsecbhad_deltar_emu_ntr9;
   TH1D *fHsecbhad_deltar_emu_ntr10;
   TH1D *fHsecbhad_deltar_emu_ntr11;
   TH1D *fHsecbhad_deltar_emu_ntr12;
   TH1D *fHsecbhad_deltar_emu_ntr13;
   TH1D *fHsecbhad_deltar_emu_ntr14;
   TH1D *fHsecbhad_deltar_emu_ntr15;

   TH1D *fHsecb_pratio_emu;
   TH1D *fHsecb_pratio_emu_ntr2;
   TH1D *fHsecb_pratio_emu_ntr3;
   TH1D *fHsecb_pratio_emu_ntr4;
   TH1D *fHsecb_pratio_emu_ntr5;
   TH1D *fHsecb_pratio_emu_ntr6;
   TH1D *fHsecb_pratio_emu_ntr7;
   TH1D *fHsecb_pratio_emu_ntr8;
   TH1D *fHsecb_pratio_emu_ntr9;
   TH1D *fHsecb_pratio_emu_ntr10;
   TH1D *fHsecb_pratio_emu_ntr11;
   TH1D *fHsecb_pratio_emu_ntr12;
   TH1D *fHsecb_pratio_emu_ntr13;
   TH1D *fHsecb_pratio_emu_ntr14;
   TH1D *fHsecb_pratio_emu_ntr15;

   TH1D *fHsecb_deltar_emu;
   TH1D *fHsecb_deltar_emu_ntr2;
   TH1D *fHsecb_deltar_emu_ntr3;
   TH1D *fHsecb_deltar_emu_ntr4;
   TH1D *fHsecb_deltar_emu_ntr5;
   TH1D *fHsecb_deltar_emu_ntr6;
   TH1D *fHsecb_deltar_emu_ntr7;
   TH1D *fHsecb_deltar_emu_ntr8;
   TH1D *fHsecb_deltar_emu_ntr9;
   TH1D *fHsecb_deltar_emu_ntr10;
   TH1D *fHsecb_deltar_emu_ntr11;
   TH1D *fHsecb_deltar_emu_ntr12;
   TH1D *fHsecb_deltar_emu_ntr13;
   TH1D *fHsecb_deltar_emu_ntr14;
   TH1D *fHsecb_deltar_emu_ntr15;

   TH2D *fHdeltar_svl_emu_2d;

   TH1D *fHdeltar_svl_emu_correct;
   TH1D *fHdeltar_svl_emu_correct_ntr2;
   TH1D *fHdeltar_svl_emu_correct_ntr3;
   TH1D *fHdeltar_svl_emu_correct_ntr4;
   TH1D *fHdeltar_svl_emu_correct_ntr5;

   TH1D *fHdeltar_svl_emu_wrong;
   TH1D *fHdeltar_svl_emu_wrong_ntr2;
   TH1D *fHdeltar_svl_emu_wrong_ntr3;
   TH1D *fHdeltar_svl_emu_wrong_ntr4;
   TH1D *fHdeltar_svl_emu_wrong_ntr5;

// sumw2
};
#endif

