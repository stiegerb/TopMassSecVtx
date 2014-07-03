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

	fHmlSv_emu_deltar = new TH1D("mlSv_emu_deltar", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar);
	fHmlSv_emu_deltar->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_deltar_correct = new TH1D("mlSv_emu_deltar_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_correct);
	fHmlSv_emu_deltar_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_deltar_wrong = new TH1D("mlSv_emu_deltar_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_wrong);
	fHmlSv_emu_deltar_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlSv_emu_deltar_ntr2 = new TH1D("mlSv_emu_deltar_ntr2", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_ntr2);
	fHmlSv_emu_deltar_ntr2->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_deltar_ntr2_correct = new TH1D("mlSv_emu_deltar_ntr2_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_ntr2_correct);
	fHmlSv_emu_deltar_ntr2_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_deltar_ntr2_wrong = new TH1D("mlSv_emu_deltar_ntr2_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_ntr2_wrong);
	fHmlSv_emu_deltar_ntr2_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlSv_emu_deltar_ntr3 = new TH1D("mlSv_emu_deltar_ntr3", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_ntr3);
	fHmlSv_emu_deltar_ntr3->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_deltar_ntr3_correct = new TH1D("mlSv_emu_deltar_ntr3_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_ntr3_correct);
	fHmlSv_emu_deltar_ntr3_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_deltar_ntr3_wrong = new TH1D("mlSv_emu_deltar_ntr3_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_ntr3_wrong);
	fHmlSv_emu_deltar_ntr3_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlSv_emu_deltar_ntr4 = new TH1D("mlSv_emu_deltar_ntr4", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_ntr4);
	fHmlSv_emu_deltar_ntr4->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlSv_emu_deltar_ntr4_correct = new TH1D("mlSv_emu_deltar_ntr4_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_ntr4_correct);
	fHmlSv_emu_deltar_ntr4_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_deltar_ntr4_wrong = new TH1D("mlSv_emu_deltar_ntr4_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_deltar_ntr4_wrong);
	fHmlSv_emu_deltar_ntr4_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");

// min mass method


	fHmlSv_emu_minmass = new TH1D("mlSv_emu_minmass", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass);
	fHmlSv_emu_minmass->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_minmass_correct = new TH1D("mlSv_emu_minmass_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_correct);
	fHmlSv_emu_minmass_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_minmass_wrong = new TH1D("mlSv_emu_minmass_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_wrong);
	fHmlSv_emu_minmass_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlSv_emu_minmass_ntr2 = new TH1D("mlSv_emu_minmass_ntr2", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_ntr2);
	fHmlSv_emu_minmass_ntr2->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_minmass_ntr2_correct = new TH1D("mlSv_emu_minmass_ntr2_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_ntr2_correct);
	fHmlSv_emu_minmass_ntr2_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_minmass_ntr2_wrong = new TH1D("mlSv_emu_minmass_ntr2_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_ntr2_wrong);
	fHmlSv_emu_minmass_ntr2_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlSv_emu_minmass_ntr3 = new TH1D("mlSv_emu_minmass_ntr3", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_ntr3);
	fHmlSv_emu_minmass_ntr3->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_minmass_ntr3_correct = new TH1D("mlSv_emu_minmass_ntr3_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_ntr3_correct);
	fHmlSv_emu_minmass_ntr3_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_minmass_ntr3_wrong = new TH1D("mlSv_emu_minmass_ntr3_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_ntr3_wrong);
	fHmlSv_emu_minmass_ntr3_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlSv_emu_minmass_ntr4 = new TH1D("mlSv_emu_minmass_ntr4", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_ntr4);
	fHmlSv_emu_minmass_ntr4->SetXTitle("Lepton/SecVtx malss [GeV]");

	fHmlSv_emu_minmass_ntr4_correct = new TH1D("mlSv_emu_minmass_ntr4_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_ntr4_correct);
	fHmlSv_emu_minmass_ntr4_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlSv_emu_minmass_ntr4_wrong = new TH1D("mlSv_emu_minmass_ntr4_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlSv_emu_minmass_ntr4_wrong);
	fHmlSv_emu_minmass_ntr4_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");
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

	std::vector <int> indices(2,-1);
        float lxymax1(0), lxymax2(0);
	
	for( int i=0; i < nj; i++){
		if(svlxy[i]>0){
			if(svlxyerr[i]!=0){
				if(svlxy[i]/svlxyerr[i]>lxymax1) {
					lxymax2=lxymax1;
					indices[1]=indices[0];
					lxymax1=svlxy[i]/svlxyerr[i];
					indices[0]=i;
				}		
		           	else if (svlxy[i]/svlxyerr[i]>lxymax2) {
					lxymax2=svlxy[i]/svlxyerr[i];
					indices[1]=i;
				}
			}
		}
        }
     if(indices[1]<0) indices.pop_back();
     if(indices[0]<0) indices.pop_back();
     bool check_secv(indices.size());
 
   //if (svlxy[i]>0){
//			indices.push_back(i);
//			check_secv=1;
//		}
//	}

	if(abs(evcat) == 11*13  && check_secv && nj > 1 ){
		// emu channel
		// inv.m of l and correct sec.v. (deltar and minmass methods)
		TLorentzVector p_secvtx1, p_secvtx2, p_secvtx1m, p_secvtx2m, p_l;		
		p_l.SetPtEtaPhiM(lpt[0], leta[0], lphi[0], 0.);	
		p_secvtx1.SetPtEtaPhiM(svpt[indices[0]], sveta[indices[0]], svphi[indices[0]], svmass[indices[0]]);
		p_secvtx1m.SetPtEtaPhiM(svpt[indices[0]], sveta[indices[0]], svphi[indices[0]], svmass[indices[0]]);
		int index_for_correct=indices[0];
		int index_for_correct_m=indices[0];
	
	for (unsigned int iii=1; iii<indices.size(); iii++){
				p_secvtx2.SetPtEtaPhiM(svpt[indices[iii]], sveta[indices[iii]], svphi[indices[iii]], svmass[indices[iii]]);
				p_secvtx2m.SetPtEtaPhiM(svpt[indices[iii]], sveta[indices[iii]], svphi[indices[iii]], svmass[indices[iii]]);				
				if(p_secvtx1.DeltaR(p_l) > p_secvtx2.DeltaR(p_l)){
					p_secvtx1=p_secvtx2;
					index_for_correct=indices[iii];
				}
				if((p_secvtx1m+p_l).M() > (p_secvtx2m+p_l).M()){
					p_secvtx1m=p_secvtx2m;
					index_for_correct_m=indices[iii];
				}
	
		}

		fHmlSv_emu_deltar->Fill((p_secvtx1+p_l).M(), w[0]);
		if (svntk[index_for_correct] ==2){fHmlSv_emu_deltar_ntr2->Fill((p_secvtx1+p_l).M(), w[0]);}
		if (svntk[index_for_correct] ==3){fHmlSv_emu_deltar_ntr3->Fill((p_secvtx1+p_l).M(), w[0]);}
		if (svntk[index_for_correct] > 3){fHmlSv_emu_deltar_ntr4->Fill((p_secvtx1+p_l).M(), w[0]);}

		fHmlSv_emu_minmass->Fill((p_secvtx1m+p_l).M(), w[0]);
		if (svntk[index_for_correct_m] ==2){fHmlSv_emu_minmass_ntr2->Fill((p_secvtx1m+p_l).M(), w[0]);}
		if (svntk[index_for_correct_m] ==3){fHmlSv_emu_minmass_ntr3->Fill((p_secvtx1m+p_l).M(), w[0]);}
		if (svntk[index_for_correct_m] > 3){fHmlSv_emu_minmass_ntr4->Fill((p_secvtx1m+p_l).M(), w[0]);}

		if( (lid[0] > 0 && bid[index_for_correct] == -5 ) || (lid[0] < 0 && bid[index_for_correct] == 5) ){  
			fHmlSv_emu_deltar_correct->Fill((p_secvtx1+p_l).M(), w[0]);
			if (svntk[index_for_correct] ==2){fHmlSv_emu_deltar_ntr2_correct->Fill((p_secvtx1+p_l).M(), w[0]);}
			if (svntk[index_for_correct] ==3){fHmlSv_emu_deltar_ntr3_correct->Fill((p_secvtx1+p_l).M(), w[0]);}
			if (svntk[index_for_correct] > 3){fHmlSv_emu_deltar_ntr4_correct->Fill((p_secvtx1+p_l).M(), w[0]);}
		}
		
		else {  
			fHmlSv_emu_deltar_wrong->Fill((p_secvtx1+p_l).M(), w[0]);
			if (svntk[index_for_correct] ==2){fHmlSv_emu_deltar_ntr2_wrong->Fill((p_secvtx1+p_l).M(), w[0]);}
			if (svntk[index_for_correct] ==3){fHmlSv_emu_deltar_ntr3_wrong->Fill((p_secvtx1+p_l).M(), w[0]);}
			if (svntk[index_for_correct] >3){fHmlSv_emu_deltar_ntr4_wrong->Fill((p_secvtx1+p_l).M(), w[0]);}
		}

		if( (lid[0] > 0 && bid[index_for_correct_m] == -5 ) || (lid[0] < 0 && bid[index_for_correct_m] == 5) ){  
			fHmlSv_emu_minmass_correct->Fill((p_secvtx1m+p_l).M(), w[0]);
			if (svntk[index_for_correct_m] ==2){fHmlSv_emu_minmass_ntr2_correct->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (svntk[index_for_correct_m] ==3){fHmlSv_emu_minmass_ntr3_correct->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (svntk[index_for_correct_m] > 3){fHmlSv_emu_minmass_ntr4_correct->Fill((p_secvtx1m+p_l).M(), w[0]);}
		}
		
		else {  
			fHmlSv_emu_minmass_wrong->Fill((p_secvtx1m+p_l).M(), w[0]);
			if (svntk[index_for_correct_m] ==2){fHmlSv_emu_minmass_ntr2_wrong->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (svntk[index_for_correct_m] ==3){fHmlSv_emu_minmass_ntr3_wrong->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (svntk[index_for_correct_m] >3){fHmlSv_emu_minmass_ntr4_wrong->Fill((p_secvtx1m+p_l).M(), w[0]);}
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
