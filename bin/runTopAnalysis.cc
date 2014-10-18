#include <iostream>
#include <boost/shared_ptr.hpp>
#include <fstream>

#include "UserCode/TopMassSecVtx/interface/MacroUtils.h"
#include "UserCode/TopMassSecVtx/interface/SmartSelectionMonitor.h"
#include "UserCode/TopMassSecVtx/interface/DataEventSummaryHandler.h"
#include "UserCode/TopMassSecVtx/interface/LxyAnalysis.h"
#include "UserCode/TopMassSecVtx/interface/TopPtWeighter.h"
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
LeptonEfficiencySF fLepEff;
FactorizedJetCorrector *fJesCor=0;
std::vector<JetCorrectionUncertainty *> fTotalJESUnc;
MuScleFitCorrector *fMuCor=0;
std::map<std::pair<TString,TString>, std::pair<TGraphErrors *,TGraphErrors *> > fBtagEffCorr;
edm::LumiReWeighting *fLumiWeights=0;
utils::cmssw::PuShifter_t fPUshifters;

using namespace std;


//
// ANALYSIS BOXES
//

//aggregates all the objects needed for the analysis
//cat identifies the category: 11-electron 13-muon 11*11,11*13,13*13-dilepton events
class AnalysisBox{
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
  for(size_t i=0; i<jets.size(); i++) { box.jets.push_back( &(jets[i]) ); }
  box.met=met;

  std::vector<int> dilCands, ljCands, vetoCands;
  for(size_t i=0; i<leptons.size(); i++){
    if(leptons[i].getFlag("passLL"))     dilCands.push_back(i);
    if(leptons[i].getFlag("passLJ"))     ljCands.push_back(i);
    else {
      if(leptons[i].getFlag("passLJveto")) vetoCands.push_back(i);
    }
  }


  //
  // ASSIGN THE BOX
  // 1. >=2 tight leptons: OS, pt>20,20 GeV -> ll, Mll>20, |Mll-MZ|>15
  // 2. =1 tight lepton: pt(e)>30  or pt(mu)>26 GeV and =0 vetoLeptons
  //
  box.lCat="";
  if(dilCands.size()>=2 && hasDileptonTrigger)
    {
      for(size_t i=0; i<dilCands.size(); i++) { box.leptons.push_back( &(leptons[ dilCands[i] ]) ); }

      int dilId(box.leptons[0]->get("id")*box.leptons[1]->get("id"));
      LorentzVector dilepton( *(box.leptons[0]) );
      dilepton += *(box.leptons[1]);
      if(dilepton.mass()>20 && dilId<0)
	{
	  if(abs(dilId)==11*11 || abs(dilId)==13*13 || abs(dilId)==11*13 )              box.cat=dilId;
	  if( (abs(dilId)==11*11 || abs(dilId)==13*13) && fabs(dilepton.mass()-91)<15)  box.lCat="z";
	}
    }
  else if(ljCands.size()==1 && vetoCands.size()==0 && hasLJetsTrigger)
    {
      box.leptons.push_back( &(leptons[ ljCands[0] ]) );
      box.cat=box.leptons[0]->get("id");
    }

  int njetsBin( box.jets.size()>6 ? 6  : box.jets.size() );
  box.jetCat="jet"; box.jetCat += njetsBin;
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
// PARTICLE SELECTORS
//

//sets the selection flags on the electron
data::PhysicsObject_t getTopSelectionTaggedElectron(data::PhysicsObject_t ele,float rho)
{
  // Kinematic cuts
  float sceta = ele.getVal("sceta");
  bool isInEB2EE    ( fabs(sceta) > 1.4442 && fabs(sceta) < 1.5660 );
  bool passLLkin    ( ele.pt()>20 && fabs(ele.eta()) < 2.5 && !isInEB2EE);
  bool passLJkin    ( ele.pt()>30 && fabs(ele.eta()) < 2.5 && !isInEB2EE);
  bool passLJvetokin( ele.pt()>20 && fabs(ele.eta()) < 2.5 && !isInEB2EE);

  //id
  bool passIdBaseQualityCuts(true);
  if( ele.getFlag("isconv") )              passIdBaseQualityCuts=false;
  if( fabs(ele.getVal("tk_d0"))>0.04 )     passIdBaseQualityCuts=false;
  if( ele.getVal("tk_lostInnerHits") > 0 ) passIdBaseQualityCuts=false;
  bool passLLid( ele.getVal("mvatrig")>0.5 && passIdBaseQualityCuts);
  bool passLJid( ele.getVal("mvatrig")>0.5 && passIdBaseQualityCuts);
  bool passLJvetoid( ele.getVal("mvatrig")>0.5 );

  // Isolation
  Float_t gIso = ele.getVal("gIso03");
  Float_t chIso = ele.getVal("chIso03");
  Float_t nhIso = ele.getVal("nhIso03");
  float relIso = (TMath::Max(nhIso+gIso-rho*utils::cmssw::getEffectiveArea(11,sceta,3),Float_t(0.))+chIso)/ele.pt();
  bool passLLiso( relIso<0.15 );
  bool passLJiso( relIso<0.15 );
  bool passLJvetoiso( relIso<0.15 );

  //set the flags
  ele.setFlag("passLL",    (passLLkin && passLLid && passLLiso));
  ele.setFlag("passLJ",    (passLJkin && passLJid && passLJiso));
  ele.setFlag("passLJveto",(passLJvetokin && passLJvetoid && passLJvetoiso));
  ele.setVal("reliso",relIso);
  return ele;
}

//sets the selection flags on the muon
data::PhysicsObject_t getTopSelectionTaggedMuon(data::PhysicsObject_t mu, float isMC)
{
  // Muon energy scale and uncertainties
  Int_t id = mu.get("id");
  if( fMuCor ){
    TLorentzVector p4(mu.px(),mu.py(),mu.pz(),mu.energy());
    fMuCor->applyPtCorrection(p4 , id<0 ? -1 : 1 );
    if( isMC ) fMuCor->applyPtSmearing(p4, id<0 ? -1 : 1, false);
    mu.SetPxPyPzE(p4.Px(),p4.Py(),p4.Pz(),p4.E());
  }
  
  // Kinematic cuts
  bool passLLkin( mu.pt()>20     && fabs(mu.eta())<2.4 );
  bool passLJkin( mu.pt()>26     && fabs(mu.eta())<2.1 );
  bool passLJvetokin( mu.pt()>20 && fabs(mu.eta())<2.4 );
  
  // ID
  Int_t idbits = mu.get("idbits");
  bool isPF((idbits >> 7) & 0x1);
  bool passLLid( ((idbits >> 10) & 0x1) && isPF );
  bool passLJid( ((idbits >> 10) & 0x1) && isPF );
  bool passLJvetoid( ((idbits >> 10) & 0x1) && isPF );
  
  // Isolation
  Float_t gIso = mu.getVal("gIso04");
  Float_t chIso = mu.getVal("chIso04");
  Float_t puchIso = mu.getVal("puchIso04");
  Float_t nhIso = mu.getVal("nhIso04");
  Float_t relIso = ( TMath::Max(nhIso+gIso-0.5*puchIso,0.)+chIso ) / mu.pt();
  bool passLLiso( relIso<0.12 );
  bool passLJiso( relIso<0.12 );
  bool passLJvetoiso( relIso<0.12 );
  
  //set the flags
  mu.setVal("reliso",relIso);
  mu.setFlag("passLL",    (passLLkin     && passLLid     && passLLiso));
  mu.setFlag("passLJ",    (passLJkin     && passLJid     && passLJiso));
  mu.setFlag("passLJveto",(passLJvetokin && passLJvetoid && passLJvetoiso));
  
  return mu;
}

//
data::PhysicsObjectCollection_t selectLeptons(data::PhysicsObjectCollection_t &leptons,float rho, bool isMC)
{
  data::PhysicsObjectCollection_t selLeptons;
  for(size_t ilep=0; ilep<leptons.size(); ilep++){
    Int_t id=leptons[ilep].get("id");
    data::PhysicsObject_t selLepton(abs(id)==11 ?
				    getTopSelectionTaggedElectron(leptons[ilep], rho) :
				    getTopSelectionTaggedMuon    (leptons[ilep], isMC) );
    if( !selLepton.getFlag("passLL") && !selLepton.getFlag("passLJ") && !selLepton.getFlag("passLJveto") ) continue;
    selLeptons.push_back(selLepton);
  }
  
  sort(selLeptons.begin(), selLeptons.end(), data::PhysicsObject_t::sortByPt);
  
  return selLeptons;
}

//
data::PhysicsObject_t getTopSelectionTaggedJet(data::PhysicsObject_t jet, data::PhysicsObjectCollection_t &leptons,float minpt, float maxeta)
{
  // kin cuts
  bool passKin(true);
  if( jet.pt() < minpt )         passKin=false;
  if( fabs(jet.eta()) > maxeta ) passKin=false;

  //cross-clean with selected leptons
  double minDRlj(9999.);
  for( size_t ilep=0; ilep<leptons.size(); ilep++ )
    {
      if( !(leptons[ilep].getFlag("passLJ")) && !(leptons[ilep].getFlag("passLL")) ) continue;
      minDRlj = TMath::Min( minDRlj, deltaR(jet, leptons[ilep]) );
    }
	
  // Require to pass the loose id
  Int_t idbits = jet.get("idbits");
  bool passPFloose( ((idbits>>0) & 0x1) );

  jet.setFlag("passGoodJet", (passKin && minDRlj>0.4 && passPFloose) );


  return jet;
}

//select jets
data::PhysicsObjectCollection_t selectJets(data::PhysicsObjectCollection_t &jets, data::PhysicsObjectCollection_t &leptons)
{
  data::PhysicsObjectCollection_t selJets;
  for(size_t ijet=0; ijet<jets.size(); ijet++)
    {
      data::PhysicsObject_t selJet = getTopSelectionTaggedJet(jets[ijet], leptons, 30., 2.5);
      
      if(!selJet.getFlag("passGoodJet")) continue;
      
      //here is a trick just to get the leading lxy jet first
      const data::PhysicsObject_t &svx=selJet.getObject("svx");
      selJet.setVal("lxy",svx.vals.find("lxy")->second);
      selJets.push_back(selJet);
    }
  
  sort(selJets.begin(), selJets.end(), data::PhysicsObject_t::sortByPt);
  
  return selJets;
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
  TString srcnames[]={
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

  //b-tag efficiencies read b-tag efficiency map
  if(weightsFile.size() && isMC)
    {
      TString btagEffCorrUrl(weightsFile[0].c_str()); btagEffCorrUrl += "/btagEff.root";
      gSystem->ExpandPathName(btagEffCorrUrl);
      TFile *btagF=TFile::Open(btagEffCorrUrl);
      if(btagF!=0 && !btagF->IsZombie())
	{
	  TList *dirs=btagF->GetListOfKeys();
	  for(int itagger=0; itagger<dirs->GetEntries(); itagger++)
	    {
	      TString iDir(dirs->At(itagger)->GetName());
	      fBtagEffCorr[ std::pair<TString,TString>(iDir,"b") ]
		= std::pair<TGraphErrors *,TGraphErrors *>( (TGraphErrors *) btagF->Get(iDir+"/beff"),(TGraphErrors *) btagF->Get(iDir+"/sfb") );
	      fBtagEffCorr[ std::pair<TString,TString>(iDir,"c") ]
		= std::pair<TGraphErrors *,TGraphErrors *>( (TGraphErrors *) btagF->Get(iDir+"/ceff"),(TGraphErrors *) btagF->Get(iDir+"/sfc") );
	      fBtagEffCorr[ std::pair<TString,TString>(iDir,"udsg") ]
		= std::pair<TGraphErrors *,TGraphErrors *>( (TGraphErrors *) btagF->Get(iDir+"/udsgeff"),(TGraphErrors *) btagF->Get(iDir+"/sfudsg") );
	    }
	}
      cout << fBtagEffCorr.size() << " b-tag correction factors have been read" << endl;
    }

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
      std::vector<float> dataPileupDistribution; for(unsigned int i=0;i<dataPileupDistributionDouble.size();i++){dataPileupDistribution.push_back(dataPileupDistributionDouble[i]);}
      std::vector<float> mcPileupDistribution;
      if(isMC){
	TString puDist(baseDir+"/pileup");
	TH1F* histo = (TH1F *) inF->Get(puDist);
	if(!histo)std::cout<<"pileup histogram is null!!!\n";
	for(int i=1;i<=histo->GetNbinsX();i++){mcPileupDistribution.push_back(histo->GetBinContent(i));}
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
  TString labels[]={"Lepton(s)", "=1 jets","=2 jets","=3 jets","#geq4 jets","Jet selection", "E_{T}^{miss}", "#geq1 SecVtx"};
  int nsteps=sizeof(labels)/sizeof(TString);
  TH1F *baseEvtFlowH = (TH1F *)controlHistos.addHistogram( new TH1F("evtflow",";Selection step;Events",nsteps,0,nsteps) );
  for(int i=0; i<nsteps; i++) baseEvtFlowH->GetXaxis()->SetBinLabel(i+1,labels[i]);
  controlHistos.addHistogram( new TH1F("thetall", ";#theta(l,l') [rad];Events",50,0,3.2) );
  TH1F *baseJetMult=(TH1F *)controlHistos.addHistogram( new TH1F("njets",   ";Jet multiplicity; Events",6,0,6) );
  TH1F *baseSecVtxMult=(TH1F *)controlHistos.addHistogram( new TH1F("nsvtx",   ";SecVtx multiplicity; Events",4,0,4) );
  for(int i=0; i<6; i++) 
    {
      TString label("= "); label += i; label += " jet"; if(i!=1) label += "s";
      baseJetMult->GetXaxis()->SetBinLabel(i+1,label);
      if(i>=4) continue;
      label.ReplaceAll("jet","SecVtx");
      baseSecVtxMult->GetXaxis()->SetBinLabel(i+1,label);
    }
  controlHistos.addHistogram( new TH1F("met",          ";Missing transverse energy [GeV]; Events",50,0,250) );
  controlHistos.addHistogram( new TH1F("metoverht",    ";E_{T}^{miss}/#sqrt{H_{T}} [GeV^{1/2}]",50,0,15));
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
  if( !evSummary.attach( (TTree *) inF->Get(baseDir+"/data") ) )  { inF->Close();  return -1; }

  Int_t entries_to_process = -1;
  if(maxEvents > 0) entries_to_process = maxEvents;
  else              entries_to_process = evSummary.getEntries();
  const Int_t totalEntries = entries_to_process;

  float cnorm=1.0;
  if(isMC){
    TH1F* cutflowH = (TH1F *) inF->Get(baseDir+"/cutflow");
    if(cutflowH) cnorm=cutflowH->GetBinContent(1);
  }

  cout << "Processing: " << proctag << " @ " << url << endl
       << "Initial number of events: " << cnorm << endl
       << "Events in tree:           " << totalEntries << endl
       << " xSec x BR:               " << xsec << endl;

  if(isTTbarMC){
    if(weightsFile.size()){
      TString shapesDir("");
      shapesDir=weightsFile[0].c_str();
      fTopPtWgt = new TopPtWeighter( proctag, out, shapesDir, evSummary.getTree() );
    }
  }

  //control the sec vtx analysis
  LxyAnalysis lxyAn;

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
    }


  //
  // analyze (puf...)
  //
  for (int inum=0; inum < totalEntries; ++inum)
    {
      if(inum%500==0) { printf("\r [ %d/100 ]",int(100*float(inum)/float(totalEntries))); cout << flush; }
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
      if(!isMC){
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
      data::PhysicsObjectCollection_t selLeptons=selectLeptons(leptons, ev.rho, isMC);
      if(!isMC)
	{
	  //dismiss data event if lepton multiplicity is not ok
	  if((eTrigger || muTrigger) && selLeptons.size()==0) continue;
	  if((mumuTrigger || emuTrigger || eeTrigger) && selLeptons.size()<2) continue;
	}


      //jet/met
      data::PhysicsObjectCollection_t jets(evSummary.getPhysicsObject(DataEventSummaryHandler::JETS));
      utils::cmssw::updateJEC(jets, fJesCor, fTotalJESUnc, ev.rho, ev.nvtx, isMC);      
      data::PhysicsObjectCollection_t selJets = selectJets(jets,selLeptons);
      data::PhysicsObjectCollection_t recoMet = evSummary.getPhysicsObject(DataEventSummaryHandler::MET);
      //0,1 - raw pfmet, 2 - type1 pfmet, 3 - type1p2 corrected met
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
		if(abs(selLeptons[0].get("id"))==13) { eta2=selLeptons[0].eta(); eta1=selLeptons[1].eta(); }
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
	puWeight     = fLumiWeights->weight(ev.ngenITpu);
	puWeightUp   = puWeight*fPUshifters[utils::cmssw::PUUP]->Eval(ev.ngenITpu);
	puWeightDown = puWeight*fPUshifters[utils::cmssw::PUDOWN]->Eval(ev.ngenITpu);
      }

      //top pT weights and MC truth
      data::PhysicsObjectCollection_t gen=evSummary.getPhysicsObject(DataEventSummaryHandler::GENPARTICLES);
      int ngenLeptonsStatus3(0);
      float topPtWgt(1.0), topPtWgtUp(1.0), topPtWgtDown(1.0);
      float genWeight(1.0);
      int genCat(1);
      if(isMC){
	float pttop(0), ptantitop(0);
	for(size_t igen=0; igen<gen.size(); igen++){
	  if(gen[igen].get("status")!=3) continue;
	  int absid=abs(gen[igen].get("id"));
	  if(absid==6) {
	    if(gen[igen].get("id")==6) pttop=gen[igen].pt();
	    else                       ptantitop=gen[igen].pt();
	  }
	  if(absid!=11 && absid!=13 && absid!=15) continue;
	  ngenLeptonsStatus3++;
	  genCat *= gen[igen].get("id");
	}
	
	//top-pt re-weighting only for TTbar!
	if(isTTbarMC)
	  {
	    //branching ratio correction for inclusive Madgraph samples: same approximation since 2010...
	    if(ngenLeptonsStatus3==2)      { genWeight=pow(0.1086/(1./9.),2);             }
	    else if(ngenLeptonsStatus3==1) { genWeight=(0.1086/(1./9.))*(0.6741/(2./3.)); }
	    else                           { genWeight=pow(0.6741/(2./3.),2);             }
	    
	    if(pttop>0 && ptantitop>0 && fTopPtWgt)
	      {
		fTopPtWgt->computeWeight(pttop,ptantitop);
		fTopPtWgt->getEventWeight(topPtWgt, topPtWgtUp, topPtWgtDown );
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

      //leadig lepton charge
      int lepid = box.leptons[0]->get("id");
      int lepcharge = -1.*lepid/abs(lepid);
      if( isMC && !url.Contains("QCDMuPt20") ) lepcharge *= -1.;
      if( url.Contains("SingleMu2012B"))       lepcharge *= -1.;
      
      float evWeight( genWeight*puWeight*lepSelectionWeight );

      //control plots for the event selection
      bool passPreSelection((passLeptonSelection||box.lCat=="z") && passJetSelection && passMetSelection);
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
		  controlHistos.fillHisto("met",  box.chCat + (( lepcharge>0 ) ? "plus" : "minus"),  box.met.pt() ,  evWeight);
		  controlHistos.fillHisto("evtflow", box.chCat, 5,            evWeight);
		  if(passMetSelection)
		    {
		      controlHistos.fillHisto("evtflow", box.chCat, 6,         evWeight);
		      controlHistos.fillHisto("metoverht",  box.chCat, box.metsig,  evWeight);
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
		  controlHistos.fillHisto("met",        box.chCat+box.jetCat, box.met.pt(), evWeight);
		  controlHistos.fillHisto("met",        box.chCat+box.jetCat+(( lepcharge>0 ) ? "plus" : "minus"), box.met.pt(),  evWeight); 
		  controlHistos.fillHisto("metoverht",  box.chCat+box.jetCat, box.metsig,  evWeight); 
		}
	    }
	}
		
      //save selected event
      if(!saveSummaryTree || !passPreSelection) continue;
      lxyAn.resetBeautyEvent();
      BeautyEvent_t &bev=lxyAn.getBeautyEvent();
      int evCatSummary(box.cat);
      if( box.lCat=="z" ) evCatSummary*=1000;
      bev.evcat=evCatSummary;
      bev.gevcat=genCat;
      bev.run=ev.run;
      bev.event=ev.event;
      bev.lumi=ev.lumi;
      bev.nvtx=ev.nvtx;
      bev.rho=ev.rho;
      bev.nw=10;
      bev.w[0]=genWeight;
      bev.w[1]=puWeight;           bev.w[2]=puWeightUp;           bev.w[3]=puWeightDown;
      bev.w[4]=lepSelectionWeight; bev.w[5]=lepSelectionWeightUp; bev.w[6]=lepSelectionWeightDown;
      bev.w[7]=topPtWgt;           bev.w[8]=topPtWgtUp;           bev.w[9]=topPtWgtDown;
      bev.qscale=ev.qscale;        bev.x1=ev.x1; bev.x2=ev.x2; bev.id1=ev.id1; bev.id2=ev.id2;
      data::PhysicsObjectCollection_t pf = evSummary.getPhysicsObject(DataEventSummaryHandler::PFCANDIDATES);
      lxyAn.analyze( box.leptons, box.jets, met, pf, gen);
      lxyAn.save();
    }
  std::cout << std::endl;
  
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
