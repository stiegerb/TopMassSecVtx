#include <iostream>
#include <boost/shared_ptr.hpp>
#include <fstream>

#include "UserCode/TopMassSecVtx/interface/MacroUtils.h"
#include "UserCode/TopMassSecVtx/interface/SmartSelectionMonitor.h"
#include "UserCode/TopMassSecVtx/interface/DataEventSummaryHandler.h"
#include "UserCode/TopMassSecVtx/interface/TopSelectionTools.h"
#include "UserCode/TopMassSecVtx/interface/LxyAnalysis.h"
#include "UserCode/TopMassSecVtx/interface/UEAnalysis.h"
#include "UserCode/TopMassSecVtx/interface/TopPtWeighter.h"
#include "UserCode/TopMassSecVtx/interface/BfragWeighter.h"
#include "UserCode/TopMassSecVtx/interface/LeptonEfficiencySF.h"
#include "UserCode/TopMassSecVtx/interface/MuScleFitCorrector.h"

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
BfragWeighter *fBfragWgt=0;
LeptonEfficiencySF fLepEff;
FactorizedJetCorrector *fJesCor=0;
std::vector<JetCorrectionUncertainty *> fTotalJESUnc;
MuScleFitCorrector *fMuCor=0;
edm::LumiReWeighting *fLumiWeights=0;
utils::cmssw::PuShifter_t fPUshifters;

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
    std::vector<data::PhysicsObject_t *> leptons,jets;
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
        box.jets.push_back( &(jets[i]) );
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
    else if(antiIsoCands.size() > 0 && vetoCands.size() == 0){
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
    TString url = TString(urls[0]);
    TString baseDir     = runProcess.getParameter<std::string>("dirName");
    TString jecDir      = runProcess.getParameter<std::string>("jecDir");
    bool isMC           = runProcess.getParameter<bool>("isMC");
    double xsec         = runProcess.getParameter<double>("xsec");
    bool isV0JetsMC(isMC && (url.Contains("DYJetsToLL_50toInf") || url.Contains("TeV_WJets")));
    bool isTTbarMC(isMC && (url.Contains("TTJets") || url.Contains("_TT_") || url.Contains("TT2l_R")));
    TString out          = runProcess.getParameter<std::string>("outdir");
    bool saveSummaryTree = runProcess.getParameter<bool>("saveSummaryTree");
    std::vector<string>  weightsFile = runProcess.getParameter<std::vector<string> >("weightsFile");
    int maxEvents = runProcess.getParameter<int>("maxEvents");

    //jet energy scale uncertainties
    gSystem->ExpandPathName(jecDir);
    fJesCor = utils::cmssw::getJetCorrector(jecDir,isMC);
    TString srcnames[]= {
        "Total",
        "AbsoluteMPFBias", //in-situ correlation group
        "RelativeFSR",     //JEC inter-calibration
        "PileUpDataMC", "PileUpPtBB", "PileUpPtEC", "PileUpPtHF",      //Pileup
        "AbsoluteStat", "AbsoluteScale","HighPtExtra", "SinglePionECAL", "SinglePionHCAL", "RelativeJEREC1", "RelativeJEREC2", "RelativeJERHF", "RelativePtBB", "RelativePtEC1",  "RelativePtEC2", "RelativePtHF", "RelativeStatEC2", "RelativeStatHF", //JEC uncorrelated
        "FlavorPureGluon", "FlavorPureQuark", "FlavorPureCharm", "FlavorPureBottom" //flavor JES
    };
    const int nsrc = sizeof(srcnames)/sizeof(TString);
    for (int isrc = 0; isrc < nsrc; isrc++) {
        JetCorrectorParameters *p = new JetCorrectorParameters((jecDir+"/DATA_UncertaintySources_AK5PFchs.txt").Data(), srcnames[isrc].Data());
        fTotalJESUnc.push_back( new JetCorrectionUncertainty(*p) );
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
    TH1F* Hhepup        = (TH1F* )controlHistos.addHistogram(new TH1F ("heupnup"    , "hepupnup"    ,20,0,20) ) ;
    controlHistos.addHistogram( new TH1F ("nvertices", "; Vertex multiplicity; Events", 50, 0.,50.) );
    TString labels[]= {"Lepton(s)", "=1 jets","=2 jets","=3 jets","#geq4 jets","Jet selection", "E_{T}^{miss}", "#geq1 SecVtx"};
    int nsteps=sizeof(labels)/sizeof(TString);
    TH1F *baseEvtFlowH = (TH1F *)controlHistos.addHistogram( new TH1F("evtflow",";Selection step;Events",nsteps,0,nsteps) );
    for(int i=0; i<nsteps; i++) baseEvtFlowH->GetXaxis()->SetBinLabel(i+1,labels[i]);
    controlHistos.addHistogram( new TH1F("thetall", ";#theta(l,l') [rad];Events",50,0,3.2) );
    TH1F *baseJetMult=(TH1F *)controlHistos.addHistogram( new TH1F("njets",   ";Jet multiplicity; Events",6,0,6) );
    TH1F *baseSecVtxMult=(TH1F *)controlHistos.addHistogram( new TH1F("nsvtx",   ";SecVtx multiplicity; Events",4,0,4) );
    for(int i=0; i<6; i++)
    {
        TString label("= ");
        label += i;
        label += " jet";
        if(i!=1) label += "s";
        baseJetMult->GetXaxis()->SetBinLabel(i+1,label);
        if(i>=4) continue;
        label.ReplaceAll("jet","SecVtx");
        baseSecVtxMult->GetXaxis()->SetBinLabel(i+1,label);
    }

    controlHistos.addHistogram( new TH1F("met",          ";Missing transverse energy [GeV]; Events",50,0,250) );
    controlHistos.addHistogram( new TH1F("metoverht",    ";E_{T}^{miss}/#sqrt{H_{T}} [GeV^{1/2}]",50,0,15));
    controlHistos.addHistogram( new TH1F("photoniso",    ";log(Photon isolation/GeV+0.5)",20,-1,5));
    controlHistos.addHistogram( new TH1F("mt",           ";Transverse mass [GeV];Events",50,0,300) );
    controlHistos.addHistogram( new TH1F("mll",          ";Dilepton mass [GeV];Events",50,10,260) );

    //control plots for the leptons selected
    controlHistos.addHistogram( new TH1F("pt",       ";Transverse momentum; Leptons",25,0,200) );
    controlHistos.addHistogram( new TH1F("eta",      ";Pseudo-rapidity; Leptons",20,0,2.5) );
    controlHistos.addHistogram( new TH1F("reliso",   ";Relative isolation; Leptons",20,0.,0.25) );


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
         << " xSec x BR:               " << xsec << endl;

    if(isTTbarMC) {
        if(weightsFile.size()) {
            TString shapesDir("");
            shapesDir=weightsFile[0].c_str();
            fTopPtWgt = new TopPtWeighter( proctag, out, shapesDir, evSummary.getTree() );
	}
    }

    if(isMC) {
      TString burl(weightsFile[0].c_str());
      burl += "/BfragWeights.root";
      fBfragWgt = new BfragWeighter( burl );
    }
    

    //control the sec vtx analysis
    LxyAnalysis lxyAn;

    //control the UE analysis
    UEAnalysis ueAn(controlHistos);

    //prepare the output file
    TString outUrl(out);
    gSystem->ExpandPathName(outUrl);
    gSystem->Exec("mkdir -p " + outUrl);
    outUrl += "/";
    outUrl += proctag;
    outUrl += ".root";
    TFile *spyFile=TFile::Open(outUrl, "recreate");
    spyFile->cd();
    TDirectory *spyDir=0;
    if(saveSummaryTree)
    {
        gSystem->Exec("mkdir -p " + out);
        gDirectory->SaveSelf();
        spyFile->rmdir(proctag);
        spyDir = spyFile->mkdir("dataAnalyzer");
        spyDir->cd();
        lxyAn.attachToDir(spyDir);
        ueAn.attachToDir(spyDir);
    }


    //
    // analyze (puf...)
    //
    for (int inum=0; inum < totalEntries; ++inum)
    {
        if(inum%500==0) {
            printf("\r [ %d/100 ]",int(100*float(inum)/float(totalEntries)));
            cout << flush;
        }
        evSummary.getEntry(inum);
        DataEventSummary &ev = evSummary.getEvent();

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
        if(abs(box.cat)==11    && !eTrigger)    continue;
        if(abs(box.cat)==13    && !muTrigger)   continue;
        if(abs(box.cat)==11*11 && !eeTrigger)   continue;
        if(abs(box.cat)==11*13 && !emuTrigger)  continue;
        if(abs(box.cat)==13*13 && !mumuTrigger) continue;

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
        int nSecVtx(0);
        for(size_t ijet=0; ijet<box.jets.size(); ijet++) nSecVtx += (box.jets[ijet]->getVal("lxy")>0);
        bool passLxy(nSecVtx>0);

        //
        // MC CORRECTIONS
        //
        Hhepup->Fill(ev.nup,1);
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

        //ready to roll!
        //do s.th. here
        bool passLeptonSelection( box.lCat=="" );
        bool passJetSelection(false);
        int jetBin(box.jets.size()>4 ? 4 : box.jets.size());
        if(abs(box.cat)==11 || abs(box.cat)==13)                              passJetSelection = (jetBin>=4);
        if(abs(box.cat)==11*11 || abs(box.cat)==13*13 || abs(box.cat)==11*13) passJetSelection = (jetBin>=2);
        bool passMetSelection( box.metCat=="" );

        //used for background estimates in the dilepton channel
        float mt(utils::cmssw::getMT<LorentzVector>( *(box.leptons[0]), box.met)),thetall(0);
        LorentzVector ll(*(box.leptons[0]));
        if(box.leptons.size()>=2)
        {
            thetall = utils::cmssw::getArcCos<LorentzVector>( *(box.leptons[0]), *(box.leptons[1]) );
            ll     += *(box.leptons[1]);
        }

        //leading lepton charge
        int lepid = box.leptons[0]->get("id");
        int lepcharge = -1.*lepid/abs(lepid);
        if( isMC && !url.Contains("QCDMuPt20") ) lepcharge *= -1.;
        if( url.Contains("SingleMu2012B"))       lepcharge *= -1.;

        float evWeight( genWeight*puWeight*lepSelectionWeight );

        //control plots for the event selection
        bool passPreSelection( (passLeptonSelection || box.lCat=="z" || box.lCat=="qcd" ) &&
        	                                      passJetSelection && passMetSelection);
        if(box.leptons.size()>=2) controlHistos.fillHisto("mll",       box.chCat+"inc",            ll.mass(),  evWeight);
        else                      controlHistos.fillHisto("mt",        box.chCat+"inc",            mt,         evWeight);
        if(passLeptonSelection)
        {
            controlHistos.fillHisto("nvertices", box.chCat, ev.nvtx,         evWeight);
            controlHistos.fillHisto("evtflow", box.chCat, 0,               evWeight);
            for(size_t ilep=0; ilep<box.leptons.size(); ilep++)
            {
                int lid=abs(box.leptons[ilep]->get("id"));
                if(lid==11)
                {
                    controlHistos.fillHisto("pt",               box.chCat+"_e", box.leptons[ilep]->pt(),                       evWeight);
                    controlHistos.fillHisto("eta",              box.chCat+"_e", fabs(box.leptons[ilep]->eta()),                evWeight);
                    controlHistos.fillHisto("reliso",           box.chCat+"_e", box.leptons[ilep]->getVal("reliso"),           evWeight);
                }
                else
                {
                    controlHistos.fillHisto("pt",               box.chCat+"_mu", box.leptons[ilep]->pt(),                      evWeight);
                    controlHistos.fillHisto("eta",              box.chCat+"_mu", fabs(box.leptons[ilep]->eta()),               evWeight);
                    controlHistos.fillHisto("reliso",           box.chCat+"_mu", box.leptons[ilep]->getVal("reliso"),          evWeight);
                }
            }


            if(passMetSelection) controlHistos.fillHisto("njets",   box.chCat, box.jets.size(), evWeight);      //N-1 plot
            if(jetBin)
            {
                controlHistos.fillHisto("evtflow", box.chCat, jetBin, evWeight);
                if(passJetSelection)
                {
                    controlHistos.fillHisto("met",          box.chCat, box.met.pt(), evWeight); //N-1 plot
                    controlHistos.fillHisto("evtflow", box.chCat, 5,            evWeight);
                    if(passMetSelection)
                    {
                        controlHistos.fillHisto("evtflow", box.chCat, 6,         evWeight);
                        controlHistos.fillHisto("metoverht",  box.chCat, box.metsig,  evWeight);
                        controlHistos.fillHisto("eta",         box.chCat , fabs(box.leptons[0]->eta()),                evWeight);
                        controlHistos.fillHisto("eta",         box.chCat + (( lepcharge>0 ) ? "plus" : "minus"), fabs(box.leptons[0]->eta()),                evWeight);
                        controlHistos.fillHisto("photoniso",   box.chCat , log(fabs(box.leptons[0]->getVal("gIso03"))+0.5),                evWeight);
                        controlHistos.fillHisto("photoniso",   box.chCat + (( lepcharge>0 ) ? "plus" : "minus"), log(fabs(box.leptons[0]->getVal("gIso03"))+0.5),                evWeight);
                        if(box.leptons.size()>=2)
                        {
                            controlHistos.fillHisto("mll", box.chCat, ll.mass(), evWeight);
                            controlHistos.fillHisto("thetall", box.chCat, thetall,   evWeight);
                        }
                        else
                        {
                            controlHistos.fillHisto("mt",         box.chCat, mt,           evWeight);
                        }

                        controlHistos.fillHisto("nsvtx",     box.chCat, nSecVtx, evWeight); //N-1
                        if(passLxy) controlHistos.fillHisto("evtflow", box.chCat, 7, evWeight);
                    }
                    else if(box.leptons.size()>=2)
                    {
                        //for DY estimation in the MET sideband region
                        controlHistos.fillHisto("thetall", box.chCat+"lowmet", thetall, evWeight);
                    }
                }
                else if(passMetSelection)
                {
                    //for QCD and W estimation cross check in a jet multiplicity control region
                    controlHistos.fillHisto("eta",        box.chCat+box.jetCat, fabs(box.leptons[0]->eta()),                evWeight);
                    controlHistos.fillHisto("eta",        box.chCat+box.jetCat+(( lepcharge>0 ) ? "plus" : "minus"), fabs(box.leptons[0]->eta()),                evWeight);
                    controlHistos.fillHisto("photoniso",  box.chCat+box.jetCat , log(fabs(box.leptons[0]->getVal("gIso03"))+0.5),                evWeight);
                    controlHistos.fillHisto("photoniso",  box.chCat+box.jetCat+(( lepcharge>0 ) ? "plus" : "minus"), log(fabs(box.leptons[0]->getVal("gIso03"))+0.5),                evWeight);
                }
            }
        }

        //save selected event
        if(!saveSummaryTree || !passPreSelection) continue;
        lxyAn.resetBeautyEvent();
        BeautyEvent_t &bev=lxyAn.getBeautyEvent();
        int evCatSummary(box.cat);
        if( box.lCat=="qcd" ) evCatSummary*=100;
        if( box.lCat=="z"   ) evCatSummary*=1000;
        bev.evcat=evCatSummary;
        bev.gevcat=genCat;
        bev.run=ev.run;
        bev.event=ev.event;
        bev.lumi=ev.lumi;
        bev.nvtx=ev.nvtx;
        bev.rho=ev.rho;
        bev.nw=11;
        bev.w[0]  = genWeight;
        bev.w[1]  = puWeight;
        bev.w[2]  = puWeightUp;
        bev.w[3]  = puWeightDown;
        bev.w[4]  = lepSelectionWeight;
        bev.w[5]  = lepSelectionWeightUp;
        bev.w[6]  = lepSelectionWeightDown;
        bev.w[7]  = topPtWgt;
        bev.w[8]  = topPtWgtUp;
        bev.w[9]  = topPtWgtDown;
        bev.w[10] = topPtStdWgt;

        //Fill lxy tree
        data::PhysicsObjectCollection_t pf = evSummary.getPhysicsObject(DataEventSummaryHandler::PFCANDIDATES);
        lxyAn.analyze( box.leptons, box.jets, met, pf, gen);

        //add fragmentation weights using matched b's and B hadrons
        if(fBfragWgt) {
            for(Int_t ij=0; ij<bev.nj; ij++)
            {
                if(abs(bev.bid[ij])!=5 || bev.bpt[ij]<=0 || bev.bhadpt[ij]<=0) continue;
                std::vector<float> bfragWeights=fBfragWgt->getEventWeights( bev.bhadpt[ij]/bev.bpt[ij] );
                bev.bwgt[ij][0]=bfragWeights[0];
                bev.bwgt[ij][1]=bfragWeights[1];
                bev.bwgt[ij][2]=bfragWeights[2];
            }
        }

        //generated proc info
        bev.qscale=ev.qscale;
        bev.x1=ev.x1;
        bev.x2=ev.x2;
        bev.id1=ev.id1;
        bev.id2=ev.id2;

        //update
        spyDir->cd();
        lxyAn.save();

        //UE analysis
        if(abs(box.cat)==11*11 || abs(box.cat)==13*13 || abs(box.cat)==11*13)
        {
            ueAn.analyze(box.leptons, box.jets, met[0], pf, gen, ev.nvtx,genWeight*puWeight*lepSelectionWeight);
            ueAn.fillSummaryTuple(genWeight*puWeight*lepSelectionWeight);
        }
    }

    //
    // close opened files
    //
    inF->Close();

    //
    // finally, save histos and tree to local file
    //
    spyFile->cd();
    spyFile->Write();
    TVectorD constVals(2);
    constVals[0] = isMC ? cnorm : 1.0;
    constVals[1] = isMC ? xsec  : 1.0;
    constVals.Write("constVals");
    controlHistos.Write();
    spyFile->Close();

    //that's all folks!
}
