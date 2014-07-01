#ifndef LxyTreeAnalysis_cxx
#define LxyTreeAnalysis_cxx
#include "UserCode/llvv_fwk/interface/LxyTreeAnalysis.h"

#include <TLorentzVector.h>
#include <iostream>

const float gMassK = 0.4937;
const float gMassPi = 0.1396;
const float gMassMu = 0.1057;

bool isOppositeSign(int id1, int id2){
	if(id1*id2 == -211*211) return true;
	if(id1*id2 == 11*211)   return true;
	if(id1*id2 == 13*211)   return true;
	if(id1*id2 == -13*13)   return true;
	if(id1*id2 == -11*13)   return true;
	if(id1*id2 == -11*11)   return true;
	return false;
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
}

void LxyTreeAnalysis::End(TFile *file){
	// Anything that has to be done once at the end
	file->cd();
	WritePlots();
	WriteHistos();
	file->Write();
	file->Close();
}

void LxyTreeAnalysis::BookHistos(){
	// Book all the histograms here
	fHMinv2LeadTrk = new TH1D("Minv2LeadTrk", "Minv2LeadTrk (EMu channel)",
		                      100, 0., 10.); fHistos.push_back(fHMinv2LeadTrk);
	fHMinv2LeadTrk->SetXTitle("Inv. Mass of leading tracks in b-jet [GeV]");
	fHDiTrkInvMass = new TH1D("DiTrkInvMass", "DiTrkInvMass (EMu channel)",
		                      100, 1.7, 2.); fHistos.push_back(fHDiTrkInvMass);
	fHDiTrkInvMass->SetXTitle("Track-track inv. Mass in b-jet [GeV]");

	fHDiMuInvMass = new TH1D("DiMuInvMass", "DiMuInvMass (EMu channel)",
		                      100, 2., 4.); fHistos.push_back(fHDiMuInvMass);
	fHDiMuInvMass->SetXTitle("Mu/mu inv. Mass in b-jet [GeV]");

	fHJPsiKInvMass = new TH1D("JPsiKInvMass", "JPsiKInvMass (EMu channel)",
		                      100, 4.5, 6.); fHistos.push_back(fHJPsiKInvMass);
	fHJPsiKInvMass->SetXTitle("Mu/mu/K inv. Mass in b-jet [GeV]");


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

void LxyTreeAnalysis::WriteHistos(){
	// Write all histos to file, then delete them
	std::vector<TH1*>::iterator h;
	for( h = fHistos.begin(); h != fHistos.end(); ++h){
		(*h)->Write((*h)->GetName());
		(*h)->Delete();
	}
}

void LxyTreeAnalysis::analyze(){
	// Called once per event
	FillPlots();

	TLorentzVector p_track1, p_track2;
	p_track1.SetPtEtaPhiM(pfpt[0], pfeta[0], pfphi[0], 0.);
	p_track2.SetPtEtaPhiM(pfpt[1], pfeta[1], pfphi[1], 0.);

	// Find best b-jet
	int btag_index(-1);
	float maxcsv(-1.);
	for (int i = 0; i < nj; ++i){
		if(jcsv[i] > maxcsv){
			maxcsv = jcsv[i];
			btag_index = i;
		}
	}

	if(abs(evcat) == 11*13 ){
		// emu channel

		if( btag_index >= 0 ){
			for (int i_trk = 0; i_trk < npf; ++i_trk){
				// Select tracks from best b-tag jet
				if( pfjetidx[i_trk] != btag_index ) continue;

				// Loop on second track
				for (int j_trk = i_trk+1; j_trk < npf; ++j_trk){
					if( pfjetidx[j_trk] != btag_index ) continue;

					// Charge selection
					if( !isOppositeSign(pfid[i_trk],pfid[j_trk]) ) continue;

					TLorentzVector p_trk1, p_trk2;

					// J/psi control plot
					if(pfid[i_trk]*pfid[j_trk] == -13*13){
						p_trk1.SetPtEtaPhiM(pfpt[i_trk], pfeta[i_trk], pfphi[i_trk], gMassMu);
						p_trk2.SetPtEtaPhiM(pfpt[j_trk], pfeta[j_trk], pfphi[j_trk], gMassMu);
						fHDiMuInvMass->Fill((p_trk1+p_trk2).M(), w[0]);

						// Find a third track if the first two gave something compatible with a J/psi
						if( fabs((p_trk1+p_trk2).M() - 3.1) < 0.1 ){
							for (int k_trk = 0; k_trk < npf; ++k_trk){
								// Select tracks from best b-tag jet
								if( pfjetidx[k_trk] != btag_index ) continue;

								// Exclude the two muons
								if( k_trk == i_trk || k_trk == j_trk ) continue;

								// pt cut > 2.0 GeV
								if( pfpt[k_trk] < 1.0 ) continue;

								TLorentzVector p_trk3;
								p_trk3.SetPtEtaPhiM(pfpt[k_trk], pfeta[k_trk], pfphi[k_trk], gMassK);

								fHJPsiKInvMass->Fill((p_trk1+p_trk2+p_trk3).M(), w[0]);
							}
						}
					}

					p_trk1.SetPtEtaPhiM(pfpt[i_trk], pfeta[i_trk], pfphi[i_trk], 0.);
					p_trk2.SetPtEtaPhiM(pfpt[j_trk], pfeta[j_trk], pfphi[j_trk], 0.);

					// Delta r cut
					if( p_trk1.DeltaR(p_trk2) > 0.3) continue;

					// pt cut / leading track selection
					// if( pfpt[i_trk] < 1.0 || pfpt[j_trk] < 1.0 ) continue;
					if( j_trk > 3 ) continue; // only look at first four tracks

					// Fill invariant mass
					// First mass hypothesis:
					p_trk1.SetPtEtaPhiM(pfpt[i_trk], pfeta[i_trk], pfphi[i_trk], gMassK);
					p_trk2.SetPtEtaPhiM(pfpt[j_trk], pfeta[j_trk], pfphi[j_trk], gMassPi);
					fHDiTrkInvMass->Fill((p_trk1+p_trk2).M(), w[0]);

					// Second mass hypothesis:
					p_trk1.SetPtEtaPhiM(pfpt[i_trk], pfeta[i_trk], pfphi[i_trk], gMassPi);
					p_trk2.SetPtEtaPhiM(pfpt[j_trk], pfeta[j_trk], pfphi[j_trk], gMassK);
					fHDiTrkInvMass->Fill((p_trk1+p_trk2).M(), w[0]);

				}
			}
		}




		fHMinv2LeadTrk->Fill((p_track1+p_track2).M(), w[0]);

		// Just take the first jet for now, should check/fix this
		float E_b1 = jpt[0]*cosh(jeta[0]);
		if(nj==2) fHEb1_emu->Fill(E_b1, w[0]);
	}

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

void LxyTreeAnalysis::Loop(){
	if (fChain == 0) return;

	Long64_t nentries = fChain->GetEntriesFast();
	if( fMaxevents > 0) nentries = TMath::Min(fMaxevents,nentries);

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
