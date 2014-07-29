#ifndef LxyTreeAnalysis_cxx
#define LxyTreeAnalysis_cxx
#include "UserCode/llvv_fwk/interface/LxyTreeAnalysis.h"

#include <TLorentzVector.h>
#include <iostream>


//plot with ./scripts/runPlotter.py lxyplots/ -j test/topss2014/samples_noqcd.json


float pionmass 			= 	0.1396;
float kaonmass 			= 	0.4937;
float electronmass		= 	0.00051;
float muonmass			=	105.66;

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
}

void LxyTreeAnalysis::End(TFile *file){
	// Anything that has to be done once at the end
	file->cd();
	WritePlots();
	WriteHistos();
	fCharmInfoTree->Write(fCharmInfoTree->GetName());
	file->Write();
	file->Close();
}

void LxyTreeAnalysis::BookHistos(){
	// Book all the histograms here
	fHMinv2LeadTrk = new TH1D("Minv2LeadTrk", "Minv2LeadTrk (All channels)",
		100, 0., 10.); fHistos.push_back(fHMinv2LeadTrk);
	fHMinv2LeadTrk->SetXTitle("Inv. Mass of in b-jet [GeV]");
	

	normal1 = new TH1D("normal1", "normal1 (All channels)",
		100, 2., 4.); fHistos.push_back(normal1);
	normal1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV]");


	normal2 = new TH1D("normal2", "normal2 (All channels)",
		100, 2., 4.); fHistos.push_back(normal2);
	normal2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV]");


	normal12 = new TH1D("normalqw", "normal12 (All channels)",
		100, 2., 4.); fHistos.push_back(normal12);
	normal12->SetXTitle("Inv. Mass of J/Psi in hardest two b-jets [GeV]");




	test1 = new TH1D("test1", "test1 (All channels)",
		100, 2., 4.); fHistos.push_back(test1);
	test1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV]");


	test2 = new TH1D("test2", "test2 (All channels)",
		100, 2., 4.); fHistos.push_back(test2);
	test2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV]");


	test12 = new TH1D("test12", "test12 (All channels)",
		100, 2., 4.); fHistos.push_back(test12);
	test12->SetXTitle("Inv. Mass of J/Psi in hardest two b-jets [GeV]");




	angle1 = new TH1D("angle1", "angle1 (All channels)",
		100, 0., 2.); fHistos.push_back(angle1);
	angle1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV]");


	angle2 = new TH1D("angle2", "angle2 (All channels)",
		100, 0., 2.); fHistos.push_back(angle2);
	angle2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV]");


	angle12 = new TH1D("angle12", "angle12 (All channels)",
		100, 0., 2.); fHistos.push_back(angle12);
	angle12->SetXTitle("Inv. Mass of J/Psi in hardest two b-jets [GeV]");




	fHMinvJPsiTrk1 = new TH1D("MinvJPsiTrk1", "MinvJPsiTrk1 (All channels)",
		100, 2., 4.); fHistos.push_back(fHMinvJPsiTrk1);
	fHMinvJPsiTrk1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV]");


	fHMinvJPsiTrk2 = new TH1D("MinvJPsiTrk2", "MinvJPsiTrk2 (All channels)",
		100, 2., 4.); fHistos.push_back(fHMinvJPsiTrk2);
	fHMinvJPsiTrk2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV]");


	fHMinvJPsiTrk12 = new TH1D("MinvJPsiTrk12", "MinvJPsiTrk12 (All channels)",
		100, 2., 4.); fHistos.push_back(fHMinvJPsiTrk12);
	fHMinvJPsiTrk12->SetXTitle("Inv. Mass of J/Psi in hardest two b-jets [GeV]");
	

	

	fHMinvJPsiTrke1 = new TH1D("MinvJPsiTrke1", "MinvJPsiTrke1 (All channels)",
		100,2.,4.); fHistos.push_back(fHMinvJPsiTrke1);
	fHMinvJPsiTrke1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV], only electrons");


	fHMinvJPsiTrke2 = new TH1D("MinvJPsiTrke2", "MinvJPsiTrke2 (All channels)",
		100,2.,4.); fHistos.push_back(fHMinvJPsiTrke2);
	fHMinvJPsiTrke2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV], only electrons");

	
	fHMinvJPsiTrke12 = new TH1D("MinvJPsiTrke12", "MinvJPsiTrke12 (All channels)",
		100,2.,4.); fHistos.push_back(fHMinvJPsiTrke12);
	fHMinvJPsiTrke12->SetXTitle("Inv. Mass of J/Psi in two hardest b-jets [GeV], only electrons");




	
	fHMinvJPsiTrkmu1 = new TH1D("MinvJPsiTrkmu1", "MinvJPsiTrkmu1 (All channels)",
		100,2.,4.); fHistos.push_back(fHMinvJPsiTrkmu1);
	fHMinvJPsiTrkmu1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV], only muons");


	fHMinvJPsiTrkmu2 = new TH1D("MinvJPsiTrkmu2", "MinvJPsiTrkmu2 (All channels)",
		100,2.,4.); fHistos.push_back(fHMinvJPsiTrkmu2);
	fHMinvJPsiTrkmu2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV], only muons");
	

	fHMinvJPsiTrkmu12 = new TH1D("MinvJPsiTrkmu12", "MinvJPsiTrkmu12 (All channels)", 
		100,2.,4.); fHistos.push_back(fHMinvJPsiTrkmu12);
	fHMinvJPsiTrkmu12->SetXTitle("Inv. Mass of J/Psi in hardest two b-jets [GeV], only muons");





	fHMinvD0Trk1 = new TH1D("MinvD0Trk1", "MinvD0Trk1 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trk1);
	fHMinvD0Trk1->SetXTitle("Inv. Mass of D0 in hardest b-jet [GeV]");


	fHMinvD0Trk2 = new TH1D("MinvD0Trk2", "MinvD0Trk2 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trk2);
	fHMinvD0Trk2->SetXTitle("Inv. Mass of D0 in second hardest b-jet [GeV]");


	fHMinvD0Trk12 = new TH1D("MinvD0Trk12", "MinvD0Trk12 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trk12);
	fHMinvD0Trk12->SetXTitle("Inv. Mass of D0 in two hardest b-jets [GeV]");



	

	fHMinvD0Trkchargeselection1 = new TH1D("MinvD0Trkchargeselection1", "MinvD0Trkchargeselection1 (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselection1);
	fHMinvD0Trkchargeselection1->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");


	fHMinvD0Trkchargeselection2 = new TH1D("MinvD0Trkchargeselection2", "MinvD0Trkchargeselection2 (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselection2);
	fHMinvD0Trkchargeselection2->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");


	fHMinvD0Trkchargeselection12 = new TH1D("MinvD0Trkchargeselection12", "MinvD0Trkchargeselection12 (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselection12);
	fHMinvD0Trkchargeselection12->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");





	fHcheckMinvD0Trk1 = new TH1D("checkMinvD0Trk1", "checkMinvD0Trk1 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHcheckMinvD0Trk1);
	fHcheckMinvD0Trk1->SetXTitle("Inv. Mass of D0 in hardest b-jet [GeV]");


	fHcheckMinvD0Trk2 = new TH1D("checkMinvD0Trk2", "checkMinvD0Trk2 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHcheckMinvD0Trk2);
	fHcheckMinvD0Trk2->SetXTitle("Inv. Mass of D0 in second hardest b-jet [GeV]");


	fHcheckMinvD0Trk12 = new TH1D("checkMinvD0Trk12", "checkMinvD0Trk12 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHcheckMinvD0Trk12);
	fHcheckMinvD0Trk12->SetXTitle("Inv. Mass of D0 in two hardest b-jets [GeV]");



	

	fHcheckMinvD0Trkchargeselection1 = new TH1D("checkMinvD0Trkchargeselection1", "checkMinvD0Trkchargeselection1 (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHcheckMinvD0Trkchargeselection1);
	fHcheckMinvD0Trkchargeselection1->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");


	fHcheckMinvD0Trkchargeselection2 = new TH1D("checkMinvD0Trkchargeselection2", "checkMinvD0Trkchargeselection2 (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHcheckMinvD0Trkchargeselection2);
	fHcheckMinvD0Trkchargeselection2->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");


	fHcheckMinvD0Trkchargeselection12 = new TH1D("checkMinvD0Trkchargeselection12", "checkMinvD0Trkchargeselection12 (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHcheckMinvD0Trkchargeselection12);
	fHcheckMinvD0Trkchargeselection12->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");





	fHMinvD0Trkchargeselectionmuon1 = new TH1D("MinvD0Trkchargeselectionmuon1", "MinvD0Trkchargeselectionmuon1 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselectionmuon1);
	fHMinvD0Trkchargeselectionmuon1->SetXTitle("Inv. Mass of D0 in hardest b-jet [GeV], CS, CWL");


	fHMinvD0Trkchargeselectionmuon2 = new TH1D("MinvD0Trkchargeselectionmuon2", "MinvD0Trkchargeselectionmuon2 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselectionmuon2);
	fHMinvD0Trkchargeselectionmuon2->SetXTitle("Inv. Mass of D0 in second hardest b-jet [GeV],CS, CWL");


	fHMinvD0Trkchargeselectionmuon12 = new TH1D("MinvD0Trkchargeselectionmuon12", "MinvD0Trkchargeselectionmuon12 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselectionmuon12);
	fHMinvD0Trkchargeselectionmuon12->SetXTitle("Inv. Mass of D0 in two hardest b-jets [GeV], CS, CWL");





	fHMinvD0Trkchargeselectionelectron1 = new TH1D("MinvD0Trkchargeselectionelectron1", "MinvD0Trkchargeselectionelectron1 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselectionelectron1);
	fHMinvD0Trkchargeselectionelectron1->SetXTitle("Inv. Mass of D0 in hardest b-jet [GeV], CS, CWL");


	fHMinvD0Trkchargeselectionelectron2 = new TH1D("MinvD0Trkchargeselectionelectron2", "MinvD0Trkchargeselectionelectron2 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselectionelectron2);
	fHMinvD0Trkchargeselectionelectron2->SetXTitle("Inv. Mass of D0 in second hardest b-jet [GeV],CS, CWL");


	fHMinvD0Trkchargeselectionelectron12 = new TH1D("MinvD0Trkchargeselectionelectron12", "MinvD0Trkchargeselectionelectron12 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselectionelectron12);
	fHMinvD0Trkchargeselectionelectron12->SetXTitle("Inv. Mass of D0 in two hardest b-jets [GeV], CS, CWL");




	fHMinvD0Trkchargeselectionlepton1 = new TH1D("MinvD0Trkchargeselectionlepton1", "MinvD0Trkchargeselectionlepton1 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselectionlepton1);
	fHMinvD0Trkchargeselectionlepton1->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS, CWL, e mu");


	fHMinvD0Trkchargeselectionlepton2 = new TH1D("MinvD0Trkchargeselectionlepton2", "MinvD0Trkchargeselectionlepton2 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselectionlepton2);
	fHMinvD0Trkchargeselectionlepton2->SetXTitle("Inv. Mass of D0 in b-jet [GeV],CS, CWL, e mu");


	fHMinvD0Trkchargeselectionlepton12 = new TH1D("MinvD0Trkchargeselectionlepton12", "MinvD0Trkchargeselectionlepton12 (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselectionlepton12);
	fHMinvD0Trkchargeselectionlepton12->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS, CWL, e mu");




	fHMinvDplusminusTrk1 = new TH1D("MinvDplusminusTrk1", "MinvDplusminusTrk1 (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHMinvDplusminusTrk1);
	fHMinvDplusminusTrk1->SetXTitle("Inv. Mass of D+- in b-jet [GeV]");


	fHMinvDplusminusTrk2 = new TH1D("MinvDplusminusTrk2", "MinvDplusminusTrk2 (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHMinvDplusminusTrk2);
	fHMinvDplusminusTrk2->SetXTitle("Inv. Mass of D+- in b-jet [GeV]");


	fHMinvDplusminusTrk12 = new TH1D("MinvDplusminusTrk12", "MinvDplusminusTrk12 (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHMinvDplusminusTrk12);
	fHMinvDplusminusTrk12->SetXTitle("Inv. Mass of D+- in b-jet [GeV]");




	fHEb1_emu = new TH1D("Eb1_emu", "E_b1 in EMu channel",
		100, 30., 500.); fHistos.push_back(fHEb1_emu);
	fHEb1_emu->SetXTitle("Energy of first b-jet [GeV]");



	fHmlSv_mu = new TH1D("mlSv_mu", "Lepton/SecVtx Mass in Mu channel",
		100, 0., 150.); fHistos.push_back(fHmlSv_mu);
	fHmlSv_mu->SetXTitle("Lepton/SecVtx mass [GeV]");

	// Call Sumw2() for all of them
	std::vector<TH1*>::iterator h;
	for(h = fHistos.begin(); h != fHistos.end(); ++h){
		(*h)->Sumw2();
	}
}

void LxyTreeAnalysis::BookCharmTree(){
	fCharmInfoTree = new TTree("CharmInfo", "Charm Info Tree");
	fCharmInfoTree->Branch("CandType",     &fTCandType,     "CandType/I");
	fCharmInfoTree->Branch("CandMass",     &fTCandMass,     "CandMass/F");
	fCharmInfoTree->Branch("CandPt",       &fTCandPt,       "CandPt/F");
	fCharmInfoTree->Branch("CandPtRel",    &fTCandPtRel,    "CandPtRel/F");
	fCharmInfoTree->Branch("CandDeltaR",   &fTCandDeltaR,   "CandDeltaR/F");
	fCharmInfoTree->Branch("JetPt",        &fTJetPt,        "JetPt/F");
	fCharmInfoTree->Branch("SumPtCharged", &fTSumPtCharged, "SumPtCharged/F");
}

void LxyTreeAnalysis::ResetCharmTree(){
	fTCandType     = -99;
	fTCandMass     = -99.99;
	fTCandPt       = -99.99;
	fTCandPtRel    = -99.99;
	fTCandDeltaR   = -99.99;
	fTJetPt        = -99.99;
	fTSumPtCharged = -99.99;
}

void LxyTreeAnalysis::FillCharmTree(int type, int jetindex,
	                                int ind1, float mass1,
	                                int ind2, float mass2){
	// Check that indices make sense
	if(jetindex < 0 || ind1 < 0 || ind2 < 0) return;
	if(jetindex >= nj || ind1 >= npf || ind2 >= npf) return;

	fTCandType = type;
	TLorentzVector p_track1, p_track2, p_cand, p_jet;
	p_track1.SetPtEtaPhiM(pfpt[ind1], pfeta[ind1], pfphi[ind1], mass1);
	p_track2.SetPtEtaPhiM(pfpt[ind2], pfeta[ind2], pfphi[ind2], mass1);
	p_cand = p_track1+p_track2;
	p_jet.SetPtEtaPhiM(jpt[jetindex], jeta[jetindex], jphi[jetindex], 0.);

	fTCandMass     = p_cand.M();
	fTCandPt       = p_cand.Pt();

	// TLorentzVector p_cand_boosted = p_cand;
	// p_cand_boosted.Boost(p_jet.BoostVector());
	// fTCandPtRel    = p_cand_boosted.Pt(); // FIXME?
	fTCandPtRel    = fTCandPt/jpt[jetindex]; // Placeholder

	fTCandDeltaR   = p_cand.DeltaR(p_jet);
	fTJetPt        = jpt[jetindex];
	fTSumPtCharged = 0.;
	for (int i = 0; i < npf; ++i){
		if (pfjetidx[i] != jetindex) continue;
		fTSumPtCharged += pfpt[i];
	}
	fCharmInfoTree->Fill();
	return;
}

void LxyTreeAnalysis::WriteHistos(){
	// Write all histos to file, then delete them
	std::vector<TH1*>::iterator h;
	for( h = fHistos.begin(); h != fHistos.end(); ++h){
		(*h)->Write((*h)->GetName());
		(*h)->Delete();
	}
}

void LxyTreeAnalysis::fillJPsiHists(int jetindex, TH1D*& a, TH1D*& b, TH1D*& c//, TH1D*& d, TH1D*& e, TH1D*& f
	){
	
float maxcsv = -1.;
int maxind=-1;
float second_max=-1.0;
int second_maxind=-1;

	for(int k = 0; k < nj; k++){
	    // use >= n not just > as max and second_max can hav same value. Ex:{1,2,3,3}   
		if(jcsv[k] >= maxcsv){  
			second_max=maxcsv;
			maxcsv=jcsv[k];   
			maxind=k;
			second_maxind=maxind;       
		}
		else if(jcsv[k] > second_max){
			second_max=jcsv[k];
			second_maxind=k;
		}
	}


	TLorentzVector p_track1, p_track2;
				
			for (int i = 0; i < npf; ++i)
			{	
				if (pfjetidx[i]!= jetindex){continue; }  //select the most probable b-jet
				if (abs(pfid[i])!=13 && abs(pfid[i]) != 11 ){continue; } //select a muon or electron
				for (int j = 0; j < npf; ++j) //find another muon or electron
				{
					if(pfjetidx[j]!=pfjetidx[i]){continue; } //select the most probable b-jet
					if(pfid[j]*pfid[i]!=-169 && pfid[j]*pfid[i]!=-121){continue; } // let both electrons or muons have opposite charge
					 // Calculate four vector
					float trackmass = 0.105;
					if(abs(pfid[j]*pfid[i]) == 121){ trackmass = 0.; }
					p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], trackmass);
					p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], trackmass);

					if (abs(pfid[i])==11){a->	Fill((p_track1+p_track2).M(), w[0]);
												// FillCharmTree(443, maxind, i, electronmass, j, electronmass);	
												// FillCharmTree(443, second_maxind, i, electronmass, j, electronmass);	
												}
					if (abs(pfid[i])==13){b->	Fill((p_track1+p_track2).M(), w[0]);
												// FillCharmTree(443, maxind, i, muonmass, j, muonmass);
												// FillCharmTree(443, second_maxind, i, muonmass, j, muonmass);	
												}
					//leptonindex1=i;
					//leptonindex2=j;
					c->Fill((p_track1+p_track2).M(), w[0]);
					

			//---------------------------------------------------------------------------------------------------------- J/Psi + K
					// TLorentzVector p_track3; 

					// if (fabs((p_track1+p_track2).M() - 3.1) < 0.1 )
					// {	
					// 	for (int k = 0; k < npf; ++k) // look for the K
					// 	{
					// 		if (pfjetidx[k]!=pfjetidx[j]){continue; }
					// 		if (abs(pfid[k])!=211){continue; }
					// 		if (pfpt[k]<2){continue; }

					// 		//if (k==leptonindex1 or k==leptonindex2 ){continue; }
					// 		p_track3.SetPtEtaPhiM(pfpt[k], pfeta[k], pfphi[k], kaonmass);
					// 		d->Fill((p_track1+p_track2+p_track3).M(), w[0]);
					// 		e->Fill((p_track1+p_track2+p_track3).M(), w[0]);
					// 		f->Fill((p_track1+p_track2+p_track3).M(), w[0]);
					// 	}
					// }
				}
			}
		}
		




void LxyTreeAnalysis::fillMuD0Hists(int jetindex, TH1D*& histo, TH1D*& histo2, float ptmin, float maxdr, int lepflav){
	TLorentzVector p_track1, p_track2, p_track3;

	for (int i = 0; i < npf; ++i)
	{
		if(pfjetidx[i] != jetindex) continue;
		if(pfpt[i] < ptmin) continue;
		if(abs(pfid[i]) < 211) continue;

		for (int j = i+1; j < npf; ++j)
		{
			if(pfjetidx[j] != jetindex) continue;
			if(pfpt[j] < ptmin) continue;
			if(abs(pfid[j]) < 211) continue;

			if(pfid[i]*pfid[j] > 0) continue;

			// found a pair of opposite sign pions
			p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], pionmass);	// Calculate four vector
			p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], kaonmass);

			if(p_track1.DeltaR(p_track2) > maxdr) continue;


			histo->Fill((p_track1+p_track2).M());
			// FillCharmTree(421, jetindex, i, pionmass, j, kaonmass);

			for (int k = 0; k < npf; ++k)
			{
				if(pfjetidx[k] != jetindex) continue;
				if(pfpt[k] < ptmin) continue;
				if(abs(pfid[k]) != lepflav) continue; // will exclude i and j also

				if( ( pfid[k] == lepflav && pfid[j] == -211 )  || ( pfid[k] == -lepflav && pfid[j] == 211 ) ) // mu- K-
				{
					histo2->Fill((p_track1+p_track2).M());
				}
				else{
					p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], kaonmass);	// Calculate four vector
					p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], pionmass);
					histo2->Fill((p_track1+p_track2).M());
				}
			}
		}
	}
}



// g=fHMinvD0Trk
// l=fHMinvD0Trk
// o=fHMinvD0Trkchargeselection


void LxyTreeAnalysis::fillD0Hists(int jetindex, TH1D*& g, TH1D*& o, TH1D*& q, TH1D*& s, TH1D*& v, TH1D*& normal, TH1D*& c)//, TH1D*& test)
{

float maxcsv = -1.;
int maxind=-1;
float second_max=-1.0;
int second_maxind=-1;

	for(int k = 0; k < nj; k++){
	    // use >= n not just > as max and second_max can hav same value. Ex:{1,2,3,3}   
		if(jcsv[k] >= maxcsv){  
			second_max=maxcsv;
			maxcsv=jcsv[k];   
			maxind=k;
			second_maxind=maxind;       
		}
		else if(jcsv[k] > second_max){
			second_max=jcsv[k];
			second_maxind=k;
		}
	}


	TLorentzVector p_track1, p_track2, p_track3;
	int ev=0;
	int r = 0;
	for (r = 0; r < npf; ++r)
	{
		if (pfjetidx[r]==jetindex)
			{break;}
	}

for (int i = r; i < r+5; ++i)
		{	
			if (pfjetidx[i]!= jetindex){continue; }  //select the first b-jet
			if (abs(pfid[i])!=211){continue; } //select a kaon or pion
			for (int j = i+1; j < r+5; ++j) //find another kaon or pion
					{
						if(pfjetidx[j]!=jetindex){continue; } //select most probable b-jet
						if(pfid[j]*pfid[i]!=-211*211){continue; } 
						//TLorentzVector p_track1, p_track2; // Calculate four vector			
				
						p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], pionmass);// Calculate four vector
						p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], kaonmass);
																			
						if (p_track1.DeltaR(p_track2)>0.2){continue; }
																
						normal->Fill((p_track1+p_track2).M(), w[0]);
																						
						p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], kaonmass);// Calculate four vector
						p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], pionmass);
																	
						if (p_track1.DeltaR(p_track2)>0.2){continue; }

						normal->Fill((p_track1+p_track2).M(), w[0]);

					}
		}
						

// permutations
int p1[] = {r+2, 	r+2, 	r+1};
int p2[] = {r+1, 	r, 		r};
int p3[] = {r, 		r+1, 	r+2};	

if (pfjetidx[r+2]!=jetindex ) {return;}



	for (int p = 0; p < 3; ++p)
	{
		int pf1id=p1[p];
		int pf2id=p2[p];
		int pf3id=p3[p];
	
	
		
		if (pfid[pf1id]*pfid[pf2id]!=-44521) continue;
	
		p_track1.SetPtEtaPhiM(pfpt[pf1id], pfeta[pf1id], pfphi[pf1id], pionmass);	// Calculate four vector
		p_track2.SetPtEtaPhiM(pfpt[pf2id], pfeta[pf2id], pfphi[pf2id], kaonmass);	

		g->Fill((p_track1+p_track2).M(), w[0]);	
		// FillCharmTree(421, maxind, p1[p], pionmass, p2[p], kaonmass);
		// FillCharmTree(421, second_maxind, p1[p], pionmass, p2[p], kaonmass);



		std::vector<int> event;
		std::vector<int> instance;

		if (abs(pfid[pf3id]+pfid[pf2id])==422) // second/third have same sign
		{

				// int i=0;

				if ((p_track1+p_track2).M()>1.8 && (p_track1+p_track2).M()<1.92){

					c->Fill((p_track1.DeltaR(p_track2), w[0]));


					// event.push_back(event);
					// event.push_back(event);
					instance.push_back(pf1id);
					instance.push_back(pf2id);
				
		 		// 	int peak[];

		 		// 	peak[i]=r;
		 		// 	peak[i+1]=r+1;
		 		// 	i=i+2;
		 		// 	peak

					// }

					// cout peak
				// mass assumption was correct (second is Kaon)

				}	

			// for (size_t v = 0;  v < instance.size(); ++v)
			// {	
				// int a = instance[v];
				// int b = instance[v+1];
			// p_track1.SetPtEtaPhiM(pfpt[a], pfeta[a], pfphi[a], pionmass);	// Calculate four vector
			//p_track2.SetPtEtaPhiM(pfpt[b], pfeta[b], pfphi[b], kaonmass);
			//test->Fill((p_track1+p_track2).M(), w[0]);
			// 	}

			o->Fill((p_track1+p_track2).M(), w[0]);
		}

		for (int t = 0; t < npf; ++t)
		{ 
			if (pfjetidx[t]!=jetindex) continue;
			if (t == pf1id) continue;
			if (t == pf2id) continue;

			if (abs(pfid[t]) != 13 && abs(pfid[t]) != 11) continue;

			if (pfid[pf2id]/abs(pfid[pf2id])==pfid[t]/-13)
			{
				q->Fill((p_track1+p_track2).M(), w[0]);
				s->Fill((p_track1+p_track2).M(), w[0]);
			}

			if (pfid[pf2id]/abs(pfid[pf2id])==pfid[t]/-11)
			{
				v->Fill((p_track1+p_track2).M(), w[0]);
				s->Fill((p_track1+p_track2).M(), w[0]);
			}
		
		}
	}
	ev=ev+1;
}				
							
						
						
void LxyTreeAnalysis::fillDplusminusHists(int jetindex, TH1D*& s){
	TLorentzVector p_track1, p_track2, p_track3;

	float maxcsv = -1.;
	int maxind=-1;
	float second_max=-1.0;
	int second_maxind=-1;

	for(int k = 0; k < nj; k++){
	    // use >= n not just > as max and second_max can hav same value. Ex:{1,2,3,3}   
		if(jcsv[k] >= maxcsv){  
			second_max=maxcsv;
			maxcsv=jcsv[k];   
			maxind=k;
			second_maxind=maxind;       
		}
		else if(jcsv[k] > second_max){
			second_max=jcsv[k];
			second_maxind=k;
		}
	}

	int r = 0;
	for (r = 0; r < npf; ++r)
	{
		if (pfjetidx[r]==jetindex)
			{break;}
	}

	// permutations
	int p1[] = {r+2, r+2, r+1};
	int p2[] = {r+1, r, r};
	int p3[] = {r, r+1, r+2};	


		if (abs(pfid[r]+pfid[r+1]+pfid[r+2])!=211) {return; } // not all the same charge

		if (pfjetidx[r+2]!=jetindex ){return; }

	for (int p = 0; p < 3; ++p)
		{
			int pf1id=p1[p];
			int pf2id=p2[p];
			int pf3id=p3[p];

			if (abs(pfid[pf1id]+pfid[pf2id])==0)		{
				p_track1.SetPtEtaPhiM(pfpt[pf1id], pfeta[pf1id], pfphi[pf1id], kaonmass);	// Calculate four vector
				p_track2.SetPtEtaPhiM(pfpt[pf2id], pfeta[pf2id], pfphi[pf2id], pionmass);	


				if (abs(pfid[pf3id]+pfid[pf2id])==422)
				{
					p_track3.SetPtEtaPhiM(pfpt[pf3id], pfeta[pf3id], pfphi[pf3id], pionmass);

					s->Fill((p_track1+p_track2+p_track3).M(), w[0]);
					// FillCharmTree(411, second_maxind, p1[p], kaonmass, p2[p], pionmass);

				}



				p_track1.SetPtEtaPhiM(pfpt[pf1id], pfeta[pf1id], pfphi[pf1id], pionmass);
				p_track2.SetPtEtaPhiM(pfpt[pf2id], pfeta[pf2id], pfphi[pf2id], kaonmass);

				if (pfid[pf3id]+pfid[pf2id]==0)
				{  				

					p_track3.SetPtEtaPhiM(pfpt[pf3id], pfeta[pf3id], pfphi[pf3id], pionmass);

					s->Fill((p_track1+p_track2+p_track3).M(), w[0]); 
					// FillCharmTree(421, second_maxind, p1[p], pionmass, p2[p], kaonmass);
				}


			}
		}
	}






void LxyTreeAnalysis::analyze(){
	// Called once per event
	FillPlots();
	ResetCharmTree();

	float maxcsv = -1.;
	int maxind=-1;
	float second_max=-1.0;
	int second_maxind=-1;

	for(int k = 0; k < nj; k++){
	    // use >= n not just > as max and second_max can hav same value. Ex:{1,2,3,3}   
		if(jcsv[k] >= maxcsv){  
			second_max=maxcsv;
			maxcsv=jcsv[k];   
			maxind=k;
			second_maxind=maxind;       
		}
		else if(jcsv[k] > second_max){
			second_max=jcsv[k];
			second_maxind=k;
		}
	}





	TLorentzVector p_track1, p_track2, p_track3;



	if 		(abs(evcat) == 11*13 || // emu
			(abs(evcat) == 11*11 && metpt > 40.) || // ee
			(abs(evcat) == 13*13 && metpt > 40.) || // mumu
			(abs(evcat) == 11 && nj > 3) ||			// singleelectron
			(abs(evcat) == 13 && nj > 3)  ){		// singlemuon
//---------------------------------------------------------------------------------------------------------- J/Psi ( + K)
//int leptonindex1;
//int leptonindex2;
fillJPsiHists(maxind,        fHMinvJPsiTrke1, 	fHMinvJPsiTrkmu1, 	fHMinvJPsiTrk1);
fillJPsiHists(second_maxind, fHMinvJPsiTrke2, 	fHMinvJPsiTrkmu2, 	fHMinvJPsiTrk2);
fillJPsiHists(maxind,        fHMinvJPsiTrke12, 	fHMinvJPsiTrkmu12, 	fHMinvJPsiTrk12);
fillJPsiHists(second_maxind, fHMinvJPsiTrke12, 	fHMinvJPsiTrkmu12, 	fHMinvJPsiTrk12);




//---------------------------------------------------------------------------------------------------------- D0
fillD0Hists(maxind, 		fHMinvD0Trk1, 	 	fHMinvD0Trkchargeselection1, 	fHMinvD0Trkchargeselectionmuon1, 	fHMinvD0Trkchargeselectionlepton1, 	fHMinvD0Trkchargeselectionelectron1, 	normal1,	angle1);//, 	test1); 
fillD0Hists(second_maxind, 	fHMinvD0Trk2, 		fHMinvD0Trkchargeselection2, 	fHMinvD0Trkchargeselectionmuon2,	fHMinvD0Trkchargeselectionlepton2,	fHMinvD0Trkchargeselectionelectron2, 	normal2,	angle2);//, 	test2);
fillD0Hists(maxind, 		fHMinvD0Trk12,	 	fHMinvD0Trkchargeselection12, 	fHMinvD0Trkchargeselectionmuon12,	fHMinvD0Trkchargeselectionlepton12,	fHMinvD0Trkchargeselectionelectron12, 	normal12,	angle12);//,	test12);	
fillD0Hists(second_maxind, 	fHMinvD0Trk12, 	 	fHMinvD0Trkchargeselection12, 	fHMinvD0Trkchargeselectionmuon12,	fHMinvD0Trkchargeselectionlepton12,	fHMinvD0Trkchargeselectionelectron12, 	normal12, 	angle12);//,	test12);


fillMuD0Hists(maxind,        fHcheckMinvD0Trk1, 		fHcheckMinvD0Trkchargeselection1, 	1.0, 	0.5);
fillMuD0Hists(second_maxind, fHcheckMinvD0Trk2, 		fHcheckMinvD0Trkchargeselection2, 	1.0, 	0.5);
fillMuD0Hists(maxind,        fHcheckMinvD0Trk12, 		fHcheckMinvD0Trkchargeselection12, 	1.0, 	0.5);
fillMuD0Hists(second_maxind, fHcheckMinvD0Trk12, 		fHcheckMinvD0Trkchargeselection12, 	1.0, 	0.5);

//------------------------------------------------------------------------------------------------------------------------- B+

fillDplusminusHists(maxind,fHMinvDplusminusTrk1);
fillDplusminusHists(second_maxind,fHMinvDplusminusTrk2);
fillDplusminusHists(maxind,fHMinvDplusminusTrk12);
fillDplusminusHists(second_maxind,fHMinvDplusminusTrk12);


	//----------------------------------------------------------------------------------------------------------  Lead ions
	// emu channel
	//TLorentzVector p_track1, p_track2;
	p_track1.SetPtEtaPhiM(pfpt[0], pfeta[0], pfphi[0], 0.);
	p_track2.SetPtEtaPhiM(pfpt[1], pfeta[1], pfphi[1], 0.);
	fHMinv2LeadTrk->Fill((p_track1+p_track2).M(), w[0]);



		// Just take the first jet for now, should check/fix this
	float E_b1 = jpt[0]*cosh(jeta[0]);
	if(nj==2) fHEb1_emu->Fill(E_b1, w[0]);
	

	if(abs(evcat) == 13 && metpt > 30. && svlxy[0] > 0. && nj > 3){
		// mu channel
		// Just take first lepton and first sec vtx now
		// Should ask them to be close by
		TLorentzVector p_secvtx, p_mu;
		p_secvtx.SetPtEtaPhiM(svpt[0], sveta[0], svphi[0], 0.);
		p_mu.SetPtEtaPhiM(lpt[0], leta[0], lphi[0], 0.);
		fHmlSv_mu->Fill((p_secvtx+p_mu).M(), w[0]);
	}
}

}

void LxyTreeAnalysis::Loop(){
	if (fChain == 0) return;

	Long64_t nentries = fChain->GetEntriesFast();

	Long64_t nbytes = 0, nb = 0;
	for (Long64_t jentry=0; jentry<nentries;jentry++) {
		Long64_t ientry = LoadTree(jentry);
		if (ientry < 0) break;
		nb = fChain->GetEntry(jentry);   nbytes += nb;

		if (jentry%500 == 0){
			printf("\r [ %3d/100 ]", int(100*float(jentry)/float(nentries)));
			std::cout << std::flush;
		}

		// std::cout << jentry << "\t" << event << std::endl;
		analyze();

	}
	std::cout << "\r [   done  ]" << std::endl;
}

#endif
