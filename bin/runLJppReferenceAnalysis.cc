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

#include "UserCode/TopMassSecVtx/interface/TopAnalysisCommon.h"

using namespace std;

struct LJEvent_t
{
  Float_t w;
  ULong64_t run,lumi,event;
  Int_t nj,ngj,nb;
  Int_t j_btag[20];  
  Float_t j_pt[20],j_eta[20],j_phi[20],j_m[20];
  Float_t gj_pt[20],gj_eta[20],gj_phi[20],gj_m[20];
  Int_t l_id;
  Float_t l_pt, l_eta, l_phi, l_m;
  Float_t gl_pt, gl_eta, gl_phi, gl_m;
  Float_t met_pt, met_phi;
  Int_t ntracks,ntracks_hp;
};


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

    if(isDoubleElePD || isDoubleMuPD || isMuEGPD) return 0;

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
    TH1F *baseJetMult=(TH1F *)controlHistos.addHistogram( new TH1F("njets",   ";Jet multiplicity; Events",6,2,8) );
    TH1F *basebJetMult=(TH1F *)controlHistos.addHistogram( new TH1F("nbjets",   ";b-jet multiplicity; Events",4,0,4) );
    for(int i=0; i<6; i++)
    {
        TString label("= ");
        label += i+2;
        label += " jet";
        if(i!=1) label += "s";
        baseJetMult->GetXaxis()->SetBinLabel(i+1,label);

        label="= ";
        label += i;
        label += " jet";
        if(i!=1) label += "s";
        basebJetMult->GetXaxis()->SetBinLabel(i+1,label);
    }

    controlHistos.addHistogram( new TH1F("mt",       ";M_{T} [GeV]; Events",50,0,250) );
    controlHistos.addHistogram( new TH1F("met",      ";Missing transverse energy [GeV]; Events",50,0,250) );
    controlHistos.addHistogram( new TH1F("ht",       ";H_{T} [GeV]; Events",50,0,500) );
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
         << " xSec x BR:               " << xsec << endl;



    if(isTTbarMC) {
        if(weightsFile.size()) {
            TString shapesDir(weightsFile[0].c_str());
            TString weightsDir(weightsFile[0].c_str());
            weightsDir += "toppt";
            fTopPtWgt = new TopPtWeighter( proctag, weightsDir, shapesDir, evSummary.getTree() );
        }
    }

    if(isMC) {
        TString burl(weightsFile[0].c_str());
        burl += "/BfragWeights.root";
        fBfragWgt = new BfragWeighter( burl );
    }


    //prepare the output file
    TString outUrl(out);
    gSystem->ExpandPathName(outUrl);
    gSystem->Exec("mkdir -p " + outUrl);
    outUrl += "/";
    outUrl += proctag;
    outUrl += ".root";
    TFile *spyFile=TFile::Open(outUrl, "recreate");
    spyFile->cd();
    LJEvent_t ljev;
    TTree *outT=0;
    if(saveSummaryTree)
    {
        gSystem->Exec("mkdir -p " + out);
        gDirectory->SaveSelf();
	outT=new TTree("data","data");
	outT->SetDirectory(spyFile);
	outT->Branch("run",     &ljev.run,      "run/l");
	outT->Branch("lumi",    &ljev.lumi,     "lumi/l");
	outT->Branch("event",   &ljev.event,    "event/l");
	outT->Branch("w",    &ljev.w,       "w/F");
	outT->Branch("nj",   &ljev.nj,      "nj/I");
	outT->Branch("nb",   &ljev.nb,      "nb/I");
	outT->Branch("j_btag", ljev.j_btag, "j_btag[nj]/I");
	outT->Branch("j_pt",   ljev.j_pt,   "j_pt[nj]/F");
	outT->Branch("j_eta",  ljev.j_eta,  "j_eta[nj]/F");
	outT->Branch("j_phi",  ljev.j_phi,  "j_phi[nj]/F");
	outT->Branch("j_m",    ljev.j_m,    "j_m[nj]/F");
	outT->Branch("l_id",  &ljev.l_id,   "l_id/I");
	outT->Branch("l_pt",  &ljev.l_pt,   "l_pt/F");
	outT->Branch("l_eta", &ljev.l_eta,  "l_eta/F");
	outT->Branch("l_phi", &ljev.l_phi,  "l_phi/F");
	outT->Branch("l_m",   &ljev.l_m,    "l_m/F");
	outT->Branch("met_pt", &ljev.met_pt,  "met_pt/F");
	outT->Branch("met_phi",   &ljev.met_phi,    "met_phi/F");
	outT->Branch("ntracks",   &ljev.ntracks,    "ntracks/I");
	outT->Branch("ntracks_hp",   &ljev.ntracks_hp,    "ntracks_hp/I");
	if(isMC)
	  {
	    outT->Branch("ngj",   &ljev.ngj,    "ngj/I");
	    outT->Branch("gj_pt",   ljev.gj_pt,   "gj_pt[ngj]/F");
	    outT->Branch("gj_eta",  ljev.gj_eta,  "gj_eta[ngj]/F");
	    outT->Branch("gj_phi",  ljev.gj_phi,  "gj_phi[ngj]/F");
	    outT->Branch("gj_m",    ljev.gj_m,    "gj_m[ngj]/F");
	    outT->Branch("gl_pt",  &ljev.gl_pt,   "gl_pt/F");
	    outT->Branch("gl_eta", &ljev.gl_eta,  "gl_eta/F");
	    outT->Branch("gl_phi", &ljev.gl_phi,  "gl_phi/F");
	    outT->Branch("gl_m",   &ljev.gl_m,    "gl_m/F");	    
	  }
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
        bool muTrigger   = ev.t_bits[6];
        bool eTrigger    = ev.t_bits[13];
        if(!isMC) {
            muTrigger   &= (!isDoubleElePD && !isMuEGPD && !isDoubleMuPD &&  isSingleMuPD && !isSingleElePD);
            eTrigger    &= (!isDoubleElePD && !isMuEGPD && !isDoubleMuPD && !isSingleMuPD &&  isSingleElePD);

            //dismiss data event if trigger is not there
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
                                    false,
                                    (eTrigger || muTrigger) );
        if(abs(box.cat)!=11 && abs(box.cat)!=13) continue;
	if(abs(box.cat)==11    && !eTrigger)    continue;
        if(abs(box.cat)==13    && !muTrigger)   continue;

	float mt( utils::cmssw::getMT<LorentzVector>(*(box.leptons[0]),box.met) );

        //efficiencies for lepton slections
        float lepSelectionWeight(1.0); //lepSelectionWeightUp(1.0),lepSelectionWeightDown(1.0);
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
            //lepSelectionWeightUp=lepSelectionWeight+lepSF.second;
            //lepSelectionWeightDown=lepSelectionWeight-lepSF.second;
        }

        //b-tagging
        int nbtags(0),njets(0);
	ljev.nj=0;
	ljev.ngj=0;
	float ht(0);
        for(size_t ijet=0; ijet<selJets.size(); ijet++) 
	  {
	    if(deltaR( selJets[ijet], selLeptons[0])<0.5) continue;
	    if(selJets[ijet].pt()<25) continue;
	    if(fabs(selJets[ijet].eta())>2.5) continue;
	    njets++;
	    bool passCSVM(selJets[ijet].getVal("csv")>0.783);
	    bool passCSVL(selJets[ijet].getVal("csv")>0.405);
	    nbtags += passCSVM;
	    ht += selJets[ijet].pt();
	    ljev.j_pt[ljev.nj]  = selJets[ijet].pt();
	    ljev.j_eta[ljev.nj] = selJets[ijet].eta();
	    ljev.j_phi[ljev.nj] = selJets[ijet].phi();
	    ljev.j_m[ljev.nj]   = selJets[ijet].mass();
	    ljev.j_btag[ljev.nj]=passCSVL | (passCSVM<<1);
	    ljev.nj++;
	    if(isMC)
	      {
		const data::PhysicsObject_t &genJet=selJets[ijet].getObject("genJet");
		ljev.gj_pt[ljev.nj]=genJet.pt(); 
		ljev.gj_phi[ljev.nj]=genJet.phi(); 
		ljev.gj_eta[ljev.nj]=genJet.eta(); 
		ljev.gj_m[ljev.nj]=genJet.mass();
		ljev.ngj++;
	      }
	  }

        //
        // MC CORRECTIONS
        //
        Hhepup->Fill(ev.nup,1);
        if(isV0JetsMC && ev.nup>5) continue;

        //pileup weight
        float puWeight(1.0);//, puWeightUp(1.0), puWeightDown(1.0);
        if(isMC && fLumiWeights) {
	  puWeight     = fLumiWeights->weight(ev.ngenTruepu);
          //  puWeightUp   = puWeight*fPUshifters[utils::cmssw::PUUP]->Eval(ev.ngenTruepu);
	  //puWeightDown = puWeight*fPUshifters[utils::cmssw::PUDOWN]->Eval(ev.ngenTruepu);
        }

        //top pT weights and MC truth
        data::PhysicsObjectCollection_t gen=evSummary.getPhysicsObject(DataEventSummaryHandler::GENPARTICLES);
        int ngenLeptonsStatus3(0);
        float topPtWgt(1.0), topPtWgtUp(1.0), topPtWgtDown(1.0); //,topPtStdWgt(1.0);
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
		ljev.gl_pt=gen[igen].pt();
		ljev.gl_eta=gen[igen].eta();
		ljev.gl_phi=gen[igen].phi();
		ljev.gl_m=gen[igen].mass();
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
                    //float a(0.156),b(-0.00137);
		    // topPtStdWgt=sqrt(exp(a+b*pttop)*exp(a+b*ptantitop));
                }
            }
        }
        else genCat = 0;

        //ready to roll!
        //do s.th. here
        bool passLeptonSelection( box.lCat=="" );
        bool passJetSelection(false);
	passJetSelection = (box.jets.size()>=2);

        //leading lepton charge
        int lepid = box.leptons[0]->get("id");
        int lepcharge = -1.*lepid/abs(lepid);
        if( isMC && !url.Contains("QCDMuPt20") ) lepcharge *= -1.;
        if( url.Contains("SingleMu2012B"))       lepcharge *= -1.;

        float evWeight( genWeight*puWeight*lepSelectionWeight );

        //control plots for the event selection
        bool passPreSelection( (passLeptonSelection || box.lCat=="qcd" ) && passJetSelection );
        if(!passPreSelection) continue;
	if(box.leptons[0]->pt()<30 || fabs(box.leptons[0]->eta())>2.1) continue;
	int lid=abs(box.leptons[0]->get("id"));
	for(int k=0; k<2; k++)
	  {
	    TString plotTag(box.chCat+box.lCat);
	    if(k==1) plotTag += Form("%dj%db",min((int)4,njets),min((int)2,(int)nbtags));
	    controlHistos.fillHisto("nvertices",  plotTag, ev.nvtx,         evWeight);
	    controlHistos.fillHisto("pt",         plotTag, box.leptons[0]->pt(),         evWeight);
	    controlHistos.fillHisto("eta",        plotTag, fabs(box.leptons[0]->eta()),  evWeight);	
	    controlHistos.fillHisto("njets",      plotTag, njets, evWeight); //N-1 plot
	    controlHistos.fillHisto("nbjets",     plotTag, nbtags,          evWeight); //N-1 plot
	    controlHistos.fillHisto("met",        plotTag, box.met.pt(),    evWeight); //N-1 plot
	    controlHistos.fillHisto("mt",         plotTag, mt,              evWeight); //N-1 plot
	    controlHistos.fillHisto("ht",         plotTag, ht,              evWeight); //N-1 plot
	  }

        //save selected event
        if(!saveSummaryTree || !passPreSelection || outT==0) continue;

	ljev.ntracks=0;
	data::PhysicsObjectCollection_t pf = evSummary.getPhysicsObject(DataEventSummaryHandler::PFCANDIDATES);
	for(size_t ipf=0; ipf<pf.size(); ipf++)
	  {
	    if( pf[ipf].get("charge")==0 ) continue;
	    ljev.ntracks++;

	    bool nearbyJet(false);
	    for(size_t ij=0; ij<min((size_t)4,box.jets.size()); ij++)
	      {
		if( deltaR( *(box.jets[ij]), pf[ipf])>0.5 ) continue;
		nearbyJet=true;
		break;
	      }
	    if(nearbyJet || deltaR( *(box.leptons[0]),pf[ipf])<0.1 ) ljev.ntracks_hp++;
	  }

	ljev.run=ev.run;
	ljev.lumi=ev.lumi;
	ljev.event=ev.event;
	ljev.w=evWeight;
	ljev.l_id=lid;
	ljev.l_pt=box.leptons[0]->pt();
	ljev.l_eta=box.leptons[0]->eta();
	ljev.l_phi=box.leptons[0]->phi();
	ljev.l_m=box.leptons[0]->mass();	
	ljev.nb=nbtags;
	ljev.nj=box.jets.size();
	ljev.met_pt=box.met.pt();
	ljev.met_phi=box.met.phi();
	if(box.lCat=="qcd" )
	  {
	    ljev.l_id*=1000;
	    if(ljev.nj>2)	outT->Fill();
	  }
	else
	  {
	    outT->Fill();
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
    outT->Write();
    controlHistos.Write();
    TH1F *normH=new TH1F("norm","norm",2,0,2);
    normH->SetBinContent(1,isMC ? cnorm : 1.0);
    normH->SetBinContent(2,isMC ? xsec  : 1.0);
    normH->Write();
    spyFile->Close();

    //that's all folks!
}
