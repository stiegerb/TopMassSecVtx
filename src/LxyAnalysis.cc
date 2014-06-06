#include "UserCode/llvv_fwk/interface/LxyAnalysis.h"
#include <Math/VectorUtil.h>

using namespace std;
typedef ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >::BetaVector BetaVector;

//
LxyAnalysis::LxyAnalysis() : outT_(0), outDir_(0)
{
  resetBeautyEvent();
}

//
void LxyAnalysis::resetBeautyEvent()
{
  bev_.nw=0;
  bev_.nl=0;
  bev_.nj=0;
  bev_.npf=0;
}

//
void LxyAnalysis::attachToDir(TDirectory *outDir)
{
  outDir_=outDir;
  outT_ = new TTree("lxy","lxy analysis tree");
  outT_->Branch("run",      &bev_.run,       "run/I");
  outT_->Branch("lumi",     &bev_.lumi,      "lumi/I");
  outT_->Branch("event",    &bev_.event,     "event/I");
  outT_->Branch("evcat",    &bev_.evcat,     "evcat/I");
  outT_->Branch("nvtx",     &bev_.nvtx,      "nvtx/I");
  outT_->Branch("nw",       &bev_.nw,        "nw/I");
  outT_->Branch("w",         bev_.w,         "w[nw]/F");
  outT_->Branch("nl",       &bev_.nl,        "nl/I");
  outT_->Branch("lid",       bev_.lid,       "lid[nl]/I");
  outT_->Branch("lpt",       bev_.lpt,       "lpt[nl]/F");
  outT_->Branch("leta",      bev_.leta,      "leta[nl]/F");
  outT_->Branch("lphi",      bev_.lphi,      "lphi[nl]/F");
  outT_->Branch("nj",       &bev_.nj,        "nj/I");
  outT_->Branch("jflav",     bev_.jflav,     "jflav[nj]/I");
  outT_->Branch("jpt",       bev_.jpt,       "jpt[nj]/F");
  outT_->Branch("jeta",      bev_.jeta,      "jeta[nj]/F");
  outT_->Branch("jphi",      bev_.jphi,      "jphi[nj]/F");
  outT_->Branch("bid",      &bev_.bid,       "bid/I");
  outT_->Branch("bhadid",   &bev_.bhadid,    "bhadid/I");
  outT_->Branch("svpt",     &bev_.svpt,      "svpt/F");
  outT_->Branch("sveta",    &bev_.sveta,     "sveta/F");
  outT_->Branch("svphi",    &bev_.svphi,     "svphi/F");
  outT_->Branch("svmass",   &bev_.svmass,    "svmass/F");
  outT_->Branch("svntk",    &bev_.svntk,     "svntk/F");
  outT_->Branch("svlxy",    &bev_.svlxy,     "svlxy/F");
  outT_->Branch("svlxyerr", &bev_.svlxyerr,  "svlxyerr/F");
  outT_->Branch("bpt",      &bev_.bpt,       "bpt/F");
  outT_->Branch("beta",     &bev_.beta,      "beta/F");
  outT_->Branch("bphi",     &bev_.bphi,      "bphi/F");
  outT_->Branch("bhadpt",   &bev_.bhadpt,    "bhadpt/F");
  outT_->Branch("bhadeta",  &bev_.bhadeta,   "bhadeta/F");
  outT_->Branch("bhadphi",  &bev_.bhadphi,   "bhadphi/F");
  outT_->Branch("bhadmass", &bev_.bhadmass,  "bhadmass/F");
  outT_->Branch("bhadlxy",  &bev_.bhadlxy,   "bhadlxy/F");
  outT_->Branch("npf",      &bev_.npf,       "npf/F");
  outT_->Branch("pfid",      bev_.pfid,      "pfid[npf]/I");
  outT_->Branch("pfpt",      bev_.pfpt,      "pfpt[npf]/F");
  outT_->Branch("pfeta",     bev_.pfeta,     "pfeta[npf]/F");
  outT_->Branch("pfphi",     bev_.pfphi,     "pfphi[npf]/F");
  outT_->Branch("metpt",    &bev_.metpt,     "metpt/F");
  outT_->Branch("metphi",   &bev_.metphi,    "metphi/F");
}


//
void LxyAnalysis::analyze(Int_t run, Int_t event, Int_t lumi,
			  Int_t nvtx, std::vector<Float_t> weights,
			  Int_t evcat,
			  data::PhysicsObjectCollection_t &leptons, 
			  data::PhysicsObjectCollection_t &jets,
			  LorentzVector &met, 
			  data::PhysicsObjectCollection_t &pf,
			  data::PhysicsObjectCollection_t &mctruth)
{
  //set all counters to 0
  resetBeautyEvent();

  //event info
  bev_.run=run;
  bev_.event=event;
  bev_.lumi=lumi;
  bev_.nvtx=nvtx;
  for(size_t i=0; i<weights.size(); i++) { bev_.w[i]=weights[i]; bev_.nw++; }
  bev_.evcat=evcat;

  //leptons
  for(size_t i=0; i<leptons.size(); i++)
    {
      bev_.lid[bev_.nl]  = leptons[i].get("id");
      bev_.lpt[bev_.nl]  = leptons[i].pt();
      bev_.leta[bev_.nl] = leptons[i].eta();
      bev_.lphi[bev_.nl] = leptons[i].phi();
      bev_.nl++;
    }


  //here is a trick just to get the leading lxy jet first
  for(size_t i=0; i<jets.size(); i++)
    {
      const data::PhysicsObject_t &svx=jets[i].getObject("svx");
      jets[i].setVal("lxy",svx.vals.find("lxy")->second);
    }
  sort(jets.begin(), jets.end(), data::PhysicsObject_t::sortByLxy);

  //look at the jets now
  for(size_t i=0; i<jets.size(); i++)
    {
      const data::PhysicsObject_t &genJet=jets[i].getObject("genJet");
      bev_.jflav[bev_.nj] = genJet.info.find("id")->second;
      bev_.jpt[bev_.nj]   = jets[i].pt();
      bev_.jeta[bev_.nj]  = jets[i].eta();
      bev_.jphi[bev_.nj]  = jets[i].phi();
      bev_.nj++;

      if(i!=0) continue;

      const data::PhysicsObject_t &genParton=jets[i].getObject("gen");
      bev_.bid=genParton.info.find("id")->second;
      bev_.bpt=genParton.pt();
      bev_.beta=genParton.eta();
      bev_.bphi=genParton.phi();

      const data::PhysicsObject_t &svx=jets[i].getObject("svx");
      bev_.svpt     = svx.pt();
      bev_.sveta    = svx.eta();
      bev_.svphi    = svx.phi();
      bev_.svmass   = svx.mass();
      bev_.svntk    = svx.info.find("ntrk")->second;
      bev_.svlxy    = svx.vals.find("lxy")->second;
      bev_.svlxyerr = svx.vals.find("lxyerr")->second;

      //match to a b-hadron
      for(size_t imc=0; imc<mctruth.size(); imc++)
	{
	  int id=mctruth[imc].get("id");
	  if(abs(id)<500) continue;
	  
	  if(deltaR(mctruth[imc],jets[i])>0.5) continue;
	  bev_.bhadpt   = mctruth[imc].pt();
	  bev_.bhadeta  = mctruth[imc].eta();
	  bev_.bhadphi  = mctruth[imc].phi();
	  bev_.bhadmass = mctruth[imc].mass();
	  bev_.bhadlxy  = mctruth[imc].getVal("lxy");
	  
	  break;
	}

      //PF candidates clustered in jet
      size_t pfstart=jets[i].get("pfstart");
      size_t pfend=jets[i].get("pfend");
      for(size_t ipfn=pfstart; ipfn<=pfend; ipfn++)
	{
	  bev_.pfid[bev_.npf]  = pf[ipfn].get("id");
	  bev_.pfpt[bev_.npf]  = pf[ipfn].pt();
	  bev_.pfeta[bev_.npf] = pf[ipfn].eta();
	  bev_.pfphi[bev_.npf] = pf[ipfn].phi();
	  bev_.npf++;
	}
    }
  
  //met
  bev_.metpt=met.pt();
  bev_.metphi=met.phi();

  //all done here
  if(bev_.svlxy>0) outT_->Fill();
}





