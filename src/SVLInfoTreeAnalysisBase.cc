#include "UserCode/TopMassSecVtx/interface/SVLInfoTreeAnalysisBase.h"

SVLInfoTreeAnalysisBase::SVLInfoTreeAnalysisBase(TTree *tree) : fChain(0)
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) return;
   Init(tree);
}

SVLInfoTreeAnalysisBase::~SVLInfoTreeAnalysisBase()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t SVLInfoTreeAnalysisBase::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t SVLInfoTreeAnalysisBase::LoadTree(Long64_t entry)
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

void SVLInfoTreeAnalysisBase::Init(TTree *tree)
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

   fChain->SetBranchAddress("Event", &Event, &b_Event);
   fChain->SetBranchAddress("Run", &Run, &b_Run);
   fChain->SetBranchAddress("Lumi", &Lumi, &b_Lumi);
   fChain->SetBranchAddress("EvCat", &EvCat, &b_EvCat);
   fChain->SetBranchAddress("Weight", Weight, &b_Weight);
   fChain->SetBranchAddress("JESWeight", JESWeight, &b_JESWeight);
   fChain->SetBranchAddress("SVBfragWeight", SVBfragWeight, &b_SVBfragWeight);
   fChain->SetBranchAddress("NJets", &NJets, &b_NJets);
   fChain->SetBranchAddress("MET", &MET, &b_MET);
   fChain->SetBranchAddress("NPVtx", &NPVtx, &b_NPVtx);
   fChain->SetBranchAddress("NCombs", &NCombs, &b_NCombs);
   fChain->SetBranchAddress("SVLMass", &SVLMass, &b_SVLMass);
   fChain->SetBranchAddress("SVLDeltaR", &SVLDeltaR, &b_SVLDeltaR);
   fChain->SetBranchAddress("SVLMass_rot", &SVLMass_rot, &b_SVLMass_rot);
   fChain->SetBranchAddress("SVLDeltaR_rot", &SVLDeltaR_rot, &b_SVLDeltaR_rot);
   fChain->SetBranchAddress("BHadNeutrino", &BHadNeutrino, &b_BHadNeutrino);
   fChain->SetBranchAddress("LPt", &LPt, &b_LPt);
   fChain->SetBranchAddress("SVPt", &SVPt, &b_SVPt);
   fChain->SetBranchAddress("SVLxy", &SVLxy, &b_SVLxy);
   fChain->SetBranchAddress("JPt", &JPt, &b_JPt);
   fChain->SetBranchAddress("JEta", &JEta, &b_JEta);
   fChain->SetBranchAddress("SVNtrk", &SVNtrk, &b_SVNtrk);
   fChain->SetBranchAddress("CombCat", &CombCat, &b_CombCat);
   fChain->SetBranchAddress("CombInfo", &CombInfo, &b_CombInfo);
   fChain->SetBranchAddress("SVLMassRank", &SVLMassRank, &b_SVLMassRank);
   fChain->SetBranchAddress("SVLDeltaRRank", &SVLDeltaRRank, &b_SVLDeltaRRank);
   fChain->SetBranchAddress("SVLMassRank_rot", &SVLMassRank_rot, &b_SVLMassRank_rot);
   fChain->SetBranchAddress("SVLDeltaRRank_rot", &SVLDeltaRRank_rot, &b_SVLDeltaRRank_rot);
   Notify();
}

Bool_t SVLInfoTreeAnalysisBase::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void SVLInfoTreeAnalysisBase::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t SVLInfoTreeAnalysisBase::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}

void SVLInfoTreeAnalysisBase::Loop()
{
//   In a ROOT session, you can do:
//      Root > .L SVLInfoTreeAnalysisBase.C
//      Root > SVLInfoTreeAnalysisBase t
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
