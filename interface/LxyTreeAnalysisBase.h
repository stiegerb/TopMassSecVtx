//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Wed Jun 11 13:21:40 2014 by ROOT version 5.32/00
// from TTree lxy/lxy analysis tree
// found on file: /afs/cern.ch/user/s/stiegerb/work/TopSummerStudents/summary/benjamin/MC8TeV_TTJets_MSDecays_173v5_0_filt2.root
//////////////////////////////////////////////////////////

#ifndef LxyTreeAnalysisBase_h
#define LxyTreeAnalysisBase_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.

// Fixed size dimensions of array or collections stored in the TTree if any.

class LxyTreeAnalysisBase {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

   // Declaration of leaf types
   Int_t           run;
   Int_t           lumi;
   Int_t           event;
   Int_t           evcat;
   Int_t           nvtx;
   Float_t         rho;
   Int_t           nw;
   Float_t         w[50];   //[nw]
   Int_t           nl;
   Int_t           lid[50];   //[nl]
   Float_t         lpt[50];   //[nl]
   Float_t         leta[50];   //[nl]
   Float_t         lphi[50];   //[nl]
   Int_t           nj;
   Int_t           jflav[50];   //[nj]
   Float_t         jpt[50];   //[nj]
   Float_t         jeta[50];   //[nj]
   Float_t         jphi[50];   //[nj]
   Float_t         jcsv[50];   //[nj]
   Float_t         jarea[50];   //[nj]
   Float_t         jtoraw[50];   //[nj]
   Float_t         svpt[2];
   Float_t         sveta[2];
   Float_t         svphi[2];
   Float_t         svmass[2];
   Float_t         svntk[2];
   Float_t         svlxy[2];
   Float_t         svlxyerr[2];
   Int_t           bid[2];
   Float_t         bpt[2];
   Float_t         beta[2];
   Float_t         bphi[2];
   Int_t           bhadid[2];
   Float_t         bhadpt[2];
   Float_t         bhadeta[2];
   Float_t         bhadphi[2];
   Float_t         bhadmass[2];
   Float_t         bhadlxy[2];
   Int_t           npf;
   Int_t           npfb1;
   Int_t           pfid[200];   //[npf]
   Float_t         pfpt[200];   //[npf]
   Float_t         pfeta[200];   //[npf]
   Float_t         pfphi[200];   //[npf]
   Float_t         metpt;
   Float_t         metphi;
   Int_t           tid[2];
   Float_t         tpt[2];
   Float_t         teta[2];
   Float_t         tphi[2];
   Float_t         tmass[2];

   // List of branches
   TBranch        *b_run;   //!
   TBranch        *b_lumi;   //!
   TBranch        *b_event;   //!
   TBranch        *b_evcat;   //!
   TBranch        *b_nvtx;   //!
   TBranch        *b_rho;   //!
   TBranch        *b_nw;   //!
   TBranch        *b_w;   //!
   TBranch        *b_nl;   //!
   TBranch        *b_lid;   //!
   TBranch        *b_lpt;   //!
   TBranch        *b_leta;   //!
   TBranch        *b_lphi;   //!
   TBranch        *b_nj;   //!
   TBranch        *b_jflav;   //!
   TBranch        *b_jpt;   //!
   TBranch        *b_jeta;   //!
   TBranch        *b_jphi;   //!
   TBranch        *b_jcsv;   //!
   TBranch        *b_jarea;   //!
   TBranch        *b_jtoraw;   //!
   TBranch        *b_svpt;   //!
   TBranch        *b_sveta;   //!
   TBranch        *b_svphi;   //!
   TBranch        *b_svmass;   //!
   TBranch        *b_svntk;   //!
   TBranch        *b_svlxy;   //!
   TBranch        *b_svlxyerr;   //!
   TBranch        *b_bid;   //!
   TBranch        *b_bpt;   //!
   TBranch        *b_beta;   //!
   TBranch        *b_bphi;   //!
   TBranch        *b_bhadid;   //!
   TBranch        *b_bhadpt;   //!
   TBranch        *b_bhadeta;   //!
   TBranch        *b_bhadphi;   //!
   TBranch        *b_bhadmass;   //!
   TBranch        *b_bhadlxy;   //!
   TBranch        *b_npf;   //!
   TBranch        *b_npfb1;   //!
   TBranch        *b_pfid;   //!
   TBranch        *b_pfpt;   //!
   TBranch        *b_pfeta;   //!
   TBranch        *b_pfphi;   //!
   TBranch        *b_metpt;   //!
   TBranch        *b_metphi;   //!
   TBranch        *b_tid;   //!
   TBranch        *b_tpt;   //!
   TBranch        *b_teta;   //!
   TBranch        *b_tphi;   //!
   TBranch        *b_tmass;   //!


   LxyTreeAnalysisBase(TTree *tree=0);
   virtual ~LxyTreeAnalysisBase();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif