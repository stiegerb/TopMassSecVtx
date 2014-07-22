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
   void fillJPsiHists(int, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&);
   void fillD0Hists(int, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&, TH1D*&);
   void fillDplusminusHists(int, TH1D*&);
   void fillMuD0Hists(int, TH1D*&, TH1D*&, float=1., float=1.0, int=13);

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
   TH1D *fHMinv2LeadTrk;// Inv. mass of two leading tracks in b-jet (emu chan)
   TH1D *fHMinvJPsiTrk;// Inv. mass of JPsi in b-jet (emu chan)
   TH1D *fHMinvJPsiTrk1;// Inv. mass of JPsi in b-jet (emu chan)
   TH1D *fHMinvJPsiTrk2;// Inv. mass of JPsi in b-jet (emu chan)
   TH1D *fHMinvJPsiTrk12;// Inv. mass of JPsi in b-jet (emu chan
   TH1D *fHMinvJPsiTrkmu;//   
   TH1D *fHMinvJPsiTrkmu1;//
   TH1D *fHMinvJPsiTrkmu2;//
   TH1D *fHMinvJPsiTrkmu12;//
   TH1D *fHMinvJPsiTrke;//
   TH1D *fHMinvJPsiTrke1;//
   TH1D *fHMinvJPsiTrke2;//
   TH1D *fHMinvJPsiTrke12;//
   TH1D *fHMinvD0Trk;//
   TH1D *fHMinvD0Trk1;// Inv. mass of D0 in b-jet (emu chan)
   TH1D *fHMinvD0Trk2;// Inv. mass of D0 in b-jet (emu chan)
   TH1D *fHMinvD0Trk12;// Inv. mass of D0 in b-jet (emu chan)
   TH1D *checkfHMinvD0Trk;//
   TH1D *checkfHMinvD0Trk1;// Inv. mass of D0 in b-jet (emu chan)
   TH1D *checkfHMinvD0Trk2;// Inv. mass of D0 in b-jet (emu chan)
   TH1D *checkfHMinvD0Trk12;// Inv. mass of D0 in b-jet (emu chan)
   TH1D *fHMinvD0Trkchargeselection;//Inv. mass of B-hadron 
   TH1D *fHMinvD0Trkchargeselection1;//Inv. mass of B-hadron 
   TH1D *fHMinvD0Trkchargeselection2;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselection12;//Inv. mass of B-hadron  
   TH1D *checkfHMinvD0Trkchargeselection;//Inv. mass of B-hadron 
   TH1D *checkfHMinvD0Trkchargeselection1;//Inv. mass of B-hadron 
   TH1D *checkfHMinvD0Trkchargeselection2;//Inv. mass of B-hadron
   TH1D *checkfHMinvD0Trkchargeselection12;//Inv. mass of B-hadron     
   TH1D *fHMinvD0Trkchargeselectionmuon;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionmuon1;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionmuon2;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionmuon12;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionelectron;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionelectron1;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionelectron2;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionelectron12;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionlepton;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionlepton1;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionlepton2;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkchargeselectionlepton12;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionelectron;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionelectron1;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionelectron2;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionelectron12;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionmuon;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionmuon1;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionmuon2;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionmuon12;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionlepton;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionlepton1;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionlepton2;//Inv. mass of B-hadron
   TH1D *fHMinvD0Trkdoublechargeselectionlepton12;//Inv. mass of B-hadron
   TH1D *fHMinvBTrkJPsiK;//Inv. mass of B-hadron 
   TH1D *fHMinvBTrkJPsiK1;//Inv. mass of B-hadron 
   TH1D *fHMinvBTrkJPsiK2;//Inv. mass of B-hadron 
   TH1D *fHMinvBTrkJPsiK12;//Inv. mass of B-hadron 
   TH1D *fHMinvBTrkD0;//Inv. mass of B-hadron
   TH1D *fHMinvBTrkD01;//Inv. mass of B-hadron
   TH1D *fHMinvBTrkD02;//Inv. mass of B-hadron
   TH1D *fHMinvBTrkD012;//Inv. mass of B-hadron
   TH1D *fHMinvBTrkD0chargeselection;//Inv. mass of B-hadron
   TH1D *fHMinvBTrkD0chargeselection1;//Inv. mass of B-hadron
   TH1D *fHMinvBTrkD0chargeselection2;//Inv. mass of B-hadron
   TH1D *fHMinvBTrkD0chargeselection12;//Inv. mass of B-hadron
   TH1D *fHMinvBTrktotal;//Inv. mass of B-hadron
   TH1D *fHMinvBTrktotal1;//Inv. mass of B-hadron
   TH1D *fHMinvBTrktotal2;//Inv. mass of B-hadron
   TH1D *fHMinvBTrktotal12;//Inv. mass of B-hadron
   TH1D *fHMinvBTrktotalchargeselection;//Inv. mass of B-hadron
   TH1D *fHMinvBTrktotalchargeselection1;//Inv. mass of B-hadron
   TH1D *fHMinvBTrktotalchargeselection2;//Inv. mass of B-hadron
   TH1D *fHMinvBTrktotalchargeselection12;//Inv. mass of B-hadron
   TH1D *fHEb1_emu;// Energy of first b-jet in emu channel
   TH1D *fHmlSv_mu;// Inv. mass of lepton and secondary vertex (mu chan) 
   TH1D *fHMinvDplusminusTrk;//
   TH1D *fHMinvDplusminusTrk1;//
   TH1D *fHMinvDplusminusTrk2;//
   TH1D *fHMinvDplusminusTrk12;//
};

#endif
