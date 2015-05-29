#ifndef MlbWidthAnalysis_cxx
#define MlbWidthAnalysis_cxx
#include "UserCode/TopMassSecVtx/interface/MlbWidthAnalysis.h"
#include "UserCode/TopMassSecVtx/interface/MacroUtils.h"

#include "Math/VectorUtil.h"

#include <TLorentzVector.h>
#include <iostream>

const float gCSVWPMedium = 0.783;
const float gCSVWPLoose = 0.405;

void MlbWidthAnalysis::RunJob(TString filename) {
    TFile *file = TFile::Open(filename, "recreate");

    //do the analysis
    Begin(file);
    Loop();
    End(file);
}
void MlbWidthAnalysis::Begin(TFile *file) {
    // Anything that has to be done once at the beginning
    file->cd();
    BookHistos();
}

void MlbWidthAnalysis::End(TFile *file) {
    // Anything that has to be done once at the end
    file->cd();
    WriteHistos();
    file->Write();
    file->Close();
}

void MlbWidthAnalysis::BookHistos() {
    fHMlb = new TH1D("Mlb","Mlb", 100, 0, 200);
    fHistos.push_back(fHMlb);
    fHMlb->SetXTitle("m(lb) [GeV]");


    // Call Sumw2() for all of them
    std::vector<TH1*>::iterator h;
    for(h = fHistos.begin(); h != fHistos.end(); ++h) {
        (*h)->Sumw2();
    }
}
void MlbWidthAnalysis::WriteHistos() {
    // Write all histos to file, then delete them
    std::vector<TH1*>::iterator h;
    for( h = fHistos.begin(); h != fHistos.end(); ++h) {
        (*h)->Write((*h)->GetName());
        (*h)->Delete();
    }
}

//
bool MlbWidthAnalysis::selectEvent() {
    float btagWP = gCSVWPLoose;
    if (abs(evcat) == 11 || abs(evcat) == 13) btagWP = gCSVWPMedium;

    // Count number of loose or medium b-tags
    int nbjets(0);
    for( int i=0; i < nj; i++) {
        bool btagStatus(jcsv[i] > btagWP);
        nbjets += btagStatus;
    }

    // Require at least one b-tagged jet (loose for dilep, med for l+jets)
    if ( nbjets==0 ) return false;

    if (abs(evcat) == 11*13) return true;                // emu
    if (abs(evcat) == 11*11 && metpt > 40.) return true; // ee
    if (abs(evcat) == 13*13 && metpt > 40.) return true; // mumu
    if (abs(evcat) == 11 && nj > 3) return true;         // e
    if (abs(evcat) == 13 && nj > 3) return true;         // mu
    return false;
}


void MlbWidthAnalysis::analyze() {
    ///////////////////////////////////////////////////
    // Remove events with spurious PF candidate information (npf == 1000)
    if(npf > 999) return;
    ///////////////////////////////////////////////////

    if(selectEvent()){

        float mlbmin = 1000.;
        // Loop on the jets
        for (int ij = 0; ij < nj; ++ij){

            // Select CSV medium tagged ones
            if(jcsv[ij] < gCSVWPMedium) continue;

            TLorentzVector pj;

            // Loop on the leptons
            for (int il = 0; il < nl; ++il){
                TLorentzVector pl;

                // Calculate invariant mass
                pj.SetPtEtaPhiM(jpt[ij], jeta[ij], jphi[ij], 0.);
                pl.SetPtEtaPhiM(lpt[il], leta[il], lphi[il], 0.);
                float mlb = (pl + pj).M();

                // Store only if it's smaller than the minimum
                if (mlb < mlbmin) mlbmin = mlb;
            }
        }

        // Fill histogram with weights for branching fractions (w[0]),
        // pileup (w[1]), and lepton selection efficiency (w[4])
        // Check l 632-642 in bin/runTopAnalysis.cc for all the weights
        if(mlbmin < 1000.) fHMlb->Fill(mlbmin, w[0]*w[1]*w[4]);
    }
}

void MlbWidthAnalysis::Loop() {
    if (fChain == 0) return;
    Long64_t nentries = fChain->GetEntriesFast();
    if( fMaxevents > 0) nentries = TMath::Min(fMaxevents,nentries);

    Long64_t nbytes = 0, nb = 0;
    for (Long64_t jentry=0; jentry<nentries; jentry++) {
        // Load the tree variables
        Long64_t ientry = LoadTree(jentry);
        if (ientry < 0) break;
        nb = fChain->GetEntry(jentry);
        nbytes += nb;

        // Print progress
        if (jentry%500 == 0) {
            printf("\r [ %3d/100 ]", int(100*float(jentry)/float(nentries)));
            std::cout << std::flush;
        }

        // Run the actual analysis
        analyze();

    }
    std::cout << "\r [   done  ]" << std::endl;

}
#endif
