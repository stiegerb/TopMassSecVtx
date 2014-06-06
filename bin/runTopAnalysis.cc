#include <iostream>
#include <boost/shared_ptr.hpp>
#include <fstream>

#include "UserCode/llvv_fwk/interface/MacroUtils.h"
#include "UserCode/llvv_fwk/interface/SmartSelectionMonitor.h"
#include "UserCode/llvv_fwk/interface/DataEventSummaryHandler.h"
#include "UserCode/llvv_fwk/interface/LxyAnalysis.h"
#include "UserCode/llvv_fwk/interface/UEAnalysis.h"
#include "UserCode/llvv_fwk/interface/BTVAnalysis.h"
#include "UserCode/llvv_fwk/interface/RAnalysis.h"
#include "UserCode/llvv_fwk/interface/TopPtWeighter.h"
#include "UserCode/llvv_fwk/interface/LeptonEfficiencySF.h"
#include "UserCode/llvv_fwk/interface/MuScleFitCorrector.h"

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

#include "TSystem.h"
#include "TFile.h"
#include "TChain.h"
#include "TChainElement.h"
#include "TCanvas.h"
#include "TString.h"
#include "TDirectory.h"
#include "TEventList.h"
#include "TRandom.h"

#include <iostream>

//correctors
TopPtWeighter *fTopPtWgt=0;
LeptonEfficiencySF fLepEff;
FactorizedJetCorrector *fJesCor=0;
JetCorrectionUncertainty *fTotalJESUnc=0;
MuScleFitCorrector *fMuCor=0;
std::map<std::pair<TString,TString>, std::pair<TGraphErrors *,TGraphErrors *> > fBtagEffCorr;
edm::LumiReWeighting *fLumiWeights=0;
utils::cmssw::PuShifter_t fPUshifters;
DuplicatesChecker duplicatesChecker;

using namespace std;




//
// ANALYSIS BOXES
//

//aggregates all the objects needed for the analysis
//cat identifies the category: 11-electron 13-muon 11*11,11*13,13*13-dilepton events
class AnalysisBox{
public:
  AnalysisBox() : cat(0), chCat(""), lCat(""), jetCat(""), metCat("") { }
  ~AnalysisBox() { }
  Int_t cat;
  TString chCat, lCat, jetCat, metCat;
  data::PhysicsObjectCollection_t leptons, jets;
  LorentzVector met;
};

//
AnalysisBox assignBox(data::PhysicsObjectCollection_t &leptons, data::PhysicsObjectCollection_t &jets, LorentzVector &met)
{
  
  AnalysisBox box;
  box.cat=0;
  box.jets=jets;
  box.met=met;
  int nLooseLeptons(0);
  for(size_t i=0; i<leptons.size(); i++){
    if(leptons[i].pt()<20) continue;
    if(leptons[i].getFlag("passTight"))      box.leptons.push_back( leptons[i] );
    else if(leptons[i].getFlag("passLoose")) nLooseLeptons++;
  }
  
  //
  // ASSIGN THE BOX
  // 1. >=2 tight leptons: OS, pt>20,20 GeV -> ll
  // 2. =1 tight lepton: pt(e)>30  or pt(mu)>26 GeV and =0 vetoLeptons
  //
  if(box.leptons.size()>=2){
    int dilId(box.leptons[0].get("id")*box.leptons[1].get("id"));
    if(dilId<0 && ( abs(dilId)==11*11 || abs(dilId)==13*13 || abs(dilId)==11*13 ) ) box.cat=dilId;
  }
  else if(box.leptons.size()==1 && nLooseLeptons==0){
    int lId=box.leptons[0].get("id");
    if( abs(lId)==11      && box.leptons[0].pt()>30) box.cat=lId;
    else if( abs(lId)==13 && box.leptons[0].pt()>26) box.cat=lId;
  }

  box.lCat="";
  if( abs(box.cat)==11*11 || abs(box.cat)==13*13 || abs(box.cat)==11*13 ) 
    {
      LorentzVector dilepton=box.leptons[0]+box.leptons[1];
      if( ( abs(box.cat)==11*11 || abs(box.cat)==13*13 ) && fabs(dilepton.mass()-91)<15 ) box.lCat="z";
      if( dilepton.mass()<12 ) box.cat=0; //this is a special cut to remove low mass states
    }

  int njetsBin( box.jets.size()>5 ? 5 : 0 );
  box.jetCat="jet"; box.jetCat += njetsBin;

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
void setGoodElectron(data::PhysicsObject_t &ele, float minpt, float maxeta,float rho)
{
  // Kinematic cuts
  bool passKin(true);
  if( ele.pt() < minpt ) passKin=false;
  if( fabs(ele.eta()) > maxeta ) passKin=false;
  float sceta = ele.getVal("sceta");
  if( fabs(sceta) > 1.4442 && fabs(sceta) < 1.5660 ) passKin=false;
  
  // Isolation
  Float_t gIso = ele.getVal("gIso03");
  Float_t chIso = ele.getVal("chIso03");
  Float_t nhIso = ele.getVal("nhIso03");
  float relIso = (TMath::Max(nhIso+gIso-rho*utils::cmssw::getEffectiveArea(11,sceta),Float_t(0.))+chIso)/ele.pt();
  
  // ID
  bool passId = true;
  if( ele.getFlag("isconv") ) passId = false;
  if( ele.getVal("tk_d0")>0.2 ) passId = false; // FIXME: is this the correct value?
  if( ele.getVal("tk_lostInnerHits") > 0 ) passId = false;
  if( ele.getVal("mvatrig")<0.5 ) passId = false;

  //set the flags
  ele.setFlag("passTight",(passKin && relIso<0.10 && passId));
  ele.setFlag("passLoose",(passKin && relIso<0.15 && passId));
}

//sets the selection flags on the muon
void setGoodMuon(data::PhysicsObject_t &mu, float minpt, float maxeta, float isMC)
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
  bool passKin(true);
  if( mu.pt() < minpt )         passKin=false;
  if( fabs(mu.eta()) > maxeta ) passKin=false;

  // Isolation
  Float_t gIso = mu.getVal("gIso04");
  Float_t chIso = mu.getVal("chIso04");
  Float_t puchIso = mu.getVal("puchIso04");
  Float_t nhIso = mu.getVal("nhIso04");
  Float_t relIso = ( TMath::Max(nhIso+gIso-0.5*puchIso,0.)+chIso ) / mu.pt();

  // ID
  Int_t idbits = mu.get("idbits");
  bool passTightId = ((idbits >> 10) & 0x1);
  bool passLooseId = ((idbits >> 8) & 0x1);

   //set the flags
  mu.setFlag("passTight",(passKin && relIso<0.12 && passTightId));
  mu.setFlag("passLoose",(passKin && relIso<0.15 && passLooseId));
}

//
void setGoodJet(data::PhysicsObject_t &jet, data::PhysicsObjectCollection_t &leptons,float minpt, float maxeta)
{
  // kin cuts
  bool passKin(true);
  if( jet.pt() < minpt ) passKin=false;
  if( fabs(jet.eta()) > maxeta ) passKin=false;

  // Cross-clean with selected leptons
  double minDRlj(9999.);
  for( size_t ilep=0; ilep<leptons.size(); ilep++ )
    {
      if( leptons[ilep].getFlag("passLoose") ) continue;
      minDRlj = TMath::Min( minDRlj, deltaR(jet, leptons[ilep]) );
    }

  // Require to pass the loose id
  Int_t idbits = jet.get("idbits");
  bool passPFloose( ((idbits>>0) & 0x1));
    
  jet.setFlag("passTight", (passKin && minDRlj>0.4 && passPFloose) );
}

//select jets
void selectJets(data::PhysicsObjectCollection_t jets, data::PhysicsObjectCollection_t leptons, data::PhysicsObjectCollection_t &selJets)
{
  for(size_t ijet=0; ijet<jets.size(); ijet++){
    setGoodJet(jets[ijet], leptons, 30., 2.5);
    if(!jets[ijet].getFlag("passTight")) continue;
    selJets.push_back(jets[ijet]);
  }
  sort(selJets.begin(), selJets.end(), data::PhysicsObject_t::sortByPt);
}

//
void selectLeptons(data::PhysicsObjectCollection_t leptons, data::PhysicsObjectCollection_t &selLeptons,float rho, bool isMC)
{
  for(size_t ilep=0; ilep<leptons.size(); ilep++){
    Int_t id=leptons[ilep].get("id");
    if(abs(id)==11) setGoodElectron(leptons[ilep], 15., 2.5, rho);
    else if(abs(id)==13) setGoodMuon(leptons[ilep], 15., 2.5, isMC);

    if(!leptons[ilep].getFlag("passLoose") && !leptons[ilep].getFlag("passTight")) continue;
    selLeptons.push_back(leptons[ilep]);
  }
  sort(selLeptons.begin(), selLeptons.end(), data::PhysicsObject_t::sortByPt);
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
  int mcTruthMode     = runProcess.getParameter<int>("mctruthmode");
  double xsec         = runProcess.getParameter<double>("xsec");
  bool isV0JetsMC(isMC && (url.Contains("DYJetsToLL_50toInf") || url.Contains("WJets")));
  bool isTTbarMC(isMC && (url.Contains("TTJets") || url.Contains("_TT_") || url.Contains("TT2l_R")));
  TString out          = runProcess.getParameter<std::string>("outdir");
  bool saveSummaryTree = runProcess.getParameter<bool>("saveSummaryTree");
  std::vector<string>  weightsFile = runProcess.getParameter<std::vector<string> >("weightsFile");
   
  //jet energy scale uncertainties
  gSystem->ExpandPathName(jecDir);
  fJesCor        = utils::cmssw::getJetCorrector(jecDir,isMC);
  fTotalJESUnc = new JetCorrectionUncertainty((jecDir+"/MC_Uncertainty_AK5PFchs.txt").Data());

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
  bool isDoubleMuPD(!isMC && url.Contains("DoubleMu"));
  bool isMuEGPD(!isMC && url.Contains("MuEG"));
  bool isSingleElePD(!isMC && url.Contains("SingleEle"));  
  bool isSingleMuPD(!isMC && url.Contains("SingleMu"));  
  
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
  SmartSelectionMonitor controlHistos;
  TH1F* Hhepup        = (TH1F* )controlHistos.addHistogram(new TH1F ("heupnup"    , "hepupnup"    ,20,0,20) ) ;
  TH1F* Hcutflow      = (TH1F*) controlHistos.addHistogram(new TH1F ("cutflow"    , "cutflow"    ,5,0,5) ) ;
  controlHistos.addHistogram( new TH1F ("nvertices", "; Vertex multiplicity; Events", 50, 0.,50.) );
  TString labels[]={"Lepton(s)", "Jets", "E_{T}^{miss}", "b-jet"};
  int nsteps=sizeof(labels)/sizeof(TString);
  TH1F *h              = (TH1F *)controlHistos.addHistogram( new TH1F("evtflow",";Selection step;Events",nsteps,0,nsteps) );
  for(int i=0; i<nsteps; i++) h->GetXaxis()->SetBinLabel(i+1,labels[i]);
  controlHistos.addHistogram( new TH1F("thetall",";#theta(l,l') [rad];Events",50,0,3.2) );
  controlHistos.addHistogram( new TH1F("njets",  ";Jet multiplicity [GeV]; Events",6,0,6) );
  controlHistos.addHistogram( new TH1F("met",    ";PF E_{T}^{miss} [GeV]; Events",50,0,250) );
  controlHistos.addHistogram( new TH1F("mt",     ";Transverse mass [GeV];Events",50,0,500) );
  controlHistos.addHistogram( new TH1F("charge",";Charge; Events",2,0,2) );
  
  ///
  // process events file
  //
  DataEventSummaryHandler evSummary;
  if( !evSummary.attach( (TTree *) inF->Get(baseDir+"/data") ) )  { inF->Close();  return -1; }  
  const Int_t totalEntries=evSummary.getEntries();
  
  float cnorm=1.0;
  if(isMC){
    TH1F* cutflowH = (TH1F *) inF->Get(baseDir+"/cutflow");
    if(cutflowH) cnorm=cutflowH->GetBinContent(1);
  }
  Hcutflow->SetBinContent(1,cnorm);

  cout << "Processing: " << proctag << " @ " << url << endl
       << "Initial number of events: " << cnorm << endl
       << "Events in tree:           " << totalEntries << endl
       << " xSec x BR:               " << xsec << endl;

  if(isTTbarMC ){
    TString shapesDir("");
    if(weightsFile.size()) shapesDir=weightsFile[0].c_str();
    fTopPtWgt = new TopPtWeighter( proctag, out, shapesDir, evSummary.getTree() );
  }

  Float_t xsecWeight(isMC ? xsec/cnorm : 1.0);

  LxyAnalysis lxyAn;

  //prepare the output file
  TString outUrl(out);
  gSystem->ExpandPathName(outUrl);
  gSystem->Exec("mkdir -p " + outUrl);
  outUrl += "/";
  outUrl += proctag;
  if(mcTruthMode!=0) { outUrl += "_filt"; outUrl += mcTruthMode; }
  outUrl += ".root";
  TFile *spyFile=TFile::Open(outUrl, "recreate");
  TDirectory *spyDir=0;
  if(saveSummaryTree)
    {
      gSystem->Exec("mkdir -p " + out);
      gDirectory->SaveSelf();
      spyFile->rmdir(proctag);
      spyDir = spyFile->mkdir("dataAnalyzer");      
      lxyAn.attachToDir(spyDir);
    }


  //
  // analyze (puf...)
  //
  int nDuplicates(0);
  for (int inum=0; inum < totalEntries; ++inum)
    {
      if(inum%500==0) { printf("\r [ %d/100 ]",int(100*float(inum)/float(totalEntries))); cout << flush; }
      evSummary.getEntry(inum);
      DataEventSummary &ev = evSummary.getEvent();
      if(!isMC && duplicatesChecker.isDuplicate( ev.run, ev.lumi, ev.event) ) { nDuplicates++; continue; }

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
	eeTrigger   &= isDoubleElePD;
	emuTrigger  &= isMuEGPD;
	mumuTrigger &= isDoubleMuPD;
	muTrigger   &= isSingleMuPD;
	eTrigger    &= isSingleElePD;
      }

      //leptons
      data::PhysicsObjectCollection_t leptons( evSummary.getPhysicsObject(DataEventSummaryHandler::LEPTONS) ), selLeptons;
      selectLeptons(leptons, selLeptons, ev.rho, isMC);

      //jet/met
      data::PhysicsObjectCollection_t jets(evSummary.getPhysicsObject(DataEventSummaryHandler::JETS)), selJets;
      utils::cmssw::updateJEC(jets,fJesCor,fTotalJESUnc,ev.rho,ev.nvtx,isMC);
      selectJets(jets,selLeptons,selJets);
      data::PhysicsObjectCollection_t recoMet=evSummary.getPhysicsObject(DataEventSummaryHandler::MET);     
      std::vector<LorentzVector> met=utils::cmssw::getMETvariations(recoMet[0],selJets,selLeptons,isMC);

      //get the category
      AnalysisBox box=assignBox(selLeptons, selJets, met[0]); 
      if(box.cat==0) continue;
      if(abs(box.cat)==11    && !eTrigger)    continue; 
      if(abs(box.cat)==13    && !muTrigger)   continue; 
      if(abs(box.cat)==11*11 && !eeTrigger)   continue; 
      if(abs(box.cat)==11*13 && !emuTrigger)  continue; 
      if(abs(box.cat)==11*13 && !mumuTrigger) continue; 


      //
      // MC CORRECTIONS
      //
      if(isV0JetsMC && ev.nup>5) continue;
      Hhepup->Fill(ev.nup,1);

      //pileup weight
      float puWeight(1.0), puWeightUp(1.0), puWeightDown(1.0);
      if(isMC && fLumiWeights) {
	puWeight     = fLumiWeights->weight(ev.ngenITpu);
	puWeightUp   = puWeight*fPUshifters[utils::cmssw::PUUP]->Eval(ev.ngenITpu);
	puWeightDown = puWeight*fPUshifters[utils::cmssw::PUDOWN]->Eval(ev.ngenITpu);

	Hcutflow->Fill(1,1);
	Hcutflow->Fill(2,puWeight);
	Hcutflow->Fill(3,puWeightUp);
	Hcutflow->Fill(4,puWeightDown);
      }

     //data/MC lepton selection weights
      float lepSelectionWeight(1.0),lepSelectionWeightUp(1.0),lepSelectionWeightDown(1.0);
      if(isMC)
	{
	  for(size_t ilep=0; ilep<box.leptons.size(); ilep++)
	    {
	      int id(abs(box.leptons[ilep].get("id")));
	      lepSelectionWeight *= fLepEff.getLeptonEfficiency( box.leptons[ilep].pt(), box.leptons[ilep].eta(), id,  "tight").first;
	    }
	  lepSelectionWeightUp = lepSelectionWeight*1.01;
	  lepSelectionWeightUp = lepSelectionWeight*0.99;
	}
      
      //top pT weights
      data::PhysicsObjectCollection_t gen=evSummary.getPhysicsObject(DataEventSummaryHandler::GENPARTICLES);
      bool hasTop(false);
      int ngenLeptonsStatus3(0);
      float topPtWgt(1.0), topPtWgtUp(1.0), topPtWgtDown(1.0);
      if(isMC)
	{
	  float pttop(0), ptantitop(0);
	  for(size_t igen=0; igen<gen.size(); igen++){
	    if(gen[igen].get("status")!=3) continue;
	    int absid=abs(gen[igen].get("id"));
	    if(absid==6) {
	      hasTop=true;
	      if(gen[igen].get("id")==6) pttop=gen[igen].pt();
	      else                       ptantitop=gen[igen].pt();
	    }
	    if(absid!=11 && absid!=13 && absid!=15) continue;
	    ngenLeptonsStatus3++;
	  }
	  if(mcTruthMode==1)
	    {
	      if( ! ( (abs(box.cat)==11 || abs(box.cat)==13) && (ngenLeptonsStatus3==1 && hasTop) ) ) continue;
	      if( ! ( (abs(box.cat)==11*11 || abs(box.cat)==11*13 || abs(box.cat)==13*13) && (ngenLeptonsStatus3==2 && hasTop) ) ) continue;
	    }
	  if(mcTruthMode==2)
	    {
	      if(  ( (abs(box.cat)==11 || abs(box.cat)==13) && (ngenLeptonsStatus3==1 && hasTop) ) ) continue;
	      if(  ( (abs(box.cat)==11*11 || abs(box.cat)==11*13 || abs(box.cat)==13*13) && (ngenLeptonsStatus3==2 && hasTop) ) ) continue;
	    }
	  if(pttop>0 && ptantitop>0 && topPtWgt)
	    {
	      fTopPtWgt->computeWeight(pttop,ptantitop);
	      fTopPtWgt->getEventWeight(topPtWgt, topPtWgtUp, topPtWgtDown );
	    }
	}

      //ready to roll!

      //do s.th. here
      bool passJetSelection(true);
      if(abs(box.cat)==11 || abs(box.cat)==13)       passJetSelection = (box.jets.size()>=4);
      bool passMetSelection(true);
      if(abs(box.cat)==11*11 || abs(box.cat)==11*13) passMetSelection =(box.met.pt()>40);

      std::vector<TString> evCats(1,box.chCat);            
      controlHistos.fillHisto("evtflow",   evCats, 0,               puWeight*lepSelectionWeight);
      controlHistos.fillHisto("nvertices", evCats, ev.nvtx,         puWeight*lepSelectionWeight);
      
      evCats.clear();
      if(box.lCat!="")         evCats.push_back(box.chCat+box.lCat);
      if(box.metCat!="")       evCats.push_back(box.chCat+box.metCat);
      controlHistos.fillHisto("njets", evCats, box.jets.size(), puWeight*lepSelectionWeight);      //N-1 plot
      if(passJetSelection) evCats.push_back(box.chCat);
      controlHistos.fillHisto("evtflow",   evCats, 1,               puWeight*lepSelectionWeight);

      evCats.clear();
      if(box.lCat!="")   evCats.push_back(box.chCat+box.lCat);
      if(box.jetCat!="") evCats.push_back(box.chCat+box.jetCat);
      controlHistos.fillHisto("met",       evCats, box.met.pt(),    puWeight*lepSelectionWeight); //N-1 plot
      if(passJetSelection && passMetSelection) evCats.push_back(box.chCat);
      controlHistos.fillHisto("evtflow",   evCats, 2,               puWeight*lepSelectionWeight);

      evCats.clear();
      if(passJetSelection && passMetSelection) evCats.push_back(box.chCat);
      if(box.lCat!="" || box.jetCat!="" || box.metCat!="")   evCats.push_back(box.chCat+box.lCat+box.jetCat+box.metCat);
      controlHistos.fillHisto("charge",       evCats, box.leptons[0].get("id")>0,    puWeight*lepSelectionWeight);
      float mt(utils::cmssw::getMT<LorentzVector>(box.leptons[0],box.met)),thetall(0);
      if(box.leptons.size()>=2)
	{
	  mt     += utils::cmssw::getMT<LorentzVector>(box.leptons[1],box.met);
	  thetall = utils::cmssw::getArcCos<LorentzVector>(box.leptons[0],box.leptons[1]);
	}
      controlHistos.fillHisto("mt",       evCats, mt,       puWeight*lepSelectionWeight);
      controlHistos.fillHisto("thetall",  evCats, thetall,  puWeight*lepSelectionWeight);
      
      
      //save selected event
      if(!saveSummaryTree || box.jets.size()==0) continue;      
      int evCatSummary(box.cat);
      if( box.lCat=="z" ) evCatSummary*=1000;
      std::vector<Float_t> allWeights(1,xsecWeight);
      allWeights.push_back(puWeight);
      allWeights.push_back(puWeightUp);
      allWeights.push_back(puWeightDown);
      allWeights.push_back(lepSelectionWeight);
      allWeights.push_back(lepSelectionWeightUp);
      allWeights.push_back(lepSelectionWeightDown);
      allWeights.push_back(topPtWgt);
      allWeights.push_back(topPtWgtUp);
      allWeights.push_back(topPtWgtDown);
      data::PhysicsObjectCollection_t pf=evSummary.getPhysicsObject(DataEventSummaryHandler::PFCANDIDATES);
      lxyAn.analyze(ev.run,ev.event,ev.lumi, ev.nvtx, allWeights, evCatSummary, box.leptons, box.jets, box.met, pf, gen);

    }
  
  if(nDuplicates) cout << "[Warning] found " << nDuplicates << " duplicate events in this ntuple" << endl;
  
  //
  // close opened files
  // 
  inF->Close();
  
  //
  // finally, save histos and tree to local file
  //
  spyFile->cd();
  controlHistos.Write();
  if(saveSummaryTree)
    {
      spyDir->cd(); 
      //spyEvents->getTree()->Write();
    }
  spyFile->Close();
  
  //that's all folks!
}  
