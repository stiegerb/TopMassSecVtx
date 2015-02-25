#ifndef SVLInfoTreeAnalysis_cxx
#define SVLInfoTreeAnalysis_cxx
#include "UserCode/TopMassSecVtx/interface/SVLInfoTreeAnalysis.h"
#include "UserCode/TopMassSecVtx/interface/MacroUtils.h"

#include "Math/VectorUtil.h"

#include <TLorentzVector.h>
#include <iostream>

//
void SVLInfoTreeAnalysis::RunJob(TString filename) {
    TFile *file = TFile::Open(filename, "recreate");
    Begin(file);
    Loop();
    End(file);
}
void SVLInfoTreeAnalysis::Begin(TFile *file) {
    // Anything that has to be done once at the beginning
    file->cd();
}

void SVLInfoTreeAnalysis::End(TFile *file) {
    // Anything that has to be done once at the end
    file->cd();
    WritePlots(file->GetName());
    file->Write();
    file->Close();
}

void SVLInfoTreeAnalysis::analyze() {
    // Called once per event
    FillPlots();
}

void SVLInfoTreeAnalysis::Loop() {
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

        analyze();

    }
    std::cout << "\r [   done  ]" << std::endl;

}
#endif
