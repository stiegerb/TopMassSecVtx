#ifndef _UEAnalysisSummary_h_
#define _UEAnalysisSummary_h_

#include "TTree.h"

struct UEAnalysisSummary_t
{
  Int_t ch,rec_nextrajets,gen_nextrajets,nvtx,njets;
  Int_t gen_nch[4][4],rec_nch[4][4];
  Float_t weight,normWeight;
  Float_t gen_ptttbar,gen_phittbar,rec_ptttbar,rec_phittbar,leadpt,trailerpt,st,sumpt;
  Float_t gen_ptflux[4][4],gen_avgpt[4][4],rec_ptflux[4][4],rec_avgpt[4][4];
};

void createUEAnalysisSummary(TTree *t,UEAnalysisSummary_t &ue)
{
  t->Branch("ch",            &ue.ch,            "ch/I");
  t->Branch("rec_nextrajets", &ue.rec_nextrajets, "rec_nextrajets/I");
  t->Branch("gen_nextrajets", &ue.gen_nextrajets, "gen_nextrajets/I");
  t->Branch("nvtx",          &ue.nvtx,          "nvtx/I");
  t->Branch("njets",         &ue.njets,         "njets/I");
  t->Branch("weight",        &ue.weight,        "weight/F");
  t->Branch("normWeight",    &ue.normWeight,    "normWeight/F");
  t->Branch("gen_ptttbar",   &ue.gen_ptttbar,   "gen_ptttbar/F");
  t->Branch("gen_phittbar",  &ue.gen_phittbar,  "gen_phittbar/F");
  t->Branch("rec_ptttbar",   &ue.rec_ptttbar,   "rec_ptttbar/F");
  t->Branch("rec_phittbar",  &ue.rec_phittbar,  "rec_phittbar/F");
  t->Branch("leadpt",        &ue.leadpt,        "leadpt/F");
  t->Branch("trailerpt",     &ue.trailerpt,     "trailerpt/F");
  t->Branch("st",            &ue.st,            "st/F");
  t->Branch("sumpt",         &ue.sumpt,         "sumpt/F");  
  t->Branch("gen_nch",            ue.gen_nch,           "gen_nch[4][4]/I");
  t->Branch("gen_ptflux",         ue.gen_ptflux,        "gen_ptflux[4][4]/F");
  t->Branch("gen_avgpt",          ue.gen_avgpt,         "gen_avgpt[4][4]/F");
  t->Branch("rec_nch",            ue.rec_nch,           "rec_nch[4][4]/I");
  t->Branch("rec_ptflux",         ue.rec_ptflux,        "rec_ptflux[4][4]/F");
  t->Branch("rec_avgpt",          ue.rec_avgpt,         "rec_avgpt[4][4]/F");
}

void attachUEAnalysisSummary(TTree *t,UEAnalysisSummary_t &ue)
{
  t->SetBranchAddress("ch",            &ue.ch);
  t->SetBranchAddress("rec_nextrajets", &ue.rec_nextrajets);
  t->SetBranchAddress("gen_nextrajets", &ue.gen_nextrajets);
  t->SetBranchAddress("nvtx",          &ue.nvtx);
  t->SetBranchAddress("njets",         &ue.njets);
  t->SetBranchAddress("weight",        &ue.weight);
  t->SetBranchAddress("normWeight",    &ue.normWeight);
  t->SetBranchAddress("gen_ptttbar",   &ue.gen_ptttbar);
  t->SetBranchAddress("gen_phittbar",  &ue.gen_phittbar);
  t->SetBranchAddress("rec_ptttbar",   &ue.rec_ptttbar);
  t->SetBranchAddress("rec_phittbar",  &ue.rec_phittbar);
  t->SetBranchAddress("leadpt",        &ue.leadpt);
  t->SetBranchAddress("trailerpt",     &ue.trailerpt);
  t->SetBranchAddress("st",            &ue.st);
  t->SetBranchAddress("sumpt",         &ue.sumpt);
  t->SetBranchAddress("gen_nch",            ue.gen_nch);
  t->SetBranchAddress("gen_ptflux",         ue.gen_ptflux);
  t->SetBranchAddress("gen_avgpt",          ue.gen_avgpt);
  t->SetBranchAddress("rec_nch",            ue.rec_nch);
  t->SetBranchAddress("rec_ptflux",         ue.rec_ptflux);
  t->SetBranchAddress("rec_avgpt",          ue.rec_avgpt);
}

#endif
