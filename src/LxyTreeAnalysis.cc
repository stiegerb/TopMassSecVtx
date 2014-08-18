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

	fHmlsv_emu_deltar = new TH1D("mlsv_emu_deltar", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar);
	fHmlsv_emu_deltar->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_flow = new TH1D("mlsv_emu_deltar_cut_flow", "Lepton/SecVtx Mass in eMu channel, deltar algorithm",
		                      4, 0.,4.); fHistos.push_back(fHmlsv_emu_deltar_cut_flow);
	fHmlsv_emu_deltar_cut_flow->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_deltar_cut = new TH1D("mlsv_emu_deltar_cut", "Lepton/SecVtx Mass in eMu channel after cut",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut);
	fHmlsv_emu_deltar_cut->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_correct = new TH1D("mlsv_emu_deltar_cut_correct", "Lepton/SecVtx Mass in eMu channel after cut_correct",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_correct);
	fHmlsv_emu_deltar_cut_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_wrong = new TH1D("mlsv_emu_deltar_cut_wrong", "Lepton/SecVtx Mass in eMu channel after cut_wrong",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_wrong);
	fHmlsv_emu_deltar_cut_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");



	fHmlsv_emu_deltar_cut_ntr2 = new TH1D("mlsv_emu_deltar_cut_ntr2", "Lepton/SecVtx Mass in eMu channel after cut (2 tracks)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_ntr2);
	fHmlsv_emu_deltar_cut_ntr2->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_ntr2_correct = new TH1D("mlsv_emu_deltar_cut_ntr2_correct", "Lepton/SecVtx Mass in eMu channel after cut (2 tracks)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_ntr2_correct);
	fHmlsv_emu_deltar_cut_ntr2_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_ntr2_wrong = new TH1D("mlsv_emu_deltar_cut_ntr2_wrong", "Lepton/SecVtx Mass in eMu channel after cut (2 tracks)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_ntr2_wrong);
	fHmlsv_emu_deltar_cut_ntr2_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_deltar_cut_ntr3 = new TH1D("mlsv_emu_deltar_cut_ntr3", "Lepton/SecVtx Mass in eMu channel after cut (3 tracks)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_ntr3);
	fHmlsv_emu_deltar_cut_ntr3->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_ntr3_correct = new TH1D("mlsv_emu_deltar_cut_ntr3_correct", "Lepton/SecVtx Mass in eMu channel after cut (3 tracks)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_ntr3_correct);
	fHmlsv_emu_deltar_cut_ntr3_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_ntr3_wrong = new TH1D("mlsv_emu_deltar_cut_ntr3_wrong", "Lepton/SecVtx Mass in eMu channel after cut (3 tracks)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_ntr3_wrong);
	fHmlsv_emu_deltar_cut_ntr3_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_deltar_cut_ntr4 = new TH1D("mlsv_emu_deltar_cut_ntr4", "Lepton/SecVtx Mass in eMu channel after cut (4 and more tracks)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_ntr4);
	fHmlsv_emu_deltar_cut_ntr4->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_ntr4_correct = new TH1D("mlsv_emu_deltar_cut_ntr4_correct", "Lepton/SecVtx Mass in eMu channel after cut (4 and more tracks)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_ntr4_correct);
	fHmlsv_emu_deltar_cut_ntr4_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_ntr4_wrong = new TH1D("mlsv_emu_deltar_cut_ntr4_wrong", "Lepton/SecVtx Mass in eMu channel after cut (4 and more tracks)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_ntr4_wrong);
	fHmlsv_emu_deltar_cut_ntr4_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");



	fHdeltar_lsv_emu_deltar_cut = new TH1D("deltar_lsv_emu_deltar_cut", "Lepton/SecVtx deltar in eMu channel after cut",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_lsv_emu_deltar_cut);
	fHdeltar_lsv_emu_deltar_cut->SetXTitle("DeltaR");

	fHdeltar_lsv_emu_deltar_cut_correct = new TH1D("deltar_lsv_emu_deltar_cut_correct", "Lepton/SecVtx deltar in eMu channel after cut_correct",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_lsv_emu_deltar_cut_correct);
	fHdeltar_lsv_emu_deltar_cut_correct->SetXTitle("DeltaR");

	fHdeltar_lsv_emu_deltar_cut_wrong = new TH1D("deltar_lsv_emu_deltar_cut_wrong", "Lepton/SecVtx deltar in eMu channel after cut_wrong",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_lsv_emu_deltar_cut_wrong);
	fHdeltar_lsv_emu_deltar_cut_wrong->SetXTitle("DeltaR");


	
	fHmlsv_emu_deltar_correct = new TH1D("mlsv_emu_deltar_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_correct);
	fHmlsv_emu_deltar_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_wrong = new TH1D("mlsv_emu_deltar_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_wrong);
	fHmlsv_emu_deltar_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_deltar_ntr2 = new TH1D("mlsv_emu_deltar_ntr2", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_ntr2);
	fHmlsv_emu_deltar_ntr2->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_ntr2_correct = new TH1D("mlsv_emu_deltar_ntr2_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_ntr2_correct);
	fHmlsv_emu_deltar_ntr2_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_ntr2_wrong = new TH1D("mlsv_emu_deltar_ntr2_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_ntr2_wrong);
	fHmlsv_emu_deltar_ntr2_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_deltar_ntr3 = new TH1D("mlsv_emu_deltar_ntr3", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_ntr3);
	fHmlsv_emu_deltar_ntr3->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_ntr3_correct = new TH1D("mlsv_emu_deltar_ntr3_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_ntr3_correct);
	fHmlsv_emu_deltar_ntr3_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_ntr3_wrong = new TH1D("mlsv_emu_deltar_ntr3_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_ntr3_wrong);
	fHmlsv_emu_deltar_ntr3_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_deltar_ntr4 = new TH1D("mlsv_emu_deltar_ntr4", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_ntr4);
	fHmlsv_emu_deltar_ntr4->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_deltar_ntr4_correct = new TH1D("mlsv_emu_deltar_ntr4_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_ntr4_correct);
	fHmlsv_emu_deltar_ntr4_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_ntr4_wrong = new TH1D("mlsv_emu_deltar_ntr4_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_ntr4_wrong);
	fHmlsv_emu_deltar_ntr4_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");

// min mass method


	fHmlsv_emu_minmass = new TH1D("mlsv_emu_minmass", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass);
	fHmlsv_emu_minmass->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_minmass_flow = new TH1D("mlsv_emu_minmass_flow", "Lepton/SecVtx Mass in eMu channel, minmass algorithm",
		                     4, 0., 4.); fHistos.push_back(fHmlsv_emu_minmass_flow);
	fHmlsv_emu_minmass_flow->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_minmass_correct = new TH1D("mlsv_emu_minmass_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_correct);
	fHmlsv_emu_minmass_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_wrong = new TH1D("mlsv_emu_minmass_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_wrong);
	fHmlsv_emu_minmass_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_minmass_ntr2 = new TH1D("mlsv_emu_minmass_ntr2", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_ntr2);
	fHmlsv_emu_minmass_ntr2->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_ntr2_correct = new TH1D("mlsv_emu_minmass_ntr2_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_ntr2_correct);
	fHmlsv_emu_minmass_ntr2_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_ntr2_wrong = new TH1D("mlsv_emu_minmass_ntr2_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_ntr2_wrong);
	fHmlsv_emu_minmass_ntr2_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_minmass_ntr3 = new TH1D("mlsv_emu_minmass_ntr3", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_ntr3);
	fHmlsv_emu_minmass_ntr3->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_ntr3_correct = new TH1D("mlsv_emu_minmass_ntr3_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_ntr3_correct);
	fHmlsv_emu_minmass_ntr3_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_ntr3_wrong = new TH1D("mlsv_emu_minmass_ntr3_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_ntr3_wrong);
	fHmlsv_emu_minmass_ntr3_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_minmass_ntr4 = new TH1D("mlsv_emu_minmass_ntr4", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_ntr4);
	fHmlsv_emu_minmass_ntr4->SetXTitle("Lepton/SecVtx malss [GeV]");

	fHmlsv_emu_minmass_ntr4_correct = new TH1D("mlsv_emu_minmass_ntr4_correct", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_ntr4_correct);
	fHmlsv_emu_minmass_ntr4_correct->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_ntr4_wrong = new TH1D("mlsv_emu_minmass_ntr4_wrong", "Lepton/SecVtx Mass in eMu channel",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_ntr4_wrong);
	fHmlsv_emu_minmass_ntr4_wrong->SetXTitle("Lepton/SecVtx mass [GeV]");

// systematics


	fHmlsv_emu_deltar_cut_correct_topweight = new TH1D("mlsv_emu_deltar_cut_correct_topweight", "Lepton/SecVtx Mass in eMu channel (incl. topweight)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_correct_topweight);
	fHmlsv_emu_deltar_cut_correct_topweight->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_correct_topweight_up = new TH1D("mlsv_emu_deltar_cut_correct_topweight_up", "Lepton/SecVtx Mass in eMu channel (incl. topweight_up)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_correct_topweight_up);
	fHmlsv_emu_deltar_cut_correct_topweight_up->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_wrong_topweight = new TH1D("mlsv_emu_deltar_cut_wrong_topweight", "Lepton/SecVtx Mass in eMu channel (incl. topweight)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_wrong_topweight);
	fHmlsv_emu_deltar_cut_wrong_topweight->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_deltar_cut_wrong_topweight_up = new TH1D("mlsv_emu_deltar_cut_wrong_topweight_up", "Lepton/SecVtx Mass in eMu channel (incl. topweight_up)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_deltar_cut_wrong_topweight_up);
	fHmlsv_emu_deltar_cut_wrong_topweight_up->SetXTitle("Lepton/SecVtx mass [GeV]");


	fHmlsv_emu_minmass_correct_topweight = new TH1D("mlsv_emu_minmass_correct_topweight", "Lepton/SecVtx Mass in eMu channel (incl. topweight)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_correct_topweight);
	fHmlsv_emu_minmass_correct_topweight->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_correct_topweight_up = new TH1D("mlsv_emu_minmass_correct_topweight_up", "Lepton/SecVtx Mass in eMu channel (incl. topweight_up)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_correct_topweight_up);
	fHmlsv_emu_minmass_correct_topweight_up->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_wrong_topweight = new TH1D("mlsv_emu_minmass_wrong_topweight", "Lepton/SecVtx Mass in eMu channel (incl. topweight)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_wrong_topweight);
	fHmlsv_emu_minmass_wrong_topweight->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_wrong_topweight_up = new TH1D("mlsv_emu_minmass_wrong_topweight_up", "Lepton/SecVtx Mass in eMu channel (incl. topweight_up)",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_wrong_topweight_up);
	fHmlsv_emu_minmass_wrong_topweight_up->SetXTitle("Lepton/SecVtx mass [GeV]");


// nvtx check

	fHmlsv_emu_minmass_correct_nvtx_1bin = new TH1D("mlsv_emu_minmass_correct_nvtx_1bin", "Lepton/SecVtx Mass in eMu channel 1-10 vtx",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_correct_nvtx_1bin);
	fHmlsv_emu_minmass_correct_nvtx_1bin->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_correct_nvtx_2bin = new TH1D("mlsv_emu_minmass_correct_nvtx_2bin", "Lepton/SecVtx Mass in eMu channel 11-14 vtx",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_correct_nvtx_2bin);
	fHmlsv_emu_minmass_correct_nvtx_2bin->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_correct_nvtx_3bin = new TH1D("mlsv_emu_minmass_correct_nvtx_3bin", "Lepton/SecVtx Mass in eMu channel 15-19 vtx",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_correct_nvtx_3bin);
	fHmlsv_emu_minmass_correct_nvtx_3bin->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_correct_nvtx_4bin = new TH1D("mlsv_emu_minmass_correct_nvtx_4bin", "Lepton/SecVtx Mass in eMu channel 20+ vtx",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_correct_nvtx_4bin);
	fHmlsv_emu_minmass_correct_nvtx_4bin->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_wrong_nvtx_1bin = new TH1D("mlsv_emu_minmass_wrong_nvtx_1bin", "Lepton/SecVtx Mass in eMu channel 1-10 vtx",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_wrong_nvtx_1bin);
	fHmlsv_emu_minmass_wrong_nvtx_1bin->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_wrong_nvtx_2bin = new TH1D("mlsv_emu_minmass_wrong_nvtx_2bin", "Lepton/SecVtx Mass in eMu channel 11-14 vtx",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_wrong_nvtx_2bin);
	fHmlsv_emu_minmass_wrong_nvtx_2bin->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_wrong_nvtx_3bin = new TH1D("mlsv_emu_minmass_wrong_nvtx_3bin", "Lepton/SecVtx Mass in eMu channel 15-19 vtx",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_wrong_nvtx_3bin);
	fHmlsv_emu_minmass_wrong_nvtx_3bin->SetXTitle("Lepton/SecVtx mass [GeV]");

	fHmlsv_emu_minmass_wrong_nvtx_4bin = new TH1D("mlsv_emu_minmass_wrong_nvtx_4bin", "Lepton/SecVtx Mass in eMu channel 20+ vtx",
		                      50, 0., 150.); fHistos.push_back(fHmlsv_emu_minmass_wrong_nvtx_4bin);
	fHmlsv_emu_minmass_wrong_nvtx_4bin->SetXTitle("Lepton/SecVtx mass [GeV]");

/*
// bhadr/secvt

	fHsecbhad_pratio_emu = new TH1D("secbhad_pratio_emu", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu);
	fHsecbhad_pratio_emu->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr2 = new TH1D("secbhad_pratio_emu_ntr2", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr2);
	fHsecbhad_pratio_emu_ntr2->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr3 = new TH1D("secbhad_pratio_emu_ntr3", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr3);
	fHsecbhad_pratio_emu_ntr3->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr4 = new TH1D("secbhad_pratio_emu_ntr4", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr4);
	fHsecbhad_pratio_emu_ntr4->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr5 = new TH1D("secbhad_pratio_emu_ntr5", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr5);
	fHsecbhad_pratio_emu_ntr5->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr6 = new TH1D("secbhad_pratio_emu_ntr6", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr6);
	fHsecbhad_pratio_emu_ntr6->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr7 = new TH1D("secbhad_pratio_emu_ntr7", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr7);
	fHsecbhad_pratio_emu_ntr7->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr8 = new TH1D("secbhad_pratio_emu_ntr8", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr8);
	fHsecbhad_pratio_emu_ntr8->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr9 = new TH1D("secbhad_pratio_emu_ntr9", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr9);
	fHsecbhad_pratio_emu_ntr9->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr10 = new TH1D("secbhad_pratio_emu_ntr10", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr10);
	fHsecbhad_pratio_emu_ntr10->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr11 = new TH1D("secbhad_pratio_emu_ntr11", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr11);
	fHsecbhad_pratio_emu_ntr11->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr12 = new TH1D("secbhad_pratio_emu_ntr12", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr12);
	fHsecbhad_pratio_emu_ntr12->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr13 = new TH1D("secbhad_pratio_emu_ntr13", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr13);
	fHsecbhad_pratio_emu_ntr13->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr14 = new TH1D("secbhad_pratio_emu_ntr14", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr14);
	fHsecbhad_pratio_emu_ntr14->SetXTitle("|p|secvt/|p|bhad");

	fHsecbhad_pratio_emu_ntr15 = new TH1D("secbhad_pratio_emu_ntr15", "ratio between |p| of secvtx and bhadron in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecbhad_pratio_emu_ntr15);
	fHsecbhad_pratio_emu_ntr15->SetXTitle("|p|secvt/|p|bhad");


	fHsecbhad_deltar_emu = new TH1D("secbhad_deltar_emu", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu);
	fHsecbhad_deltar_emu->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr2 = new TH1D("secbhad_deltar_emu_ntr2", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr2);
	fHsecbhad_deltar_emu_ntr2->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr3 = new TH1D("secbhad_deltar_emu_ntr3", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr3);
	fHsecbhad_deltar_emu_ntr3->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr4 = new TH1D("secbhad_deltar_emu_ntr4", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr4);
	fHsecbhad_deltar_emu_ntr4->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr5 = new TH1D("secbhad_deltar_emu_ntr5", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr5);
	fHsecbhad_deltar_emu_ntr5->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr6 = new TH1D("secbhad_deltar_emu_ntr6", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr6);
	fHsecbhad_deltar_emu_ntr6->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr7 = new TH1D("secbhad_deltar_emu_ntr7", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr7);
	fHsecbhad_deltar_emu_ntr7->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr8 = new TH1D("secbhad_deltar_emu_ntr8", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr8);
	fHsecbhad_deltar_emu_ntr8->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr9 = new TH1D("secbhad_deltar_emu_ntr9", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr9);
	fHsecbhad_deltar_emu_ntr9->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr10 = new TH1D("secbhad_deltar_emu_ntr10", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr10);
	fHsecbhad_deltar_emu_ntr10->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr11 = new TH1D("secbhad_deltar_emu_ntr11", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr11);
	fHsecbhad_deltar_emu_ntr11->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr12 = new TH1D("secbhad_deltar_emu_ntr12", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr12);
	fHsecbhad_deltar_emu_ntr12->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr13 = new TH1D("secbhad_deltar_emu_ntr13", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr13);
	fHsecbhad_deltar_emu_ntr13->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr14 = new TH1D("secbhad_deltar_emu_ntr14", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr14);
	fHsecbhad_deltar_emu_ntr14->SetXTitle("deltaR between bhad and secvtx");

	fHsecbhad_deltar_emu_ntr15 = new TH1D("secbhad_deltar_emu_ntr15", "deltar between secvtx and bhadron in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecbhad_deltar_emu_ntr15);
	fHsecbhad_deltar_emu_ntr15->SetXTitle("deltaR between bhad and secvtx");


// b quark/secvt

	fHsecb_pratio_emu = new TH1D("secb_pratio_emu", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu);
	fHsecb_pratio_emu->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr2 = new TH1D("secb_pratio_emu_ntr2", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr2);
	fHsecb_pratio_emu_ntr2->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr3 = new TH1D("secb_pratio_emu_ntr3", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr3);
	fHsecb_pratio_emu_ntr3->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr4 = new TH1D("secb_pratio_emu_ntr4", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr4);
	fHsecb_pratio_emu_ntr4->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr5 = new TH1D("secb_pratio_emu_ntr5", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr5);
	fHsecb_pratio_emu_ntr5->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr6 = new TH1D("secb_pratio_emu_ntr6", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr6);
	fHsecb_pratio_emu_ntr6->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr7 = new TH1D("secb_pratio_emu_ntr7", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr7);
	fHsecb_pratio_emu_ntr7->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr8 = new TH1D("secb_pratio_emu_ntr8", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr8);
	fHsecb_pratio_emu_ntr8->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr9 = new TH1D("secb_pratio_emu_ntr9", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr9);
	fHsecb_pratio_emu_ntr9->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr10 = new TH1D("secb_pratio_emu_ntr10", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr10);
	fHsecb_pratio_emu_ntr10->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr11 = new TH1D("secb_pratio_emu_ntr11", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr11);
	fHsecb_pratio_emu_ntr11->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr12 = new TH1D("secb_pratio_emu_ntr12", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr12);
	fHsecb_pratio_emu_ntr12->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr13 = new TH1D("secb_pratio_emu_ntr13", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr13);
	fHsecb_pratio_emu_ntr13->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr14 = new TH1D("secb_pratio_emu_ntr14", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr14);
	fHsecb_pratio_emu_ntr14->SetXTitle("|p|secvt/|p|b");

	fHsecb_pratio_emu_ntr15 = new TH1D("secb_pratio_emu_ntr15", "ratio between |p| of secvtx and b quark in eMu channel",
		                      50, 0., 1.); fHistos.push_back(fHsecb_pratio_emu_ntr15);
	fHsecb_pratio_emu_ntr15->SetXTitle("|p|secvt/|p|b");


	fHsecb_deltar_emu = new TH1D("secb_deltar_emu", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu);
	fHsecb_deltar_emu->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr2 = new TH1D("secb_deltar_emu_ntr2", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr2);
	fHsecb_deltar_emu_ntr2->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr3 = new TH1D("secb_deltar_emu_ntr3", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr3);
	fHsecb_deltar_emu_ntr3->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr4 = new TH1D("secb_deltar_emu_ntr4", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr4);
	fHsecb_deltar_emu_ntr4->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr5 = new TH1D("secb_deltar_emu_ntr5", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr5);
	fHsecb_deltar_emu_ntr5->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr6 = new TH1D("secb_deltar_emu_ntr6", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr6);
	fHsecb_deltar_emu_ntr6->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr7 = new TH1D("secb_deltar_emu_ntr7", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr7);
	fHsecb_deltar_emu_ntr7->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr8 = new TH1D("secb_deltar_emu_ntr8", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr8);
	fHsecb_deltar_emu_ntr8->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr9 = new TH1D("secb_deltar_emu_ntr9", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr9);
	fHsecb_deltar_emu_ntr9->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr10 = new TH1D("secb_deltar_emu_ntr10", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr10);
	fHsecb_deltar_emu_ntr10->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr11 = new TH1D("secb_deltar_emu_ntr11", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr11);
	fHsecb_deltar_emu_ntr11->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr12 = new TH1D("secb_deltar_emu_ntr12", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr12);
	fHsecb_deltar_emu_ntr12->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr13 = new TH1D("secb_deltar_emu_ntr13", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr13);
	fHsecb_deltar_emu_ntr13->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr14 = new TH1D("secb_deltar_emu_ntr14", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr14);
	fHsecb_deltar_emu_ntr14->SetXTitle("deltaR between b and secvtx");

	fHsecb_deltar_emu_ntr15 = new TH1D("secb_deltar_emu_ntr15", "deltar between secvtx and b quark in eMu channel",
		                      100, 0., 0.4); fHistos.push_back(fHsecb_deltar_emu_ntr15);
	fHsecb_deltar_emu_ntr15->SetXTitle("deltaR between b and secvtx");

// deltar values

	fHdeltar_svl_emu_2d = new TH2D("deltar_svl_emu_2d", "deltar between secvtx (x axis - correct charge, y - wrong) and lepton in eMu channel",
		                      100, 0., 6., 100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_2d);
	fHdeltar_svl_emu_2d->SetXTitle("deltaR between l and secvtx");


	fHdeltar_svl_emu_correct = new TH1D("deltar_svl_emu_correct", "deltar between secvtx (correct charge) and lepton in eMu channel",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_correct);
	fHdeltar_svl_emu_correct->SetXTitle("deltaR between l and secvtx");

	fHdeltar_svl_emu_correct_ntr2 = new TH1D("deltar_svl_emu_correct_ntr2", "deltar between secvtx (correct charge) and lepton in eMu channel (2 tracks)",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_correct_ntr2);
	fHdeltar_svl_emu_correct_ntr2->SetXTitle("deltaR between l and secvtx");

	fHdeltar_svl_emu_correct_ntr3 = new TH1D("deltar_svl_emu_correct_ntr3", "deltar between secvtx (correct charge) and lepton in eMu channel (3 tracks)",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_correct_ntr3);
	fHdeltar_svl_emu_correct_ntr3->SetXTitle("deltaR between l and secvtx");

	fHdeltar_svl_emu_correct_ntr4 = new TH1D("deltar_svl_emu_correct_ntr4", "deltar between secvtx (correct charge) and lepton in eMu channel (4 tracks)",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_correct_ntr4);
	fHdeltar_svl_emu_correct_ntr4->SetXTitle("deltaR between l and secvtx");

	fHdeltar_svl_emu_correct_ntr5 = new TH1D("deltar_svl_emu_correct_ntr5", "deltar between secvtx (correct charge) and lepton in eMu channel (5 and more tracks)",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_correct_ntr5);
	fHdeltar_svl_emu_correct_ntr5->SetXTitle("deltaR between l and secvtx");


	fHdeltar_svl_emu_wrong = new TH1D("deltar_svl_emu_wrong", "deltar between secvtx (wrong charge) and lepton in eMu channel",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_wrong);
	fHdeltar_svl_emu_wrong->SetXTitle("deltaR between l and secvtx");

	fHdeltar_svl_emu_wrong_ntr2 = new TH1D("deltar_svl_emu_wrong_ntr2", "deltar between secvtx (wrong charge) and lepton in eMu channel (2 tracks)",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_wrong_ntr2);
	fHdeltar_svl_emu_wrong_ntr2->SetXTitle("deltaR between l and secvtx");

	fHdeltar_svl_emu_wrong_ntr3 = new TH1D("deltar_svl_emu_wrong_ntr3", "deltar between secvtx (wrong charge) and lepton in eMu channel (3 tracks)",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_wrong_ntr3);
	fHdeltar_svl_emu_wrong_ntr3->SetXTitle("deltaR between l and secvtx");

	fHdeltar_svl_emu_wrong_ntr4 = new TH1D("deltar_svl_emu_wrong_ntr4", "deltar between secvtx (wrong charge) and lepton in eMu channel (4 tracks)",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_wrong_ntr4);
	fHdeltar_svl_emu_wrong_ntr4->SetXTitle("deltaR between l and secvtx");

	fHdeltar_svl_emu_wrong_ntr5 = new TH1D("deltar_svl_emu_wrong_ntr5", "deltar between secvtx (wrong charge) and lepton in eMu channel (5 and more tracks)",
		                      100, 0., 6.); fHistos.push_back(fHdeltar_svl_emu_wrong_ntr5);
	fHdeltar_svl_emu_wrong_ntr5->SetXTitle("deltaR between l and secvtx");
*/

	fHsvntk = new TH1D("svntk", "number of tracks of sec.vertex in eMu channel",
		                      15, 0., 15.); fHistos.push_back(fHsvntk);
	fHsvntk->SetXTitle("n vtx");

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
	bool check_secv2=0;
	if(lxymax2>0) check_secv2=1;
	if(indices[1]<0) indices.pop_back();
	if(indices[0]<0) indices.pop_back();
	bool check_secv(indices.size());
 
   //if (svlxy[i]>0){
//			indices.push_back(i);
//			check_secv=1;
//		}
//	}

/*	if (abs(evcat) == 11*13 && abs(bid[indices[0]])==5 && bhadpt[indices[0]] > 0 && check_secv){
		TVector3 p_secvtx, p_bhadron;
		int index_for_correct=indices[0];
		p_secvtx.SetPtEtaPhi(svpt[index_for_correct], sveta[index_for_correct], svphi[index_for_correct]);
		p_bhadron.SetPtEtaPhi(bhadpt[index_for_correct], bhadeta[index_for_correct], bhadphi[index_for_correct]);
		fHsecbhad_pratio_emu->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
		fHsecbhad_deltar_emu->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		if (svntk[index_for_correct]==2){
			fHsecbhad_pratio_emu_ntr2->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr2->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}	
		if (svntk[index_for_correct]==3){
			fHsecbhad_pratio_emu_ntr3->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr3->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}
		if (svntk[index_for_correct]==4){
			fHsecbhad_pratio_emu_ntr4->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr4->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}
		if (svntk[index_for_correct]==5){
			fHsecbhad_pratio_emu_ntr5->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr5->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==6){
			fHsecbhad_pratio_emu_ntr6->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr6->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==7){
			fHsecbhad_pratio_emu_ntr7->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr7->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==8){
			fHsecbhad_pratio_emu_ntr8->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr8->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==9){
			fHsecbhad_pratio_emu_ntr9->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr9->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==10){
			fHsecbhad_pratio_emu_ntr10->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr10->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==11){
			fHsecbhad_pratio_emu_ntr11->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr11->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==12){
			fHsecbhad_pratio_emu_ntr12->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr12->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==13){
			fHsecbhad_pratio_emu_ntr13->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr13->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==14){
			fHsecbhad_pratio_emu_ntr14->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr14->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==15){
			fHsecbhad_pratio_emu_ntr15->Fill((p_secvtx.Mag()/p_bhadron.Mag()), w[0]);
			fHsecbhad_deltar_emu_ntr15->Fill((p_bhadron.DeltaR(p_secvtx)), w[0]);
		}
	}	

	if (abs(evcat) == 11*13 && abs(bid[indices[0]])==5 && bpt[indices[0]] > 0 && check_secv){
		TVector3 p_secvtx, p_bquark;
		int index_for_correct=indices[0];
		p_secvtx.SetPtEtaPhi(svpt[index_for_correct], sveta[index_for_correct], svphi[index_for_correct]);
		p_bquark.SetPtEtaPhi(bpt[index_for_correct], beta[index_for_correct], bphi[index_for_correct]);
		fHsecb_pratio_emu->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
		fHsecb_deltar_emu->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		if (svntk[index_for_correct]==2){
			fHsecb_pratio_emu_ntr2->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr2->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}	
		if (svntk[index_for_correct]==3){
			fHsecb_pratio_emu_ntr3->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr3->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}
		if (svntk[index_for_correct]==4){
			fHsecb_pratio_emu_ntr4->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr4->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}
		if (svntk[index_for_correct]==5){
			fHsecb_pratio_emu_ntr5->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr5->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==6){
			fHsecb_pratio_emu_ntr6->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr6->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==7){
			fHsecb_pratio_emu_ntr7->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr7->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==8){
			fHsecb_pratio_emu_ntr8->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr8->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==9){
			fHsecb_pratio_emu_ntr9->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr9->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==10){
			fHsecb_pratio_emu_ntr10->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr10->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==11){
			fHsecb_pratio_emu_ntr11->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr11->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==12){
			fHsecb_pratio_emu_ntr12->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr12->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==13){
			fHsecb_pratio_emu_ntr13->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr13->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==14){
			fHsecb_pratio_emu_ntr14->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr14->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}

		if (svntk[index_for_correct]==15){
			fHsecb_pratio_emu_ntr15->Fill((p_secvtx.Mag()/p_bquark.Mag()), w[0]);
			fHsecb_deltar_emu_ntr15->Fill((p_bquark.DeltaR(p_secvtx)), w[0]);
		}
	}		
	
	if(abs(evcat) == 11*13  && check_secv2 && nj > 1 ){
		TLorentzVector p_secvtx1, p_secvtx2, p_l;		
		p_l.SetPtEtaPhiM(lpt[0], leta[0], lphi[0], 0.);	
		p_secvtx1.SetPtEtaPhiM(svpt[indices[0]], sveta[indices[0]], svphi[indices[0]], svmass[indices[0]]);
		p_secvtx2.SetPtEtaPhiM(svpt[indices[1]], sveta[indices[1]], svphi[indices[1]], svmass[indices[1]]);
		if( ( (lid[0] > 0 && bid[indices[0]] == -5 ) || (lid[0] < 0 && bid[indices[0]] == 5) ) && ( (lid[0] > 0 && bid[indices[1]] == 5 ) || (lid[0] < 0 && bid[indices[1]] == -5) ) ){
			fHdeltar_svl_emu_2d->Fill(p_secvtx1.DeltaR(p_l), p_secvtx2.DeltaR(p_l), w[0]);
			fHdeltar_svl_emu_correct->Fill(p_secvtx1.DeltaR(p_l), w[0]);
			if (svntk[indices[0]] ==2){fHdeltar_svl_emu_correct_ntr2->Fill(p_l.DeltaR(p_secvtx1), w[0]);}
			if (svntk[indices[0]] ==3){fHdeltar_svl_emu_correct_ntr3->Fill(p_l.DeltaR(p_secvtx1), w[0]);}
			if (svntk[indices[0]] ==4){fHdeltar_svl_emu_correct_ntr4->Fill(p_l.DeltaR(p_secvtx1), w[0]);}
			if (svntk[indices[0]] >4){fHdeltar_svl_emu_correct_ntr5->Fill(p_l.DeltaR(p_secvtx1), w[0]);}
			fHdeltar_svl_emu_wrong->Fill(p_l.DeltaR(p_secvtx2), w[0]);
			if (svntk[indices[0]] ==2){fHdeltar_svl_emu_wrong_ntr2->Fill(p_l.DeltaR(p_secvtx2), w[0]);}
			if (svntk[indices[0]] ==3){fHdeltar_svl_emu_wrong_ntr3->Fill(p_l.DeltaR(p_secvtx2), w[0]);}
			if (svntk[indices[0]] ==4){fHdeltar_svl_emu_wrong_ntr4->Fill(p_l.DeltaR(p_secvtx2), w[0]);}
			if (svntk[indices[0]] >4){fHdeltar_svl_emu_wrong_ntr5->Fill(p_l.DeltaR(p_secvtx2), w[0]);}
		}

		if( ( (lid[0] < 0 && bid[indices[0]] == -5 ) || (lid[0] > 0 && bid[indices[0]] == 5) ) && ( (lid[0] < 0 && bid[indices[1]] == 5 ) || (lid[0] > 0 && bid[indices[1]] == -5) ) ){
			fHdeltar_svl_emu_2d->Fill(p_secvtx2.DeltaR(p_l), p_secvtx1.DeltaR(p_l), w[0]);
			fHdeltar_svl_emu_correct->Fill(p_l.DeltaR(p_secvtx2), w[0]);
			if (svntk[indices[1]] ==2){fHdeltar_svl_emu_correct_ntr2->Fill(p_l.DeltaR(p_secvtx2), w[0]);}
			if (svntk[indices[1]] ==3){fHdeltar_svl_emu_correct_ntr3->Fill(p_l.DeltaR(p_secvtx2), w[0]);}
			if (svntk[indices[1]] ==4){fHdeltar_svl_emu_correct_ntr4->Fill(p_l.DeltaR(p_secvtx2), w[0]);}
			if (svntk[indices[1]] >4){fHdeltar_svl_emu_correct_ntr5->Fill(p_l.DeltaR(p_secvtx2), w[0]);}
			fHdeltar_svl_emu_wrong->Fill(p_l.DeltaR(p_secvtx1), w[0]);
			if (svntk[indices[1]] ==2){fHdeltar_svl_emu_wrong_ntr2->Fill(p_l.DeltaR(p_secvtx1), w[0]);}
			if (svntk[indices[1]] ==3){fHdeltar_svl_emu_wrong_ntr3->Fill(p_l.DeltaR(p_secvtx1), w[0]);}
			if (svntk[indices[1]] ==4){fHdeltar_svl_emu_wrong_ntr4->Fill(p_l.DeltaR(p_secvtx1), w[0]);}
			if (svntk[indices[1]] >4){fHdeltar_svl_emu_wrong_ntr5->Fill(p_l.DeltaR(p_secvtx1), w[0]);}
		}
	}
*/
	if(abs(evcat) == 11*13  && check_secv && nj > 1 ){
		// emu channel
		// inv.m of l and correct sec.v. (deltar and minmass methods)
		
		std::vector <TLorentzVector> leptons(2,0);
		std::vector <TLorentzVector> secvertices(2,0);
		std::vector <double> deltar;		
		leptons[0].SetPtEtaPhiM(lpt[0], leta[0], lphi[0], 0.);	
		leptons[1].SetPtEtaPhiM(lpt[1], leta[1], lphi[1], 0.);	
		secvertices[0].SetPtEtaPhiM(svpt[indices[0]], sveta[indices[0]], svphi[indices[0]], svmass[indices[0]]);
		if (indices.size() > 1) {secvertices[1].SetPtEtaPhiM(svpt[indices[1]], sveta[indices[1]], svphi[indices[1]], svmass[indices[1]]);}
		else {secvertices.pop_back();}
		double mindeltar=100.;
		int mindeltar_index=0;
		int mindeltar_index2= abs(3-mindeltar_index);
		for(unsigned int j=0; j<secvertices.size(); j++){
			for(unsigned int i=0; i<2; i++){
				deltar.push_back(leptons[i].DeltaR(secvertices[j]));
			}	
		}
		for(unsigned int i=0; i<deltar.size(); i++){
			if (deltar[i]<mindeltar){
				mindeltar_index=i;
				mindeltar=deltar[i];
				mindeltar_index2= abs(3-mindeltar_index);
			}
		}

		//now if we have 2 sec.vertices
		if(deltar.size()>2){
	//		if(deltar[mindeltar_index]<2.2){

				int l1=0,s1=0;
				if(mindeltar_index==1){l1=1;}
				else if(mindeltar_index==2){s1=1;}
				else if(mindeltar_index==3){s1=1;l1=1;}
				
				fHmlsv_emu_deltar_cut_flow->Fill(0.,w[0]);
				fHmlsv_emu_deltar_cut->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
				fHdeltar_lsv_emu_deltar_cut->Fill(deltar[mindeltar_index],w[0]);
				fHsvntk->Fill(svntk[indices[s1]], w[0]);
				if(svntk[indices[s1]]==2){
					fHmlsv_emu_deltar_cut_ntr2->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
					fHmlsv_emu_deltar_cut_flow->Fill(1.,w[0]);
					}
				if(svntk[indices[s1]]==3){
					fHmlsv_emu_deltar_cut_ntr3->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
					fHmlsv_emu_deltar_cut_flow->Fill(2.,w[0]);
					}
				if(svntk[indices[s1]]>3){
					fHmlsv_emu_deltar_cut_ntr4->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
					fHmlsv_emu_deltar_cut_flow->Fill(3.,w[0]);					
					}

				if( (lid[l1] > 0 && bid[indices[s1]] == -5 ) || (lid[l1] < 0 && bid[indices[s1]] == 5) ){
					fHmlsv_emu_deltar_cut_correct->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
					fHdeltar_lsv_emu_deltar_cut_correct->Fill(deltar[mindeltar_index],w[0]);
					fHmlsv_emu_deltar_cut_correct_topweight->Fill((leptons[l1]+secvertices[s1]).M(), (w[0]*w[6]));
					fHmlsv_emu_deltar_cut_correct_topweight_up->Fill((leptons[l1]+secvertices[s1]).M(), (w[0]*w[7]));
					if (svntk[indices[s1]]==2){fHmlsv_emu_deltar_cut_ntr2_correct->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
					if (svntk[indices[s1]]==3){fHmlsv_emu_deltar_cut_ntr3_correct->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
					if (svntk[indices[s1]]>3){fHmlsv_emu_deltar_cut_ntr4_correct->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
				}
				else{
					fHmlsv_emu_deltar_cut_wrong->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
					fHdeltar_lsv_emu_deltar_cut_wrong->Fill(deltar[mindeltar_index],w[0]);
					fHmlsv_emu_deltar_cut_wrong_topweight->Fill((leptons[l1]+secvertices[s1]).M(), (w[0]*w[6]));
					fHmlsv_emu_deltar_cut_wrong_topweight_up->Fill((leptons[l1]+secvertices[s1]).M(), (w[0]*w[7]));
					if (svntk[indices[s1]]==2){fHmlsv_emu_deltar_cut_ntr2_wrong->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
					if (svntk[indices[s1]]==3){fHmlsv_emu_deltar_cut_ntr3_wrong->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
					if (svntk[indices[s1]]>3){fHmlsv_emu_deltar_cut_ntr4_wrong->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
				}

//			}
//			if(deltar[mindeltar_index2]<2.2){

				if(mindeltar_index2==0){l1=0;s1=0;}
				else if(mindeltar_index2==1){l1=1;s1=0;}
				else if(mindeltar_index2==2){l1=0;s1=1;}
				else if(mindeltar_index2==3){s1=1;l1=1;}

				fHmlsv_emu_deltar_cut_flow->Fill(0.,w[0]);
				fHmlsv_emu_deltar_cut->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
				fHdeltar_lsv_emu_deltar_cut->Fill(deltar[mindeltar_index],w[0]);
				fHsvntk->Fill(svntk[indices[s1]], w[0]);
				if(svntk[indices[s1]]==2){
					fHmlsv_emu_deltar_cut_ntr2->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
					fHmlsv_emu_deltar_cut_flow->Fill(1.,w[0]);
					}
				if(svntk[indices[s1]]==3){
					fHmlsv_emu_deltar_cut_ntr3->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
					fHmlsv_emu_deltar_cut_flow->Fill(2.,w[0]);
					}
				if(svntk[indices[s1]]>3){
					fHmlsv_emu_deltar_cut_ntr4->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
					fHmlsv_emu_deltar_cut_flow->Fill(3.,w[0]);					
					}



				if( (lid[l1] > 0 && bid[indices[s1]] == -5 ) || (lid[l1] < 0 && bid[indices[s1]] == 5) ){
					fHmlsv_emu_deltar_cut_correct->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
					fHdeltar_lsv_emu_deltar_cut_correct->Fill(deltar[mindeltar_index2],w[0]);
					fHmlsv_emu_deltar_cut_correct_topweight->Fill((leptons[l1]+secvertices[s1]).M(), (w[0]*w[6]));
					fHmlsv_emu_deltar_cut_correct_topweight_up->Fill((leptons[l1]+secvertices[s1]).M(), (w[0]*w[7]));
					if (svntk[indices[s1]]==2){fHmlsv_emu_deltar_cut_ntr2_correct->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
					if (svntk[indices[s1]]==3){fHmlsv_emu_deltar_cut_ntr3_correct->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
					if (svntk[indices[s1]]>3){fHmlsv_emu_deltar_cut_ntr4_correct->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
				}
				else{
					fHmlsv_emu_deltar_cut_wrong->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);
					fHdeltar_lsv_emu_deltar_cut_wrong->Fill(deltar[mindeltar_index2],w[0]);
					fHmlsv_emu_deltar_cut_wrong_topweight->Fill((leptons[l1]+secvertices[s1]).M(), (w[0]*w[6]));
					fHmlsv_emu_deltar_cut_wrong_topweight_up->Fill((leptons[l1]+secvertices[s1]).M(), (w[0]*w[7]));
					if (svntk[indices[s1]]==2){fHmlsv_emu_deltar_cut_ntr2_wrong->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
					if (svntk[indices[s1]]==3){fHmlsv_emu_deltar_cut_ntr3_wrong->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
					if (svntk[indices[s1]]>3){fHmlsv_emu_deltar_cut_ntr4_wrong->Fill((leptons[l1]+secvertices[s1]).M(),w[0]);}
				}
//			}


		}
		//if we have only 1 sec.vertex
		else {
//			if(deltar[mindeltar_index]<2.2){
				fHmlsv_emu_deltar_cut->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);
				fHmlsv_emu_deltar_cut_flow->Fill(0.,w[0]);
				fHdeltar_lsv_emu_deltar_cut->Fill(deltar[mindeltar_index],w[0]);
				fHsvntk->Fill(svntk[indices[0]], w[0]);	
				if(svntk[indices[0]]==2){
					fHmlsv_emu_deltar_cut_ntr2->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);
					fHmlsv_emu_deltar_cut_flow->Fill(1.,w[0]);
					}
				if(svntk[indices[0]]==3){
					fHmlsv_emu_deltar_cut_ntr3->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);
					fHmlsv_emu_deltar_cut_flow->Fill(2.,w[0]);
					}
				if(svntk[indices[0]]>3){
					fHmlsv_emu_deltar_cut_ntr4->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);
					fHmlsv_emu_deltar_cut_flow->Fill(3.,w[0]);
					}


				if( (lid[mindeltar_index] > 0 && bid[indices[0]] == -5 ) || (lid[mindeltar_index] < 0 && bid[indices[0]] == 5) ){
					fHmlsv_emu_deltar_cut_correct->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);
					fHdeltar_lsv_emu_deltar_cut_correct->Fill(deltar[mindeltar_index],w[0]);
					fHmlsv_emu_deltar_cut_correct_topweight->Fill((leptons[mindeltar_index]+secvertices[0]).M(), (w[0]*w[6]));
					fHmlsv_emu_deltar_cut_correct_topweight_up->Fill((leptons[mindeltar_index]+secvertices[0]).M(), (w[0]*w[7]));
					if(svntk[indices[0]]==2){fHmlsv_emu_deltar_cut_ntr2_correct->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);}
					if(svntk[indices[0]]==3){fHmlsv_emu_deltar_cut_ntr3_correct->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);}
					if(svntk[indices[0]]>3){fHmlsv_emu_deltar_cut_ntr4_correct->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);}
				}				
				else {
					fHmlsv_emu_deltar_cut_wrong->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);
					fHdeltar_lsv_emu_deltar_cut_wrong->Fill(deltar[mindeltar_index],w[0]);
					fHmlsv_emu_deltar_cut_wrong_topweight->Fill((leptons[mindeltar_index]+secvertices[0]).M(), (w[0]*w[6]));
					fHmlsv_emu_deltar_cut_wrong_topweight_up->Fill((leptons[mindeltar_index]+secvertices[0]).M(), (w[0]*w[7]));
					if(svntk[indices[0]]==2){fHmlsv_emu_deltar_cut_ntr2_wrong->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);}
					if(svntk[indices[0]]==3){fHmlsv_emu_deltar_cut_ntr3_wrong->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);}
					if(svntk[indices[0]]>3){fHmlsv_emu_deltar_cut_ntr4_wrong->Fill((leptons[mindeltar_index]+secvertices[0]).M(),w[0]);}
				}
//			}
		}
	}

			
	if(abs(evcat) == 11*13  && check_secv2 && nj > 1 ){
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

		fHmlsv_emu_deltar->Fill((p_secvtx1+p_l).M(), w[0]);
		if (svntk[index_for_correct] ==2){fHmlsv_emu_deltar_ntr2->Fill((p_secvtx1+p_l).M(), w[0]);}
		if (svntk[index_for_correct] ==3){fHmlsv_emu_deltar_ntr3->Fill((p_secvtx1+p_l).M(), w[0]);}
		if (svntk[index_for_correct] > 3){fHmlsv_emu_deltar_ntr4->Fill((p_secvtx1+p_l).M(), w[0]);}

		fHmlsv_emu_minmass_flow->Fill(0.,w[0]);
		fHmlsv_emu_minmass->Fill((p_secvtx1m+p_l).M(), w[0]);
		if (svntk[index_for_correct_m] ==2){
			fHmlsv_emu_minmass_ntr2->Fill((p_secvtx1m+p_l).M(), w[0]);
			fHmlsv_emu_minmass_flow->Fill(1., w[0]);
			}
		if (svntk[index_for_correct_m] ==3){
			fHmlsv_emu_minmass_ntr3->Fill((p_secvtx1m+p_l).M(), w[0]);
			fHmlsv_emu_minmass_flow->Fill(2., w[0]);
			}	
		if (svntk[index_for_correct_m] > 3){
			fHmlsv_emu_minmass_ntr4->Fill((p_secvtx1m+p_l).M(), w[0]);
			fHmlsv_emu_minmass_flow->Fill(3., w[0]);
			}


		if( (lid[0] > 0 && bid[index_for_correct] == -5 ) || (lid[0] < 0 && bid[index_for_correct] == 5) ){  
			fHmlsv_emu_deltar_correct->Fill((p_secvtx1+p_l).M(), w[0]);
			if (svntk[index_for_correct] ==2){fHmlsv_emu_deltar_ntr2_correct->Fill((p_secvtx1+p_l).M(), w[0]);}
			if (svntk[index_for_correct] ==3){fHmlsv_emu_deltar_ntr3_correct->Fill((p_secvtx1+p_l).M(), w[0]);}
			if (svntk[index_for_correct] > 3){fHmlsv_emu_deltar_ntr4_correct->Fill((p_secvtx1+p_l).M(), w[0]);}
		}
		
		else {  
			fHmlsv_emu_deltar_wrong->Fill((p_secvtx1+p_l).M(), w[0]);
			if (svntk[index_for_correct] ==2){fHmlsv_emu_deltar_ntr2_wrong->Fill((p_secvtx1+p_l).M(), w[0]);}
			if (svntk[index_for_correct] ==3){fHmlsv_emu_deltar_ntr3_wrong->Fill((p_secvtx1+p_l).M(), w[0]);}
			if (svntk[index_for_correct] >3){fHmlsv_emu_deltar_ntr4_wrong->Fill((p_secvtx1+p_l).M(), w[0]);}
		}

		if( (lid[0] > 0 && bid[index_for_correct_m] == -5 ) || (lid[0] < 0 && bid[index_for_correct_m] == 5) ){  
			fHmlsv_emu_minmass_correct->Fill((p_secvtx1m+p_l).M(), w[0]);
			fHmlsv_emu_minmass_correct_topweight->Fill((p_secvtx1m+p_l).M(), (w[0]*w[6]));
			fHmlsv_emu_minmass_correct_topweight_up->Fill((p_secvtx1m+p_l).M(), (w[0]*w[7]));

			if (nvtx > 0 && nvtx < 11) {fHmlsv_emu_minmass_correct_nvtx_1bin->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (nvtx > 10 && nvtx < 15) {fHmlsv_emu_minmass_correct_nvtx_2bin->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (nvtx > 14 && nvtx < 20) {fHmlsv_emu_minmass_correct_nvtx_3bin->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (nvtx > 20) {fHmlsv_emu_minmass_correct_nvtx_4bin->Fill((p_secvtx1m+p_l).M(), w[0]);}

			if (svntk[index_for_correct_m] ==2){fHmlsv_emu_minmass_ntr2_correct->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (svntk[index_for_correct_m] ==3){fHmlsv_emu_minmass_ntr3_correct->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (svntk[index_for_correct_m] > 3){fHmlsv_emu_minmass_ntr4_correct->Fill((p_secvtx1m+p_l).M(), w[0]);}
		}
		
		else {  
			fHmlsv_emu_minmass_wrong->Fill((p_secvtx1m+p_l).M(), w[0]);
			fHmlsv_emu_minmass_wrong_topweight->Fill((p_secvtx1m+p_l).M(), (w[0]*w[6]));
			fHmlsv_emu_minmass_wrong_topweight_up->Fill((p_secvtx1m+p_l).M(), (w[0]*w[7]));

			if (nvtx > 0 && nvtx < 11) {fHmlsv_emu_minmass_wrong_nvtx_1bin->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (nvtx > 10 && nvtx < 15) {fHmlsv_emu_minmass_wrong_nvtx_2bin->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (nvtx > 14 && nvtx < 20) {fHmlsv_emu_minmass_wrong_nvtx_3bin->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (nvtx > 20) {fHmlsv_emu_minmass_wrong_nvtx_4bin->Fill((p_secvtx1m+p_l).M(), w[0]);}

			if (svntk[index_for_correct_m] ==2){fHmlsv_emu_minmass_ntr2_wrong->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (svntk[index_for_correct_m] ==3){fHmlsv_emu_minmass_ntr3_wrong->Fill((p_secvtx1m+p_l).M(), w[0]);}
			if (svntk[index_for_correct_m] >3){fHmlsv_emu_minmass_ntr4_wrong->Fill((p_secvtx1m+p_l).M(), w[0]);}
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
