#ifndef LxyTreeAnalysis_h
#define LxyTreeAnalysis_h

#include <TFile.h>
#include <TH1D.h>
#include <TString.h>
#include <TTreeFormula.h>
#include <TLorentzVector.h>

#include <iostream>

#include "UserCode/llvv_fwk/interface/LxyTreeAnalysisBase.h"

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
    std::vector<Plot*> fPlotList;
    Long64_t fMaxevents;

    std::vector<TH1*> fHistos;
    TH1D *fHMJPsi, *fHMJPsimu, *fHMJPsie, *fHMJPsiK;
    TH1D *fHMD0Incl5TrkDR;
    TH1D *fHMD0Incl3Trk;
    TH1D *fHMD0mu, *fHMD0e, *fHMD0lep;
    TH1D *fHMDs2010lep;
    TH1D *fHDMDs2010D0lep;
    TH1D *fHMDpm, *fHMDpmZO;
    // TH1D *fHMDpmKKPi;
    TH1D *fHMDpme, *fHMDpmmu, *fHMDpmlep;

    TTree *fCharmInfoTree;
    Int_t   fTCandType; // J/Psi = 443, D0 = 421, D+ = 411
    Float_t fTCandMass, fTCandPt, fTCandPz, fTCandEta;
    Float_t fTCandPtRel, fTCandDeltaR;
    Float_t fTJetPt, fTJetEta, fTSumPtCharged, fTJetPz, fTSumPzCharged;

};

#endif
