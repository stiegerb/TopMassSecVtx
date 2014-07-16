#ifndef LxyTreeAnalysis_cxx
#define LxyTreeAnalysis_cxx
#include "UserCode/llvv_fwk/interface/LxyTreeAnalysis.h"

#include <TLorentzVector.h>
#include <iostream>


//plot with ./scripts/runPlotter.py lxyplots/ -j test/topss2014/samples_noqcd.json


float pionmass = 0.1396;
float kaonmass = 0.4937;

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
	fHMinv2LeadTrk = new TH1D("Minv2LeadTrk", "Minv2LeadTrk (All channels)",
		100, 0., 10.); fHistos.push_back(fHMinv2LeadTrk);
	fHMinv2LeadTrk->SetXTitle("Inv. Mass of leading tracks in b-jet [GeV]");
	


	fHMinvJPsiTrk = new TH1D("MinvJPsiTrk", "MinvJPsiTrk (All channels)",
		100, 2., 4.); fHistos.push_back(fHMinvJPsiTrk);
	fHMinvJPsiTrk->SetXTitle("Inv. Mass of leading tracks J/Psi in b-jet [GeV]");
	
	

	fHMinvJPsiTrke = new TH1D("MinvJPsiTrke", "MinvJPsiTrke (All channels)",
		100,2.,4.); fHistos.push_back(fHMinvJPsiTrke);
	fHMinvJPsiTrke->SetXTitle("Inv. Mass of leading tracks J/Psi in b-jet [GeV], only electrons");

	

	fHMinvJPsiTrkmu = new TH1D("MinvJPsiTrkmu", "MinvJPsiTrkmu (All channels)", 
		100,2.,4.); fHistos.push_back(fHMinvJPsiTrkmu);
	fHMinvJPsiTrkmu->SetXTitle("Inv. Mass of leading tracks J/Psi in b-jet [GeV], only muons");


	
	fHMinvD0Trk = new TH1D("MinvD0Trk", "MinvD0Trk (EMu channel)",
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trk);
	fHMinvD0Trk->SetXTitle("Inv. Mass of leading tracks D0 in b-jet [GeV]");

	

	fHMinvD0Trkchargeselection = new TH1D("MinvD0Trkchargeselection", "MinvD0Trkchargeselection (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHMinvD0Trkchargeselection);
	fHMinvD0Trkchargeselection->SetXTitle("Inv. Mass of leading tracks D0 in b-jet [GeV], new");



	fHMinvDplusminusTrk = new TH1D("MinvDplusminusTrk", "MinvDplusminusTrk (EMu channel)",	
		100, 1.6, 2.2); fHistos.push_back(fHMinvDplusminusTrk);
	fHMinvDplusminusTrk->SetXTitle("Inv. Mass of leading tracks D0 in b-jet [GeV], new");



	fHMinvBTrkJPsiK = new TH1D("MinvBTrkJPsiK", "MinvBTrkJPsiK (EMu channel)",
		100, 4., 7.); fHistos.push_back(fHMinvBTrkJPsiK);
	fHMinvBTrkJPsiK->SetXTitle("Inv. Mass of leading tracks B in b-jet [GeV]");



	fHMinvBTrkD0 = new TH1D("MinvBTrkD0", "MinvBTrkD0 (EMu channel)",
		100, 4., 7.); fHistos.push_back(fHMinvBTrkD0);
	fHMinvBTrkD0->SetXTitle("Inv. Mass of leading tracks B in b-jet [GeV]");



	fHMinvBTrkD0chargeselection = new TH1D("MinvBTrkD0chargeselection", "MinvBTrkD0chargeselection (EMu channel)",
		100, 4., 7.); fHistos.push_back(fHMinvBTrkD0chargeselection);
	fHMinvBTrkD0chargeselection->SetXTitle("Inv. Mass of leading tracks B in b-jet [GeV], new");



	fHMinvBTrktotal = new TH1D("HMinvBTrktotal", "HMinvBTrktotal (EMu channel)",
		100, 4., 7.); fHistos.push_back(fHMinvBTrktotal);
	fHMinvBTrktotal->SetXTitle("Inv. Mass of leading tracks B in b-jet [GeV], new");



	fHMinvBTrktotalchargeselection = new TH1D("MinvBTrktotalchargeselection", "MinvBTrktotalchargeselection (EMu channel)",
		100, 4., 7.); fHistos.push_back(fHMinvBTrktotalchargeselection);
	fHMinvBTrktotalchargeselection->SetXTitle("Inv. Mass of leading tracks B in b-jet [GeV], new");



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

void LxyTreeAnalysis::fillJPsiHists(int jetindex){
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

			if (abs(pfid[i])==11){fHMinvJPsiTrke->Fill((p_track1+p_track2).M(), w[0]);}
			if (abs(pfid[i])==13){fHMinvJPsiTrkmu->Fill((p_track1+p_track2).M(), w[0]);}
			//leptonindex1=i;
			//leptonindex2=j;
			fHMinvJPsiTrk->Fill((p_track1+p_track2).M(), w[0]);
//---------------------------------------------------------------------------------------------------------- J/Psi + K
			TLorentzVector p_track3;

			if (fabs((p_track1+p_track2).M() - 3.1) < 0.1 )
			{	
				for (int k = 0; k < npf; ++k) // look for the K
				{
					if (pfjetidx[k]!=pfjetidx[j]){continue; }
					if (abs(pfid[k])!=211){continue; }
					if (pfpt[k]<2){continue; }

					//if (k==leptonindex1 or k==leptonindex2 ){continue; }
					p_track3.SetPtEtaPhiM(pfpt[k], pfeta[k], pfphi[k], kaonmass);
					fHMinvBTrkJPsiK->Fill((p_track1+p_track2+p_track3).M(), w[0]);
					fHMinvBTrktotalchargeselection->Fill((p_track1+p_track2+p_track3).M(), w[0]);
					fHMinvBTrktotal->Fill((p_track1+p_track2+p_track3).M(), w[0]);
				}
			}
		}
	}
}

void LxyTreeAnalysis::fillD0Hist(int jetindex, TH1D*& d0histo){
	d0histo->Fill(1.0);
}


void LxyTreeAnalysis::analyze(){
	// Called once per event
	FillPlots();

	
	//	for (int k = 0; k < nj; ++k)
	//	{
	//		if (jcsv[k]>maxcsv){ maxcsv = jcsv[k]; maxind=k; }
	//	}


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



	if(abs(evcat) == 11*13 || // emu
	   (abs(evcat) == 11*11 && metpt > 40.) || // ee
	   (abs(evcat) == 13*13 && metpt > 40.) ||
	   (abs(evcat) == 11 && nj > 3) ||
	   (abs(evcat) == 13 && nj > 3)  ){
//---------------------------------------------------------------------------------------------------------- J/Psi
		//int leptonindex1;
		//int leptonindex2;
		fillJPsiHists(maxind);
		// fillD0Hist(maxind, fHMinvD0Trk);
		// fillD0Hist(second_maxind, fHMinvD0SecondTrk);



//---------------------------------------------------------------------------------------------------------- D0



	int r[] = {0, 0};
	for (r[0] = 0; r[0] < npf; ++r[0])
	{
		if (pfjetidx[r[0]]==maxind)
			{break;}
	}


	for (r[1] = 0; r[1] < npf; ++r[1])
	{
		if (pfjetidx[r[1]]==second_maxind)
			{break;}
	}


	for (int n = 0; n < 2; ++n) // loop on the two jets
	{
		if (abs(pfid[r[n]]+pfid[r[n]+1]+pfid[r[n]+2])!=211) {continue; } // not all the same charge

		if (n == 0 && pfjetidx[r[n]+2]!=maxind ) continue;
		if (n == 1 && pfjetidx[r[n]+2]!=second_maxind ) continue;

		// permutations
		int p1[] = {r[n]+2, r[n]+2, r[n]+1};
		int p2[] = {r[n]+1, r[n], r[n]};
		int p3[] = {r[n], r[n]+1, r[n]+2};


		for (int p = 0; p < 3; ++p)
		{
			int pf1id=p1[p];
			int pf2id=p2[p];
			int pf3id=p3[p];
			
			if (abs(pfid[pf1id]+pfid[pf2id])==0){
				p_track1.SetPtEtaPhiM(pfpt[pf1id], pfeta[pf1id], pfphi[pf1id], pionmass);	// Calculate four vector
				p_track2.SetPtEtaPhiM(pfpt[pf2id], pfeta[pf2id], pfphi[pf2id], kaonmass);	
				p_track3.SetPtEtaPhiM(pfpt[pf3id], pfeta[pf3id], pfphi[pf3id], pionmass);

				fHMinvD0Trk->Fill((p_track1+p_track2).M(), w[0]);	
				fHMinvBTrkD0->Fill((p_track1+p_track2+p_track3).M(), w[0]);
				fHMinvBTrktotal->Fill((p_track1+p_track2+p_track3).M(), w[0]);

				if (abs(pfid[pf3id]+pfid[pf2id])==422) // second/third have same sign
				{
					// mass assumption was correct (second is Kaon)
					fHMinvD0Trkchargeselection->Fill((p_track1+p_track2).M(), w[0]);
					
					if (abs((p_track1+p_track2).M()-1.86)<0.06)
					{
						fHMinvBTrkD0chargeselection->Fill((p_track1+p_track2+p_track3).M(), w[0]);
						fHMinvBTrktotalchargeselection->Fill((p_track1+p_track2+p_track3).M(), w[0]);
					}
				}

				// switch masses:
				p_track1.SetPtEtaPhiM(pfpt[pf1id], pfeta[pf1id], pfphi[pf1id], kaonmass);	// Calculate four vector
				p_track2.SetPtEtaPhiM(pfpt[pf2id], pfeta[pf2id], pfphi[pf2id], pionmass);	

				fHMinvD0Trk->Fill((p_track1+p_track2).M(), w[0]);	
				fHMinvBTrkD0->Fill((p_track1+p_track2+p_track3).M(), w[0]);
				fHMinvBTrktotal->Fill((p_track1+p_track2+p_track3).M(), w[0]);
	
				if (abs(pfid[pf3id]+pfid[pf1id])==422) // first/third have same sign
				{  	
					// mass assumption was wrong (second is pion, first is kaon)
					fHMinvD0Trkchargeselection->Fill((p_track1+p_track2).M(), w[0]);
					
					if (abs((p_track1+p_track2).M()-1.86)<0.06)
					{
						fHMinvBTrkD0chargeselection->Fill((p_track1+p_track2+p_track3).M(), w[0]);
						fHMinvBTrktotalchargeselection->Fill((p_track1+p_track2+p_track3).M(), w[0]);
					}
				}
			}
		}


//------------------------------------------------------------------------------------------------------------------------- B+

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

					fHMinvDplusminusTrk->Fill((p_track1+p_track2+p_track3).M(), w[0]);

				}



				p_track1.SetPtEtaPhiM(pfpt[pf1id], pfeta[pf1id], pfphi[pf1id], pionmass);
				p_track2.SetPtEtaPhiM(pfpt[pf2id], pfeta[pf2id], pfphi[pf2id], kaonmass);

				if (pfid[pf3id]+pfid[pf2id]==0)
				{  				

					p_track3.SetPtEtaPhiM(pfpt[pf3id], pfeta[pf3id], pfphi[pf3id], pionmass);

					fHMinvDplusminusTrk->Fill((p_track1+p_track2+p_track3).M(), w[0]); 
				}


			}
		}
	}
		//if(abs(pfid[r+2]+pfid[r+1])==422)		{	p_track1.SetPtEtaPhiM(pfpt[r], pfeta[r], pfphi[r], kaonmass);	// Calculate four vector
		//											p_track2.SetPtEtaPhiM(pfpt[r+1], pfeta[r+1], pfphi[r+1], pionmass);	

		//											fHMinvD0Trk->Fill((p_track1+p_track2).M(), w[0]);						}




	//	for (int i = r; i < r+5; ++i)
	//	{	
	//		if (pfjetidx[i]!= maxind){continue; }  //select the first b-jet
	//		if (abs(pfid[i])!=211){continue; } //select a kaon or pion
	//		for (int j = i+1; j < r+5; ++j) //find another kaon or pion
	//				{
	//					if(pfjetidx[j]!=maxind){continue; } //select most probable b-jet
	//					if(pfid[j]*pfid[i]!=-211*211){continue; } 
	//					//TLorentzVector p_track1, p_track2; // Calculate four vector				
	//					p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], pionmass);// Calculate four vector
	//					p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], kaonmass);
	//																		
	//					if (p_track1.DeltaR(p_track2)>0.2){continue; }
	//															
	//					fHMinvD0Trk->Fill((p_track1+p_track2).M(), w[0]);
	//																					
	//					p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], kaonmass);// Calculate four vector
	//					p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], pionmass);
	//																
	//					if (p_track1.DeltaR(p_track2)>0.2){continue; }
	//					fHMinvD0Trk->Fill((p_track1+p_track2).M(), w[0]);
	//																}

	//							}







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
