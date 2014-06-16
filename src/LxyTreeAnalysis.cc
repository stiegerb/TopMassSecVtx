#ifndef LxyTreeAnalysis_cxx
#define LxyTreeAnalysis_cxx
#include "UserCode/llvv_fwk/interface/LxyTreeAnalysis.h"

#include <TLorentzVector.h>
#include <iostream>

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
	fHEb1_emu = new TH1D("Eb1_emu", "E_b1 in EMu channel",
		                      100, 30., 500.); fHistos.push_back(fHEb1_emu);
	fHmlSv_mu = new TH1D("mlSv_mu", "Lepton/SecVtx Mass in Mu channel",
		                      100, 0., 150.); fHistos.push_back(fHmlSv_mu);

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

	if(abs(evcat) == 11*13 && nj > 3){
		// emu channel
		fHMinv2LeadTrk->Fill((p_track1+p_track2).M(), w[0]);

		// Just take the first jet for now, should check/fix this
		float E_b1 = jpt[0]*cosh(jeta[0]);
		fHEb1_emu->Fill(E_b1, w[0]);
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
