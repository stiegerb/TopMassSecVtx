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
	// Reset all the tree variables
	bev_.run=-999;
	bev_.event=-999;
	bev_.lumi=-999;
	bev_.evcat=-999;
	bev_.gevcat=-999;
	bev_.nvtx=-999;
	bev_.rho=-999.99;

	bev_.nw=0;
	bev_.nl=0;
	bev_.nj=0;
	bev_.npf=0;
	bev_.npfb1=0;

	for(size_t i=0; i<bev_.gMaxNWeights; i++){
		bev_.w[i] = -999.99;
	}
	for(size_t i=0; i<bev_.gMaxNLeps; i++){
		bev_.lid[i]  = 0;
		bev_.glid[i] = 0;
		bev_.lpt[i]   = -999.99;
		bev_.leta[i]  = -999.99;
		bev_.lphi[i]  = -999.99;
		bev_.glpt[i]  = -999.99;
		bev_.gleta[i] = -999.99;
		bev_.glphi[i] = -999.99;
	}
	for(size_t i=0; i<bev_.gMaxNJets; i++){
		bev_.jflav[i] = 0;
		bev_.jpt[i]  = -999.99;
		bev_.jeta[i] = -999.99;
		bev_.jphi[i] = -999.99;
		bev_.jcsv[i] = -999.99;
		bev_.jarea[i] = -999.99;
		bev_.jtoraw[i] = -999.99;
	}
	for(size_t i=0; i<bev_.gMaxNSV; i++){
		bev_.tid[i] = 0;
		bev_.tpt[i]   = -999.99;
		bev_.teta[i]  = -999.99;
		bev_.tphi[i]  = -999.99;
		bev_.tmass[i] = -999.99;

		bev_.bid[i] = 0;
		bev_.bpt[i]  = -999.99;
		bev_.beta[i] = -999.99;
		bev_.bphi[i] = -999.99;

		bev_.bhadid[i] = 0;
		bev_.bhadpt[i]   = -999.99;
		bev_.bhadeta[i]  = -999.99;
		bev_.bhadphi[i]  = -999.99;
		bev_.bhadmass[i] = -999.99;
		bev_.bhadlxy[i]  = -999.99;

		bev_.svmass[i]   = -999.99;
		bev_.svpt[i]     = -999.99;
		bev_.sveta[i]    = -999.99;
		bev_.svphi[i]    = -999.99;
		bev_.svmass[i]   = -999.99;
		bev_.svntk[i]    = -999;
		bev_.svlxy[i]    = -999.99;
		bev_.svlxyerr[i] = -999.99;
	}
	for(size_t i=0; i<bev_.gMaxNPFCands; i++){
		bev_.pfid[i] = 0;
		bev_.pfjetidx[i] = 0;
		bev_.pfpt[i]  = -999.99;
		bev_.pfeta[i] = -999.99;
		bev_.pfphi[i] = -999.99;
	}

	bev_.metpt  = -999.99;
	bev_.metphi = -999.99;
}

//
void LxyAnalysis::attachToDir(TDirectory *outDir)
{
	outDir_=outDir;
	outT_ = new TTree("lxy","lxy analysis tree");
	outT_->SetDirectory(outDir_);
	outT_->SetAutoSave(500000);
	outT_->Branch("run",      &bev_.run,       "run/I");
	outT_->Branch("lumi",     &bev_.lumi,      "lumi/I");
	outT_->Branch("event",    &bev_.event,     "event/I");
	outT_->Branch("evcat",    &bev_.evcat,     "evcat/I");
	outT_->Branch("gevcat",   &bev_.gevcat,    "gevcat/I");
	outT_->Branch("nvtx",     &bev_.nvtx,      "nvtx/I");
	outT_->Branch("rho",      &bev_.rho,       "rho/F");
	outT_->Branch("nw",       &bev_.nw,        "nw/I");
	outT_->Branch("w",         bev_.w,         "w[nw]/F");
	outT_->Branch("nl",       &bev_.nl,        "nl/I");
	outT_->Branch("lid",       bev_.lid,       "lid[nl]/I");
	outT_->Branch("lpt",       bev_.lpt,       "lpt[nl]/F");
	outT_->Branch("leta",      bev_.leta,      "leta[nl]/F");
	outT_->Branch("lphi",      bev_.lphi,      "lphi[nl]/F");
	outT_->Branch("glid",      bev_.glid,      "glid[nl]/I");
	outT_->Branch("glpt",      bev_.glpt,      "glpt[nl]/F");
	outT_->Branch("gleta",     bev_.gleta,     "gleta[nl]/F");
	outT_->Branch("glphi",     bev_.glphi,     "glphi[nl]/F");
	outT_->Branch("nj",       &bev_.nj,        "nj/I");
	outT_->Branch("jflav",     bev_.jflav,     "jflav[nj]/I");
	outT_->Branch("jpt",       bev_.jpt,       "jpt[nj]/F");
	outT_->Branch("jeta",      bev_.jeta,      "jeta[nj]/F");
	outT_->Branch("jphi",      bev_.jphi,      "jphi[nj]/F");
	outT_->Branch("jcsv",      bev_.jcsv,      "jcsv[nj]/F");
	outT_->Branch("jarea",     bev_.jarea,     "jarea[nj]/F");
	outT_->Branch("jtoraw",    bev_.jtoraw,    "jtoraw[nj]/F");
	outT_->Branch("gjpt",      bev_.gjpt,      "gjpt[nj]/F");
	outT_->Branch("gjeta",     bev_.gjeta,     "gjeta[nj]/F");
	outT_->Branch("gjphi",     bev_.gjphi,     "gjphi[nj]/F");
	outT_->Branch("svpt",      bev_.svpt,      "svpt[nj]/F");
	outT_->Branch("sveta",     bev_.sveta,     "sveta[nj]/F");
	outT_->Branch("svphi",     bev_.svphi,     "svphi[nj]/F");
	outT_->Branch("svmass",    bev_.svmass,    "svmass[nj]/F");
	outT_->Branch("svntk",     bev_.svntk,     "svntk[nj]/F");
	outT_->Branch("svlxy",     bev_.svlxy,     "svlxy[nj]/F");
	outT_->Branch("svlxyerr",  bev_.svlxyerr,  "svlxyerr[nj]/F");
	outT_->Branch("bid",       bev_.bid,       "bid[nj]/I");
	outT_->Branch("bpt",       bev_.bpt,       "bpt[nj]/F");
	outT_->Branch("beta",      bev_.beta,      "beta[nj]/F");
	outT_->Branch("bphi",      bev_.bphi,      "bphi[nj]/F");
	outT_->Branch("bhadid",    bev_.bhadid,    "bhadid[nj]/I");
	outT_->Branch("bhadpt",    bev_.bhadpt,    "bhadpt[nj]/F");
	outT_->Branch("bhadeta",   bev_.bhadeta,   "bhadeta[nj]/F");
	outT_->Branch("bhadphi",   bev_.bhadphi,   "bhadphi[nj]/F");
	outT_->Branch("bhadmass",  bev_.bhadmass,  "bhadmass[nj]/F");
	outT_->Branch("bhadlxy",   bev_.bhadlxy,   "bhadlxy[nj]/F");
	outT_->Branch("npf",      &bev_.npf,       "npf/I");
	outT_->Branch("npfb1",    &bev_.npfb1,     "npfb1/I");
	outT_->Branch("pfid",      bev_.pfid,      "pfid[npf]/I");
	outT_->Branch("pfjetidx",  bev_.pfjetidx,  "pfjetidx[npf]/I");
	outT_->Branch("pfpt",      bev_.pfpt,      "pfpt[npf]/F");
	outT_->Branch("pfeta",     bev_.pfeta,     "pfeta[npf]/F");
	outT_->Branch("pfphi",     bev_.pfphi,     "pfphi[npf]/F");
	outT_->Branch("metpt",    &bev_.metpt,     "metpt/F");
	outT_->Branch("metphi",   &bev_.metphi,    "metphi/F");
	outT_->Branch("tid",       bev_.tid,       "tid[nj]/I");
	outT_->Branch("tpt",       bev_.tpt,       "tpt[nj]/F");
	outT_->Branch("teta",      bev_.teta,      "teta[nj]/F");
	outT_->Branch("tphi",      bev_.tphi,      "tphi[nj]/F");
	outT_->Branch("tmass",     bev_.tmass,     "tmass[nj]/F");
}


//
bool LxyAnalysis::analyze(Int_t run, Int_t event, Int_t lumi,
						  Int_t nvtx, Float_t rho, std::vector<Float_t> weights,
						  Int_t evcat, Int_t gevcat,
						  std::vector<data::PhysicsObject_t *> &leptons,
						  std::vector<data::PhysicsObject_t *> &jets,
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
	bev_.rho=rho;
	for(size_t i=0; i<weights.size(); i++) { bev_.w[i]=weights[i]; bev_.nw++; }
	bev_.evcat=evcat;
	bev_.gevcat=gevcat;

	//leptons
	for(size_t i=0; i<leptons.size(); i++)
	{
		bev_.lid[bev_.nl]  = leptons[i]->get("id");
		bev_.lpt[bev_.nl]  = leptons[i]->pt();
		bev_.leta[bev_.nl] = leptons[i]->eta();
		bev_.lphi[bev_.nl] = leptons[i]->phi();

		bev_.glid[bev_.nl]  = leptons[i]->get("id");
		bev_.glpt[bev_.nl]  = leptons[i]->pt();
		bev_.gleta[bev_.nl] = leptons[i]->eta();
		bev_.glphi[bev_.nl] = leptons[i]->phi();

		bev_.nl++;
	}


	//look at the jets now
	bool hasCSVtag(false);
	float btagCut(leptons.size()==1 ? 0.783 : 0.405 );
	for(size_t i=0; i<jets.size(); i++)
	{
		const data::PhysicsObject_t &genJet=jets[i]->getObject("genJet");
		bev_.jpt[bev_.nj]   = jets[i]->pt();
		bev_.jeta[bev_.nj]  = jets[i]->eta();
		bev_.jphi[bev_.nj]  = jets[i]->phi();
		if(genJet.pt()>0){
			bev_.jflav[bev_.nj] = genJet.info.find("id")->second;
			bev_.gjpt[bev_.nj]   = genJet.pt();
			bev_.gjeta[bev_.nj]  = genJet.eta();
			bev_.gjphi[bev_.nj]  = genJet.phi();
		}
		bev_.jcsv[bev_.nj]  = jets[i]->getVal("csv");
		hasCSVtag |= (jets[i]->getVal("csv")>btagCut);
		bev_.jarea[bev_.nj]  = jets[i]->getVal("area");
		bev_.jtoraw[bev_.nj]  = jets[i]->getVal("torawsf");

		const data::PhysicsObject_t &genParton=jets[i]->getObject("gen");
		if(genParton.pt()>0){
			bev_.bid[bev_.nj]=genParton.info.find("id")->second;
			bev_.bpt[bev_.nj]=genParton.pt();
			bev_.beta[bev_.nj]=genParton.eta();
			bev_.bphi[bev_.nj]=genParton.phi();
		}

		const data::PhysicsObject_t &svx=jets[i]->getObject("svx");
		if(svx.pt()>0){
			bev_.svpt[bev_.nj]     = svx.pt();
			bev_.sveta[bev_.nj]    = svx.eta();
			bev_.svphi[bev_.nj]    = svx.phi();
			bev_.svmass[bev_.nj]   = svx.mass();
			bev_.svntk[bev_.nj]    = svx.info.find("ntrk")->second;
			bev_.svlxy[bev_.nj]    = svx.vals.find("lxy")->second;
			bev_.svlxyerr[bev_.nj] = svx.vals.find("lxyErr")->second;
		}

		//match to a b-hadron
		for(size_t imc=0; imc<mctruth.size(); imc++)
		{
			int id=mctruth[imc].get("id");

			//check if top can be matched by charge to the quark
			if(genParton.pt()>0 && abs(id)==6 && abs(bev_.bid[bev_.nj])==5 && bev_.bid[bev_.nj]*id<0 && mctruth[imc].get("status")==3 )
			{
				bev_.tid[bev_.nj]=id;
				bev_.tpt[bev_.nj]=mctruth[imc].pt();
				bev_.teta[bev_.nj]=mctruth[imc].eta();
				bev_.tphi[bev_.nj]=mctruth[imc].phi();
				bev_.tmass[bev_.nj]=mctruth[imc].mass();
			}

			if(abs(id)<500) continue;

			if(deltaR(mctruth[imc],*(jets[i]))>0.5) continue;
			bev_.bhadpt[bev_.nj]   = mctruth[imc].pt();
			bev_.bhadeta[bev_.nj]  = mctruth[imc].eta();
			bev_.bhadphi[bev_.nj]  = mctruth[imc].phi();
			bev_.bhadmass[bev_.nj] = mctruth[imc].mass();
			bev_.bhadlxy[bev_.nj]  = mctruth[imc].getVal("lxy");

			break;
		}

		//charged PF candidates clustered in jet
		size_t pfstart=jets[i]->get("pfstart");
		size_t pfend=jets[i]->get("pfend");
		if(pfstart<pf.size() && pfend<pf.size())
		{
			for(size_t ipfn=pfstart; ipfn<=pfend; ipfn++)
			{
				if(pf[ipfn].get("charge")==0) continue;

				bev_.pfid[bev_.npf]  = pf[ipfn].get("id");
				bev_.pfpt[bev_.npf]  = pf[ipfn].pt();
				bev_.pfeta[bev_.npf] = pf[ipfn].eta();
				bev_.pfphi[bev_.npf] = pf[ipfn].phi();
				bev_.pfjetidx[bev_.npf]=i;
				bev_.npf++;
				if(bev_.npf > int(bev_.gMaxNPFCands)){
					cout << "Over 500 PF candidates associated to the jets!" << endl;
					break;
				}
			}
		}

		bev_.nj++;
	}

	//met
	bev_.metpt=met.pt();
	bev_.metphi=met.phi();

	//event selection
	if( hasCSVtag ){
		outT_->Fill();
		return true;
	}
	return false;
}





