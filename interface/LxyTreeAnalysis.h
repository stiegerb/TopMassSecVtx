#ifndef LxyTreeAnalysis_h
#define LxyTreeAnalysis_h

#include <TFile.h>
#include <TH1D.h>
#include <TString.h>
#include <TTreeFormula.h>

#include <iostream>

#include "UserCode/llvv_fwk/interface/LxyTreeAnalysisBase.h"

class Plot {
   public:
      Plot(){};
      Plot(TString name, TString var, TString selection,
           Int_t nbins, Float_t minx, Float_t maxx, TTree *tree=0){
         fName = name;
         fHisto = new TH1D(name, name, nbins, minx, maxx);
         fHisto->Sumw2();
         fHisto->SetXTitle(var);
         fVariable  = new TTreeFormula("Variable", var, tree);
         fSelection = new TTreeFormula("Formula", selection, tree);
      };

      virtual ~Plot(){
         fHisto->Delete();
         fVariable->Delete();
         fSelection->Delete();
      };

      virtual void Fill(){
         float weight = fSelection->EvalInstance();
         if( weight == 0. ) return;
         float var = fVariable->EvalInstance();
         fHisto->Fill(var, weight);
      }

      virtual void Print(){
         std::cout << "fName=" << fName.Data()
              << " fBranchName=\"" << fVariable->GetExpFormula().Data()
              << "\" fSelection=\"" << fSelection->GetExpFormula().Data()
              << "\"" << std::endl;
      };

      virtual void SetTree(TTree *tree){
         fSelection->SetTree(tree);
         fVariable->SetTree(tree);
      }

      virtual void Notify(){
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
   LxyTreeAnalysis(TTree *tree=0):LxyTreeAnalysisBase(tree){}
   virtual ~LxyTreeAnalysis(){}
   virtual void RunJob(TString);
   virtual void Begin(TFile*);
   virtual void End(TFile*);
   virtual void Loop();

   virtual void BookHistos();
   virtual void WriteHistos();

   virtual void analyze();

   /////////////////////////////////////////////
   // LxyTreeAnalysis interface:
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


   virtual Bool_t Notify(){
      // Called when a new tree is loaded in the chain
      // std::cout << "New tree (" << fCurrent
      //           << ") from "
      //           << fChain->GetCurrentFile()->GetName() << std::endl;

      for (size_t i = 0; i < fPlotList.size(); ++i){
         fPlotList[i]->SetTree(fChain->GetTree());
         fPlotList[i]->Notify();
      }
      return kTRUE;
   }

/////////////////////////////////////////////
   std::vector<Plot*> fPlotList;

   std::vector<TH1*> fHistos;

   TH1D *fHmlSv_emu_deltar;
   TH1D *fHmlSv_emu_deltar_correct;
   TH1D *fHmlSv_emu_deltar_wrong;

   TH1D *fHmlSv_emu_deltar_ntr2;
   TH1D *fHmlSv_emu_deltar_ntr2_correct;
   TH1D *fHmlSv_emu_deltar_ntr2_wrong;

   TH1D *fHmlSv_emu_deltar_ntr3;
   TH1D *fHmlSv_emu_deltar_ntr3_correct;
   TH1D *fHmlSv_emu_deltar_ntr3_wrong;

   TH1D *fHmlSv_emu_deltar_ntr4;
   TH1D *fHmlSv_emu_deltar_ntr4_correct;
   TH1D *fHmlSv_emu_deltar_ntr4_wrong;

//minmass

   TH1D *fHmlSv_emu_minmass;
   TH1D *fHmlSv_emu_minmass_correct;
   TH1D *fHmlSv_emu_minmass_wrong;

   TH1D *fHmlSv_emu_minmass_ntr2;
   TH1D *fHmlSv_emu_minmass_ntr2_correct;
   TH1D *fHmlSv_emu_minmass_ntr2_wrong;

   TH1D *fHmlSv_emu_minmass_ntr3;
   TH1D *fHmlSv_emu_minmass_ntr3_correct;
   TH1D *fHmlSv_emu_minmass_ntr3_wrong;

   TH1D *fHmlSv_emu_minmass_ntr4;
   TH1D *fHmlSv_emu_minmass_ntr4_correct;
   TH1D *fHmlSv_emu_minmass_ntr4_wrong;
/*
   TH1D *fHMinv2LeadTrk; // Inv. mass of two leading tracks in b-jet (emu chan)
   TH1D *fHEb1_emu; // Energy of first b-jet in emu channel

//Jevgeny
   TH1D *fHmlSv_mu_deltar; // Inv. mass of lepton and secondary vertex(the closest one of first two) (mu chan)
   TH1D *fHmlSv_e_deltar;
   TH1D *fHmlSv_ee_deltar;
   TH1D *fHmlSv_mumu_deltar;
   TH1D *fHmlSv_emu_deltar; // inv.m. of lepton and secondary vertex (emu chan)  
   TH1D *fHmlSv_emu_deltar_correct; // inv.m. of lepton and secondary vertex (emu chan) (correct charge)
   TH1D *fHmlSv_emu_deltar_wrong; // inv.m. of lepton and secondary vertex (emu chan)  (wrong charge)

   //number of tracks
   TH1D *fHntrSv_emu_deltar;
   TH1D *fHntrSv_emu_deltar_wrong;
   TH1D *fHntrSv_emu_deltar_correct;

   // using 2 leptopns
   TH1D *fHm2lSv_emu;

   //using charge to find correct sec.v.
   TH1D *fHmlSv_emu_wrong;
   TH1D *fHmlSv_mumu;
   TH1D *fHmlSv_emu;
   TH1D *fHmlSv_ee;

   //using charge to find correct bhadron
   TH1D *fHmlbh_emu;
   TH1D *fHmlbh_emu_correct;
   TH1D *fHmlbh_emu_wrong;

   //various number of tracks

   TH1D *fHmlSv_emu_deltar_ntr2; // inv.m. of lepton and secondary vertex (emu chan)  
   TH1D *fHmlSv_emu_deltar_ntr2_correct; // inv.m. of lepton and secondary vertex (emu chan) (correct charge)
   TH1D *fHmlSv_emu_deltar_ntr2_wrong; // inv.m. of lepton and secondary vertex (emu chan)  (wrong charge)

   TH1D *fHmlSv_emu_deltar_ntr3; // inv.m. of lepton and secondary vertex (emu chan)  
   TH1D *fHmlSv_emu_deltar_ntr3_correct; // inv.m. of lepton and secondary vertex (emu chan) (correct charge)
   TH1D *fHmlSv_emu_deltar_ntr3_wrong; // inv.m. of lepton and secondary vertex (emu chan)  (wrong charge)

   TH1D *fHmlSv_emu_deltar_ntr4; // inv.m. of lepton and secondary vertex (emu chan)  
   TH1D *fHmlSv_emu_deltar_ntr4_correct; // inv.m. of lepton and secondary vertex (emu chan) (correct charge)
   TH1D *fHmlSv_emu_deltar_ntr4_wrong; // inv.m. of lepton and secondary vertex (emu chan)  (wrong charge)
// only sec v mass

   TH1D *fHmSv_emu_deltar; // inv.m. of lepton and secondary vertex (emu chan)  
   TH1D *fHmSv_emu_deltar_correct; // inv.m. of lepton and secondary vertex (emu chan) (correct charge)
   TH1D *fHmSv_emu_deltar_wrong; // inv.m. of lepton and secondary vertex (emu chan)  (wrong charge)

   TH1D *fHmSv_emu_deltar_ntr2; // inv.m. of lepton and secondary vertex (emu chan)  
   TH1D *fHmSv_emu_deltar_ntr2_correct; // inv.m. of lepton and secondary vertex (emu chan) (correct charge)
   TH1D *fHmSv_emu_deltar_ntr2_wrong; // inv.m. of lepton and secondary vertex (emu chan)  (wrong charge)

   TH1D *fHmSv_emu_deltar_ntr3; // inv.m. of lepton and secondary vertex (emu chan)  
   TH1D *fHmSv_emu_deltar_ntr3_correct; // inv.m. of lepton and secondary vertex (emu chan) (correct charge)
   TH1D *fHmSv_emu_deltar_ntr3_wrong; // inv.m. of lepton and secondary vertex (emu chan)  (wrong charge)

   TH1D *fHmSv_emu_deltar_ntr4; // inv.m. of lepton and secondary vertex (emu chan)  
   TH1D *fHmSv_emu_deltar_ntr4_correct; // inv.m. of lepton and secondary vertex (emu chan) (correct charge)
   TH1D *fHmSv_emu_deltar_ntr4_wrong; // inv.m. of lepton and secondary vertex (emu chan)  (wrong charge)
*/

};
#endif

