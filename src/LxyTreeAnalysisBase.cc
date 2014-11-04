#include "UserCode/llvv_fwk/interface/LxyTreeAnalysisBase.h"

LxyTreeAnalysisBase::LxyTreeAnalysisBase(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
  if (tree == 0) return;
  Init(tree);
}

LxyTreeAnalysisBase::~LxyTreeAnalysisBase()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t LxyTreeAnalysisBase::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t LxyTreeAnalysisBase::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}

void LxyTreeAnalysisBase::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("run", &run, &b_run);
   fChain->SetBranchAddress("lumi", &lumi, &b_lumi);
   fChain->SetBranchAddress("event", &event, &b_event);
   fChain->SetBranchAddress("evcat", &evcat, &b_evcat);
   fChain->SetBranchAddress("gevcat", &gevcat, &b_gevcat);
   fChain->SetBranchAddress("nvtx", &nvtx, &b_nvtx);
   fChain->SetBranchAddress("rho", &rho, &b_rho);
   fChain->SetBranchAddress("qscale", &qscale, &b_qscale);
   fChain->SetBranchAddress("x1", &x1, &b_x1);
   fChain->SetBranchAddress("x2", &x2, &b_x2);
   fChain->SetBranchAddress("id1", &id1, &b_id1);
   fChain->SetBranchAddress("id2", &id2, &b_id2);
   fChain->SetBranchAddress("nw", &nw, &b_nw);
   fChain->SetBranchAddress("w", w, &b_w);
   fChain->SetBranchAddress("nl", &nl, &b_nl);
   fChain->SetBranchAddress("lid", lid, &b_lid);
   fChain->SetBranchAddress("lpt", lpt, &b_lpt);
   fChain->SetBranchAddress("leta", leta, &b_leta);
   fChain->SetBranchAddress("lphi", lphi, &b_lphi);
   fChain->SetBranchAddress("glid", glid, &b_glid);
   fChain->SetBranchAddress("glpt", glpt, &b_glpt);
   fChain->SetBranchAddress("gleta", gleta, &b_gleta);
   fChain->SetBranchAddress("glphi", glphi, &b_glphi);
   fChain->SetBranchAddress("nj", &nj, &b_nj);
   fChain->SetBranchAddress("jflav", jflav, &b_jflav);
   fChain->SetBranchAddress("jpt", jpt, &b_jpt);
   fChain->SetBranchAddress("jeta", jeta, &b_jeta);
   fChain->SetBranchAddress("jphi", jphi, &b_jphi);
   fChain->SetBranchAddress("jcsv", jcsv, &b_jcsv);
   fChain->SetBranchAddress("jarea", jarea, &b_jarea);
   fChain->SetBranchAddress("jtoraw", jtoraw, &b_jtoraw);
   fChain->SetBranchAddress("jjesup", jjesup, &b_jjesup);
   fChain->SetBranchAddress("jjesdn", jjesdn, &b_jjesdn);
   fChain->SetBranchAddress("jbhadmatchdr", jbhadmatchdr, &b_jbhadmatchdr);
   fChain->SetBranchAddress("gjpt", gjpt, &b_gjpt);
   fChain->SetBranchAddress("gjeta", gjeta, &b_gjeta);
   fChain->SetBranchAddress("gjphi", gjphi, &b_gjphi);
   fChain->SetBranchAddress("svpt", svpt, &b_svpt);
   fChain->SetBranchAddress("sveta", sveta, &b_sveta);
   fChain->SetBranchAddress("svphi", svphi, &b_svphi);
   fChain->SetBranchAddress("svmass", svmass, &b_svmass);
   fChain->SetBranchAddress("svntk", svntk, &b_svntk);
   fChain->SetBranchAddress("svlxy", svlxy, &b_svlxy);
   fChain->SetBranchAddress("svlxyerr", svlxyerr, &b_svlxyerr);
   fChain->SetBranchAddress("bid", bid, &b_bid);
   fChain->SetBranchAddress("bpt", bpt, &b_bpt);
   fChain->SetBranchAddress("beta", beta, &b_beta);
   fChain->SetBranchAddress("bphi", bphi, &b_bphi);
   fChain->SetBranchAddress("bhadid", bhadid, &b_bhadid);
   fChain->SetBranchAddress("bhadpt", bhadpt, &b_bhadpt);
   fChain->SetBranchAddress("bhadeta", bhadeta, &b_bhadeta);
   fChain->SetBranchAddress("bhadphi", bhadphi, &b_bhadphi);
   fChain->SetBranchAddress("bhadmass", bhadmass, &b_bhadmass);
   fChain->SetBranchAddress("bhadlxy", bhadlxy, &b_bhadlxy);
   fChain->SetBranchAddress("npf", &npf, &b_npf);
   fChain->SetBranchAddress("npfb1", &npfb1, &b_npfb1);
   fChain->SetBranchAddress("pfid", pfid, &b_pfid);
   fChain->SetBranchAddress("pfjetidx", pfjetidx, &b_pfjetidx);
   fChain->SetBranchAddress("pfpt", pfpt, &b_pfpt);
   fChain->SetBranchAddress("pfeta", pfeta, &b_pfeta);
   fChain->SetBranchAddress("pfphi", pfphi, &b_pfphi);
   fChain->SetBranchAddress("metpt", &metpt, &b_metpt);
   fChain->SetBranchAddress("metphi", &metphi, &b_metphi);
   fChain->SetBranchAddress("metvar", metvar, &b_metvar);
   fChain->SetBranchAddress("tid", tid, &b_tid);
   fChain->SetBranchAddress("tpt", tpt, &b_tpt);
   fChain->SetBranchAddress("teta", teta, &b_teta);
   fChain->SetBranchAddress("tphi", tphi, &b_tphi);
   fChain->SetBranchAddress("tmass", tmass, &b_tmass);
   Notify();
}

Bool_t LxyTreeAnalysisBase::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void LxyTreeAnalysisBase::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t LxyTreeAnalysisBase::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}

void LxyTreeAnalysisBase::Loop()
{
//   In a ROOT session, you can do:
//      Root > .L LxyTreeAnalysisBase.C
//      Root > LxyTreeAnalysisBase t
//      Root > t.GetEntry(12); // Fill t data members with entry number 12
//      Root > t.Show();       // Show values of entry 12
//      Root > t.Show(16);     // Read and show values of entry 16
//      Root > t.Loop();       // Loop on all entries
//

//     This is the loop skeleton where:
//    jentry is the global entry number in the chain
//    ientry is the entry number in the current Tree
//  Note that the argument to GetEntry must be:
//    jentry for TChain::GetEntry
//    ientry for TTree::GetEntry and TBranch::GetEntry
//
//       To read only selected branches, Insert statements like:
// METHOD1:
//    fChain->SetBranchStatus("*",0);  // disable all branches
//    fChain->SetBranchStatus("branchname",1);  // activate branchname
// METHOD2: replace line
//    fChain->GetEntry(jentry);       //read all branches
//by  b_branchname->GetEntry(ientry); //read only this branch
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntriesFast();

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;
      // if (Cut(ientry) < 0) continue;
   }
}
