#ifndef SVLInfoTreeAnalysis_h
#define SVLInfoTreeAnalysis_h

#include <TFile.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TRandom3.h>
#include <TString.h>
#include <TTreeFormula.h>
#include <TLorentzVector.h>

#include <iostream>

#include "UserCode/TopMassSecVtx/interface/SVLInfoTreeAnalysisBase.h"

class Plot {
public:
    Plot() {};
    Plot(TString name, TString var, TString selection,
         Int_t nbins, Float_t minx, Float_t maxx, TString xtitle,
         TTree *tree=0) {
        fName = name;
        fHisto = new TH1D(name, name, nbins, minx, maxx);
        fHisto->Sumw2();
        fHisto->SetXTitle(xtitle);
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

class SVLInfoTreeAnalysis : public SVLInfoTreeAnalysisBase {
public:
    SVLInfoTreeAnalysis(TTree *tree=0):SVLInfoTreeAnalysisBase(tree) {
        fMaxevents = -1;
    }
    virtual ~SVLInfoTreeAnalysis() {}
    virtual void RunJob(TString);
    virtual void Begin(TFile*);
    virtual void End(TFile*);
    virtual void Loop();

    virtual void analyze();

    inline virtual void setMaxEvents(Long64_t max) {
        fMaxevents = max;
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
                         TString xtitle) {
        // Add a plot through the external interface
        Plot *plot = new Plot(name, var, sel, nbins, minx, maxx, xtitle, fChain);
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

    virtual void WritePlots(TString filename) {
        int totentries = 0;
        for (size_t i = 0; i < fPlotList.size(); ++i) {
            fPlotList[i]->fHisto->Write(fPlotList[i]->fHisto->GetName());
            totentries += fPlotList[i]->fHisto->GetEntries();
            delete fPlotList[i];
        }
        if(totentries == 0) {
            std::cout << "WARNING: all histograms for " << filename << " are empty! " << std::endl;
        }
    }

    /////////////////////////////////////////////
    std::vector<Plot*> fPlotList;
    Long64_t fMaxevents;

};
#endif

