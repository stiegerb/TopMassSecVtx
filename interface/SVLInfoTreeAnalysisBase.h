//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Tue Feb 24 14:15:58 2015 by ROOT version 5.32/00
// from TTree SVLInfo/SecVtx Lepton Tree
// found on file: SVLInfo/Feb23c/MC8TeV_TTJets_MSDecays_172v5.root
//////////////////////////////////////////////////////////

#ifndef SVLInfoTreeAnalysisBase_h
#define SVLInfoTreeAnalysisBase_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.

// Fixed size dimensions of array or collections stored in the TTree if any.

class SVLInfoTreeAnalysisBase {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

   // Declaration of leaf types
   Int_t           Event;
   Int_t           Run;
   Int_t           Lumi;
   Int_t           EvCat;
   Float_t         Weight[11];
   Float_t         JESWeight[3];
   Float_t         METWeight[2];
   Float_t         SVBfragWeight[3];
   Float_t         NJets;
   Float_t         MET;
   Int_t           NPVtx;
   Int_t           NCombs;
   Float_t         SVLMass;
   Float_t         SVLMass_sf[2];
   Float_t         SVLDeltaR;
   Float_t         SVLMass_rot;
   Float_t         SVLDeltaR_rot;
   Int_t           BHadNeutrino;
   Float_t         LPt;
   Float_t         SVPt;
   Float_t         SVLxy;
   Float_t         JPt;
   Float_t         JEta;
   Int_t           SVNtrk;
   Int_t           CombCat;
   Int_t           CombInfo;
   Int_t           SVLMassRank;
   Int_t           SVLDeltaRRank;
   Int_t           SVLMassRank_rot;
   Int_t           SVLDeltaRRank_rot;

   // List of branches
   TBranch        *b_Event;   //!
   TBranch        *b_Run;   //!
   TBranch        *b_Lumi;   //!
   TBranch        *b_EvCat;   //!
   TBranch        *b_Weight;   //!
   TBranch        *b_JESWeight;   //!
   TBranch        *b_METWeight;   //!
   TBranch        *b_SVBfragWeight;   //!
   TBranch        *b_NJets;   //!
   TBranch        *b_MET;   //!
   TBranch        *b_NPVtx;   //!
   TBranch        *b_NCombs;   //!
   TBranch        *b_SVLMass;   //!
   TBranch        *b_SVLMass_sf;   //!
   TBranch        *b_SVLDeltaR;   //!
   TBranch        *b_SVLMass_rot;   //!
   TBranch        *b_SVLDeltaR_rot;   //!
   TBranch        *b_BHadNeutrino;   //!
   TBranch        *b_LPt;   //!
   TBranch        *b_SVPt;   //!
   TBranch        *b_SVLxy;   //!
   TBranch        *b_JPt;   //!
   TBranch        *b_JEta;   //!
   TBranch        *b_SVNtrk;   //!
   TBranch        *b_CombCat;   //!
   TBranch        *b_CombInfo;   //!
   TBranch        *b_SVLMassRank;   //!
   TBranch        *b_SVLDeltaRRank;   //!
   TBranch        *b_SVLMassRank_rot;   //!
   TBranch        *b_SVLDeltaRRank_rot;   //!

   SVLInfoTreeAnalysisBase(TTree *tree=0);
   virtual ~SVLInfoTreeAnalysisBase();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif

