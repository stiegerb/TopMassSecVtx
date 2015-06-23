#ifndef LxyTreeAnalysis_cxx
#define LxyTreeAnalysis_cxx
#include "UserCode/TopMassSecVtx/interface/LxyTreeAnalysis.h"
#include "UserCode/TopMassSecVtx/interface/MacroUtils.h"

#include "Math/VectorUtil.h"

#include <TLorentzVector.h>
#include <iostream>

const float gMassK  = 0.4937;
const float gMassPi = 0.1396;
const float gMassMu = 0.1057;

const float gCSVWPMedium = 0.783;
const float gCSVWPLoose = 0.405;

const int njetbins = 6;
const int nsvbins = 4;

struct SVLInfo { // needed for sorting...
    unsigned counter;
    int lepindex;
    int svindex;
    int combcat;
    float svlmass, svlmass_rot;
    float svldeltar, svldeltar_rot;
    float svlmass_sf[2];
    float umetweights[3];
    float btagweights[3];
    int jesweights[5];
    float bfragweights[6];
};
bool compare_mass (SVLInfo svl1, SVLInfo svl2) {
    return (svl1.svlmass < svl2.svlmass);
}
bool compare_deltar (SVLInfo svl1, SVLInfo svl2) {
    return (svl1.svldeltar < svl2.svldeltar);
}
bool compare_mass_rot (SVLInfo svl1, SVLInfo svl2) {
    return (svl1.svlmass_rot < svl2.svlmass_rot);
}
bool compare_deltar_rot (SVLInfo svl1, SVLInfo svl2) {
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
        ntries++;
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


void LxyTreeAnalysis::RunJob(TString filename) {
    TFile *file = TFile::Open(filename, "recreate");

    //add PDF information, if relevant
    fPDFInfo=0;
    TString curFile=fChain->GetCurrentFile()->GetName();
    if(curFile.Contains("/MC") && !curFile.Contains("syst/") && !curFile.Contains("mass_scan/")) {
        // FIXME: this is a potential bug. If the path contains "syst" or "mass_scan" for some reason
        //        no pdf weights will be produced.
        TString pdfFileName=curFile;
        pdfFileName=pdfFileName.ReplaceAll("/MC","/pdf/MC");
        pdfFileName=pdfFileName.ReplaceAll(".root","_pdf.root");
        fPDFInfo=new PDFInfo(pdfFileName,"CT10");
        if(fPDFInfo->numberPDFs()) {
            std::cout << "Read "
                      << fPDFInfo->numberPDFs()
                      << " PDF variations from "
                      << pdfFileName
                      << " (have fun with those)"
                      << std::endl;
        }
        else {
            delete fPDFInfo;
            fPDFInfo=0;
        }
    }

    //do the analysis
    Begin(file);
    Loop();
    End(file);
}

//
void LxyTreeAnalysis::Begin(TFile *file)
{
    // Anything that has to be done once at the beginning
    file->cd();
    BookHistos();
    BookCharmTree();
    BookSVLTree();
    BookDileptonTree();
    fTXSWeight = fProcessNorm;
}

void LxyTreeAnalysis::End(TFile *file)
{
    // Anything that has to be done once at the end
    file->cd();
    WritePlots();
    WriteHistos();
    fCharmInfoTree->Write(fCharmInfoTree->GetName());
    fSVLInfoTree->Write(fSVLInfoTree->GetName());
    fDileptonInfoTree->Write(fDileptonInfoTree->GetName());
    file->Write();
    file->Close();
}

void LxyTreeAnalysis::BookCharmHistos() {
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


    fHMDsm = new TH1D("Dsm", "Dsm",100, 1.8, 2.4);
    fHistos.push_back(fHMDsm);
    fHMDsm->SetXTitle("m(K#pi#pi) [GeV]");

    fHDMDsmD0loose = new TH1D("DMDsmD0loose", "DMDsmD0, 100 MeV mass window on D0",100, 0.135, 0.17);
    fHistos.push_back(fHDMDsmD0loose);
    fHDMDsmD0loose->SetXTitle("m(K#pi#pi) - m(K#pi) [GeV]");

    fHDMDsmD0 = new TH1D("DMDsmD0", "DMDsmD0, 50 MeV mass window on D0",100, 0.135, 0.17);
    fHistos.push_back(fHDMDsmD0);
    fHDMDsmD0->SetXTitle("m(K#pi#pi) - m(K#pi) [GeV]");


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
void LxyTreeAnalysis::BookSVLHistos() {
    fHNJets    = new TH1D("NJets",    "NJets (inclusive)", njetbins, 2, 2+njetbins);
    fHistos.push_back(fHNJets);
    fHNJets->SetXTitle("Jet Multiplicity");
    fHNJets_e  = new TH1D("NJets_e",  "NJets (single e)",  njetbins, 2, 2+njetbins);
    fHistos.push_back(fHNJets_e);
    fHNJets_e->SetXTitle("Jet Multiplicity");
    fHNJets_m  = new TH1D("NJets_m",  "NJets (single mu)", njetbins, 2, 2+njetbins);
    fHistos.push_back(fHNJets_m);
    fHNJets_m->SetXTitle("Jet Multiplicity");
    fHNJets_ee = new TH1D("NJets_ee", "NJets (ee)",        njetbins, 2, 2+njetbins);
    fHistos.push_back(fHNJets_ee);
    fHNJets_ee->SetXTitle("Jet Multiplicity");
    fHNJets_mm = new TH1D("NJets_mm", "NJets (mumu)",      njetbins, 2, 2+njetbins);
    fHistos.push_back(fHNJets_mm);
    fHNJets_mm->SetXTitle("Jet Multiplicity");
    fHNJets_em = new TH1D("NJets_em", "NJets (emu)",       njetbins, 2, 2+njetbins);
    fHistos.push_back(fHNJets_em);
    fHNJets_em->SetXTitle("Jet Multiplicity");

    fHNSVJets    = new TH1D("NSVJets",    "NJets with SV (inclusive)", nsvbins, 1, 1+nsvbins);
    fHistos.push_back(fHNSVJets);
    fHNSVJets->SetXTitle("SV Multiplicity");
    fHNSVJets_e  = new TH1D("NSVJets_e",  "NJets with SV (single e)",  nsvbins, 1, 1+nsvbins);
    fHistos.push_back(fHNSVJets_e);
    fHNSVJets_e->SetXTitle("SV Multiplicity");
    fHNSVJets_m  = new TH1D("NSVJets_m",  "NJets with SV (single mu)", nsvbins, 1, 1+nsvbins);
    fHistos.push_back(fHNSVJets_m);
    fHNSVJets_m->SetXTitle("SV Multiplicity");
    fHNSVJets_ee = new TH1D("NSVJets_ee", "NJets with SV (ee)",        nsvbins, 1, 1+nsvbins);
    fHistos.push_back(fHNSVJets_ee);
    fHNSVJets_ee->SetXTitle("SV Multiplicity");
    fHNSVJets_mm = new TH1D("NSVJets_mm", "NJets with SV (mumu)",      nsvbins, 1, 1+nsvbins);
    fHistos.push_back(fHNSVJets_mm);
    fHNSVJets_mm->SetXTitle("SV Multiplicity");
    fHNSVJets_em = new TH1D("NSVJets_em", "NJets with SV (emu)",       nsvbins, 1, 1+nsvbins);
    fHistos.push_back(fHNSVJets_em);
    fHNSVJets_em->SetXTitle("SV Multiplicity");

    fHNbJets    = new TH1D("NbJets",    "NbJets (inclusive)", nsvbins, 0, nsvbins);
    fHistos.push_back(fHNbJets);
    fHNbJets->SetXTitle("CSV med-tagged Jet Multiplicity");
    fHNbJets_e  = new TH1D("NbJets_e",  "NbJets (single e)",  nsvbins, 0, nsvbins);
    fHistos.push_back(fHNbJets_e);
    fHNbJets_e->SetXTitle("CSV med-tagged Jet Multiplicity");
    fHNbJets_m  = new TH1D("NbJets_m",  "NbJets (single mu)", nsvbins, 0, nsvbins);
    fHistos.push_back(fHNbJets_m);
    fHNbJets_m->SetXTitle("CSV med-tagged Jet Multiplicity");
    fHNbJets_ee = new TH1D("NbJets_ee", "NbJets (ee)",        nsvbins, 0, nsvbins);
    fHistos.push_back(fHNbJets_ee);
    fHNbJets_ee->SetXTitle("CSV med-tagged Jet Multiplicity");
    fHNbJets_mm = new TH1D("NbJets_mm", "NbJets (mumu)",      nsvbins, 0, nsvbins);
    fHistos.push_back(fHNbJets_mm);
    fHNbJets_mm->SetXTitle("CSV med-tagged Jet Multiplicity");
    fHNbJets_em = new TH1D("NbJets_em", "NbJets (emu)",       nsvbins, 0, nsvbins);
    fHistos.push_back(fHNbJets_em);
    fHNbJets_em->SetXTitle("CSV med-tagged Jet Multiplicity");

    fHMET    = new TH1D("MET",    "MET (inclusive)", 100, 0, 200.);
    fHistos.push_back(fHMET);
    fHMET->SetXTitle("Missing ET [GeV]");
    fHMET_e  = new TH1D("MET_e",  "MET (single e)",  100, 0, 200.);
    fHistos.push_back(fHMET_e);
    fHMET_e->SetXTitle("Missing ET [GeV]");
    fHMET_m  = new TH1D("MET_m",  "MET (single mu)", 100, 0, 200.);
    fHistos.push_back(fHMET_m);
    fHMET_m->SetXTitle("Missing ET [GeV]");
    fHMET_ee = new TH1D("MET_ee", "MET (ee)",        80, 40.,200.);
    fHistos.push_back(fHMET_ee);
    fHMET_ee->SetXTitle("Missing ET [GeV]");
    fHMET_mm = new TH1D("MET_mm", "MET (mumu)",      80, 40.,200.);
    fHistos.push_back(fHMET_mm);
    fHMET_mm->SetXTitle("Missing ET [GeV]");
    fHMET_em = new TH1D("MET_em", "MET (emu)",       100, 0, 200.);
    fHistos.push_back(fHMET_em);
    fHMET_em->SetXTitle("Missing ET [GeV]");

    fHMjj  = new TH1D("Mjj",    "Mjj (inclusive);M_{jj} [GeV]",100,0,250);
    fHistos.push_back(fHMjj);
    fHMjj_e  = new TH1D("Mjj_e",    "Mjj (single e);M_{jj} [GeV]",100,0,250);
    fHistos.push_back(fHMjj_e);
    fHMjj_m  = new TH1D("Mjj_m",    "Mjj (single mu);M_{jj} [GeV]",100,0,250);
    fHistos.push_back(fHMjj_m);
    fHMT  = new TH1D("Mt",    "MT (inclusive);M_{T} [GeV]",100,0,250);
    fHistos.push_back(fHMT);
    fHMT_e  = new TH1D("Mt_e",    "MT (single e);M_{T} [GeV]",100,0,250);
    fHistos.push_back(fHMT_e);
    fHMT_m  = new TH1D("Mt_m",    "MT (single mu);M_{T} [GeV]",100,0,250);
    fHistos.push_back(fHMT_m);

    fHDY_mll_ee = new TH1D("DY_mll_ee", "m(ll) in DY ee control", 100, 60., 120.);
    fHistos.push_back(fHDY_mll_ee);
    fHDY_mll_ee->SetXTitle("Dilepton invariant mass [GeV]");
    fHDY_mll_mm = new TH1D("DY_mll_mm", "m(ll) in DY mm control", 100, 60., 120.);
    fHistos.push_back(fHDY_mll_mm);
    fHDY_mll_mm->SetXTitle("Dilepton invariant mass [GeV]");
    fHDY_met_ee = new TH1D("DY_met_ee", "MET in DY ee control",   100, 0., 100.);
    fHistos.push_back(fHDY_met_ee);
    fHDY_met_ee->SetXTitle("Missing ET [GeV]");
    fHDY_met_mm = new TH1D("DY_met_mm", "MET in DY mm control",   100, 0., 100.);
    fHistos.push_back(fHDY_met_mm);
    fHDY_met_mm->SetXTitle("Missing ET [GeV]");
}
void LxyTreeAnalysis::BookHistos() {
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
void LxyTreeAnalysis::WriteHistos() {
    // Write all histos to file, then delete them
    std::vector<TH1*>::iterator h;
    for( h = fHistos.begin(); h != fHistos.end(); ++h) {
        (*h)->Write((*h)->GetName());
        (*h)->Delete();
    }
}


void LxyTreeAnalysis::BookCharmTree() {
    fCharmInfoTree = new TTree("CharmInfo", "Charm Info Tree");
    fCharmInfoTree->Branch("EvCat",        &fTCharmEvCat,   "EvCat/I");
    fCharmInfoTree->Branch("Weight",        fTWeight,       "Weight[11]/F");
    fCharmInfoTree->Branch("XSWeight",     &fTXSWeight,     "XSWeight/F");
    fCharmInfoTree->Branch("BFragWeight",   fTSVBfragWeight,"BFragWeight[6]/F");
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
    for (int i=0; i<6; i++) fTSVBfragWeight[i] = -99.99;
}

int LxyTreeAnalysis::firstTrackIndex(int jetindex) {
    // Find index of the first track in this jet
    int result = 0;
    for (result = 0; result < npf; ++result) {
        if (pfjetidx[result]==jetindex) {
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
                                    float hardpt, float softpt) {
    FillCharmTree(type, jind, p_cand.M(), p_cand, p_jet, hardpt, softpt);
    return;
}
void LxyTreeAnalysis::FillCharmTree(int type, int jind,
                                    float candmass,
                                    TLorentzVector p_cand,
                                    TLorentzVector p_jet,
                                    float hardpt, float softpt) {
    fTCandType   = type;
    fTCharmEvCat = evcat;
    fTCandMass  = candmass;
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

    fTSVBfragWeight[0] = bwgt[jind][0];
    fTSVBfragWeight[1] = bwgt[jind][1];
    fTSVBfragWeight[2] = bwgt[jind][2];
    fTSVBfragWeight[3] = bwgt[jind][3];
    fTSVBfragWeight[4] = bwgt[jind][4];
    fTSVBfragWeight[5] = bwgt[jind][5];

    fCharmInfoTree->Fill();
    return;
}

void LxyTreeAnalysis::fillJPsiHists(int jetindex) {
    if(jetindex < 0) return;
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

            for (int tk3 = 0; tk3 < npf; ++tk3) { // look for a third track
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
void LxyTreeAnalysis::fillD0Hists(int jetindex) {
    if(jetindex < 0) return;
    TLorentzVector p_track1, p_track2;
    int nstart = firstTrackIndex(jetindex);

    for (int i = nstart; i < nstart+5; ++i) {
        if (pfjetidx[i]!= jetindex) continue; // select the jet
        // (in case less then 5 tracks in this jet)
        if (abs(pfid[i])!=211) continue; // not a lepton

        for (int j = i+1; j < nstart+5; ++j) { //find another kaon or pion
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

    // permutations of hardest three tracks
    // including interchanging them!
    int p1[] = {nstart,   nstart,   nstart+1, nstart+1, nstart+2, nstart+2};
    int p2[] = {nstart+1, nstart+2, nstart+2, nstart,   nstart,   nstart+1};

    for (int p = 0; p < 6; ++p) {
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

        // Look for a lepton
        for (int tk3 = 0; tk3 < npf; ++tk3) {
            if (pfjetidx[tk3]!=jetindex) continue;
            if (tk3 == tk1) continue;
            if (tk3 == tk2) continue;

            if( abs(pfid[tk3]) != 13 && abs(pfid[tk3]) != 11) continue;

            if( pfid[tk2]/abs(pfid[tk2]) == -pfid[tk3]/abs(pfid[tk3]) ) {
                // Kaon and lepton have same charge
                // I.e. correct mass assumption
                fHMD0lep->Fill(mass12, w[0]);

                if (abs(pfid[tk3]) == 13) {
                    fHMD0mu->Fill(mass12, w[0]);
                    if (mass12>1.6 && mass12<2.5)
                        FillCharmTree(421013, jetindex, tk1, gMassPi, tk2, gMassK);
                }

                if (abs(pfid[tk3]) == 11) {
                    fHMD0e->Fill(mass12, w[0]);
                    if (mass12>1.6 && mass12<2.5)
                        FillCharmTree(421011, jetindex, tk1, gMassPi, tk2, gMassK);
                }
            }
        }

        // Look for a pion
        for (int tk3 = 0; tk3 < npf; ++tk3) {
            if (pfjetidx[tk3]!=jetindex) continue;
            if (tk3 == tk1) continue;
            if (tk3 == tk2) continue;

            if( abs(pfid[tk3]) != 211 ) continue;

            if( pfid[tk2]/abs(pfid[tk2]) == -pfid[tk3]/abs(pfid[tk3]) ) {
                // Kaon and pion have opposite charges
                // I.e. correct mass assumption

                if(abs(mass12-1.864) < 0.10) { // mass window cut
                    TLorentzVector p_track3;
                    p_track3.SetPtEtaPhiM(pfpt[tk3], pfeta[tk3], pfphi[tk3], gMassPi);

                    TLorentzVector p_cand, p_jet;
                    p_cand = p_track1+p_track2+p_track3;
                    p_jet.SetPtEtaPhiM(jpt[jetindex], jeta[jetindex], jphi[jetindex], 0.);

                    float hardpt = std::max(pfpt[tk3], std::max(pfpt[tk1], pfpt[tk2]));
                    float softpt = std::min(pfpt[tk3], std::min(pfpt[tk1], pfpt[tk2]));
                    float deltam = (p_track1+p_track2+p_track3).M() - mass12;

                    fHDMDsmD0loose->Fill(deltam, w[0]);
                    if(abs(mass12-1.864) < 0.05) { // tighter mass window cut
                        FillCharmTree(413,  jetindex, tk1, gMassPi, tk2, gMassK, tk3, gMassPi);
                        FillCharmTree(-413, jetindex, deltam, p_cand, p_jet, hardpt, softpt);
                        fHDMDsmD0->Fill(deltam, w[0]);
                    }
                }
            }
        }
    }
}
void LxyTreeAnalysis::fillDpmHists(int jetindex) {
    if(jetindex < 0) return;
    int nstart = firstTrackIndex(jetindex);
    int ntracks = 3;

    for (int tk1 = nstart; tk1 < nstart+ntracks; ++tk1) {
        if(pfjetidx[tk1] != jetindex) continue;

        for (int tk2 = tk1+1; tk2 < nstart+ntracks; ++tk2) {
            if(pfjetidx[tk2] != jetindex) continue;

            for (int tk3 = tk2+1; tk3 < nstart+ntracks; ++tk3) {
                if(pfjetidx[tk3] != jetindex) continue;

                int sumid = pfid[tk1]+pfid[tk2]+pfid[tk3];
                if( abs(sumid) != 211 ) return;

                float tk1mass(gMassPi), tk2mass(gMassPi), tk3mass(gMassPi);
                if( sumid == 211 ) { // +211+211-211 i.e. two positive tracks
                    if(pfid[tk1] < 0) tk1mass = gMassK;
                    if(pfid[tk2] < 0) tk2mass = gMassK;
                    if(pfid[tk3] < 0) tk3mass = gMassK;
                }
                if( sumid == -211 ) { // +211-211-211 i.e. two negative tracks
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

                for (int tk4 = 0; tk4 < npf; ++tk4) { // look for a lepton
                    if (pfjetidx[tk4]!=jetindex) continue;
                    if (tk4 == tk1) continue;
                    if (tk4 == tk2) continue;
                    if (tk4 == tk3) continue;

                    if( abs(pfid[tk4]) != 13 && abs(pfid[tk4]) != 11) continue;

                    if( pfid[tk4] * sumid > 0 ) {
                        // both pos or neg, i.e. opposite sign between lep and had
                        fHMDpmlep->Fill(mass123, w[0]);

                        if (abs(pfid[tk4]) == 13) {
                            fHMDpmmu->Fill(mass123, w[0]);
                            if (mass123>1.6 && mass123<2.5)
                                FillCharmTree(411013, jetindex, tk1, tk1mass, tk2, tk2mass, tk3, tk3mass);
                        }

                        if (abs(pfid[tk4]) == 11) {
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

//
bool LxyTreeAnalysis::selectEvent() {

    float btagWP = gCSVWPLoose;
    if (abs(evcat) == 11 || abs(evcat) == 13)       btagWP = gCSVWPMedium;

    int nbjets(0);
    for( int i=0; i < nj; i++)
    {
        bool btagStatus(jcsv[i] > btagWP);
        nbjets += btagStatus;
    }

    // Require at least one b-tagged jet (loose for dilep, med for l+jets)
    if ( nbjets==0 ) return false;
    if (abs(evcat) == 23) return true;                   // Z control region
    if (abs(evcat) == 11*13) return true;                // emu
    if (abs(evcat) == 11*11 && metpt > 40.) return true; // ee
    if (abs(evcat) == 13*13 && metpt > 40.) return true; // mumu
    if (abs(evcat) == 11 && nj > 3) return true;         // e
    if (abs(evcat) == 13 && nj > 3) return true;         // mu
    return false;
}

//
bool LxyTreeAnalysis::selectSVLEvent(bool &passBtagNom, bool &passBtagUp, bool &passBtagDown,
                                     bool &passMETNom, bool &passMETUp, bool &passMETDown) {
    float btagWP = gCSVWPMedium;
    TString btagger("csvM");
    int nsvjets(0);
    int nbjets(0),nbjetsUp(0), nbjetsDown(0);
    for( int i=0; i < nj; i++)
    {
        bool btagStatus(jcsv[i] > btagWP); //original btag status
        bool nomBtagStatus(btagStatus);
        bool nomBtagStatusDown(btagStatus);
        bool nomBtagStatusUp(btagStatus);

        if(!btagEffCorr_.empty())
        {
            TString flavKey("udsg");
            if(abs(jflav[i])==5) flavKey="b";
            else if (abs(jflav[i])==4) flavKey="c";
            std::pair<TString,TString> key(btagger,flavKey);

            TGraphErrors *mceffGr = btagEffCorr_[key].first;
            TGraphErrors *sfGr    = btagEffCorr_[key].second;
            float eff             = mceffGr->Eval(jpt[i]);
            float sf              = sfGr->Eval(jpt[i]);
            //take uncertainty for sf from point #3 ~ pT=50 GeV
            //(otherwise one needs to loop to find the closest pt)
            float sfunc           = sfGr->GetErrorY(3);

            //correct for sf (+/- unc)
            btsfutil_.modifyBTagsWithSF(nomBtagStatus,sf,eff);
            btsfutil_.modifyBTagsWithSF(nomBtagStatusUp,sf+sfunc,eff);
            btsfutil_.modifyBTagsWithSF(nomBtagStatusDown,sf-sfunc,eff);
        }

        nbjets     += (svlxy[i] > 0 || nomBtagStatus);
        nbjetsUp   += (svlxy[i] > 0 || nomBtagStatusUp);
        nbjetsDown += (svlxy[i] > 0 || nomBtagStatusDown);

        //count svtx separately
        nsvjets += (svlxy[i] > 0);
    }

    // At least one SV in any channel
    if (nsvjets < 1) return false;

    // That's it for emu, Z,W photon and dijet qcd control regions
    if (abs(evcat) == 11*13) return true;
    if (abs(evcat) == 23) return true;
    if (abs(evcat) == 24) return true;
    if (abs(evcat) == 22) return true;
    if (abs(evcat) == 1) return true;

    // For dilepton also MET > 40 GeV
    if (abs(evcat) == 11*11 || abs(evcat) == 13*13) {
        passMETNom  = (metpt>40);
        passMETUp   = (metvar[4]>40);
        passMETDown = (metvar[5]>40);
        if(!passMETNom && !passMETUp && !passMETDown) return false;
        return true;
    }

    // For single lepton, at least 4 jets, and either 2 SV or 1 SV + 1 CSVM
    if (abs(evcat) == 11 || abs(evcat) == 13) {
        if (nj < 4)
        {
            TLorentzVector lp4;
            lp4.SetPtEtaPhiM(lpt[0],leta[0],lphi[0],0.0);
            TLorentzVector metp4;
            metp4.SetPtEtaPhiM(metpt,0,metphi,0.);
            TLorentzVector metp4Up;
            metp4Up.SetPtEtaPhiM(metvar[4],0,metphi,0.);
            TLorentzVector metp4Dn;
            metp4Dn.SetPtEtaPhiM(metvar[5],0,metphi,0.);
            float mT(utils::cmssw::getMT<TLorentzVector,TLorentzVector>( lp4, metp4) );
            float mTUp(utils::cmssw::getMT<TLorentzVector,TLorentzVector>( lp4, metp4Up) );
            float mTDn(utils::cmssw::getMT<TLorentzVector,TLorentzVector>( lp4, metp4Dn) );
            passMETNom  = (mT>50);
            passMETUp   = (mTUp>50);
            passMETDown = (mTDn>50);
            if(nfj==0)   return false;
        }
        if (nsvjets > 1)
        {
            passBtagNom=true;
            passBtagUp=true;
            passBtagDown=true;
            return true; // two SV
        }

        //two b-tagged jets
        passBtagNom  = (nbjets>1);
        passBtagUp   = (nbjetsUp>1);
        passBtagDown = (nbjetsDown>1);

        if(passBtagNom || passBtagUp || passBtagDown) return true;
        return false;
    }

    // QCD control sample (non-isolated leptons)
    if (abs(evcat) == 11*100 || abs(evcat) == 13*100) {
        if (nj < 4 && nfj==0) return false;
        if (nbjets > 1 || nsvjets > 1) return false; // suppress ttbar
        return true;
    }
    return false;
}

bool LxyTreeAnalysis::selectDYControlEvent() {
    int nsvjets(0), nbjets(0);
    for( int i=0; i < nj; i++) {
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
    fSVLInfoTree->Branch("Weight",     fTWeight,    "Weight[11]/F");
    fSVLInfoTree->Branch("JESWeight",  fTJESWeight, "JESWeight[5]/F");
    fSVLInfoTree->Branch("METWeight",  fTMETWeight, "METWeight[3]/F");
    fSVLInfoTree->Branch("BtagWeight",  fTBtagWeight, "BtagWeight[3]/F");
    fSVLInfoTree->Branch("XSWeight",  &fTXSWeight,  "XSWeight/F");
    fSVLInfoTree->Branch("SVBfragWeight" , fTSVBfragWeight  , "SVBfragWeight[6]/F");
    TString pdfWeightAlloc("PDFWeight[");
    if(fPDFInfo && fPDFInfo->numberPDFs()) pdfWeightAlloc += fPDFInfo->numberPDFs();
    else                                   pdfWeightAlloc += "1";
    pdfWeightAlloc += "]/F";
    fSVLInfoTree->Branch("PDFWeight", fPDFWeight,   pdfWeightAlloc);
    fSVLInfoTree->Branch("NPVtx",     &fTNPVtx,     "NPVtx/I");
    fSVLInfoTree->Branch("NJets",     &fTNJets,     "NJets/I");
    fSVLInfoTree->Branch("NBTags",    &fTNBTags,    "NBTags/I");
    fSVLInfoTree->Branch("MET",       &fTMET,       "MET/F");
    fSVLInfoTree->Branch("NCombs",    &fTNCombs,    "NCombs/I");
    fSVLInfoTree->Branch("SVLMass",   &fTSVLMass,   "SVLMass/F");
    fSVLInfoTree->Branch("SVLMass_sf",   fTSVLMass_sf,   "SVLMass_sf[2]/F");
    fSVLInfoTree->Branch("SVLDeltaR", &fTSVLDeltaR, "SVLDeltaR/F");
    fSVLInfoTree->Branch("SVLMass_rot",   &fTSVLMass_rot,   "SVLMass_rot/F");
    fSVLInfoTree->Branch("SVLDeltaR_rot", &fTSVLDeltaR_rot, "SVLDeltaR_rot/F");
    fSVLInfoTree->Branch("BHadNeutrino", &fTBHadNeutrino, "BHadNeutrino/I");
    fSVLInfoTree->Branch("BHadId", &fTBHadId, "BHadId/I");
    fSVLInfoTree->Branch("LPt",       &fTLPt,       "LPt/F");
    fSVLInfoTree->Branch("SVMass",    &fTSVMass,    "SVMass/F");
    fSVLInfoTree->Branch("SVNtrk",    &fTSVNtrk,    "SVNtrk/I");
    fSVLInfoTree->Branch("SVPt",      &fTSVPt,      "SVPt/F");
    fSVLInfoTree->Branch("SVLxy",     &fTSVLxy,     "SVLxy/F");
    fSVLInfoTree->Branch("SVLxySig",  &fTSVLxySig,  "SVLxySig/F");
    fSVLInfoTree->Branch("SVPtChFrac",  &fTSVPtChFrac, "SVPtChFrac/F");
    fSVLInfoTree->Branch("SVPzChFrac",  &fTSVPzChFrac, "SVPzChFrac/F");
    fSVLInfoTree->Branch("SVProjFrac",  &fTSVProjFrac, "SVProjFrac/F");
    fSVLInfoTree->Branch("SVPtRel",   &fTSVPtRel,   "SVPtRel/F");
    fSVLInfoTree->Branch("JPt",       &fTJPt,       "JPt/F");
    fSVLInfoTree->Branch("JEta",      &fTJEta,      "JEta/F");
    fSVLInfoTree->Branch("JFlav",     &fTJFlav,     "JFlav/I");
    fSVLInfoTree->Branch("FJPt",       &fTFJPt,       "FJPt/F");
    fSVLInfoTree->Branch("MT",       &fTMT,       "MT/F");
    fSVLInfoTree->Branch("FJEta",      &fTFJEta,      "FJEta/F");
    fSVLInfoTree->Branch("GenMlb",    &fTGenMlb,    "GenMlb/F");
    fSVLInfoTree->Branch("GenTopPt",  &fTGenTopPt,  "GenTopPt/F");
    // CombCat = 11, 12, 21, 22 for the four possible lepton/sv combinations
    fSVLInfoTree->Branch("CombCat"       , &fTCombCat       , "CombCat/I");
    // CombInfo = -1 for data or unmatched, 0 for wrong combs, 1 for correct combs
    fSVLInfoTree->Branch("CombInfo"      , &fTCombInfo      , "CombInfo/I");

    // Intra event rankings
    fSVLInfoTree->Branch("SVLMassRank",       &fTSVLMinMassRank,     "SVLMassRank/I");
    fSVLInfoTree->Branch("SVLCombRank",       &fTSVLCombRank,        "SVLCombRank/I");
    fSVLInfoTree->Branch("SVLDeltaRRank",     &fTSVLDeltaRRank,      "SVLDeltaRRank/I");
    fSVLInfoTree->Branch("SVLMassRank_rot",   &fTSVLMinMassRank_rot, "SVLMassRank_rot/I");
    fSVLInfoTree->Branch("SVLDeltaRRank_rot", &fTSVLDeltaRRank_rot,  "SVLDeltaRRank_rot/I");
}

//
void LxyTreeAnalysis::ResetSVLTree()
{
    fTEvent     = event;
    fTRun       = run;
    fTLumi      = lumi;
    fTEvCat     = evcat;
    fTMET       = metpt;
    fTNJets     = nj;
    fTNBTags    = -1;
    fTNPVtx     = nvtx;
    for (int i = 0; i < 11; ++i) {
        if(nw<i+1) fTWeight[i]=0;
        else       fTWeight[i]=w[i];
    }

    for (int i = 0; i < 3; ++i) fTMETWeight[i] = -99.99;
    for (int i = 0; i < 3; ++i) fTBtagWeight[i] = -99.99;
    for (int i = 0; i < 5; ++i) fTJESWeight[i] = -99.99;
    for (int i=0; i<6; i++) fTSVBfragWeight[i] = -99.99;
    fTNCombs         = -99.99;
    fTSVLMass        = -99.99;
    fTSVLDeltaR      = -99.99;
    fTSVLMass_rot    = -99.99;
    fTSVLDeltaR_rot  = -99.99;
    fTBHadNeutrino   = -99;
    fTBHadId         = 0;
    fTLPt            = -99.99;
    fTSVPt           = -99.99;
    fTSVLxy          = -99.99;
    fTSVLxySig       = -99.99;
    fTSVPtChFrac     = -99.99;
    fTSVPzChFrac     = -99.99;
    fTSVProjFrac     = -99.99;
    fTSVPtRel        = -99.99;
    fTJEta           = -99.99;
    fTJPt            = -99.99;
    fTFJEta          = -99.99;
    fTFJPt           = -99.99;
    fTMT             = 0;
    fTJFlav          = 0;
    fTSVNtrk         = -99;
    fTSVMass         = -99;
    fTCombCat        = -99;
    fTCombInfo       = -99;

    fTGenMlb         = -99.99;
    fTGenTopPt       = -99.99;

    fTSVLMinMassRank = -99;
    fTSVLDeltaRRank  = -99;
}

//
void LxyTreeAnalysis::BookDileptonTree()
{
    fDileptonInfoTree = new TTree("DileptonInfo", "DiLepton Tree");
    fDileptonInfoTree->Branch("Event",     &fTEvent,     "Event/I");
    fDileptonInfoTree->Branch("Run",       &fTRun,       "Run/I");
    fDileptonInfoTree->Branch("Lumi",      &fTLumi,      "Lumi/I");
    fDileptonInfoTree->Branch("EvCat",     &fTEvCat,     "EvCat/I");
    fDileptonInfoTree->Branch("Weight",     fTWeight,    "Weight[11]/F");
    fDileptonInfoTree->Branch("JESWeight",  fTJESWeight, "JESWeight[5]/F");
    fDileptonInfoTree->Branch("METWeight",  fTMETWeight, "METWeight[3]/F");
    fDileptonInfoTree->Branch("BtagWeight",  fTBtagWeight, "BtagWeight[3]/F");
    fDileptonInfoTree->Branch("XSWeight",  &fTXSWeight,  "XSWeight/F");
    TString pdfWeightAlloc("PDFWeight[");
    if(fPDFInfo && fPDFInfo->numberPDFs()) pdfWeightAlloc += fPDFInfo->numberPDFs();
    else                                   pdfWeightAlloc += "1";
    pdfWeightAlloc += "]/F";
    fDileptonInfoTree->Branch("PDFWeight", fPDFWeight,   pdfWeightAlloc);
    fDileptonInfoTree->Branch("NJets",     &fTNJets,     "NJets/I");
    fDileptonInfoTree->Branch("MET",       &fTMET,       "MET/F");
    fDileptonInfoTree->Branch("NPVtx",     &fTNPVtx,     "NPVtx/I");
    fDileptonInfoTree->Branch("LpPt",      &fLpPt,     "LpPt/F");
    fDileptonInfoTree->Branch("LmPt",      &fLmPt,     "LmPt/F");
    fDileptonInfoTree->Branch("LpEta",      &fLpEta,     "LpEta/F");
    fDileptonInfoTree->Branch("LpId",      &fLpId,     "LpId/I");
    fDileptonInfoTree->Branch("LmEta",      &fLmEta,     "LmEta/F");
    fDileptonInfoTree->Branch("LpPhi",      &fLpPhi,     "LpPhi/F");
    fDileptonInfoTree->Branch("LmPhi",      &fLmPhi,     "LmPhi/F");
    fDileptonInfoTree->Branch("LmId",      &fLmId,     "LmId/I");
    fDileptonInfoTree->Branch("GenLpPt",      &fGenLpPt,     "GenLpPt/F");
    fDileptonInfoTree->Branch("GenLmPt",      &fGenLmPt,     "GenLmPt/F");
    fDileptonInfoTree->Branch("GenLpEta",     &fGenLpEta,    "GenLpEta/F");
    fDileptonInfoTree->Branch("GenLpId",      &fGenLpId,     "GenLpId/I");
    fDileptonInfoTree->Branch("GenLmEta",     &fGenLmEta,    "GenLmEta/F");
    fDileptonInfoTree->Branch("GenLpPhi",     &fGenLpPhi,    "GenLpPhi/F");
    fDileptonInfoTree->Branch("GenLmPhi",     &fGenLmPhi,    "GenLmPhi/F");
    fDileptonInfoTree->Branch("GenLmId",      &fGenLmId,     "GenLmId/I");
}

void LxyTreeAnalysis::ResetDileptonTree()
{
    fLpPt=0;
    fLmPt=0;
    fLpEta=0;
    fLmEta=0;
    fLpPhi=0;
    fLmPhi=0;
    fGenLpPt=0;
    fGenLmPt=0;
    fGenLpEta=0;
    fGenLmEta=0;
    fGenLpPhi=0;
    fGenLmPhi=0;
    fLpId=0;
    fLmId=0;
    fGenLpId=0;
    fGenLmId=0;
}


//
void LxyTreeAnalysis::analyze() {
    ///////////////////////////////////////////////////
    // Remove events with spurious PF candidate information (npf == 1000)
    if(npf > 999) return;
    ///////////////////////////////////////////////////

    // Called once per event
    FillPlots();

    //reset trees
    ResetCharmTree();
    ResetSVLTree();
    ResetDileptonTree();
    bool storeDileptonTree(false);

    ///////////////////////////////////////////////////
    // Charm resonance stuff:
    float maxcsv(-1.), maxcsv2(-1.);
    int maxind(-1), maxind2(-1);

    for(int k = 0; k < nj; k++) {
        // use >= n not just > as max and max2 can have same value. Ex:{1,2,3,3}
        if(jcsv[k] >= maxcsv) {
            maxcsv2=maxcsv;
            maxind2=maxind;

            maxcsv=jcsv[k];
            maxind=k;
        }
        else if(jcsv[k] > maxcsv2) {
            maxcsv2=jcsv[k];
            maxind2=k;
        }
    }

    if (maxind < 0 && maxind2 < 0) {
        // In case we didn't find ANY jets with csv > 0,
        // just take the hardest two jets
        maxind = 0;
        maxind2 = 1;
    }
    else if (maxind >= 0 && maxind2 < 0) {
        // In case we only found ONE jet with csv > 0,
        // Take the next-hardest one (or the hardest altogether)
        // There are only two options:
        // - the one we found was the hardest one -> take second one
        if(maxind == 0) maxind2 = 1;
        // - the one we found was NOT the hardest one -> take the first one
        else maxind2 = 0;
    }

    if(selectEvent()) {
        fillJPsiHists(maxind);
        fillD0Hists(maxind);
        fillDpmHists(maxind);

        if(maxind2 != maxind) { // remove double counting
            fillJPsiHists(maxind2);
            fillD0Hists(maxind2);
            fillDpmHists(maxind2);
        }
    }


    ///////////////////////////////////////////////////
    // Lepton + Secondary Vertex stuff:
    // Find jets with SVs:
    std::vector<int> svindices(2,-1);
    int nsvjets(0), nbjets(0);
    float lxymax1(0), lxymax2(0);
    std::vector<TLorentzVector> lightJetsP4;
    for( int i=0; i < nj; i++) {
        if(svlxy[i]>0) {
            nsvjets++;
            if(jcsv[i] > gCSVWPMedium) nbjets++;
            if(svlxyerr[i]!=0) {
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
        else
        {
            if(jcsv[i] > gCSVWPMedium) nbjets++;
            else {
                TLorentzVector p4;
                p4.SetPtEtaPhiM(jpt[i], jeta[i], jphi[i], 0.);
                lightJetsP4.push_back(p4);
            }
        }
    }
    if(svindices[1]<0) svindices.pop_back();
    if(svindices[0]<0) svindices.pop_back();

    //Elizabeth
    bool fjexists = false;
    float fwd_jet_eta(0), fwd_jet_pt(0);
    for(int i=0; i<nfj; i++){
      fjexists = true;
      if(i==0){
	fwd_jet_eta=fjeta[i];
	fwd_jet_pt=fjpt[i];
      }
      if(fabs(fwd_jet_eta)<fjeta[i]){
	fwd_jet_eta=fjeta[i];
	fwd_jet_pt=fjpt[i];
      }
    }
    if(fjexists==false){
      for(int i=0;i<nj; i++){
	if(svpt[i]<0){
	  if(fwd_jet_pt==0){
	    fwd_jet_eta=jeta[i];
	    fwd_jet_pt=jpt[i];
	  }
	  if(fwd_jet_eta<jeta[i]){
	    fwd_jet_eta=jeta[i];
	    fwd_jet_pt=jpt[i];
	  }
	}
      }
    }
    //End Elizabeth

    std::vector<TLorentzVector> isoObjects;
    for (int il = 0; il < nl; ++il) {
        TLorentzVector p4;
        p4.SetPtEtaPhiM(lpt[il], leta[il], lphi[il], 0.);
        isoObjects.push_back(p4);
    }
    for (int ij = 0; ij < nj; ++ij) {
        TLorentzVector p4;
        p4.SetPtEtaPhiM(jpt[ij], jeta[ij], jphi[ij], 0.);
        isoObjects.push_back(p4);
    }

    TLorentzVector metP4;
    metP4.SetPtEtaPhiM(metpt,0,metphi,0);
    float mT(utils::cmssw::getMT<TLorentzVector,TLorentzVector>( isoObjects[0], metP4) );
    float mjj( lightJetsP4.size()>=2 ? (lightJetsP4[0]+lightJetsP4[1]).M() : -99);

    bool passBtag(true), passBtagup(true), passBtagdown(true);
    bool passMET(true), passMETup(true),passMETdown(true);
    if(selectSVLEvent(passBtag, passBtagup, passBtagdown,passMET,passMETup,passMETdown))
    {
        // Fill some control histograms:
        if(passBtag && passMET){
            if (abs(evcat) <= 13*13) { // Inclusive (exclude control samples)
                fHNJets     ->Fill(nj,       w[0]*w[1]*w[4]);
                fHNSVJets   ->Fill(nsvjets,  w[0]*w[1]*w[4]);
                fHNbJets    ->Fill(nbjets,   w[0]*w[1]*w[4]);
                fHMET       ->Fill(metpt,    w[0]*w[1]*w[4]);
                fHMT        ->Fill(mT,       w[0]*w[1]*w[4]);
                if(mjj>=0.) fHMjj->Fill(mjj, w[0]*w[1]*w[4]); // only fill if there are 2 light jets
            }

            if (abs(evcat) == 11*13) {
                fHNJets_em  ->Fill(nj,      w[0]*w[1]*w[4]);
                fHNSVJets_em->Fill(nsvjets, w[0]*w[1]*w[4]);
                fHNbJets_em ->Fill(nbjets,  w[0]*w[1]*w[4]);
                fHMET_em    ->Fill(metpt,   w[0]*w[1]*w[4]);
                storeDileptonTree=true;
            }
            else if (abs(evcat) == 11*11) {
                fHNJets_ee  ->Fill(nj,      w[0]*w[1]*w[4]);
                fHNSVJets_ee->Fill(nsvjets, w[0]*w[1]*w[4]);
                fHNbJets_ee ->Fill(nbjets,  w[0]*w[1]*w[4]);
                fHMET_ee    ->Fill(metpt,   w[0]*w[1]*w[4]);
                storeDileptonTree=true;
            }
            else if (abs(evcat) == 13*13) {
                fHNJets_mm  ->Fill(nj,      w[0]*w[1]*w[4]);
                fHNSVJets_mm->Fill(nsvjets, w[0]*w[1]*w[4]);
                fHNbJets_mm ->Fill(nbjets,  w[0]*w[1]*w[4]);
                fHMET_mm    ->Fill(metpt,   w[0]*w[1]*w[4]);
                storeDileptonTree=true;
            }
            else if (abs(evcat) == 11 && nj>=4) {
                fHNJets_e   ->Fill(nj,      w[0]*w[1]*w[4]);
                fHMjj_e     ->Fill(mjj,     w[0]*w[1]*w[4]);
                fHNSVJets_e ->Fill(nsvjets, w[0]*w[1]*w[4]);
                fHNbJets_e  ->Fill(nbjets,  w[0]*w[1]*w[4]);
                fHMT_e      ->Fill(mT,      w[0]*w[1]*w[4]);
                fHMET_e     ->Fill(metpt,   w[0]*w[1]*w[4]);
            }
            else if (abs(evcat) == 13 && nj>=4) {
                fHNJets_m   ->Fill(nj,      w[0]*w[1]*w[4]);
                fHMjj_m     ->Fill(mjj,     w[0]*w[1]*w[4]);
                fHNSVJets_m ->Fill(nsvjets, w[0]*w[1]*w[4]);
                fHNbJets_m  ->Fill(nbjets,  w[0]*w[1]*w[4]);
                fHMT_m      ->Fill(mT,      w[0]*w[1]*w[4]);
                fHMET_m     ->Fill(metpt,   w[0]*w[1]*w[4]);
            }
            fTNBTags=nbjets;
        }

        // First find all pairs and get their ranking in mass and deltar
        std::vector<SVLInfo> svl_pairs;
        for (int il = 0; il < nl; ++il) { // lepton loop
            for (size_t ij = 0; ij < svindices.size(); ++ij) { // sv loop
                int svind = svindices[ij];
                // Jet selection here
                SVLInfo svl_pairing;
                svl_pairing.jesweights[0] = 0;
                svl_pairing.jesweights[1] = 0;
                svl_pairing.jesweights[2] = 0;
                svl_pairing.jesweights[3] = 0;
                svl_pairing.jesweights[4] = 0;
                if(jpt[svind]       > 30.) svl_pairing.jesweights[0] = 1; // nominal
                if(jjesup[svind][0] > 30.) svl_pairing.jesweights[1] = 1; // jes up
                if(jjesdn[svind][0] > 30.) svl_pairing.jesweights[2] = 1; // jes down
                if(jjerup[svind]    > 30.) svl_pairing.jesweights[3] = 1; // jes up
                if(jjerdn[svind]    > 30.) svl_pairing.jesweights[4] = 1; // jes down
                svl_pairing.bfragweights[0] = bwgt[svind][0];
                svl_pairing.bfragweights[1] = bwgt[svind][1];
                svl_pairing.bfragweights[2] = bwgt[svind][2];
                svl_pairing.bfragweights[3] = bwgt[svind][3];
                svl_pairing.bfragweights[4] = bwgt[svind][4];
                svl_pairing.bfragweights[5] = bwgt[svind][5];
                svl_pairing.umetweights[0]  = passMET;
                svl_pairing.umetweights[1]  = passMETdown;
                svl_pairing.umetweights[2]  = passMETup;
                svl_pairing.btagweights[0]  = passBtag;
                svl_pairing.btagweights[1]  = passBtagdown;
                svl_pairing.btagweights[2]  = passBtagup;

                if(jpt[svind] > 30. || jjesup[svind][0] > 30. || jjesdn[svind][0] > 30.) {
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

                    //lepton energy scale variation on mass
                    for(size_t ivar=0; ivar<2; ivar++)
                    {
                        svl_pairing.svlmass_sf[ivar]=1.0;
                        if(svl_pairing.svlmass<=0) continue;
                        float lesf(1.0);
                        int varSign( ivar==0 ? -1 : 1 );
                        float lesUnc(0.002);
                        if(abs(lid[il])==11) lesUnc=utils::cmssw::getElectronEnergyScale(lpt[il],leta[il]);
                        lesf=(1.0+varSign*lesUnc);
                        TLorentzVector p_lep_var;
                        p_lep_var.SetPtEtaPhiM(lesf*lpt[il], leta[il], lphi[il], 0.);
                        svl_pairing.svlmass_sf[ivar]=((p_lep_var + p_sv).M() / svl_pairing.svlmass );
                    }

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

        //based on AN 10/316 (mass from endpoints)
        std::vector<SVLInfo> svl_pairs_combranked;
        size_t npairs=svl_pairs_massranked.size();
        if(npairs)
        {
            svl_pairs_combranked.push_back( svl_pairs_massranked[0] );
            if(npairs==4)
            {
                svl_pairs_combranked.push_back( svl_pairs_massranked[1] );
                if(svl_pairs_massranked[0].lepindex==svl_pairs_massranked[1].lepindex)
                    svl_pairs_combranked.push_back( svl_pairs_massranked[2] );
            }
        }

        std::vector<SVLInfo> svl_pairs_drranked = svl_pairs;
        std::sort (svl_pairs_drranked.begin(), svl_pairs_drranked.end(), compare_deltar);
        std::vector<SVLInfo> svl_pairs_massranked_rot = svl_pairs;
        std::sort (svl_pairs_massranked_rot.begin(), svl_pairs_massranked_rot.end(), compare_mass_rot);
        std::vector<SVLInfo> svl_pairs_drranked_rot = svl_pairs;
        std::sort (svl_pairs_drranked_rot.begin(), svl_pairs_drranked_rot.end(), compare_deltar_rot);

        // Now put the info in the tree
        fTNCombs = svl_pairs.size();
        for (size_t isvl = 0; isvl < svl_pairs.size(); ++isvl) {
            SVLInfo svl = svl_pairs[isvl];

            // Apply a Delta R cut to remove fake leptons in the QCD control region
            if (abs(evcat) == 11*100 || abs(evcat) == 13*100) {
                if ( svl.svldeltar < 0.4 ) continue;
            }

            fTSVLMass       = svl.svlmass;
            fTSVLMass_sf[0] = svl.svlmass_sf[0];
            fTSVLMass_sf[1] = svl.svlmass_sf[1];
            fTSVLDeltaR     = svl.svldeltar;
            fTSVLMass_rot   = svl.svlmass_rot;
            fTSVLDeltaR_rot = svl.svldeltar_rot;
            fTCombCat       = svl.combcat;

            // Find the mass and dr ranks:
            fTSVLCombRank=-1;
            for(size_t i=0; i< svl_pairs_combranked.size(); ++i) {
                if(svl_pairs_combranked[i].counter != isvl) continue;
                fTSVLCombRank = i+1;
            }
            for (size_t i = 0; i < svl_pairs.size(); ++i) {
                if(svl_pairs_massranked[i].counter != isvl) continue;
                fTSVLMinMassRank = i+1;
            }
            for (size_t i = 0; i < svl_pairs.size(); ++i) {
                if(svl_pairs_massranked_rot[i].counter != isvl) continue;
                fTSVLMinMassRank_rot = i+1;
            }
            for (size_t i = 0; i < svl_pairs.size(); ++i) {
                if(svl_pairs_drranked[i].counter != isvl) continue;
                fTSVLDeltaRRank = i+1;
            }
            for (size_t i = 0; i < svl_pairs.size(); ++i) {
                if(svl_pairs_drranked_rot[i].counter != isvl) continue;
                fTSVLDeltaRRank_rot = i+1;
            }
            TLorentzVector p_trks(0.,0.,0.,0.);
            for (int i = 0; i < npf; ++i) {
                if (pfjetidx[i] != svl.svindex) continue;
                TLorentzVector p_tk;
                p_tk.SetPtEtaPhiM(pfpt[i], pfeta[i], pfphi[i], gMassPi);
                p_trks = p_trks + p_tk;
            }
            TLorentzVector svp4;
            svp4.SetPtEtaPhiM( svpt[svl.svindex],sveta[svl.svindex],svphi[svl.svindex],svmass[svl.svindex]);
            TLorentzVector lp4;
            lp4.SetPtEtaPhiM(lpt[svl.lepindex],leta[svl.lepindex],lphi[svl.lepindex],0.0);
            TLorentzVector metp4;
            metp4.SetPtEtaPhiM(metpt,0,metphi,0.);

            fTMT           = mT;
            fTLPt          = lpt  [svl.lepindex];
            fTSVPt         = svpt [svl.svindex];
            fTSVLxy        = svlxy[svl.svindex];
            if(svlxyerr[svl.svindex]) fTSVLxySig =  svlxy[svl.svindex]/svlxyerr[svl.svindex];
            if(p_trks.Pt()>0) {
                fTSVPtChFrac = fTSVPt/p_trks.Pt();
                fTSVPzChFrac = svp4.Pz()/p_trks.Pz();
                fTSVPtRel    = ROOT::Math::VectorUtil::Perp(svp4.Vect(),p_trks.Vect());
            }
            fTSVProjFrac = 1.0+svp4.Vect().Dot(lp4.Vect())/lp4.Vect().Mag2();
            fTJPt          = jpt  [svl.svindex];
            fTJFlav        = jflav[svl.svindex];
            fTJEta         = jeta [svl.svindex];
	    //Elizabeth
            fTFJPt         = fwd_jet_pt;//fjpt [0];
            fTFJEta        = fwd_jet_eta;//fjeta[0];
	    //End Elizabeth
            fTSVNtrk       = svntk[svl.svindex];
            fTSVMass       = svmass[svl.svindex];
            fTBHadNeutrino = bhadneutrino[svl.svindex]; // either -999, 0, or 1
            if(fTBHadNeutrino < 0) fTBHadNeutrino = -1; // set -999 to -1

            fTJESWeight[0] = svl.jesweights[0]; // nominal
            fTJESWeight[1] = svl.jesweights[1]; // jes up
            fTJESWeight[2] = svl.jesweights[2]; // jes down
            fTJESWeight[3] = svl.jesweights[3]; // jer up
            fTJESWeight[4] = svl.jesweights[4]; // jer down
            fTMETWeight[0] = svl.umetweights[0]; // nominal
            fTMETWeight[1] = svl.umetweights[1]; // unclustered met down
            fTMETWeight[2] = svl.umetweights[2]; // unclustered met up
            fTBtagWeight[0] = svl.btagweights[0]; // nominal
            fTBtagWeight[1] = svl.btagweights[1]; // unclustered met down
            fTBtagWeight[2] = svl.btagweights[2]; // unclustered met up

            fTSVBfragWeight[0] = svl.bfragweights[0]; // nominal (Z2star_rbLEP_weight)
            fTSVBfragWeight[1] = svl.bfragweights[1]; // bfrag up (Z2star_rbLEPhard_weight)
            fTSVBfragWeight[2] = svl.bfragweights[2]; // bfrag dn (Z2star_rbLEPsoft_weight)
            fTSVBfragWeight[3] = svl.bfragweights[3]; // p11
            fTSVBfragWeight[4] = svl.bfragweights[4]; // Z2star_peterson
            fTSVBfragWeight[5] = svl.bfragweights[5]; // Z2star_lund

            // MC truth information on correct/wrong matchings
            fTCombInfo = -1;    // unmatched
            if( (lid[svl.lepindex] > 0 && bid[svl.svindex] == -5 ) || // el-/mu- / tbar/bbar
                    (lid[svl.lepindex] < 0 && bid[svl.svindex] == 5  ) )  // el+/mu+ / t/b
                fTCombInfo = 1; // correct
            else if(
                (lid[svl.lepindex] > 0 && bid[svl.svindex] == 5  ) || // el-/mu- / t/b
                (lid[svl.lepindex] < 0 && bid[svl.svindex] == -5 ) )  // el+/mu+ / tbar/bbar
                fTCombInfo = 0; // wrong

            // Generator level info
            fTGenTopPt = tpt[svl.svindex];
            TLorentzVector p_genb, p_genl;
            p_genb.SetPtEtaPhiM(bpt[svl.svindex], beta[svl.svindex], bphi[svl.svindex], 0.);
            p_genl.SetPtEtaPhiM(glpt[svl.lepindex], gleta[svl.lepindex], glphi[svl.lepindex], 0.);
            fTGenMlb = (p_genb+p_genl).M();

            fSVLInfoTree->Fill();
        }

        if(storeDileptonTree)
        {
            int pidx(lid[0]>0 ? 1 : 0), midx(lid[0]>0 ? 0 : 1);
            fLmPt=lpt[midx];
            fLmEta=leta[midx];
            fLmPhi=lphi[midx];
            fLmId=lid[midx];
            fGenLmPt=glpt[midx];
            fGenLmEta=gleta[midx];
            fGenLmPhi=glphi[midx];
            fGenLmId=glid[midx];
            fLpPt=lpt[pidx];
            fLpEta=leta[pidx];
            fLpPhi=lphi[pidx];
            fLpId=lid[pidx];
            fGenLpPt=glpt[pidx];
            fGenLpEta=gleta[pidx];
            fGenLpPhi=glphi[pidx];
            fGenLmId=glid[pidx];
            fDileptonInfoTree->Fill();
        }
    }

    // Fill DY control histograms
    if(selectDYControlEvent()) {
        TLorentzVector p_l1, p_l2;
        p_l1.SetPtEtaPhiM(lpt[0], leta[0], lphi[0], 0.);
        p_l2.SetPtEtaPhiM(lpt[1], leta[1], lphi[1], 0.);
        float mll = (p_l1+p_l2).M();
        if(abs(evcat) == 11*11*1000) {
            fHDY_mll_ee->Fill(mll,   w[0]*w[1]*w[4]);
            fHDY_met_ee->Fill(metpt, w[0]*w[1]*w[4]);
        }
        if(abs(evcat) == 13*13*1000) {
            fHDY_mll_mm->Fill(mll,   w[0]*w[1]*w[4]);
            fHDY_met_mm->Fill(metpt, w[0]*w[1]*w[4]);
        }
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

        //pdf information
        if( fPDFInfo )
        {
            const std::vector<float> &wgts=fPDFInfo->getWeights(jentry);
            for(size_t i=0; i<wgts.size(); i++) fPDFWeight[i]=wgts[i];
        }
        else
        {
            for (int i=0; i<100; i++) fPDFWeight[i]    = 1.0;
        }

        if (jentry%500 == 0) {
            printf("\r [ %3d/100 ]", int(100*float(jentry)/float(nentries)));
            std::cout << std::flush;
        }

        analyze();

    }
    std::cout << "\r [   done  ]" << std::endl;

}
#endif
