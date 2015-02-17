#ifndef LxyTreeAnalysis_cxx
#define LxyTreeAnalysis_cxx
#include "UserCode/TopMassSecVtx/interface/LxyTreeAnalysis.h"

#include "Math/VectorUtil.h"

#include <TLorentzVector.h>
#include <iostream>

const float gMassK  = 0.4937;
const float gMassPi = 0.1396;
const float gMassMu = 0.1057;

const float gCSVWPMedium = 0.783;

const int njetbins = 6;
const int nsvbins = 4;

struct SVLInfo{ // needed for sorting...
	unsigned counter;
	int lepindex;
	int svindex;
	int combcat;
	float svlmass, svlmass_rot;
	float svldeltar, svldeltar_rot;
	int jesweights[3];
	float bfragweights[3];
};
bool compare_mass (SVLInfo svl1, SVLInfo svl2){
	return (svl1.svlmass < svl2.svlmass);
}
bool compare_deltar (SVLInfo svl1, SVLInfo svl2){
	return (svl1.svldeltar < svl2.svldeltar);
}
bool compare_mass_rot (SVLInfo svl1, SVLInfo svl2){
	return (svl1.svlmass_rot < svl2.svlmass_rot);
}
bool compare_deltar_rot (SVLInfo svl1, SVLInfo svl2){
	return (svl1.svldeltar_rot < svl2.svldeltar_rot);
}

bool isOppositeSign(int id1, int id2) {
	if(id1*id2 == -211*211) return true;
	if(id1*id2 == 11*211)   return true;
	if(id1*id2 == 13*211)   return true;
	if(id1*id2 == -13*13)   return true;
	if(id1*id2 == -11*13)   return true;
	if(id1*id2 == -11*11)   return true;
	return false;
}

//
TLorentzVector LxyTreeAnalysis::RotateLepton(TLorentzVector &origLep,
	                                std::vector<TLorentzVector> &isoObjects)
{
  //rotate lepton
  int ntries(0);
  while(ntries<100)
    {
      TLorentzVector rotLepton(origLep);
      double en    = rotLepton.E();
      double pabs  = rotLepton.P();
      double phi   = rndGen_.Uniform(0,2*TMath::Pi());
      double theta = TMath::ACos( rndGen_.Uniform(-1,1) );
      rotLepton.SetPxPyPzE(pabs*TMath::Cos(phi)*TMath::Sin(theta),
      	                   pabs*TMath::Sin(phi)*TMath::Sin(theta),
      	                   pabs*TMath::Cos(theta),en);

      //require selectable kinematics
      if( TMath::Abs(rotLepton.Eta())>2.4 || rotLepton.Pt()<20 ) continue;

      //require object separation wrt to jets
      double minDR(1000);
      for(std::vector<TLorentzVector>::iterator it = isoObjects.begin();
      	  it!=isoObjects.end();
      	  it++)
	{
	  double dR = it->DeltaR(rotLepton);
	  if(dR>minDR) continue;
	  minDR=dR;
	}
      if(minDR<0.4) continue;
      return rotLepton;
    }

  return TLorentzVector(0,0,0,0);
}


void LxyTreeAnalysis::RunJob(TString filename){
	TFile *file = TFile::Open(filename, "recreate");
	Begin(file);
	Loop();
	End(file);
}
void LxyTreeAnalysis::Begin(TFile *file){
	// Anything that has to be done once at the beginning
	file->cd();
	BookHistos();
	BookCharmTree();
	BookSVLTree();
}

void LxyTreeAnalysis::End(TFile *file){
	// Anything that has to be done once at the end
	file->cd();
	WritePlots();
	WriteHistos();
	fCharmInfoTree->Write(fCharmInfoTree->GetName());
	fSVLInfoTree->Write(fSVLInfoTree->GetName());
	file->Write();
	file->Close();
}

void LxyTreeAnalysis::BookCharmHistos(){
	fHMJPsi = new TH1D("JPsi", "JPsi", 100, 2., 4.);
	fHistos.push_back(fHMJPsi);
	fHMJPsi->SetXTitle("m(ll) [GeV]");

	fHMJPsie = new TH1D("JPsie", "JPsie",100,2.,4.);
	fHistos.push_back(fHMJPsie);
	fHMJPsie->SetXTitle("m(ee) [GeV]");

	fHMJPsimu = new TH1D("JPsimu", "JPsimu",100,2.,4.);
	fHistos.push_back(fHMJPsimu);
	fHMJPsimu->SetXTitle("m(#mu#mu) [GeV]");

	fHMJPsiK = new TH1D("JPsiK", "JPsiK",100, 4.5, 6.);
	fHistos.push_back(fHMJPsiK);
	fHMJPsiK->SetXTitle("m(llK) [GeV]");

	fHMD0Incl5TrkDR = new TH1D("D0Incl5TrkDR", "D0 Incl 5Trk DR<0.2",100, 1.6, 2.2);
	fHistos.push_back(fHMD0Incl5TrkDR);
	fHMD0Incl5TrkDR->SetXTitle("m(K#pi) [GeV]");

	fHMD0Incl3Trk = new TH1D("D0Incl3Trk", "D0 Incl 3Trk",100, 1.6, 2.2);
	fHistos.push_back(fHMD0Incl3Trk);
	fHMD0Incl3Trk->SetXTitle("m(K#pi) [GeV]");

	fHMD0mu = new TH1D("D0mu", "D0mu",100, 1.6, 2.2);
	fHistos.push_back(fHMD0mu);
	fHMD0mu->SetXTitle("m(K#pi) [GeV]");

	fHMD0e = new TH1D("D0e", "D0e",100, 1.6, 2.2);
	fHistos.push_back(fHMD0e);
	fHMD0e->SetXTitle("m(K#pi) [GeV]");

	fHMD0lep = new TH1D("D0lep", "D0lep",100, 1.6, 2.2);
	fHistos.push_back(fHMD0lep);
	fHMD0lep->SetXTitle("m(K#pi) [GeV]");


	fHMDs2010lep = new TH1D("Ds2010lep", "Ds2010lep",100, 1.8, 2.4);
	fHistos.push_back(fHMDs2010lep);
	fHMDs2010lep->SetXTitle("m(K#pi#pi) [GeV]");

	fHDMDs2010D0lep = new TH1D("DMDs2010D0lep", "DMDs2010D0lep",100, 0.14, 0.15);
	fHistos.push_back(fHDMDs2010D0lep);
	fHDMDs2010D0lep->SetXTitle("m(K#pi#pi) - m(K#pi) [GeV]");


	fHMDpmZO = new TH1D("DpmZO", "Dpm Zoom Out",100, 1.0, 3.0);
	fHistos.push_back(fHMDpmZO);
	fHMDpmZO->SetXTitle("m(K#pi#pi) [GeV]");

	// fHMDpmKKPi = new TH1D("DpmKKPi", "Dpm KKpi",100, 1.0, 3.0);
	// fHistos.push_back(fHMDpmKKPi);
	// fHMDpmKKPi->SetXTitle("m(KK#pi) [GeV]");

	fHMDpm = new TH1D("Dpm", "Dpm",100, 1.6, 2.2);
	fHistos.push_back(fHMDpm);
	fHMDpm->SetXTitle("m(K#pi#pi) [GeV]");

	fHMDpme = new TH1D("Dpme", "Dpme",60, 1.6, 2.2);
	fHistos.push_back(fHMDpme);
	fHMDpme->SetXTitle("m(K#pi#pi) [GeV]");

	fHMDpmmu = new TH1D("Dpmmu", "Dpmmu",60, 1.6, 2.2);
	fHistos.push_back(fHMDpmmu);
	fHMDpmmu->SetXTitle("m(K#pi#pi) [GeV]");

	fHMDpmlep = new TH1D("Dpmlep", "Dpmlep",60, 1.6, 2.2);
	fHistos.push_back(fHMDpmlep);
	fHMDpmlep->SetXTitle("m(K#pi#pi) [GeV]");
}
void LxyTreeAnalysis::BookSVLHistos(){
	fHNJets    = new TH1D("NJets",    "NJets (inclusive)", njetbins, 2, 2+njetbins); fHistos.push_back(fHNJets); fHNJets->SetXTitle("Jet Multiplicity");
	fHNJets_e  = new TH1D("NJets_e",  "NJets (single e)",  njetbins, 2, 2+njetbins); fHistos.push_back(fHNJets_e); fHNJets_e->SetXTitle("Jet Multiplicity");
	fHNJets_m  = new TH1D("NJets_m",  "NJets (single mu)", njetbins, 2, 2+njetbins); fHistos.push_back(fHNJets_m); fHNJets_m->SetXTitle("Jet Multiplicity");
	fHNJets_ee = new TH1D("NJets_ee", "NJets (ee)",        njetbins, 2, 2+njetbins); fHistos.push_back(fHNJets_ee); fHNJets_ee->SetXTitle("Jet Multiplicity");
	fHNJets_mm = new TH1D("NJets_mm", "NJets (mumu)",      njetbins, 2, 2+njetbins); fHistos.push_back(fHNJets_mm); fHNJets_mm->SetXTitle("Jet Multiplicity");
	fHNJets_em = new TH1D("NJets_em", "NJets (emu)",       njetbins, 2, 2+njetbins); fHistos.push_back(fHNJets_em); fHNJets_em->SetXTitle("Jet Multiplicity");

	fHNSVJets    = new TH1D("NSVJets",    "NJets with SV (inclusive)", nsvbins, 1, 1+nsvbins); fHistos.push_back(fHNSVJets); fHNSVJets->SetXTitle("SV Multiplicity");
	fHNSVJets_e  = new TH1D("NSVJets_e",  "NJets with SV (single e)",  nsvbins, 1, 1+nsvbins); fHistos.push_back(fHNSVJets_e); fHNSVJets_e->SetXTitle("SV Multiplicity");
	fHNSVJets_m  = new TH1D("NSVJets_m",  "NJets with SV (single mu)", nsvbins, 1, 1+nsvbins); fHistos.push_back(fHNSVJets_m); fHNSVJets_m->SetXTitle("SV Multiplicity");
	fHNSVJets_ee = new TH1D("NSVJets_ee", "NJets with SV (ee)",        nsvbins, 1, 1+nsvbins); fHistos.push_back(fHNSVJets_ee); fHNSVJets_ee->SetXTitle("SV Multiplicity");
	fHNSVJets_mm = new TH1D("NSVJets_mm", "NJets with SV (mumu)",      nsvbins, 1, 1+nsvbins); fHistos.push_back(fHNSVJets_mm); fHNSVJets_mm->SetXTitle("SV Multiplicity");
	fHNSVJets_em = new TH1D("NSVJets_em", "NJets with SV (emu)",       nsvbins, 1, 1+nsvbins); fHistos.push_back(fHNSVJets_em); fHNSVJets_em->SetXTitle("SV Multiplicity");

	fHNbJets    = new TH1D("NbJets",    "NbJets (inclusive)", nsvbins, 0, nsvbins); fHistos.push_back(fHNbJets); fHNbJets->SetXTitle("CSV med-tagged Jet Multiplicity");
	fHNbJets_e  = new TH1D("NbJets_e",  "NbJets (single e)",  nsvbins, 0, nsvbins); fHistos.push_back(fHNbJets_e); fHNbJets_e->SetXTitle("CSV med-tagged Jet Multiplicity");
	fHNbJets_m  = new TH1D("NbJets_m",  "NbJets (single mu)", nsvbins, 0, nsvbins); fHistos.push_back(fHNbJets_m); fHNbJets_m->SetXTitle("CSV med-tagged Jet Multiplicity");
	fHNbJets_ee = new TH1D("NbJets_ee", "NbJets (ee)",        nsvbins, 0, nsvbins); fHistos.push_back(fHNbJets_ee); fHNbJets_ee->SetXTitle("CSV med-tagged Jet Multiplicity");
	fHNbJets_mm = new TH1D("NbJets_mm", "NbJets (mumu)",      nsvbins, 0, nsvbins); fHistos.push_back(fHNbJets_mm); fHNbJets_mm->SetXTitle("CSV med-tagged Jet Multiplicity");
	fHNbJets_em = new TH1D("NbJets_em", "NbJets (emu)",       nsvbins, 0, nsvbins); fHistos.push_back(fHNbJets_em); fHNbJets_em->SetXTitle("CSV med-tagged Jet Multiplicity");

	fHMET    = new TH1D("MET",    "MET (inclusive)", 100, 0, 200.); fHistos.push_back(fHMET); fHMET->SetXTitle("Missing ET [GeV]");
	fHMET_e  = new TH1D("MET_e",  "MET (single e)",  100, 0, 200.); fHistos.push_back(fHMET_e); fHMET_e->SetXTitle("Missing ET [GeV]");
	fHMET_m  = new TH1D("MET_m",  "MET (single mu)", 100, 0, 200.); fHistos.push_back(fHMET_m); fHMET_m->SetXTitle("Missing ET [GeV]");
	fHMET_ee = new TH1D("MET_ee", "MET (ee)",        80, 40.,200.); fHistos.push_back(fHMET_ee); fHMET_ee->SetXTitle("Missing ET [GeV]");
	fHMET_mm = new TH1D("MET_mm", "MET (mumu)",      80, 40.,200.); fHistos.push_back(fHMET_mm); fHMET_mm->SetXTitle("Missing ET [GeV]");
	fHMET_em = new TH1D("MET_em", "MET (emu)",       100, 0, 200.); fHistos.push_back(fHMET_em); fHMET_em->SetXTitle("Missing ET [GeV]");

    fHDY_mll_ee = new TH1D("DY_mll_ee", "m(ll) in DY ee control", 100, 60., 120.); fHistos.push_back(fHDY_mll_ee); fHDY_mll_ee->SetXTitle("Dilepton invariant mass [GeV]");
    fHDY_mll_mm = new TH1D("DY_mll_mm", "m(ll) in DY mm control", 100, 60., 120.); fHistos.push_back(fHDY_mll_mm); fHDY_mll_mm->SetXTitle("Dilepton invariant mass [GeV]");
    fHDY_met_ee = new TH1D("DY_met_ee", "MET in DY ee control",   100, 0., 100.);  fHistos.push_back(fHDY_met_ee); fHDY_met_ee->SetXTitle("Missing ET [GeV]");
    fHDY_met_mm = new TH1D("DY_met_mm", "MET in DY mm control",   100, 0., 100.);  fHistos.push_back(fHDY_met_mm); fHDY_met_mm->SetXTitle("Missing ET [GeV]");
}
void LxyTreeAnalysis::BookHistos(){
	// charm resonance histos:
	BookCharmHistos();

	// lepton sec vertex histos:
	BookSVLHistos();

	// Call Sumw2() for all of them
	std::vector<TH1*>::iterator h;
	for(h = fHistos.begin(); h != fHistos.end(); ++h) {
		(*h)->Sumw2();
	}
}
void LxyTreeAnalysis::WriteHistos(){
	// Write all histos to file, then delete them
	std::vector<TH1*>::iterator h;
	for( h = fHistos.begin(); h != fHistos.end(); ++h){
		(*h)->Write((*h)->GetName());
		(*h)->Delete();
	}
}


void LxyTreeAnalysis::BookCharmTree() {
	fCharmInfoTree = new TTree("CharmInfo", "Charm Info Tree");
	fCharmInfoTree->Branch("EvCat",        &fTCharmEvCat,   "EvCat/I");
	fCharmInfoTree->Branch("CandType",     &fTCandType,     "CandType/I");
	fCharmInfoTree->Branch("CandMass",     &fTCandMass,     "CandMass/F");
	fCharmInfoTree->Branch("CandPt",       &fTCandPt,       "CandPt/F");
	fCharmInfoTree->Branch("CandEta",      &fTCandEta,      "CandEta/F");
	fCharmInfoTree->Branch("CandPz",       &fTCandPz,       "CandPz/F");
	fCharmInfoTree->Branch("CandPtRel",    &fTCandPtRel,    "CandPtRel/F");
	fCharmInfoTree->Branch("CandDeltaR",   &fTCandDeltaR,   "CandDeltaR/F");
	fCharmInfoTree->Branch("JetPt",        &fTJetPt,        "JetPt/F");
	fCharmInfoTree->Branch("JetEta",       &fTJetEta,       "JetEta/F");
	fCharmInfoTree->Branch("JetPz",        &fTJetPz,        "JetPz/F");
	fCharmInfoTree->Branch("HardTkPt",     &fTHardTkPt,     "HardTkPt/F");
	fCharmInfoTree->Branch("SoftTkPt",     &fTSoftTkPt,     "SoftTkPt/F");
	fCharmInfoTree->Branch("SumPtCharged", &fTSumPtCharged, "SumPtCharged/F");
	fCharmInfoTree->Branch("SumPzCharged", &fTSumPzCharged, "SumPzCharged/F");
}
void LxyTreeAnalysis::ResetCharmTree() {
	fTCharmEvCat   = -99;
	fTCandType     = -99;
	fTCandMass     = -99.99;
	fTCandPt       = -99.99;
	fTCandEta      = -99.99;
	fTCandPz       = -99.99;
	fTCandPtRel    = -99.99;
	fTCandDeltaR   = -99.99;
	fTJetPt        = -99.99;
	fTJetEta       = -99.99;
	fTJetPz        = -99.99;
	fTHardTkPt     = -99.99;
	fTSoftTkPt     = -99.99;
	fTSumPtCharged = -99.99;
	fTSumPzCharged = -99.99;
}

int LxyTreeAnalysis::firstTrackIndex(int jetindex){
	// Find index of the first track in this jet
	int result = 0;
	for (result = 0; result < npf; ++result){
		if (pfjetidx[result]==jetindex){
			break; // at this point, result is correct
		}
	}
	return result;
}

void LxyTreeAnalysis::FillCharmTree(int type, int jind,
									int ind1, float mass1,
									int ind2, float mass2) {
	// Check that indices make sense
	if(jind < 0 || ind1 < 0 || ind2 < 0) return;
	if(jind >= nj || ind1 >= npf || ind2 >= npf) return;

	TLorentzVector p_track1, p_track2, p_cand, p_jet;
	p_track1.SetPtEtaPhiM(pfpt[ind1], pfeta[ind1], pfphi[ind1], mass1);
	p_track2.SetPtEtaPhiM(pfpt[ind2], pfeta[ind2], pfphi[ind2], mass2);
	p_cand = p_track1+p_track2;
	p_jet.SetPtEtaPhiM(jpt[jind], jeta[jind], jphi[jind], 0.);

	float hardpt = std::max(pfpt[ind1], pfpt[ind2]);
	float softpt = std::min(pfpt[ind1], pfpt[ind2]);

	FillCharmTree(type, jind, p_cand, p_jet, hardpt, softpt);
	return;
}
void LxyTreeAnalysis::FillCharmTree(int type, int jind,
									int ind1, float mass1,
									int ind2, float mass2,
									int ind3, float mass3) {
	// Check that indices make sense
	if(jind<0 || ind1<0 || ind2<0 || ind3<0) return;
	if(jind>=nj || ind1>=npf || ind2>=npf || ind3>=npf) return;

	TLorentzVector p_track1, p_track2, p_track3;
	p_track1.SetPtEtaPhiM(pfpt[ind1], pfeta[ind1], pfphi[ind1], mass1);
	p_track2.SetPtEtaPhiM(pfpt[ind2], pfeta[ind2], pfphi[ind2], mass2);
	p_track3.SetPtEtaPhiM(pfpt[ind3], pfeta[ind3], pfphi[ind3], mass3);

	TLorentzVector p_cand, p_jet;
	p_cand = p_track1+p_track2+p_track3;
	p_jet.SetPtEtaPhiM(jpt[jind], jeta[jind], jphi[jind], 0.);

	float hardpt = std::max(pfpt[ind3], std::max(pfpt[ind1], pfpt[ind2]));
	float softpt = std::min(pfpt[ind3], std::min(pfpt[ind1], pfpt[ind2]));

	FillCharmTree(type, jind, p_cand, p_jet, hardpt, softpt);
	return;
}
void LxyTreeAnalysis::FillCharmTree(int type, int jind,
									TLorentzVector p_cand,
									TLorentzVector p_jet,
									float hardpt, float softpt){
	fTCandType   = type;
	fTCharmEvCat = evcat;
	fTCandMass  = p_cand.M();
	fTCandPt    = p_cand.Pt();
	fTCandEta   = p_cand.Eta();
	fTCandPz    = p_cand.Pz();
	fTCandPtRel = ROOT::Math::VectorUtil::Perp(p_cand.Vect(), p_jet.Vect());
	fTCandDeltaR = p_cand.DeltaR(p_jet);

	fTJetPt  = p_jet.Pt();
	fTJetEta = p_jet.Eta();
	fTJetPz  = p_jet.Pz();
	fTSumPtCharged = 0.;
	fTSumPzCharged = 0.;
	TLorentzVector p_trks(0.,0.,0.,0.);
	for (int i = 0; i < npf; ++i) {
		if (pfjetidx[i] != jind) continue;
		TLorentzVector p_tk;
		p_tk.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], gMassPi);
		p_trks = p_trks + p_tk;
	}

	fTHardTkPt = hardpt;
	fTSoftTkPt = softpt;

	fTSumPtCharged = p_trks.Pt();
	fTSumPzCharged = p_trks.Pz();
	fCharmInfoTree->Fill();
	return;
}

void LxyTreeAnalysis::fillJPsiHists(int jetindex) {
	TLorentzVector p_track1, p_track2;

	for (int i = 0; i < npf; ++i)
	{
		if (pfjetidx[i]!= jetindex) continue; //select the most probable b-jet
		if (abs(pfid[i])!=13 && abs(pfid[i]) != 11 ) continue;    //select a muon or electron
		for (int j = 0; j < npf; ++j) //find another muon or electron
		{
			if(pfjetidx[j]!=pfjetidx[i]) continue; // select the most probable b-jet
			if(pfid[j]*pfid[i]!=-169 && pfid[j]*pfid[i]!=-121) continue; // let both electrons or muons have opposite charge

			float trackmass = gMassMu;
			if(abs(pfid[j]*pfid[i]) == 121) trackmass = 0.;
			p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], trackmass);
			p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], trackmass);

			float mass12 = (p_track1+p_track2).M();
			if (abs(pfid[i])==11) { // ee
				fHMJPsie->Fill(mass12, w[0]);
				if (mass12>2.5 && mass12<3.5) {
					FillCharmTree(443, jetindex, i, trackmass, j, trackmass);
				}
			}
			if (abs(pfid[i])==13) { // mm
				fHMJPsimu->Fill(mass12, w[0]);
				if (mass12>2.5 && mass12<3.5) {
					FillCharmTree(443*100, jetindex, i, trackmass, j, trackmass);
				}
			}
			fHMJPsi->Fill(mass12, w[0]);

			// Mass window cut
			if(mass12 > 3.2 || mass12 < 3.0) continue;

			for (int tk3 = 0; tk3 < npf; ++tk3){ // look for a third track
				if (pfjetidx[tk3]!=jetindex) continue;
				if (tk3 == i) continue;
				if (tk3 == j) continue;

				if( abs(pfid[tk3]) != 211) continue;
				TLorentzVector p_track3;
				p_track3.SetPtEtaPhiM(pfpt[tk3], pfeta[tk3], pfphi[tk3], gMassK);
				fHMJPsiK->Fill((p_track1+p_track2+p_track3).M(), w[0]);
				FillCharmTree(521, jetindex, i, trackmass, j, trackmass, tk3, gMassK);
			}
		}
	}
}
void LxyTreeAnalysis::fillD0Hists(int jetindex){
	TLorentzVector p_track1, p_track2;
	int nstart = firstTrackIndex(jetindex);

	for (int i = nstart; i < nstart+5; ++i){
		if (pfjetidx[i]!= jetindex) continue; // select the jet
		// (in case less then 5 tracks in this jet)
		if (abs(pfid[i])!=211) continue; // not a lepton

		for (int j = i+1; j < nstart+5; ++j){ //find another kaon or pion
			if(pfjetidx[j]!=jetindex) continue; // select the jet
			if(pfid[j]*pfid[i]!=-211*211) continue; // opposite sign, not a lepton

			p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], gMassPi);
			p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], gMassK);

			if (p_track1.DeltaR(p_track2)>0.2) continue;

			fHMD0Incl5TrkDR->Fill((p_track1+p_track2).M(), w[0]);

			p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], gMassK);
			p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], gMassPi);

			fHMD0Incl5TrkDR->Fill((p_track1+p_track2).M(), w[0]);
		}
	}

	// less than three tracks for this jet
	if (pfjetidx[nstart+2]!=jetindex ) return;

	// permutations of hardest three trackmass
	// including interchanging them!
	int p1[] = {nstart,   nstart,   nstart+1, nstart+1, nstart+2, nstart+2};
	int p2[] = {nstart+1, nstart+2, nstart+2, nstart,   nstart,   nstart+1};

	for (int p = 0; p < 6; ++p){
		int tk1=p1[p];
		int tk2=p2[p];

		// Opposite sign
		if (pfid[tk1]*pfid[tk2] != -211*211) continue;

		p_track1.SetPtEtaPhiM(pfpt[tk1], pfeta[tk1], pfphi[tk1], gMassPi);
		p_track2.SetPtEtaPhiM(pfpt[tk2], pfeta[tk2], pfphi[tk2], gMassK);
		float mass12 = (p_track1+p_track2).M();

		// Fill both mass assumptions
		fHMD0Incl3Trk->Fill(mass12, w[0]);
		if (mass12>1.65 && mass12<2.0)
			FillCharmTree(421, jetindex, tk1, gMassPi, tk2, gMassK);

		for (int tk3 = 0; tk3 < npf; ++tk3){ // look for a lepton
			if (pfjetidx[tk3]!=jetindex) continue;
			if (tk3 == tk1) continue;
			if (tk3 == tk2) continue;

			if( abs(pfid[tk3]) != 13 && abs(pfid[tk3]) != 11) continue;

			if( pfid[tk2]/abs(pfid[tk2]) == -pfid[tk3]/abs(pfid[tk3]) ){
				// Kaon and lepton have same charge
				// I.e. correct mass assumption
				fHMD0lep->Fill(mass12, w[0]);

				if (abs(pfid[tk3]) == 13){
					fHMD0mu->Fill(mass12, w[0]);
					if (mass12>1.6 && mass12<2.5)
						FillCharmTree(421013, jetindex, tk1, gMassPi, tk2, gMassK);
				}

				if (abs(pfid[tk3]) == 11){
					fHMD0e->Fill(mass12, w[0]);
					if (mass12>1.6 && mass12<2.5)
						FillCharmTree(421011, jetindex, tk1, gMassPi, tk2, gMassK);
				}

				if(abs(mass12-1.864) < 0.05){ // mass window cut
					for(int tk4 = 0; tk4 < npf; ++tk4){ // look for a pion
						if (pfjetidx[tk4]!=jetindex) continue;
						if (tk4==tk1 || tk4==tk2 || tk4==tk3) continue;
						if (abs(pfid[tk4]) != 211) continue;

						// same charge as first pion
						if (pfid[tk4]*pfid[tk1] != 211*211) continue;
						TLorentzVector p_track4;
						p_track4.SetPtEtaPhiM(pfpt[tk4], pfeta[tk4], pfphi[tk4], gMassPi);
						fHMDs2010lep->Fill((p_track1+p_track2+p_track4).M(), w[0]);
						FillCharmTree(413, jetindex, tk1, gMassPi, tk2, gMassK, tk4, gMassPi);

						fHDMDs2010D0lep->Fill((p_track1+p_track2+p_track4).M() - mass12, w[0]);
					}
				}
			}
		}
	}
}
void LxyTreeAnalysis::fillDpmHists(int jetindex){
	int nstart = firstTrackIndex(jetindex);
	int ntracks = 3;

	for (int tk1 = nstart; tk1 < nstart+ntracks; ++tk1){
		if(pfjetidx[tk1] != jetindex) continue;

		for (int tk2 = tk1+1; tk2 < nstart+ntracks; ++tk2){
			if(pfjetidx[tk2] != jetindex) continue;

			for (int tk3 = tk2+1; tk3 < nstart+ntracks; ++tk3){
				if(pfjetidx[tk3] != jetindex) continue;

				int sumid = pfid[tk1]+pfid[tk2]+pfid[tk3];
				if( abs(sumid) != 211 ) return;

				float tk1mass(gMassPi), tk2mass(gMassPi), tk3mass(gMassPi);
				if( sumid == 211 ){ // +211+211-211 i.e. two positive tracks
					if(pfid[tk1] < 0) tk1mass = gMassK;
					if(pfid[tk2] < 0) tk2mass = gMassK;
					if(pfid[tk3] < 0) tk3mass = gMassK;
				}
				if( sumid == -211 ){ // +211-211-211 i.e. two negative tracks
					if(pfid[tk1] > 0) tk1mass = gMassK;
					if(pfid[tk2] > 0) tk2mass = gMassK;
					if(pfid[tk3] > 0) tk3mass = gMassK;
				}

				TLorentzVector p_track1, p_track2, p_track3;
				p_track1.SetPtEtaPhiM(pfpt[tk1], pfeta[tk1], pfphi[tk1], tk1mass);
				p_track2.SetPtEtaPhiM(pfpt[tk2], pfeta[tk2], pfphi[tk2], tk2mass);
				p_track3.SetPtEtaPhiM(pfpt[tk3], pfeta[tk3], pfphi[tk3], tk3mass);
				float mass123 = (p_track1+p_track2+p_track3).M();

				fHMDpm->Fill(mass123, w[0]);
				fHMDpmZO->Fill(mass123, w[0]);
				FillCharmTree(411, jetindex, tk1, tk1mass, tk2, tk2mass, tk3, tk3mass);

				// // Switched mass hypotheses (Kpipi -> piKK)
				// float tk1massS(gMassK), tk2massS(gMassK), tk3massS(gMassK);
				// if( sumid == 211 ){ // +211+211-211 i.e. two positive tracks
				//     if(pfid[tk1] < 0) tk1massS = gMassPi;
				//     if(pfid[tk2] < 0) tk2massS = gMassPi;
				//     if(pfid[tk3] < 0) tk3massS = gMassPi;
				// }
				// if( sumid == -211 ){ // +211-211-211 i.e. two negative tracks
				//     if(pfid[tk1] > 0) tk1massS = gMassPi;
				//     if(pfid[tk2] > 0) tk2massS = gMassPi;
				//     if(pfid[tk3] > 0) tk3massS = gMassPi;
				// }

				// p_track1.SetPtEtaPhiM(pfpt[tk1], pfeta[tk1], pfphi[tk1], tk1massS);
				// p_track2.SetPtEtaPhiM(pfpt[tk2], pfeta[tk2], pfphi[tk2], tk2massS);
				// p_track3.SetPtEtaPhiM(pfpt[tk3], pfeta[tk3], pfphi[tk3], tk3massS);
				// fHMDpmKKPi->Fill((p_track1+p_track2+p_track3).M());

				for (int tk4 = 0; tk4 < npf; ++tk4){ // look for a lepton
					if (pfjetidx[tk4]!=jetindex) continue;
					if (tk4 == tk1) continue;
					if (tk4 == tk2) continue;
					if (tk4 == tk3) continue;

					if( abs(pfid[tk4]) != 13 && abs(pfid[tk4]) != 11) continue;

					if( pfid[tk4] * sumid > 0 ){
						// both pos or neg, i.e. opposite sign between lep and had
						fHMDpmlep->Fill(mass123, w[0]);

						if (abs(pfid[tk4]) == 13){
							fHMDpmmu->Fill(mass123, w[0]);
							if (mass123>1.6 && mass123<2.5)
								FillCharmTree(411013, jetindex, tk1, tk1mass, tk2, tk2mass, tk3, tk3mass);
						}

						if (abs(pfid[tk4]) == 11){
							fHMDpme->Fill(mass123, w[0]);
							if (mass123>1.6 && mass123<2.5)
								FillCharmTree(411011, jetindex, tk1, tk1mass, tk2, tk2mass, tk3, tk3mass);
						}
					}
				}
			}
		}
	}
}
bool LxyTreeAnalysis::selectEvent(){
	if (abs(evcat) == 11*13) return true;                // emu
	if (abs(evcat) == 11*11 && metpt > 40.) return true; // ee
	if (abs(evcat) == 13*13 && metpt > 40.) return true; // mumu
	if (abs(evcat) == 11 && nj > 3) return true;         // e
	if (abs(evcat) == 13 && nj > 3) return true;         // mu
	return false;
}

bool LxyTreeAnalysis::selectSVLEvent(){
	int nsvjets(0), nbjets(0);
	for( int i=0; i < nj; i++){
		// count as bjet either jet with SV or jet with CSVM tag
		nbjets  += (svlxy[i] > 0 || jcsv[i] > gCSVWPMedium);
		nsvjets += (svlxy[i] > 0);
		// this implies nbjets >= nsvjets
	}

	// At least one SV in any channel
	if (nsvjets < 1) return false;

	// That's it for emu
	if (abs(evcat) == 11*13) return true;

	// For dilepton also MET > 40 GeV
	if (abs(evcat) == 11*11 || abs(evcat) == 13*13){
		if (metpt > 40.) return true;
		return false;
	}

	// For single lepton, at least 4 jets, and either 2 SV or 1 SV + 1 CSVM
	if (abs(evcat) == 11 || abs(evcat) == 13){
		if (nj < 4) return false;
		if (nsvjets > 1) return true; // two SV
		if (nbjets > 1) return true;  // one SV and one CSVM
		return false;
	}

	// QCD control sample (non-isolated leptons)
	if (abs(evcat) == 11*100 || abs(evcat) == 13*100){
		if (nj < 4) return false;
		if (nbjets > 1 || nsvjets > 1) return false; // suppress ttbar
		return true;
	}
	return false;
}

bool LxyTreeAnalysis::selectDYControlEvent(){
	int nsvjets(0), nbjets(0);
	for( int i=0; i < nj; i++){
		// count as bjet either jet with SV or jet with CSVM tag
		nbjets  += (svlxy[i] > 0 || jcsv[i] > gCSVWPMedium);
		nsvjets += (svlxy[i] > 0);
		// this implies nbjets >= nsvjets
	}

	// Note that there is a MET > 40 cut already applied in the pre-selection

	// At least one SV in any channel
	if (nsvjets < 1) return false;

	// |mll-mZ| < 15 GeV
	if (abs(evcat) == 11*11*1000 || abs(evcat) == 13*13*1000) return true;

	return false;
}

void LxyTreeAnalysis::BookSVLTree() {
	fSVLInfoTree = new TTree("SVLInfo", "SecVtx Lepton Tree");
	fSVLInfoTree->Branch("Event",     &fTEvent,     "Event/I");
	fSVLInfoTree->Branch("Run",       &fTRun,       "Run/I");
	fSVLInfoTree->Branch("Lumi",      &fTLumi,      "Lumi/I");
	fSVLInfoTree->Branch("EvCat",     &fTEvCat,     "EvCat/I");
	fSVLInfoTree->Branch("Weight",     fTWeight,    "Weight[10]/F");
	fSVLInfoTree->Branch("JESWeight",  fTJESWeight, "JESWeight[3]/F");
	fSVLInfoTree->Branch("SVBfragWeight" , fTSVBfragWeight  , "SVBfragWeight[3]/F");
	fSVLInfoTree->Branch("NPVtx",     &fTNPVtx,     "NPVtx/I");
	fSVLInfoTree->Branch("NCombs",    &fTNCombs,    "NCombs/I");
	fSVLInfoTree->Branch("SVLMass",   &fTSVLMass,   "SVLMass/F");
	fSVLInfoTree->Branch("SVLDeltaR", &fTSVLDeltaR, "SVLDeltaR/F");
	fSVLInfoTree->Branch("SVLMass_rot",   &fTSVLMass_rot,   "SVLMass_rot/F");
	fSVLInfoTree->Branch("SVLDeltaR_rot", &fTSVLDeltaR_rot, "SVLDeltaR_rot/F");
	fSVLInfoTree->Branch("LPt",       &fTLPt,       "LPt/F");
	fSVLInfoTree->Branch("SVPt",      &fTSVPt,      "SVPt/F");
	fSVLInfoTree->Branch("SVLxy",     &fTSVLxy,     "SVLxy/F");
	fSVLInfoTree->Branch("JPt",       &fTJPt,       "JPt/F");
	fSVLInfoTree->Branch("JEta",      &fTJEta,      "JEta/F");
	fSVLInfoTree->Branch("SVNtrk",    &fTSVNtrk,    "SVNtrk/I");
	// CombCat = 11, 12, 21, 22 for the four possible lepton/sv combinations
	fSVLInfoTree->Branch("CombCat"       , &fTCombCat       , "CombCat/I");
	// CombInfo = -1 for data or unmatched, 0 for wrong combs, 1 for correct combs
	fSVLInfoTree->Branch("CombInfo"      , &fTCombInfo      , "CombInfo/I");

	// Intra event rankings
	fSVLInfoTree->Branch("SVLMassRank",   &fTSVLMinMassRank, "SVLMassRank/I");
	fSVLInfoTree->Branch("SVLDeltaRRank", &fTSVLDeltaRRank,  "SVLDeltaRRank/I");
	fSVLInfoTree->Branch("SVLMassRank_rot",   &fTSVLMinMassRank_rot, "SVLMassRank_rot/I");
	fSVLInfoTree->Branch("SVLDeltaRRank_rot", &fTSVLDeltaRRank_rot,  "SVLDeltaRRank_rot/I");
}
void LxyTreeAnalysis::ResetSVLTree() {
	fTEvent     = event;
	fTRun       = run;
	fTLumi      = lumi;
	fTEvCat     = evcat;
	for (int i = 0; i < 10; ++i){
		fTWeight[i] = w[i];
	}
	for (int i = 0; i < 3; ++i){
		fTJESWeight[i] = -99.99;
		fTSVBfragWeight[i] = -99.99;
	}
	fTNPVtx          = nvtx;
	fTNCombs         = -99.99;
	fTSVLMass        = -99.99;
	fTSVLDeltaR      = -99.99;
	fTSVLMass_rot    = -99.99;
	fTSVLDeltaR_rot  = -99.99;
	fTLPt            = -99.99;
	fTSVPt           = -99.99;
	fTSVLxy          = -99.99;
	fTJEta           = -99.99;
	fTJPt            = -99.99;
	fTSVNtrk         = -99;
	fTCombCat        = -99;
	fTCombInfo       = -99;

	fTSVLMinMassRank = -99;
	fTSVLDeltaRRank  = -99;
}

void LxyTreeAnalysis::analyze(){
	///////////////////////////////////////////////////
	// Remove events with spurious PF candidate information (npf == 1000)
	if(npf > 999) return;
	///////////////////////////////////////////////////

	// Called once per event
	FillPlots();

	///////////////////////////////////////////////////
	// Charm resonance stuff:
	ResetCharmTree();

	float maxcsv = -1.;
	int maxind=-1;
	float second_max=-1.0;
	int maxind2=-1;

	for(int k = 0; k < nj; k++) {
		// use >= n not just > as max and max2 can have same value. Ex:{1,2,3,3}
		if(jcsv[k] >= maxcsv) {
			second_max=maxcsv;
			maxcsv=jcsv[k];
			maxind=k;
			maxind2=maxind;
		}
		else if(jcsv[k] > second_max) {
			second_max=jcsv[k];
			maxind2=k;
		}
	}

	if(selectEvent()){
		// J/Psi ( + K)
		fillJPsiHists(maxind);
		fillJPsiHists(maxind2);

		// D0
		fillD0Hists(maxind);
		fillD0Hists(maxind2);

		// D+
		fillDpmHists(maxind);
		fillDpmHists(maxind2);
	}


	///////////////////////////////////////////////////
	// Lepton + Secondary Vertex stuff:
	ResetSVLTree();

	// Find jets with SVs:
	std::vector<int> svindices(2,-1);
	int nsvjets(0), nbjets(0);
	float lxymax1(0), lxymax2(0);

	for( int i=0; i < nj; i++){
		if(svlxy[i]>0){
			nsvjets++;
			if(jcsv[i] > gCSVWPMedium) nbjets++;
			if(svlxyerr[i]!=0){
				if(svlxy[i]/svlxyerr[i]>lxymax1) {
					lxymax2=lxymax1;
					svindices[1]=svindices[0];
					lxymax1=svlxy[i]/svlxyerr[i];
					svindices[0]=i;
				}
				else if (svlxy[i]/svlxyerr[i]>lxymax2) {
					lxymax2=svlxy[i]/svlxyerr[i];
					svindices[1]=i;
				}
			}
		}
	}
	if(svindices[1]<0) svindices.pop_back();
	if(svindices[0]<0) svindices.pop_back();

	std::vector<TLorentzVector> isoObjects;
	for (int il = 0; il < nl; ++il) { TLorentzVector p4; p4.SetPtEtaPhiM(lpt[il], leta[il], lphi[il], 0.); isoObjects.push_back(p4); }
	for (int ij = 0; ij < nj; ++ij) { TLorentzVector p4; p4.SetPtEtaPhiM(jpt[ij], jeta[ij], jphi[ij], 0.); isoObjects.push_back(p4); }

	if(selectSVLEvent()){
		// Fill some control histograms:
		fHNJets   ->Fill(nj,      w[1]*w[4]);
		fHNSVJets ->Fill(nsvjets, w[1]*w[4]);
		fHNbJets  ->Fill(nbjets,  w[1]*w[4]);
		fHMET     ->Fill(metpt,   w[1]*w[4]);
		if (abs(evcat) == 11*13){
			fHNJets_em   ->Fill(nj,      w[1]*w[4]);
			fHNSVJets_em ->Fill(nsvjets, w[1]*w[4]);
			fHNbJets_em  ->Fill(nbjets,  w[1]*w[4]);
			fHMET_em     ->Fill(metpt,   w[1]*w[4]);
		}
		if (abs(evcat) == 11*11){
			fHNJets_ee   ->Fill(nj,      w[1]*w[4]);
			fHNSVJets_ee ->Fill(nsvjets, w[1]*w[4]);
			fHNbJets_ee  ->Fill(nbjets,  w[1]*w[4]);
			fHMET_ee     ->Fill(metpt,   w[1]*w[4]);
		}
		if (abs(evcat) == 13*13){
			fHNJets_mm   ->Fill(nj,      w[1]*w[4]);
			fHNSVJets_mm ->Fill(nsvjets, w[1]*w[4]);
			fHNbJets_mm  ->Fill(nbjets,  w[1]*w[4]);
			fHMET_mm     ->Fill(metpt,   w[1]*w[4]);
		}
		if (abs(evcat) == 11){
			fHNJets_e   ->Fill(nj,      w[1]*w[4]);
			fHNSVJets_e ->Fill(nsvjets, w[1]*w[4]);
			fHNbJets_e  ->Fill(nbjets,  w[1]*w[4]);
			fHMET_e     ->Fill(metpt,   w[1]*w[4]);
		}
		if (abs(evcat) == 13){
			fHNJets_m   ->Fill(nj,      w[1]*w[4]);
			fHNSVJets_m ->Fill(nsvjets, w[1]*w[4]);
			fHNbJets_m  ->Fill(nbjets,  w[1]*w[4]);
			fHMET_m     ->Fill(metpt,   w[1]*w[4]);
		}

		// First find all pairs and get their ranking in mass and deltar
		std::vector<SVLInfo> svl_pairs;
		for (int il = 0; il < nl; ++il){ // lepton loop
			for (size_t ij = 0; ij < svindices.size(); ++ij){ // sv loop
				int svind = svindices[ij];
				// Jet selection here
				SVLInfo svl_pairing;
				svl_pairing.jesweights[0] = 0;
				svl_pairing.jesweights[1] = 0;
				svl_pairing.jesweights[2] = 0;
				if(jpt[svind]       > 30.) svl_pairing.jesweights[0] = 1; // nominal
				if(jjesup[svind][0] > 30.) svl_pairing.jesweights[1] = 1; // jes up
				if(jjesdn[svind][0] > 30.) svl_pairing.jesweights[2] = 1; // jes down

				svl_pairing.bfragweights[0] = bwgt[svind][0];
				svl_pairing.bfragweights[1] = bwgt[svind][1];
				svl_pairing.bfragweights[2] = bwgt[svind][2];

				if(jpt[svind] > 30. || jjesup[svind][0] > 30. || jjesdn[svind][0] > 30.){
					int combcat = (il+1)*10 + (ij+1); // 10(20) + 1(2): 11, 21, 12, 22
					svl_pairing.counter = svl_pairs.size();
					svl_pairing.lepindex = il;
					svl_pairing.svindex = svind;
					svl_pairing.combcat = combcat;

					TLorentzVector p_lep, p_sv;
					p_lep.SetPtEtaPhiM(lpt[il], leta[il], lphi[il], 0.);
					p_sv.SetPtEtaPhiM(svpt[svind], sveta[svind],
									  svphi[svind], svmass[svind]);

					svl_pairing.svlmass = (p_lep + p_sv).M();
					svl_pairing.svldeltar = p_lep.DeltaR(p_sv);

					TLorentzVector p_lep_rot=RotateLepton(p_lep,isoObjects);
					svl_pairing.svlmass_rot = (p_lep_rot + p_sv).M();
					svl_pairing.svldeltar_rot = p_lep_rot.DeltaR(p_sv);

					svl_pairs.push_back(svl_pairing);
				}
			}
		}

		// Sort them according to mass and delta r
		std::vector<SVLInfo> svl_pairs_massranked = svl_pairs;
		std::sort (svl_pairs_massranked.begin(), svl_pairs_massranked.end(), compare_mass);
		std::vector<SVLInfo> svl_pairs_drranked = svl_pairs;
		std::sort (svl_pairs_drranked.begin(), svl_pairs_drranked.end(), compare_deltar);
		std::vector<SVLInfo> svl_pairs_massranked_rot = svl_pairs;
		std::sort (svl_pairs_massranked_rot.begin(), svl_pairs_massranked_rot.end(), compare_mass_rot);
		std::vector<SVLInfo> svl_pairs_drranked_rot = svl_pairs;
		std::sort (svl_pairs_drranked_rot.begin(), svl_pairs_drranked_rot.end(), compare_deltar_rot);

		// Now put the info in the tree
		fTNCombs = svl_pairs.size();
		for (size_t isvl = 0; isvl < svl_pairs.size(); ++isvl){
			SVLInfo svl = svl_pairs[isvl];
			fTSVLMass   = svl.svlmass;
			fTSVLDeltaR = svl.svldeltar;
			fTSVLMass_rot   = svl.svlmass_rot;
			fTSVLDeltaR_rot = svl.svldeltar_rot;
			fTCombCat   = svl.combcat;

			// Find the mass and dr ranks:
			for (size_t i = 0; i < svl_pairs.size(); ++i){
				if(svl_pairs_massranked[i].counter != isvl) continue;
				fTSVLMinMassRank = i+1;
			}
			for (size_t i = 0; i < svl_pairs.size(); ++i){
				if(svl_pairs_massranked_rot[i].counter != isvl) continue;
				fTSVLMinMassRank_rot = i+1;
			}
			for (size_t i = 0; i < svl_pairs.size(); ++i){
				if(svl_pairs_drranked[i].counter != isvl) continue;
				fTSVLDeltaRRank = i+1;
			}
			for (size_t i = 0; i < svl_pairs.size(); ++i){
			        if(svl_pairs_drranked_rot[i].counter != isvl) continue;
				fTSVLDeltaRRank_rot = i+1;
			}
			fTLPt          = lpt  [svl.lepindex];
			fTSVPt         = svpt [svl.svindex];
			fTSVLxy        = svlxy[svl.svindex];
			fTJPt          = jpt  [svl.svindex];
			fTJEta         = jeta [svl.svindex];
			fTSVNtrk       = svntk[svl.svindex];
			fTJESWeight[0] = svl.jesweights[0]; // nominal
			fTJESWeight[1] = svl.jesweights[1]; // jes up
			fTJESWeight[2] = svl.jesweights[2]; // jes down
			fTSVBfragWeight[0] = svl.bfragweights[0]; // nominal (Z2star_rbLEP_weight)
			fTSVBfragWeight[1] = svl.bfragweights[1]; // bfrag up (Z2star_rbLEPhard_weight)
			fTSVBfragWeight[2] = svl.bfragweights[2]; // bfrag dn (Z2star_rbLEPsoft_weight)

			// MC truth information on correct/wrong matchings
			fTCombInfo = -1;    // unmatched
			if( (lid[svl.lepindex] > 0 && bid[svl.svindex] == -5 ) || // el-/mu- / tbar/bbar
				(lid[svl.lepindex] < 0 && bid[svl.svindex] == 5  ) )  // el+/mu+ / t/b
				fTCombInfo = 1; // correct
			else if(
				(lid[svl.lepindex] > 0 && bid[svl.svindex] == 5  ) || // el-/mu- / t/b
				(lid[svl.lepindex] < 0 && bid[svl.svindex] == -5 ) )  // el+/mu+ / tbar/bbar
				fTCombInfo = 0; // wrong
			fSVLInfoTree->Fill();
		}
	}

	// Fill DY control histograms
	if(selectDYControlEvent()){
		TLorentzVector p_l1, p_l2;
		p_l1.SetPtEtaPhiM(lpt[0], leta[0], lphi[0], 0.);
		p_l2.SetPtEtaPhiM(lpt[1], leta[1], lphi[1], 0.);
		float mll = (p_l1+p_l2).M();
		if(abs(evcat) == 11*11*1000){
			fHDY_mll_ee->Fill(mll,   w[1]*w[4]);
			fHDY_met_ee->Fill(metpt, w[1]*w[4]);
		}
		if(abs(evcat) == 13*13*1000){
			fHDY_mll_mm->Fill(mll,   w[1]*w[4]);
			fHDY_met_mm->Fill(metpt, w[1]*w[4]);
		}
	}
}

void LxyTreeAnalysis::Loop(){
	if (fChain == 0) return;
	Long64_t nentries = fChain->GetEntriesFast();
	if( fMaxevents > 0) nentries = TMath::Min(fMaxevents,nentries);

	Long64_t nbytes = 0, nb = 0;
	for (Long64_t jentry=0; jentry<nentries; jentry++) {
		Long64_t ientry = LoadTree(jentry);
		if (ientry < 0) break;
		nb = fChain->GetEntry(jentry);
		nbytes += nb;

		if (jentry%500 == 0){
			printf("\r [ %3d/100 ]", int(100*float(jentry)/float(nentries)));
			std::cout << std::flush;
		}

		analyze();

	}
	std::cout << "\r [   done  ]" << std::endl;

}
#endif
