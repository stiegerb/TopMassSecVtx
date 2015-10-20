#include <iostream>
#include <boost/shared_ptr.hpp>
#include <fstream>

#include "UserCode/TopMassSecVtx/interface/MacroUtils.h"
#include "UserCode/TopMassSecVtx/interface/SmartSelectionMonitor.h"
#include "UserCode/TopMassSecVtx/interface/DataEventSummaryHandler.h"
#include "UserCode/TopMassSecVtx/interface/TopSelectionTools.h"
#include "UserCode/TopMassSecVtx/interface/TopPtWeighter.h"
#include "UserCode/TopMassSecVtx/interface/LeptonEfficiencySF.h"
#include "UserCode/TopMassSecVtx/interface/MuScleFitCorrector.h"
#include "UserCode/TopMassSecVtx/interface/BtagUncertaintyComputer.h"

#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"

#include "FWCore/FWLite/interface/AutoLibraryLoader.h"
#include "FWCore/PythonParameterSet/interface/MakeParameterSets.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "PhysicsTools/Utilities/interface/LumiReWeighting.h"

#include "PhysicsTools/CondLiteIO/interface/RecordWriter.h"
#include "DataFormats/FWLite/interface/Record.h"
#include "DataFormats/FWLite/interface/EventSetup.h"
#include "DataFormats/FWLite/interface/ESHandle.h"
#include "CondFormats/PhysicsToolsObjects/interface/BinningPointByMap.h"
#include "RecoBTag/PerformanceDB/interface/BtagPerformance.h"
#include "PhysicsTools/FWLite/interface/CommandLineParser.h"

#include "TRandom2.h"
#include "TVectorD.h"
#include "TSystem.h"
#include "TFile.h"
#include "TChain.h"
#include "TChainElement.h"
#include "TCanvas.h"
#include "TString.h"
#include "TDirectory.h"
#include "TEventList.h"
#include "TRandom.h"
#include "TGraphErrors.h"

#include <iostream>

//correctors
TopPtWeighter *fTopPtWgt=0;
LeptonEfficiencySF fLepEff;
FactorizedJetCorrector *fJesCor=0;
std::vector<JetCorrectionUncertainty *> fTotalJESUnc;
MuScleFitCorrector *fMuCor=0;
edm::LumiReWeighting *fLumiWeights=0;
utils::cmssw::PuShifter_t fPUshifters;
TTree *fDileptonInfoTree;
Float_t fTqscale,fTx1,fTx2;
Int_t fTid1,fTid2;
Int_t fTEvent,fTRun,fTLumi,fTEvCat,fTNJets,fTNbJets,fTNPVtx;
Float_t fTWeight[11],fTJESWeight[5],fTBtagWeight[5],fTXSWeight;
Float_t fTMET;
Float_t fLpPt,fLmPt,fLpEta,fLmEta,fLpPhi,fLmPhi,fLpScale,fLmScale;
Int_t fLmId,fLpId;
Float_t fGenLpPt,fGenLmPt,fGenLpEta,fGenLmEta,fGenLpPhi,fGenLmPhi;
Int_t fGenLpId,fGenLmId;


using namespace std;


//
// ANALYSIS BOXES
//

//aggregates all the objects needed for the analysis
//cat identifies the category: 11-electron 13-muon 11*11,11*13,13*13-dilepton events
class AnalysisBox {
public:
    AnalysisBox() : cat(0), chCat(""), lCat(""), jetCat(""), metCat(""), metsig(0) { }
    ~AnalysisBox() { }
    Int_t cat;
    TString chCat, lCat, jetCat, metCat;
    std::vector<data::PhysicsObject_t *> leptons,jets,fjets;
    LorentzVector met;
    float metsig;
};

//
AnalysisBox assignBox(data::PhysicsObjectCollection_t &leptons,
                      data::PhysicsObjectCollection_t &jets,
                      LorentzVector &met,
                      bool hasDileptonTrigger,
                      bool hasLJetsTrigger)
{
    AnalysisBox box;
    box.cat=0;
    for(size_t i=0; i<jets.size(); i++) {
        if(fabs(jets[i].eta()) < 2.5) box.jets.push_back( &(jets[i]) );
        else                          box.fjets.push_back(&(jets[i]) );
    }
    box.met=met;

    std::vector<int> dilCands, ljCands, vetoCands, antiIsoCands;
    for(size_t i=0; i<leptons.size(); i++) {
        if(leptons[i].getFlag("passLL"))     dilCands.push_back(i);
        if(leptons[i].getFlag("passLJ"))     ljCands.push_back(i);
        else {
            if(leptons[i].getFlag("passLJveto")) vetoCands.push_back(i);
        }
        if(leptons[i].getFlag("passLAntiIso")) antiIsoCands.push_back(i);
    }

    //
    // ASSIGN THE BOX
    // 1. >=2 tight leptons: OS, pt>20,20 GeV -> ll, Mll>20, |Mll-MZ|>15
    // 2. =1 tight lepton: pt(e)>30  or pt(mu)>26 GeV and =0 vetoLeptons
    //
    box.lCat="";
    if(dilCands.size()>=2 && hasDileptonTrigger)
    {
        for(size_t i=0; i<dilCands.size(); i++) {
            box.leptons.push_back( &(leptons[ dilCands[i] ]) );
        }

        int dilId(box.leptons[0]->get("id")*box.leptons[1]->get("id"));
        LorentzVector dilepton( *(box.leptons[0]) );
        dilepton += *(box.leptons[1]);
        if(dilepton.mass()>20 && dilId<0)
        {
            if(  abs(dilId)==11*11 || abs(dilId)==13*13 || abs(dilId)==11*13 )            box.cat=dilId;
            if( (abs(dilId)==11*11 || abs(dilId)==13*13) && fabs(dilepton.mass()-91)<15)  box.lCat="z";
        }
    }
    else if(ljCands.size()==1 && vetoCands.size()==0 && hasLJetsTrigger)
    {
        box.leptons.push_back( &(leptons[ ljCands[0] ]) );
        box.cat=box.leptons[0]->get("id");
    }
    else if(antiIsoCands.size() > 0 && vetoCands.size() == 0) {
        box.leptons.push_back( &(leptons[ antiIsoCands[0] ]) );
        box.cat=box.leptons[0]->get("id");
        box.lCat="qcd";
    }

    int njetsBin( box.jets.size()>6 ? 6  : box.jets.size() );
    box.jetCat="jet";
    box.jetCat += njetsBin;
    float ht(0);
    for(size_t i=0; i<box.jets.size(); i++) ht += box.jets[i]->pt();
    box.metsig=(ht>0 ? box.met.pt()/sqrt(ht) : 9999. );

    box.metCat="";
    if( (abs(box.cat)==11*11 || abs(box.cat)==13*13) && met.pt()<40 ) box.metCat="lowmet";

    box.chCat="";
    if(abs(box.cat)==11)    box.chCat="e";
    if(abs(box.cat)==13)    box.chCat="mu";
    if(abs(box.cat)==11*11) box.chCat="ee";
    if(abs(box.cat)==11*13) box.chCat="emu";
    if(abs(box.cat)==13*13) box.chCat="mumu";

    //all done here
    return box;
}

//
void BookDileptonTree()
{
    fDileptonInfoTree = new TTree("DileptonInfo", "DiLepton Tree");
    fDileptonInfoTree->Branch("Event",     &fTEvent,     "Event/I");
    fDileptonInfoTree->Branch("Run",       &fTRun,       "Run/I");
    fDileptonInfoTree->Branch("Lumi",      &fTLumi,      "Lumi/I");
    fDileptonInfoTree->Branch("EvCat",     &fTEvCat,     "EvCat/I");
    fDileptonInfoTree->Branch("Weight",     fTWeight,    "Weight[11]/F");
    fDileptonInfoTree->Branch("JESWeight",  fTJESWeight, "JESWeight[5]/F");
    fDileptonInfoTree->Branch("BtagWeight",  fTBtagWeight, "BtagWeight[5]/F");
    fDileptonInfoTree->Branch("NJets",     &fTNJets,     "NJets/I");
    fDileptonInfoTree->Branch("NbJets",     &fTNbJets,     "NbJets/I");
    fDileptonInfoTree->Branch("MET",       &fTMET,       "MET/F");
    fDileptonInfoTree->Branch("NPVtx",     &fTNPVtx,     "NPVtx/I");
    fDileptonInfoTree->Branch("LpScale",   &fLpScale,     "LpScale/F");
    fDileptonInfoTree->Branch("LmScale",   &fLmScale,     "LmScale/F");
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

//
void ResetDileptonTree()
{
    fLpPt=0;
    fLmPt=0;
    fLpScale=1.0;
    fLmScale=1.0;
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
// THE MAIN METHOD
//
int main(int argc, char* argv[])
{
  // load framework libraries
  gSystem->Load( "libFWCoreFWLite" );
  AutoLibraryLoader::enable();
  
  //check arguments
  if ( argc < 2 ) {
    std::cout << "Usage : " << argv[0] << " parameters_cfg.py" << std::endl;
    return 0;
  }
  
  //
  // configure
  //
  const edm::ParameterSet &runProcess = edm::readPSetsFrom(argv[1])->getParameter<edm::ParameterSet>("runProcess");
  std::vector<std::string> urls=runProcess.getParameter<std::vector<std::string> >("input");
  TString url         = TString(urls[0]);
  TString baseDir     = runProcess.getParameter<std::string>("dirName");
  TString jecDir      = runProcess.getParameter<std::string>("jecDir");
  bool isMC           = runProcess.getParameter<bool>("isMC");
  fTXSWeight          = runProcess.getParameter<double>("xsec");
  bool isV0JetsMC(isMC && (url.Contains("DYJetsToLL_50toInf") || url.Contains("TeV_WJets")));
  bool isTTbarMC(isMC && (url.Contains("TTJets") || url.Contains("_TT_") || url.Contains("TT2l_R")));
  TString out          = runProcess.getParameter<std::string>("outdir");    
  std::vector<string>  weightsFile = runProcess.getParameter<std::vector<string> >("weightsFile");
  int maxEvents = runProcess.getParameter<int>("maxEvents");
  
  //jet energy scale uncertainties
  gSystem->ExpandPathName(jecDir);
  fJesCor = utils::cmssw::getJetCorrector(jecDir,isMC);
  JetCorrectorParameters *p = new JetCorrectorParameters((jecDir+"/DATA_UncertaintySources_AK5PFchs.txt").Data(), "Total");
  fTotalJESUnc.push_back( new JetCorrectionUncertainty(*p) );
  
  //random generator
  TRandom2 rndGen;
  
  //btagging utils
  BTagSFUtil btsfutil;
  std::map<std::pair<TString,TString>, std::pair<TGraphErrors *,TGraphErrors *> > btagEffCorr_;
  if(jecDir!="")
    {
      TString btagEffCorrUrl(jecDir);
      btagEffCorrUrl += "/../weights/btagEff.root";
      gSystem->ExpandPathName(btagEffCorrUrl);
      TFile *btagF=TFile::Open(btagEffCorrUrl);
      cout << btagEffCorrUrl << endl;
      if(btagF!=0 && !btagF->IsZombie())
	{
	  TList *dirs=btagF->GetListOfKeys();
	  for(int itagger=0; itagger<dirs->GetEntries(); itagger++)
	    {
	      TString iDir(dirs->At(itagger)->GetName());
	      btagEffCorr_[ std::pair<TString,TString>(iDir,"b") ]
		= std::pair<TGraphErrors *,TGraphErrors *>( (TGraphErrors *) btagF->Get(iDir+"/beff"),(TGraphErrors *) btagF->Get(iDir+"/sfb") );
	      btagEffCorr_[ std::pair<TString,TString>(iDir,"c") ]
		= std::pair<TGraphErrors *,TGraphErrors *>( (TGraphErrors *) btagF->Get(iDir+"/ceff"),(TGraphErrors *) btagF->Get(iDir+"/sfc") );
	      btagEffCorr_[ std::pair<TString,TString>(iDir,"udsg") ]
		= std::pair<TGraphErrors *,TGraphErrors *>( (TGraphErrors *) btagF->Get(iDir+"/udsgeff"),(TGraphErrors *) btagF->Get(iDir+"/sfudsg") );
	    }
	}
      std::cout << btagEffCorr_.size() << " b-tag correction factors have been read" << std::endl;
    }
  
    //muon energy corrector
    fMuCor = getMuonCorrector(jecDir,url);

    //
    // check input file
    //
    TFile *inF = TFile::Open(url);
    if(inF==0) return -1;
    if(inF->IsZombie()) return -1;
    TString proctag=gSystem->BaseName(url);
    Ssiz_t pos=proctag.Index(".root");
    proctag.Remove(pos,proctag.Length());
    bool isDoubleElePD(!isMC && url.Contains("DoubleEle"));
    bool isDoubleMuPD (!isMC && url.Contains("DoubleMu"));
    bool isMuEGPD     (!isMC && url.Contains("MuEG"));
    bool isSingleElePD(!isMC && url.Contains("SingleEle"));
    bool isSingleMuPD (!isMC && url.Contains("SingleMu"));

    //
    // pileup reweighter
    //
    if(isMC)
    {
        std::vector<double> dataPileupDistributionDouble = runProcess.getParameter< std::vector<double> >("datapileup");
        std::vector<float> dataPileupDistribution;
        for(unsigned int i=0; i<dataPileupDistributionDouble.size(); i++) {
            dataPileupDistribution.push_back(dataPileupDistributionDouble[i]);
        }
        std::vector<float> mcPileupDistribution;
        if(isMC) {
            TString puDist(baseDir+"/pileuptrue");
            TH1F* histo = (TH1F *) inF->Get(puDist);
            if(!histo)std::cout<<"pileuptrue histogram is null!!!\n";
            for(int i=1; i<=histo->GetNbinsX(); i++) {
                mcPileupDistribution.push_back(histo->GetBinContent(i));
            }
            delete histo;
        }
        while(mcPileupDistribution.size()<dataPileupDistribution.size()) mcPileupDistribution.push_back(0.0);
        while(mcPileupDistribution.size()>dataPileupDistribution.size()) dataPileupDistribution.push_back(0.0);

        gROOT->cd();  //THIS LINE IS NEEDED TO MAKE SURE THAT HISTOGRAM INTERNALLY PRODUCED IN LumiReWeighting ARE NOT DESTROYED WHEN CLOSING THE FILE
        fLumiWeights = new edm::LumiReWeighting(mcPileupDistribution,dataPileupDistribution);
        fPUshifters=utils::cmssw::getPUshifters(dataPileupDistribution,0.05);
    }

    //
    // control histograms
    //
    gROOT->cd(); //do not, i repeat, do not remove me ;)
    SmartSelectionMonitor controlHistos;    
    controlHistos.addHistogram( new TH1F ("nvertices", "; Vertex multiplicity; Events", 50, 0.,50.) );
    TString labels[]= {"e#mu", "#geq1 jets","#geq1 b-tags"};
    int nsteps=sizeof(labels)/sizeof(TString);
    TH1F *evtFlowH = (TH1F *)controlHistos.addHistogram( new TH1F("evtflow",";Selection step;Events",nsteps,0,nsteps) );
    for(int i=0; i<nsteps; i++) evtFlowH->GetXaxis()->SetBinLabel(i+1,labels[i]);
    controlHistos.addHistogram( new TH1F("njets",   ";Jet multiplicity; Events",4,0,4) );
    controlHistos.addHistogram( new TH1F("nbtags",   ";b-tag multiplicity; Events",4,0,4) );
    controlHistos.addHistogram( new TH1F("met",          ";Missing transverse energy [GeV]; Events",50,0,250) );
    controlHistos.addHistogram( new TH1F("mll",          ";Dilepton mass [GeV];Events",50,10,260) );
    controlHistos.addHistogram( new TH1F("pt",       ";Transverse momentum; Leptons",25,0,200) );
    controlHistos.addHistogram( new TH1F("eta",      ";Pseudo-rapidity; Leptons",20,0,2.5) );


    ///
    // process events file
    //
    DataEventSummaryHandler evSummary;
    if( !evSummary.attach( (TTree *) inF->Get(baseDir+"/data") ) )  {
        inF->Close();
        return -1;
    }

    Int_t entries_to_process = -1;
    if(maxEvents > 0) entries_to_process = maxEvents;
    else              entries_to_process = evSummary.getEntries();
    const Int_t totalEntries = entries_to_process;

    float cnorm=1.0;
    if(isMC) {
        TH1F* cutflowH = (TH1F *) inF->Get(baseDir+"/cutflow");
        if(cutflowH) cnorm=cutflowH->GetBinContent(1);
    }

    cout << "Processing: " << proctag << " @ " << url << endl
         << "Initial number of events: " << cnorm << endl
         << "Events in tree:           " << totalEntries << endl
         << "xSec x BR:                " << fTXSWeight << endl;

    if(isTTbarMC) {
        if(weightsFile.size()) {
            TString shapesDir(weightsFile[0].c_str());
            TString weightsDir(weightsFile[0].c_str());
            weightsDir += "toppt";
            fTopPtWgt = new TopPtWeighter( proctag, weightsDir, shapesDir, evSummary.getTree() );
        }
    }

    //prepare the output file
    TString outUrl(out);
    gSystem->ExpandPathName(outUrl);
    gSystem->Exec("mkdir -p " + outUrl);
    outUrl += "/";
    outUrl += proctag;
    outUrl += ".root";
    TFile *spyFile=TFile::Open(outUrl, "recreate");
    BookDileptonTree();
    fDileptonInfoTree->SetDirectory(spyFile);


    //
    // analyze (puf...)
    //
    for (int inum=0; inum < totalEntries; ++inum)
      {
        if(inum%100==0) {
            printf("\r [ %d/100 ]",int(100*float(inum)/float(totalEntries)));
            cout << flush;
        }
        evSummary.getEntry(inum);
        DataEventSummary &ev = evSummary.getEvent();
	ResetDileptonTree();

        //
        // OBJECT SELECTION
        //

        //trigger bits
        bool eeTrigger   = ev.t_bits[0];
        bool emuTrigger  = ev.t_bits[4] || ev.t_bits[5];
        bool mumuTrigger = ev.t_bits[2] || ev.t_bits[3];
        bool muTrigger   = ev.t_bits[6];
        bool eTrigger    = ev.t_bits[13];
        if(!isMC) {
            eeTrigger   &= ( isDoubleElePD && !isMuEGPD && !isDoubleMuPD && !isSingleMuPD && !isSingleElePD);
            emuTrigger  &= (!isDoubleElePD &&  isMuEGPD && !isDoubleMuPD && !isSingleMuPD && !isSingleElePD);
            mumuTrigger &= (!isDoubleElePD && !isMuEGPD &&  isDoubleMuPD && !isSingleMuPD && !isSingleElePD);
            muTrigger   &= (!isDoubleElePD && !isMuEGPD && !isDoubleMuPD &&  isSingleMuPD && !isSingleElePD);
            eTrigger    &= (!isDoubleElePD && !isMuEGPD && !isDoubleMuPD && !isSingleMuPD &&  isSingleElePD);

            //dismiss data event if trigger is not there
            if(isDoubleElePD && !eeTrigger)   continue;
            if(isMuEGPD      && !emuTrigger)  continue;
            if(isDoubleMuPD  && !mumuTrigger) continue;
            if(isSingleMuPD  && !muTrigger)   continue;
            if(isSingleElePD && !eTrigger)    continue;
        }
        // Disable single electron trigger for MC
        if(isMC) eTrigger = true;

        //leptons
        data::PhysicsObjectCollection_t leptons( evSummary.getPhysicsObject(DataEventSummaryHandler::LEPTONS) );
        data::PhysicsObjectCollection_t selLeptons=top::selectLeptons(leptons,fMuCor, ev.rho, isMC);
        if(!isMC)
	  {
            //dismiss data event if lepton multiplicity is not ok
            if((eTrigger || muTrigger) && selLeptons.size()==0) continue;
            if((mumuTrigger || emuTrigger || eeTrigger) && selLeptons.size()<2) continue;
        }
	
        //jet/met
        data::PhysicsObjectCollection_t jets(evSummary.getPhysicsObject(DataEventSummaryHandler::JETS));
        LorentzVector jetDiff=utils::cmssw::updateJEC(jets, fJesCor, fTotalJESUnc, ev.rho, ev.nvtx, isMC);
        data::PhysicsObjectCollection_t selJets = top::selectJets(jets,selLeptons);
        data::PhysicsObjectCollection_t recoMet = evSummary.getPhysicsObject(DataEventSummaryHandler::MET);
        //0,1 - raw pfmet, 2 - type1 pfmet, 3 - type1p2 corrected met
        recoMet[2].SetPxPyPzE(recoMet[2].px()-jetDiff.px(),
                              recoMet[2].py()-jetDiff.py(),
                              0.,
                              sqrt(pow(recoMet[2].px()-jetDiff.px(),2)+pow(recoMet[2].py()-jetDiff.py(),2))
                             );
        std::vector<LorentzVector> met = utils::cmssw::getMETvariations(recoMet[2], selJets, selLeptons, isMC);

        //get the category and check if trigger is consistent
        AnalysisBox box = assignBox(selLeptons, selJets, met[0],
                                    (eeTrigger || emuTrigger || mumuTrigger),
                                    (eTrigger || muTrigger) );
        if(box.cat==0) continue;

        //efficiencies for lepton slections
        float lepSelectionWeight(1.0),lepSelectionWeightUp(1.0),lepSelectionWeightDown(1.0);
        if(isMC)
        {
            std::pair<float,float> lepSF(1.0,0.0);
            if(abs(box.cat)==13 || abs(box.cat)==11) lepSF=fLepEff.getSingleLeptonEfficiencySF(selLeptons[0].eta(),box.cat);
            else
            {
                float eta1(selLeptons[0].eta()),eta2(selLeptons[1].eta());
                if(abs(box.cat)==11*13) {
                    if(abs(selLeptons[0].get("id"))==13) {
                        eta2=selLeptons[0].eta();
                        eta1=selLeptons[1].eta();
                    }
                }
                lepSF=fLepEff.getDileptonEfficiencySF(eta1,eta2,box.cat);
            }
            lepSelectionWeight=lepSF.first;
            lepSelectionWeightUp=lepSelectionWeight+lepSF.second;
            lepSelectionWeightDown=lepSelectionWeight-lepSF.second;
        }

        //b-tagging
	int njets(0), njetsJESUp(0), njetsJESDown(0), njetsJERUp(0), njetsJERDown(0);
	int nbtags(0), nbtagsSFbUp(0), nbtagsSFbDown(0), nbtagsSFlUp(0), nbtagsSFlDown(0);	
        for(size_t ijet=0; ijet<box.jets.size(); ijet++) 
	  {
	    if(fabs(box.jets[ijet]->eta())>2.5) continue;
	    float jetpt=box.jets[ijet]->pt();
	    njets        += (jetpt>30);
	    njetsJESUp   += (box.jets[ijet]->getVal("unc0_up")>30);
	    njetsJESDown += (box.jets[ijet]->getVal("unc0_down")>30);
	    njetsJERUp   += (box.jets[ijet]->getVal("jerup")>30);
	    njetsJERDown += (box.jets[ijet]->getVal("jerdown")>30);

	    bool btagStatus (box.jets[ijet]->getVal("csv")>0.783);
	    bool nomBtagStatus(btagStatus);
	    bool nomBtagStatusSFbDown(btagStatus);
	    bool nomBtagStatusSFbUp(btagStatus);
	    bool nomBtagStatusSFlDown(btagStatus);
	    bool nomBtagStatusSFlUp(btagStatus);
	    
	    const data::PhysicsObject_t &genJet=box.jets[ijet]->getObject("genJet");
	    if(genJet.pt()>0 && !btagEffCorr_.empty()) 
	      {
		Int_t jflav = genJet.info.find("id")->second;
		TString flavKey("udsg");
		if(abs(jflav)==5) flavKey="b";
		else if (abs(jflav)==4) flavKey="c";
		std::pair<TString,TString> key("csvM",flavKey);
		
		TGraphErrors *mceffGr = btagEffCorr_[key].first;
		TGraphErrors *sfGr    = btagEffCorr_[key].second;
		float eff             = mceffGr->Eval(box.jets[ijet]->pt());
		float sf              = sfGr->Eval(box.jets[ijet]->pt());
		//take uncertainty for sf from point #3 ~ pT=50 GeV
		//(otherwise one needs to loop to find the closest pt)
		//it's ok as this is a uncertainty for a rate
		float sfunc           = sfGr->GetErrorY(3);
		
		//correct for sf (+/- unc)
		btsfutil.modifyBTagsWithSF(nomBtagStatus,sf,eff);
		if(flavKey!="b")
		  {
		    btsfutil.modifyBTagsWithSF(nomBtagStatusSFbUp,sf+sfunc,eff);
		    btsfutil.modifyBTagsWithSF(nomBtagStatusSFbDown,sf-sfunc,eff);
		    nomBtagStatusSFlDown=nomBtagStatus;
		    nomBtagStatusSFlUp=nomBtagStatus;
		  }
		else
		  {
		    btsfutil.modifyBTagsWithSF(nomBtagStatusSFlUp,sf+sfunc,eff);
		    btsfutil.modifyBTagsWithSF(nomBtagStatusSFlDown,sf-sfunc,eff);
		    nomBtagStatusSFbDown=nomBtagStatus;
		    nomBtagStatusSFbUp=nomBtagStatus;
		  }
	      }

	    nbtags        += nomBtagStatus;
	    nbtagsSFbUp   += nomBtagStatusSFbUp;
	    nbtagsSFbDown += nomBtagStatusSFbDown;
	    nbtagsSFlUp   += nomBtagStatusSFlUp;
	    nbtagsSFlDown += nomBtagStatusSFlDown;
	  }

	//
        // MC CORRECTIONS
        //
        if(isV0JetsMC && ev.nup>5) continue;

        //pileup weight
        float puWeight(1.0), puWeightUp(1.0), puWeightDown(1.0);
        if(isMC && fLumiWeights) {
            puWeight     = fLumiWeights->weight(ev.ngenTruepu);
            puWeightUp   = puWeight*fPUshifters[utils::cmssw::PUUP]->Eval(ev.ngenTruepu);
            puWeightDown = puWeight*fPUshifters[utils::cmssw::PUDOWN]->Eval(ev.ngenTruepu);
        }

        //top pT weights and MC truth
        data::PhysicsObjectCollection_t gen=evSummary.getPhysicsObject(DataEventSummaryHandler::GENPARTICLES);
        int ngenLeptonsStatus3(0);
        float topPtWgt(1.0), topPtWgtUp(1.0), topPtWgtDown(1.0),topPtStdWgt(1.0);
        float genWeight(1.0);
        int genCat(1);
        if(isMC) {
            float pttop(0), ptantitop(0);
            for(size_t igen=0; igen<gen.size(); igen++) {
                if(gen[igen].get("status")!=3) continue;
                int absid=abs(gen[igen].get("id"));
                if(absid==6) {
                    if(gen[igen].get("id")==6) pttop=gen[igen].pt();
                    else                       ptantitop=gen[igen].pt();
                }
                if(absid!=11 && absid!=13 && absid!=15) continue;
                ngenLeptonsStatus3++;
                genCat *= absid;
            }

            //top-pt and BR re-weighting only for TTbar!
            if(isTTbarMC)
            {
                //branching ratio correction for inclusive Madgraph samples: same approximation since 2010...
                if(ngenLeptonsStatus3==2)      {
                    genWeight=pow(0.1086/(1./9.),2);
                }
                else if(ngenLeptonsStatus3==1) {
                    genWeight=(0.1086/(1./9.))*(0.6741/(2./3.));
                }
                else                           {
                    genWeight=pow(0.6741/(2./3.),2);
                }

                if(pttop>0 && ptantitop>0 && fTopPtWgt)
                {
                    fTopPtWgt->computeWeight(pttop,ptantitop);
                    fTopPtWgt->getEventWeight(topPtWgt, topPtWgtUp, topPtWgtDown );

                    //cf. https://twiki.cern.ch/twiki/bin/view/CMS/TopPtReweighting
                    float a(0.156),b(-0.00137);
                    topPtStdWgt=sqrt(exp(a+b*pttop)*exp(a+b*ptantitop));
                }
            }
        }
        else genCat = 0;

        float evWeight( genWeight*puWeight*lepSelectionWeight );

	fTNPVtx=ev.nvtx;
        if(abs(box.cat)!=11*13) continue;
	if(!emuTrigger)  continue;
	controlHistos.fillHisto("nvertices", box.chCat, fTNPVtx, evWeight);
	controlHistos.fillHisto("evtflow",   box.chCat, 0,       evWeight);

	fTNJets=njets;
	controlHistos.fillHisto("njets",   box.chCat, fTNJets, evWeight);      
	if(njets+njetsJESUp+njetsJESDown+njetsJERUp+njetsJERDown==0) continue;

	fTNbJets=nbtags;
	if(njets>0)
	  {
	    controlHistos.fillHisto("nbtags",   box.chCat, nbtags, evWeight);      
	    controlHistos.fillHisto("evtflow", box.chCat, 1,               evWeight);
	  }       
	if(nbtags+nbtagsSFbUp+nbtagsSFbDown+nbtagsSFlUp+nbtagsSFlDown==0) continue;

	fTMET=box.met.pt();
	LorentzVector ll( *(box.leptons[0]) + *(box.leptons[1]) );
	if(njets>0 && nbtags>0)
	  {
	    controlHistos.fillHisto("met", box.chCat, fTMET, evWeight);
	    controlHistos.fillHisto("mll", box.chCat, ll.mass(), evWeight);
	    controlHistos.fillHisto("evtflow", box.chCat, 2,               evWeight);
	    for(size_t ilep=0; ilep<2; ilep++)
	      {
		int lid=abs(box.leptons[ilep]->get("id"));
		if(lid==11)
		  {
		    controlHistos.fillHisto("pt",               box.chCat+"_e", box.leptons[ilep]->pt(),                       evWeight);
		    controlHistos.fillHisto("eta",              box.chCat+"_e", fabs(box.leptons[ilep]->eta()),                evWeight);
		  }
		else
		  {
		    controlHistos.fillHisto("pt",               box.chCat+"_mu", box.leptons[ilep]->pt(),                      evWeight);
		    controlHistos.fillHisto("eta",              box.chCat+"_mu", fabs(box.leptons[ilep]->eta()),               evWeight);
		  }
	      }	    
	  }

	//fill event
	fTEvent=ev.event;
	fTRun=ev.run;
	fTLumi=ev.lumi;
	fTEvCat=box.cat;
	fTWeight[0] = genWeight;
        fTWeight[1]  = puWeight;
        fTWeight[2]  = puWeightUp;
        fTWeight[3]  = puWeightDown;
        fTWeight[4]  = lepSelectionWeight;
        fTWeight[5]  = lepSelectionWeightUp;
        fTWeight[6]  = lepSelectionWeightDown;
        fTWeight[7]  = topPtWgt;
        fTWeight[8]  = topPtWgtUp;
        fTWeight[9]  = topPtWgtDown;
        fTWeight[10] = topPtStdWgt;
        fTJESWeight[0] = (njets>0 ? 1. : 0.);
	fTJESWeight[1] = (njetsJESUp>0 ? 1. : 0.);
	fTJESWeight[2] = (njetsJESDown>0 ? 1. : 0.);
	fTJESWeight[3] = (njetsJERUp>0 ? 1. : 0.);
	fTJESWeight[4] = (njetsJERDown>0? 1. : 0.);
	fTBtagWeight[0] = (nbtags>0? 1. : 0.);
	fTBtagWeight[1] = (nbtagsSFbUp>0?1. : 0.);
	fTBtagWeight[2] = (nbtagsSFbDown>0?1. : 0.);
	fTBtagWeight[3] = (nbtagsSFlUp>0?1.:0.);
	fTBtagWeight[4] = (nbtagsSFlDown>0?1.:0.);	
	fTqscale=ev.qscale;
        fTx1=ev.x1;
        fTx2=ev.x2;
        fTid1=ev.id1;
        fTid2=ev.id2;	
	for(size_t ilep=0; ilep<2; ilep++)
	  {
	    int lepid = box.leptons[ilep]->get("id");
	    int lepcharge = -1.*lepid/abs(lepid);
	    if( isMC && !url.Contains("QCDMuPt20") ) lepcharge *= -1.;
	    if( url.Contains("SingleMu2012B"))       lepcharge *= -1.;	    
	    const data::PhysicsObject_t &genl=box.leptons[ilep]->getObject("gen");
	    float glpt(genl.pt()), gleta(genl.eta()), glphi(genl.phi());
	    Int_t glid( glpt>0 ? genl.info.find("id")->second : 0);	    
	    if(lepcharge<0)
	      {
		fLmPt=box.leptons[ilep]->pt();
		fLmEta=box.leptons[ilep]->eta();
		fLmPhi=box.leptons[ilep]->phi();
		fLmId=(-1)*lepcharge*abs(lepid);
		fLmScale=abs(fLmId)==11 ? utils::cmssw::getElectronEnergyScale(fLmPt,fabs(fLmEta)): 0.002;
		fGenLmPt=glpt;
		fGenLmEta=gleta;
		fGenLmPhi=glphi;
		fGenLmId=glid;
	      }
	    else
	      {
		fLpPt=box.leptons[ilep]->pt();
		fLpEta=box.leptons[ilep]->eta();
		fLpPhi=box.leptons[ilep]->phi();
		fLpId=(-1)*lepcharge*abs(lepid);
		fLpScale=abs(fLpId)==11 ? utils::cmssw::getElectronEnergyScale(fLpPt,fabs(fLpEta)): 0.002;
		fGenLpPt=glpt;
		fGenLpEta=gleta;
		fGenLpPhi=glphi;
		fGenLpId=glid;
	      }
	  }

	fDileptonInfoTree->Fill();
    }

    //
    // close opened files
    //
    inF->Close();

    //
    // finally, save histos and tree to local file
    //
    spyFile->cd();
    controlHistos.Write();
    TVectorD constVals(2);
    constVals[0] = isMC ? cnorm : 1.0;    
    constVals[1] = isMC ? fTXSWeight  : 1.0;
    constVals.Write("constVals");
    fDileptonInfoTree->Write();
    spyFile->Close();
 }
