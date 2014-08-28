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

#include "Math/VectorUtil.h"

#include <TLorentzVector.h>
#include <iostream>

//plot with ./scripts/runPlotter.py lxyplots/ -j test/topss2014/samples_noqcd.json
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
    fCharmInfoTree->Branch("CandEta",      &fTCandEta,      "CandEta/F");
    fCharmInfoTree->Branch("CandPz",       &fTCandPz,       "CandPz/F");
    fCharmInfoTree->Branch("CandPtRel",    &fTCandPtRel,    "CandPtRel/F");
    fCharmInfoTree->Branch("CandDeltaR",   &fTCandDeltaR,   "CandDeltaR/F");
    fCharmInfoTree->Branch("JetPt",        &fTJetPt,        "JetPt/F");
    fCharmInfoTree->Branch("JetEta",       &fTJetEta,       "JetEta/F");
    fCharmInfoTree->Branch("JetPz",        &fTJetPz,        "JetPz/F");
    fCharmInfoTree->Branch("SumPtCharged", &fTSumPtCharged, "SumPtCharged/F");
    fCharmInfoTree->Branch("SumPzCharged", &fTSumPzCharged, "SumPzCharged/F");
}

void LxyTreeAnalysis::ResetCharmTree() {
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

    FillCharmTree(type, jind, p_cand, p_jet);
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

    FillCharmTree(type, jind, p_cand, p_jet);
    return;
}

void LxyTreeAnalysis::FillCharmTree(int type, int jind,
                                    TLorentzVector p_cand,
                                    TLorentzVector p_jet){
    fTCandType = type;
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

    fTSumPtCharged = p_trks.Pt();
    fTSumPzCharged = p_trks.Pz();
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

void LxyTreeAnalysis::analyze() {
    // Called once per event
    FillPlots();
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
