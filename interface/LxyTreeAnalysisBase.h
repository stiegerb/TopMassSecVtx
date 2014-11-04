//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Wed Nov  5 00:02:54 2014 by ROOT version 5.32/00
// from TTree lxy/lxy analysis tree
// found on file: root://eoscms//eos/cms/store/cmst3/group/top/summer2014/e1fa735/MC8TeV_TTJets_MSDecays_172v5_0.root
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
   Int_t           gevcat;
   Int_t           nvtx;
   Float_t         rho;
   Float_t         qscale;
   Float_t         x1;
   Float_t         x2;
   Int_t           id1;
   Int_t           id2;
   Int_t           nw;
   Float_t         w[50];   //[nw]
   Int_t           nl;
   Int_t           lid[5];   //[nl]
   Float_t         lpt[5];   //[nl]
   Float_t         leta[5];   //[nl]
   Float_t         lphi[5];   //[nl]
   Int_t           glid[5];   //[nl]
   Float_t         glpt[5];   //[nl]
   Float_t         gleta[5];   //[nl]
   Float_t         glphi[5];   //[nl]
   Int_t           nj;
   Int_t           jflav[50];   //[nj]
   Float_t         jpt[50];   //[nj]
   Float_t         jeta[50];   //[nj]
   Float_t         jphi[50];   //[nj]
   Float_t         jcsv[50];   //[nj]
   Float_t         jarea[50];   //[nj]
   Float_t         jtoraw[50];   //[nj]
   Float_t         jjesup[50][26];   //[nj]
   Float_t         jjesdn[50][26];   //[nj]
   Float_t         jbhadmatchdr[50];   //[nj]
   Float_t         gjpt[50];   //[nj]
   Float_t         gjeta[50];   //[nj]
   Float_t         gjphi[50];   //[nj]
   Float_t         svpt[50];   //[nj]
   Float_t         sveta[50];   //[nj]
   Float_t         svphi[50];   //[nj]
   Float_t         svmass[50];   //[nj]
   Float_t         svntk[50];   //[nj]
   Float_t         svlxy[50];   //[nj]
   Float_t         svlxyerr[50];   //[nj]
   Int_t           bid[50];   //[nj]
   Float_t         bpt[50];   //[nj]
   Float_t         beta[50];   //[nj]
   Float_t         bphi[50];   //[nj]
   Int_t           bhadid[50];   //[nj]
   Float_t         bhadpt[50];   //[nj]
   Float_t         bhadeta[50];   //[nj]
   Float_t         bhadphi[50];   //[nj]
   Float_t         bhadmass[50];   //[nj]
   Float_t         bhadlxy[50];   //[nj]
   Int_t           npf;
   Int_t           npfb1;
   Int_t           pfid[1000];   //[npf]
   Int_t           pfjetidx[1000];   //[npf]
   Float_t         pfpt[1000];   //[npf]
   Float_t         pfeta[1000];   //[npf]
   Float_t         pfphi[1000];   //[npf]
   Float_t         metpt;
   Float_t         metphi;
   Float_t         metvar[8];
   Int_t           tid[50];   //[nj]
   Float_t         tpt[50];   //[nj]
   Float_t         teta[50];   //[nj]
   Float_t         tphi[50];   //[nj]
   Float_t         tmass[50];   //[nj]

   // List of branches
   TBranch        *b_run;   //!
   TBranch        *b_lumi;   //!
   TBranch        *b_event;   //!
   TBranch        *b_evcat;   //!
   TBranch        *b_gevcat;   //!
   TBranch        *b_nvtx;   //!
   TBranch        *b_rho;   //!
   TBranch        *b_qscale;   //!
   TBranch        *b_x1;   //!
   TBranch        *b_x2;   //!
   TBranch        *b_id1;   //!
   TBranch        *b_id2;   //!
   TBranch        *b_nw;   //!
   TBranch        *b_w;   //!
   TBranch        *b_nl;   //!
   TBranch        *b_lid;   //!
   TBranch        *b_lpt;   //!
   TBranch        *b_leta;   //!
   TBranch        *b_lphi;   //!
   TBranch        *b_glid;   //!
   TBranch        *b_glpt;   //!
   TBranch        *b_gleta;   //!
   TBranch        *b_glphi;   //!
   TBranch        *b_nj;   //!
   TBranch        *b_jflav;   //!
   TBranch        *b_jpt;   //!
   TBranch        *b_jeta;   //!
   TBranch        *b_jphi;   //!
   TBranch        *b_jcsv;   //!
   TBranch        *b_jarea;   //!
   TBranch        *b_jtoraw;   //!
   TBranch        *b_jjesup;   //!
   TBranch        *b_jjesdn;   //!
   TBranch        *b_jbhadmatchdr;   //!
   TBranch        *b_gjpt;   //!
   TBranch        *b_gjeta;   //!
   TBranch        *b_gjphi;   //!
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
   TBranch        *b_pfjetidx;   //!
   TBranch        *b_pfpt;   //!
   TBranch        *b_pfeta;   //!
   TBranch        *b_pfphi;   //!
   TBranch        *b_metpt;   //!
   TBranch        *b_metphi;   //!
   TBranch        *b_metvar;   //!
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

