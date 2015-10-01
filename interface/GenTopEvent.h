#ifndef _gentopevent_h_
#define _gentopevent_h_

#include "TTree.h"

struct GenTopEvent_t
{
  Float_t tpt[2],teta[2],tphi[2],tmass[2];
  Int_t tid[2];
  Int_t nj;
  Int_t jflav[100];
  Float_t jpt[100],jeta[100],jphi[100],jmass[100];
  Float_t bpt[100],beta[100],bphi[100],bmass[100];
  Int_t nl;
  Int_t lid[100];
  Float_t lpt[100],leta[100],lphi[100],lmass[100];
};

void bookGenTopEvent(TTree *t, GenTopEvent_t &ev)
{
  //summary tree
  t->Branch("tpt",   ev.tpt,    "tpt[2]/F");
  t->Branch("teta",   ev.teta,    "teta[2]/F");
  t->Branch("tphi",   ev.tphi,    "tphi[2]/F");
  t->Branch("tmass",   ev.tmass,    "tmass[2]/F");
  t->Branch("tid",   ev.tid,    "tid[2]/I");
  t->Branch("nj",    &ev.nj,    "nj/I");
  t->Branch("jpt",    ev.jpt,   "jpt[nj]/F");
  t->Branch("jeta",   ev.jeta,   "jeta[nj]/F");
  t->Branch("jphi",   ev.jphi,   "jphi[nj]/F");
  t->Branch("jmass",  ev.jmass,  "jmass[nj]/F");
  t->Branch("jflav",  ev.jflav,  "jflav[nj]/I");
  t->Branch("bpt",    ev.bpt,   "bpt[nj]/F");
  t->Branch("beta",   ev.beta,   "beta[nj]/F");
  t->Branch("bphi",   ev.bphi,   "bphi[nj]/F");
  t->Branch("bmass",  ev.bmass,  "bmass[nj]/F");
  t->Branch("nl",    &ev.nl,     "nl/I");
  t->Branch("lpt",    ev.lpt,    "lpt[nj]/F");
  t->Branch("leta",   ev.leta,   "leta[nj]/F");
  t->Branch("lphi",   ev.lphi,   "lphi[nj]/F");
  t->Branch("lmass",  ev.lmass,  "lmass[nj]/F");
  t->Branch("lid",    ev.lid,    "lid[nj]/I");
}



#endif
