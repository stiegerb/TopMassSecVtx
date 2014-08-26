// 421000			= roughD0           x
// 842				= CSD0				x
// 842000		 	= eD0    			0
// 1263000			= muD0 				0
// 443 				= muJ/Psi			0
// 44300			= eJ/Psi			0
// 411				= D+-				x


#ifndef LxyTreeAnalysis_cxx
#define LxyTreeAnalysis_cxx
#include "UserCode/llvv_fwk/interface/LxyTreeAnalysis.h"

#include <TLorentzVector.h>
#include <iostream>

//plot with ./scripts/runPlotter.py lxyplots/ -j test/topss2014/samples_noqcd.json
const float pionmass 			= 	0.1396;
const float kaonmass 			= 	0.4937;
const float electronmass		= 	0.00051;
const float muonmass			=	0.10566;

const float gMassK  = 0.4937;
const float gMassPi = 0.1396;
const float gMassMu = 0.1057;

bool isOppositeSign(int id1, int id2) {
    if(id1*id2 == -211*211) return true;
    if(id1*id2 == 11*211)   return true;
    if(id1*id2 == 13*211)   return true;
    if(id1*id2 == -13*13)   return true;
    if(id1*id2 == -11*13)   return true;
    if(id1*id2 == -11*11)   return true;
    return false;
}

void LxyTreeAnalysis::RunJob(TString filename) {
    TFile *file = TFile::Open(filename, "recreate");
    Begin(file);
    Loop();
    End(file);
}

void LxyTreeAnalysis::Begin(TFile *file) {
    // Anything that has to be done once at the beginning
    file->cd();
    BookHistos();
    BookCharmTree();
}

void LxyTreeAnalysis::End(TFile *file) {
    // Anything that has to be done once at the end
    file->cd();
    WritePlots();
    WriteHistos();
    fCharmInfoTree->Write(fCharmInfoTree->GetName());
    file->Write();
    file->Close();
}

void LxyTreeAnalysis::BookHistos() {
    // Book all the histograms here
    fHMinv2LeadTrk = new TH1D("Minv2LeadTrk", "Minv2LeadTrk (All channels)",
                              100, 0., 10.);
    fHistos.push_back(fHMinv2LeadTrk);
    fHMinv2LeadTrk->SetXTitle("Inv. Mass of in b-jet [GeV]");


    normal1 = new TH1D("normal1", "normal1 (All channels)",
                       100, 2., 4.);
    fHistos.push_back(normal1);
    normal1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV]");


    normal2 = new TH1D("normal2", "normal2 (All channels)",
                       100, 2., 4.);
    fHistos.push_back(normal2);
    normal2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV]");


    normal12 = new TH1D("normalqw", "normal12 (All channels)",
                        100, 2., 4.);
    fHistos.push_back(normal12);
    normal12->SetXTitle("Inv. Mass of J/Psi in hardest two b-jets [GeV]");




    test1 = new TH1D("test1", "test1 (All channels)",
                     100, 2., 4.);
    fHistos.push_back(test1);
    test1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV]");


    test2 = new TH1D("test2", "test2 (All channels)",
                     100, 2., 4.);
    fHistos.push_back(test2);
    test2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV]");


    test12 = new TH1D("test12", "test12 (All channels)",
                      100, 2., 4.);
    fHistos.push_back(test12);
    test12->SetXTitle("Inv. Mass of J/Psi in hardest two b-jets [GeV]");




    angle1 = new TH1D("angle1", "angle1 (All channels)",
                      100, 0., 2.);
    fHistos.push_back(angle1);
    angle1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV]");


    angle2 = new TH1D("angle2", "angle2 (All channels)",
                      100, 0., 2.);
    fHistos.push_back(angle2);
    angle2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV]");


    angle12 = new TH1D("angle12", "angle12 (All channels)",
                       100, 0., 2.);
    fHistos.push_back(angle12);
    angle12->SetXTitle("Inv. Mass of J/Psi in hardest two b-jets [GeV]");




    fHMinvJPsiTrk1 = new TH1D("MinvJPsiTrk1", "MinvJPsiTrk1 (All channels)",
                              100, 2., 4.);
    fHistos.push_back(fHMinvJPsiTrk1);
    fHMinvJPsiTrk1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV]");


    fHMinvJPsiTrk2 = new TH1D("MinvJPsiTrk2", "MinvJPsiTrk2 (All channels)",
                              100, 2., 4.);
    fHistos.push_back(fHMinvJPsiTrk2);
    fHMinvJPsiTrk2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV]");


    fHMinvJPsiTrk12 = new TH1D("MinvJPsiTrk12", "MinvJPsiTrk12 (All channels)",
                               100, 2., 4.);
    fHistos.push_back(fHMinvJPsiTrk12);
    fHMinvJPsiTrk12->SetXTitle("Inv. Mass of J/Psi in hardest two b-jets [GeV]");




    fHMinvJPsiTrke1 = new TH1D("MinvJPsiTrke1", "MinvJPsiTrke1 (All channels)",
                               100,2.,4.);
    fHistos.push_back(fHMinvJPsiTrke1);
    fHMinvJPsiTrke1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV], only electrons");


    fHMinvJPsiTrke2 = new TH1D("MinvJPsiTrke2", "MinvJPsiTrke2 (All channels)",
                               100,2.,4.);
    fHistos.push_back(fHMinvJPsiTrke2);
    fHMinvJPsiTrke2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV], only electrons");


    fHMinvJPsiTrke12 = new TH1D("MinvJPsiTrke12", "MinvJPsiTrke12 (All channels)",
                                100,2.,4.);
    fHistos.push_back(fHMinvJPsiTrke12);
    fHMinvJPsiTrke12->SetXTitle("Inv. Mass of J/Psi in two hardest b-jets [GeV], only electrons");





    fHMinvJPsiTrkmu1 = new TH1D("MinvJPsiTrkmu1", "MinvJPsiTrkmu1 (All channels)",
                                100,2.,4.);
    fHistos.push_back(fHMinvJPsiTrkmu1);
    fHMinvJPsiTrkmu1->SetXTitle("Inv. Mass of J/Psi in hardest b-jet [GeV], only muons");


    fHMinvJPsiTrkmu2 = new TH1D("MinvJPsiTrkmu2", "MinvJPsiTrkmu2 (All channels)",
                                100,2.,4.);
    fHistos.push_back(fHMinvJPsiTrkmu2);
    fHMinvJPsiTrkmu2->SetXTitle("Inv. Mass of J/Psi in second hardest b-jet [GeV], only muons");


    fHMinvJPsiTrkmu12 = new TH1D("MinvJPsiTrkmu12", "MinvJPsiTrkmu12 (All channels)",
                                 100,2.,4.);
    fHistos.push_back(fHMinvJPsiTrkmu12);
    fHMinvJPsiTrkmu12->SetXTitle("Inv. Mass of J/Psi in hardest two b-jets [GeV], only muons");





    fHMinvD0Trk1 = new TH1D("MinvD0Trk1", "MinvD0Trk1 (EMu channel)",
                            100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trk1);
    fHMinvD0Trk1->SetXTitle("Inv. Mass of D0 in hardest b-jet [GeV]");


    fHMinvD0Trk2 = new TH1D("MinvD0Trk2", "MinvD0Trk2 (EMu channel)",
                            100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trk2);
    fHMinvD0Trk2->SetXTitle("Inv. Mass of D0 in second hardest b-jet [GeV]");


    fHMinvD0Trk12 = new TH1D("MinvD0Trk12", "MinvD0Trk12 (EMu channel)",
                             100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trk12);
    fHMinvD0Trk12->SetXTitle("Inv. Mass of D0 in two hardest b-jets [GeV]");





    fHMinvD0Trkchargeselection1 = new TH1D("MinvD0Trkchargeselection1", "MinvD0Trkchargeselection1 (EMu channel)",
                                           100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trkchargeselection1);
    fHMinvD0Trkchargeselection1->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");


    fHMinvD0Trkchargeselection2 = new TH1D("MinvD0Trkchargeselection2", "MinvD0Trkchargeselection2 (EMu channel)",
                                           100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trkchargeselection2);
    fHMinvD0Trkchargeselection2->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");


    fHMinvD0Trkchargeselection12 = new TH1D("MinvD0Trkchargeselection12", "MinvD0Trkchargeselection12 (EMu channel)",
                                            100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trkchargeselection12);
    fHMinvD0Trkchargeselection12->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");





    fHcheckMinvD0Trk1 = new TH1D("checkMinvD0Trk1", "checkMinvD0Trk1 (EMu channel)",
                                 100, 1.6, 2.2);
    fHistos.push_back(fHcheckMinvD0Trk1);
    fHcheckMinvD0Trk1->SetXTitle("Inv. Mass of D0 in hardest b-jet [GeV]");


    fHcheckMinvD0Trk2 = new TH1D("checkMinvD0Trk2", "checkMinvD0Trk2 (EMu channel)",
                                 100, 1.6, 2.2);
    fHistos.push_back(fHcheckMinvD0Trk2);
    fHcheckMinvD0Trk2->SetXTitle("Inv. Mass of D0 in second hardest b-jet [GeV]");


    fHcheckMinvD0Trk12 = new TH1D("checkMinvD0Trk12", "checkMinvD0Trk12 (EMu channel)",
                                  100, 1.6, 2.2);
    fHistos.push_back(fHcheckMinvD0Trk12);
    fHcheckMinvD0Trk12->SetXTitle("Inv. Mass of D0 in two hardest b-jets [GeV]");





    fHcheckMinvD0Trkchargeselection1 = new TH1D("checkMinvD0Trkchargeselection1", "checkMinvD0Trkchargeselection1 (EMu channel)",
            100, 1.6, 2.2);
    fHistos.push_back(fHcheckMinvD0Trkchargeselection1);
    fHcheckMinvD0Trkchargeselection1->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");


    fHcheckMinvD0Trkchargeselection2 = new TH1D("checkMinvD0Trkchargeselection2", "checkMinvD0Trkchargeselection2 (EMu channel)",
            100, 1.6, 2.2);
    fHistos.push_back(fHcheckMinvD0Trkchargeselection2);
    fHcheckMinvD0Trkchargeselection2->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");


    fHcheckMinvD0Trkchargeselection12 = new TH1D("checkMinvD0Trkchargeselection12", "checkMinvD0Trkchargeselection12 (EMu channel)",
            100, 1.6, 2.2);
    fHistos.push_back(fHcheckMinvD0Trkchargeselection12);
    fHcheckMinvD0Trkchargeselection12->SetXTitle("Inv. Mass of D0 in b-jet [GeV], CS");





    fHMinvD0Trkmuon1 = new TH1D("MinvD0Trkmuon1", "MinvD0Trkmuon1 (EMu channel)",
                                100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trkmuon1);
    fHMinvD0Trkmuon1->SetXTitle("Inv. Mass of D0 in hardest b-jet [GeV], CWL");


    fHMinvD0Trkmuon2 = new TH1D("MinvD0Trkmuon2", "MinvD0Trkmuon2 (EMu channel)",
                                100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trkmuon2);
    fHMinvD0Trkmuon2->SetXTitle("Inv. Mass of D0 in second hardest b-jet [GeV], CWL");


    fHMinvD0Trkmuon12 = new TH1D("MinvD0Trkmuon12", "MinvD0Trkmuon12 (EMu channel)",
                                 100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trkmuon12);
    fHMinvD0Trkmuon12->SetXTitle("Inv. Mass of D0 in two hardest b-jets [GeV], CWL");





    fHMinvD0Trkelectron1 = new TH1D("MinvD0Trkelectron1", "MinvD0Trkelectron1 (EMu channel)",
                                    100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trkelectron1);
    fHMinvD0Trkelectron1->SetXTitle("Inv. Mass of D0 in hardest b-jet [GeV], CWL");


    fHMinvD0Trkelectron2 = new TH1D("MinvD0Trkelectron2", "MinvD0Trkelectron2 (EMu channel)",
                                    100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trkelectron2);
    fHMinvD0Trkelectron2->SetXTitle("Inv. Mass of D0 in second hardest b-jet [GeV], CWL");


    fHMinvD0Trkelectron12 = new TH1D("MinvD0Trkelectron12", "MinvD0Trkelectron12 (EMu channel)",
                                     100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trkelectron12);
    fHMinvD0Trkelectron12->SetXTitle("Inv. Mass of D0 in two hardest b-jets [GeV], CWL");




    fHMinvD0Trklepton1 = new TH1D("MinvD0Trklepton1", "MinvD0Trklepton1 (EMu channel)",
                                  100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trklepton1);
    fHMinvD0Trklepton1->SetXTitle("Inv. Mass of D0 in hardest b-jet [GeV], CWL, e mu");


    fHMinvD0Trklepton2 = new TH1D("MinvD0Trklepton2", "MinvD0Trklepton2 (EMu channel)",
                                  100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trklepton2);
    fHMinvD0Trklepton2->SetXTitle("Inv. Mass of D0 in second hardest b-jet [GeV], CWL, e mu");


    fHMinvD0Trklepton12 = new TH1D("MinvD0Trklepton12", "MinvD0Trklepton12 (EMu channel)",
                                   100, 1.6, 2.2);
    fHistos.push_back(fHMinvD0Trklepton12);
    fHMinvD0Trklepton12->SetXTitle("Inv. Mass of D0 in two hardest b-jets [GeV], CWL, e mu");




    fHMinvDplusminusTrk1 = new TH1D("MinvDplusminusTrk1", "MinvDplusminusTrk1 (EMu channel)",
                                    100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrk1);
    fHMinvDplusminusTrk1->SetXTitle("Inv. Mass of D+- in hardest b-jet [GeV]");


    fHMinvDplusminusTrk2 = new TH1D("MinvDplusminusTrk2", "MinvDplusminusTrk2 (EMu channel)",
                                    100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrk2);
    fHMinvDplusminusTrk2->SetXTitle("Inv. Mass of D+- in second hardest b-jet [GeV]");


    fHMinvDplusminusTrk12 = new TH1D("MinvDplusminusTrk12", "MinvDplusminusTrk12 (EMu channel)",
                                     100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrk12);
    fHMinvDplusminusTrk12->SetXTitle("Inv. Mass of D+- in two hardest b-jets [GeV]");



    fHMinvDplusminusTrkelectron1 = new TH1D("MinvDplusminusTrkelectron1", "MinvDplusminusTrkelectron1 (EMu channel)",
                                            100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrkelectron1);
    fHMinvDplusminusTrkelectron1->SetXTitle("Inv. Mass of D+- in hardest b-jet [GeV]");


    fHMinvDplusminusTrkelectron2 = new TH1D("MinvDplusminusTrkelectron2", "MinvDplusminusTrkelectron2 (EMu channel)",
                                            100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrkelectron2);
    fHMinvDplusminusTrkelectron2->SetXTitle("Inv. Mass of D+- in second hardest b-jet [GeV]");


    fHMinvDplusminusTrkelectron12 = new TH1D("MinvDplusminusTrkelectron12", "MinvDplusminusTrkelectron12 (EMu channel)",
            100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrkelectron12);
    fHMinvDplusminusTrkelectron12->SetXTitle("Inv. Mass of D+- in two hardest b-jets [GeV]");



    fHMinvDplusminusTrkmuon1 = new TH1D("MinvDplusminusTrkmuon1", "MinvDplusminusTrkmuon1 (EMu channel)",
                                        100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrkmuon1);
    fHMinvDplusminusTrkmuon1->SetXTitle("Inv. Mass of D+- in hardest b-jet [GeV]");


    fHMinvDplusminusTrkmuon2 = new TH1D("MinvDplusminusTrkmuon2", "MinvDplusminusTrkmuon2 (EMu channel)",
                                        100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrkmuon2);
    fHMinvDplusminusTrkmuon2->SetXTitle("Inv. Mass of D+- in second hardest b-jet [GeV]");


    fHMinvDplusminusTrkmuon12 = new TH1D("MinvDplusminusTrkmuon12", "MinvDplusminusTrkmuon12 (EMu channel)",
                                         100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrkmuon12);
    fHMinvDplusminusTrkmuon12->SetXTitle("Inv. Mass of D+- in two hardest b-jets [GeV]");


    fHMinvDplusminusTrklepton1 = new TH1D("MinvDplusminusTrklepton1", "MinvDplusminusTrklepton1 (EMu channel)",
                                          100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrklepton1);
    fHMinvDplusminusTrklepton1->SetXTitle("Inv. Mass of D+- in hardest b-jet [GeV]");


    fHMinvDplusminusTrklepton2 = new TH1D("MinvDplusminusTrklepton2", "MinvDplusminusTrklepton2 (EMu channel)",
                                          100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrklepton2);
    fHMinvDplusminusTrklepton2->SetXTitle("Inv. Mass of D+- in second hardest b-jet [GeV]");


    fHMinvDplusminusTrklepton12 = new TH1D("MinvDplusminusTrklepton12", "MinvDplusminusTrklepton12 (EMu channel)",
                                           100, 1.6, 2.2);
    fHistos.push_back(fHMinvDplusminusTrklepton12);
    fHMinvDplusminusTrklepton12->SetXTitle("Inv. Mass of D+- in two hardest b-jets [GeV]");


    fHDiTrkInvMass = new TH1D("DiTrkInvMass", "DiTrkInvMass (EMu channel)",
                              100, 1.7, 2.);
    fHistos.push_back(fHDiTrkInvMass);
    fHDiTrkInvMass->SetXTitle("Track-track inv. Mass in b-jet [GeV]");

    fHDiMuInvMass = new TH1D("DiMuInvMass", "DiMuInvMass (EMu channel)",
                             100, 2., 4.);
    fHistos.push_back(fHDiMuInvMass);
    fHDiMuInvMass->SetXTitle("Mu/mu inv. Mass in b-jet [GeV]");

    fHJPsiKInvMass = new TH1D("JPsiKInvMass", "JPsiKInvMass (EMu channel)",
                              100, 4.5, 6.);
    fHistos.push_back(fHJPsiKInvMass);
    fHJPsiKInvMass->SetXTitle("Mu/mu/K inv. Mass in b-jet [GeV]");


    fHEb1_emu = new TH1D("Eb1_emu", "E_b1 in EMu channel",
                         100, 30., 500.);
    fHistos.push_back(fHEb1_emu);
    fHEb1_emu->SetXTitle("Energy of first b-jet [GeV]");



    fHmlSv_mu = new TH1D("mlSv_mu", "Lepton/SecVtx Mass in Mu channel",
                         100, 0., 150.);
    fHistos.push_back(fHmlSv_mu);
    fHmlSv_mu->SetXTitle("Lepton/SecVtx mass [GeV]");

    // Call Sumw2() for all of them
    std::vector<TH1*>::iterator h;
    for(h = fHistos.begin(); h != fHistos.end(); ++h) {
        (*h)->Sumw2();
    }
}

void LxyTreeAnalysis::BookCharmTree() {
    fCharmInfoTree = new TTree("CharmInfo", "Charm Info Tree");
    fCharmInfoTree->Branch("CandType",     &fTCandType,     "CandType/I");
    fCharmInfoTree->Branch("CandMass",     &fTCandMass,     "CandMass/F");
    fCharmInfoTree->Branch("CandPt",       &fTCandPt,       "CandPt/F");
    fCharmInfoTree->Branch("CandPtRel",    &fTCandPtRel,    "CandPtRel/F");
    fCharmInfoTree->Branch("CandDeltaR",   &fTCandDeltaR,   "CandDeltaR/F");
    fCharmInfoTree->Branch("JetPt",        &fTJetPt,        "JetPt/F");
    fCharmInfoTree->Branch("SumPtCharged", &fTSumPtCharged, "SumPtCharged/F");
}

void LxyTreeAnalysis::ResetCharmTree() {
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
                                    int ind2, float mass2) {
    // Check that indices make sense
    if(jetindex < 0 || ind1 < 0 || ind2 < 0) return;
    if(jetindex >= nj || ind1 >= npf || ind2 >= npf) return;

    fTCandType = type;
    TLorentzVector p_track1, p_track2, p_cand, p_jet;
    p_track1.SetPtEtaPhiM(pfpt[ind1], pfeta[ind1], pfphi[ind1], mass1);
    p_track2.SetPtEtaPhiM(pfpt[ind2], pfeta[ind2], pfphi[ind2], mass2);
    p_cand = p_track1+p_track2;
    p_jet.SetPtEtaPhiM(jpt[jetindex], jeta[jetindex], jphi[jetindex], 0.);

    fTCandMass     = p_cand.M();
    fTCandPt       = p_cand.Pt();

    //ptrel
    float jet2=pow(p_jet.P(),2);
    float candXjet2=pow(p_cand*p_jet,2);
    float pLrel2=candXjet2/jet2;
    float cand2=pow(p_cand.P(),2);
    float pTrel2=cand2-pLrel2;
    fTCandPtRel    = (pTrel2 > 0) ? std::sqrt(pTrel2) : 0.0;

    fTCandDeltaR   = p_cand.DeltaR(p_jet);
    fTJetPt        = jpt[jetindex];
    fTSumPtCharged = 0.;
    for (int i = 0; i < npf; ++i) {
        if (pfjetidx[i] != jetindex) continue;
        fTSumPtCharged += pfpt[i];
    }

    fCharmInfoTree->Fill();
    return;
}

void LxyTreeAnalysis::WriteHistos() {
    // Write all histos to file, then delete them
    std::vector<TH1*>::iterator h;
    for( h = fHistos.begin(); h != fHistos.end(); ++h) {
        (*h)->Write((*h)->GetName());
        (*h)->Delete();
    }
}

void LxyTreeAnalysis::fillJPsiHists(int jetindex, TH1D*& a, TH1D*& b, TH1D*& c//, TH1D*& d, TH1D*& e, TH1D*& f
                                   ) {

    float maxcsv = -1.;
    int maxind=-1;
    float second_max=-1.0;
    int second_maxind=-1;

    for(int k = 0; k < nj; k++) {
        // use >= n not just > as max and second_max can hav same value. Ex:{1,2,3,3}
        if(jcsv[k] >= maxcsv) {
            second_max=maxcsv;
            maxcsv=jcsv[k];
            maxind=k;
            second_maxind=maxind;
        }
        else if(jcsv[k] > second_max) {
            second_max=jcsv[k];
            second_maxind=k;
        }
    }


    TLorentzVector p_track1, p_track2;

    for (int i = 0; i < npf; ++i)
    {
        if (pfjetidx[i]!= jetindex) {
            continue;    //select the most probable b-jet
        }
        if (abs(pfid[i])!=13 && abs(pfid[i]) != 11 ) {
            continue;    //select a muon or electron
        }
        for (int j = 0; j < npf; ++j) //find another muon or electron
        {
            if(pfjetidx[j]!=pfjetidx[i]) {
                continue;    //select the most probable b-jet
            }
            if(pfid[j]*pfid[i]!=-169 && pfid[j]*pfid[i]!=-121) {
                continue;    // let both electrons or muons have opposite charge
            }

            float trackmass = 0.105;
            if(abs(pfid[j]*pfid[i]) == 121) {
                trackmass = 0.;
            }
            p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], trackmass);			 // Calculate four vector
            p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], trackmass);

            if (abs(pfid[i])==11) {
                a->	Fill((p_track1+p_track2).M(), w[0]);
                if ((p_track1+p_track2).M()>2.5 && (p_track1+p_track2).M()<3.5) {
                    FillCharmTree(443, jetindex, i, trackmass, j, trackmass);
                }
            }
            if (abs(pfid[i])==13) {
                b->	Fill((p_track1+p_track2).M(), w[0]);
                if ((p_track1+p_track2).M()>2.5 && (p_track1+p_track2).M()<3.5) {
                    FillCharmTree(443*100, jetindex, i, trackmass, j, trackmass);
                }
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





void LxyTreeAnalysis::fillMuD0Hists(int jetindex, TH1D*& histo, TH1D*& histo2, float ptmin, float maxdr, int lepflav) {
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
            //FillCharmTree(421, jetindex, i, pionmass, j, kaonmass);

            for (int k = 0; k < npf; ++k)
            {
                if(pfjetidx[k] != jetindex) continue;
                if(pfpt[k] < ptmin) continue;
                if(abs(pfid[k]) != lepflav) continue; // will exclude i and j also

                if( ( pfid[k] == lepflav && pfid[j] == -211 )  || ( pfid[k] == -lepflav && pfid[j] == 211 ) ) // mu- K-
                {
                    histo2->Fill((p_track1+p_track2).M());
                }
                else {
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

    for(int k = 0; k < nj; k++) {
        // use >= n not just > as max and second_max can hav same value. Ex:{1,2,3,3}
        if(jcsv[k] >= maxcsv) {
            second_max=maxcsv;
            maxcsv=jcsv[k];
            maxind=k;
            second_maxind=maxind;
        }
        else if(jcsv[k] > second_max) {
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
        {
            break;
        }
    }

    for (int i = r; i < r+5; ++i)
    {
        if (pfjetidx[i]!= jetindex) {
            continue;    //select the first b-jet
        }
        if (abs(pfid[i])!=211) {
            continue;    //select a kaon or pion
        }
        for (int j = i+1; j < r+5; ++j) //find another kaon or pion
        {
            if(pfjetidx[j]!=jetindex) {
                continue;    //select most probable b-jet
            }
            if(pfid[j]*pfid[i]!=-211*211) {
                continue;
            }
            //TLorentzVector p_track1, p_track2; // Calculate four vector

            p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], pionmass);// Calculate four vector
            p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], kaonmass);

            if (p_track1.DeltaR(p_track2)>0.2) {
                continue;
            }

            normal->Fill((p_track1+p_track2).M(), w[0]);

            p_track1.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], kaonmass);// Calculate four vector
            p_track2.SetPtEtaPhiM(pfpt[j], pfeta[j], pfphi[j], pionmass);

            if (p_track1.DeltaR(p_track2)>0.2) {
                continue;
            }

            normal->Fill((p_track1+p_track2).M(), w[0]);

        }
    }


// permutations
    int p1[] = {r+2, 	r+2, 	r+1};
    int p2[] = {r+1, 	r, 		r};
    int p3[] = {r, 		r+1, 	r+2};

    if (pfjetidx[r+2]!=jetindex ) {
        return;
    }



    for (int p = 0; p < 3; ++p)
    {
        int pf1id=p1[p];
        int pf2id=p2[p];
        int pf3id=p3[p];



        if (pfid[pf1id]*pfid[pf2id]!=-44521) continue;

        p_track1.SetPtEtaPhiM(pfpt[pf1id], pfeta[pf1id], pfphi[pf1id], pionmass);	// Calculate four vector
        p_track2.SetPtEtaPhiM(pfpt[pf2id], pfeta[pf2id], pfphi[pf2id], kaonmass);

        g->Fill((p_track1+p_track2).M(), w[0]);										// does not make sense can be ignored
        if ((p_track1+p_track2).M()>1.65 && (p_track1+p_track2).M()<2) {
            FillCharmTree(421*1000, jetindex, p1[p], pionmass, p2[p], kaonmass);
        }



        std::vector<int> event;
        std::vector<int> instance;

        if (abs(pfid[pf3id]+pfid[pf2id])==422) // second/third have same sign
        {

            // int i=0;

            if ((p_track1+p_track2).M()>1.8 && (p_track1+p_track2).M()<1.92) {

                c->Fill((p_track1.DeltaR(p_track2), w[0]));


                // event.push_back(event);
                // event.push_back(event);
                // instance.push_back(pf1id);
                // instance.push_back(pf2id);

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
            // p_track1.SetPtEtaPhiM(pfpt[a], 		[a], pfphi[a], pionmass);	// Calculate four vector
            //p_track2.SetPtEtaPhiM(pfpt[b], pfeta[b], pfphi[b], kaonmass);
            //test->Fill((p_track1+p_track2).M(), w[0]);
            // 	}

            o->Fill((p_track1+p_track2).M(), w[0]);
            if ((p_track1+p_track2).M()>1.66 && (p_track1+p_track2).M()<2) {
                FillCharmTree(421*2, jetindex, p1[p], pionmass, p2[p], kaonmass);
            }																	// plots both mass combinations
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
                if ((p_track1+p_track2).M()>1.6 && (p_track1+p_track2).M()<2.5) {
                    FillCharmTree(421*2000, jetindex, p1[p], pionmass, p2[p], kaonmass);
                }
                s->Fill((p_track1+p_track2).M(), w[0]);
            }

            if (pfid[pf2id]/abs(pfid[pf2id])==pfid[t]/-11)
            {
                v->Fill((p_track1+p_track2).M(), w[0]);
                if ((p_track1+p_track2).M()>1.6 && (p_track1+p_track2).M()<2.5) {
                    FillCharmTree(421*3000, jetindex, p1[p], pionmass, p2[p], kaonmass);
                }
                s->Fill((p_track1+p_track2).M(), w[0]);
            }

        }
    }
    ev=ev+1;
}



void LxyTreeAnalysis::fillDplusminusHists(int jetindex, TH1D*& s, TH1D*& q, TH1D*& v, TH1D*& g) {
    TLorentzVector p_track1, p_track2, p_track3;

    float maxcsv = -1.;
    int maxind=-1;
    float second_max=-1.0;
    int second_maxind=-1;

    for(int k = 0; k < nj; k++) {
        // use >= n not just > as max and second_max can hav same value. Ex:{1,2,3,3}
        if(jcsv[k] >= maxcsv) {
            second_max=maxcsv;
            maxcsv=jcsv[k];
            maxind=k;
            second_maxind=maxind;
        }
        else if(jcsv[k] > second_max) {
            second_max=jcsv[k];
            second_maxind=k;
        }
    }

    int r = 0;
    for (r = 0; r < npf; ++r)
    {
        if (pfjetidx[r]==jetindex)
        {
            break;
        }
    }

    // permutations
    int p1[] = {r+2, r+2, r+1};
    int p2[] = {r+1, r, r};
    int p3[] = {r, r+1, r+2};


    if (abs(pfid[r]+pfid[r+1]+pfid[r+2])!=211) {
        return;    // not all the same charge
    }

    if (pfjetidx[r+2]!=jetindex ) {
        return;
    }

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

                if ((p_track1+p_track2).M()>1.6 && (p_track1+p_track2).M()<2.5) {
                    FillCharmTree(411, jetindex, p1[p], kaonmass, p2[p], pionmass);
                }
            }



            p_track1.SetPtEtaPhiM(pfpt[pf1id], pfeta[pf1id], pfphi[pf1id], pionmass);
            p_track2.SetPtEtaPhiM(pfpt[pf2id], pfeta[pf2id], pfphi[pf2id], kaonmass);

            if (pfid[pf3id]+pfid[pf2id]==0)
            {

                p_track3.SetPtEtaPhiM(pfpt[pf3id], pfeta[pf3id], pfphi[pf3id], pionmass);

                s->Fill((p_track1+p_track2+p_track3).M(), w[0]);
                if ((p_track1+p_track2).M()>1.6 && (p_track1+p_track2).M()<2.5) {
                    FillCharmTree(411, second_maxind, p1[p], pionmass, p2[p], kaonmass);
                }
            }


        }

        for (int t = 0; t < npf; ++t)
        {
            if (pfjetidx[t]!=jetindex) continue;
            if (t == pf1id) continue;
            if (t == pf2id) continue;


            if (abs(pfid[t]) != 13 && abs(pfid[t]) != 11) continue;

            if (pfid[pf2id]/abs(pfid[pf2id])==pfid[t]/13)
            {
                q->Fill((p_track1+p_track2).M(), w[0]);
                if ((p_track1+p_track2).M()>1.6 && (p_track1+p_track2).M()<2.5) {
                    FillCharmTree(421*5000, jetindex, p1[p], pionmass, p2[p], kaonmass);
                }
                g->Fill((p_track1+p_track2).M(), w[0]);
            }

            if (pfid[pf2id]/abs(pfid[pf2id])==pfid[t]/11)
            {
                v->Fill((p_track1+p_track2).M(), w[0]);
                if ((p_track1+p_track2).M()>1.6 && (p_track1+p_track2).M()<2.5) {
                    FillCharmTree(421*8000, jetindex, p1[p], pionmass, p2[p], kaonmass);
                }
                g->Fill((p_track1+p_track2).M(), w[0]);
            }

        }







    }


}






void LxyTreeAnalysis::analyze() {
    // Called once per event
    FillPlots();
    ResetCharmTree();

    float maxcsv = -1.;
    int maxind=-1;
    float second_max=-1.0;
    int second_maxind=-1;

    for(int k = 0; k < nj; k++) {
        // use >= n not just > as max and second_max can hav same value. Ex:{1,2,3,3}
        if(jcsv[k] >= maxcsv) {
            second_max=maxcsv;
            maxcsv=jcsv[k];
            maxind=k;
            second_maxind=maxind;
        }
        else if(jcsv[k] > second_max) {
            second_max=jcsv[k];
            second_maxind=k;
        }
    }





    TLorentzVector p_track1, p_track2, p_track3;



    if 		(abs(evcat) == 11*13 || // emu
             (abs(evcat) == 11*11 && metpt > 40.) || // ee
             (abs(evcat) == 13*13 && metpt > 40.) || // mumu
             (abs(evcat) == 11 && nj > 3) ||			// singleelectron
             (abs(evcat) == 13 && nj > 3)  ) {		// singlemuon
//---------------------------------------------------------------------------------------------------------- J/Psi ( + K)
//int leptonindex1;
//int leptonindex2;
        fillJPsiHists(maxind,        fHMinvJPsiTrke1, 	fHMinvJPsiTrkmu1, 	fHMinvJPsiTrk1);
        fillJPsiHists(second_maxind, fHMinvJPsiTrke2, 	fHMinvJPsiTrkmu2, 	fHMinvJPsiTrk2);
        fillJPsiHists(maxind,        fHMinvJPsiTrke12, 	fHMinvJPsiTrkmu12, 	fHMinvJPsiTrk12);
        fillJPsiHists(second_maxind, fHMinvJPsiTrke12, 	fHMinvJPsiTrkmu12, 	fHMinvJPsiTrk12);




//---------------------------------------------------------------------------------------------------------- D0
        fillD0Hists(maxind, 		fHMinvD0Trk1, 	 	fHMinvD0Trkchargeselection1, 	fHMinvD0Trkmuon1, 	fHMinvD0Trklepton1, 	fHMinvD0Trkelectron1, 	normal1,	angle1);//, 	test1);
        fillD0Hists(second_maxind, 	fHMinvD0Trk2, 		fHMinvD0Trkchargeselection2, 	fHMinvD0Trkmuon2,	fHMinvD0Trklepton2,		fHMinvD0Trkelectron2, 	normal2,	angle2);//, 	test2);
        fillD0Hists(maxind, 		fHMinvD0Trk12,	 	fHMinvD0Trkchargeselection12, 	fHMinvD0Trkmuon12,	fHMinvD0Trklepton12,	fHMinvD0Trkelectron12, 	normal12,	angle12);//,	test12);
        fillD0Hists(second_maxind, 	fHMinvD0Trk12, 	 	fHMinvD0Trkchargeselection12, 	fHMinvD0Trkmuon12,	fHMinvD0Trklepton12,	fHMinvD0Trkelectron12, 	normal12, 	angle12);//,	test12);


// fillMuD0Hists(maxind,        fHcheckMinvD0Trk1, 		fHcheckMinvD0Trkchargeselection1, 	1.0, 	0.5);
// fillMuD0Hists(second_maxind, fHcheckMinvD0Trk2, 		fHcheckMinvD0Trkchargeselection2, 	1.0, 	0.5);
// fillMuD0Hists(maxind,        fHcheckMinvD0Trk12, 		fHcheckMinvD0Trkchargeselection12, 	1.0, 	0.5);
// fillMuD0Hists(second_maxind, fHcheckMinvD0Trk12, 		fHcheckMinvD0Trkchargeselection12, 	1.0, 	0.5);

//------------------------------------------------------------------------------------------------------------------------- B+

        fillDplusminusHists(maxind,fHMinvDplusminusTrk1, fHMinvDplusminusTrkelectron1, fHMinvDplusminusTrkmuon1, fHMinvDplusminusTrklepton1);
        fillDplusminusHists(second_maxind,fHMinvDplusminusTrk2, fHMinvDplusminusTrkelectron2, fHMinvDplusminusTrkmuon2, fHMinvDplusminusTrklepton2);
        fillDplusminusHists(maxind,fHMinvDplusminusTrk12, fHMinvDplusminusTrkelectron12, fHMinvDplusminusTrkmuon12, fHMinvDplusminusTrklepton12);
        fillDplusminusHists(second_maxind,fHMinvDplusminusTrk12, fHMinvDplusminusTrkelectron12, fHMinvDplusminusTrkmuon12, fHMinvDplusminusTrklepton12);


        //----------------------------------------------------------------------------------------------------------  Lead ions

   }
}

void LxyTreeAnalysis::Loop() {
    if (fChain == 0) return;

    Long64_t nentries = fChain->GetEntriesFast();
    if( fMaxevents > 0) nentries = TMath::Min(fMaxevents,nentries);

    Long64_t nbytes = 0, nb = 0;
    for (Long64_t jentry=0; jentry<nentries; jentry++) {
        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0) break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;

        if (jentry%500 == 0) {
            printf("\r [ %3d/100 ]", int(100*float(jentry)/float(nentries)));
            std::cout << std::flush;
        }

        // std::cout << jentry << "\t" << event << std::endl;
        analyze();

    }
    std::cout << "\r [   done  ]" << std::endl;
}

#endif
