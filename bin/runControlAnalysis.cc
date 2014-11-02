#include "UserCode/TopMassSecVtx/interface/MacroUtils.h"
#include "UserCode/TopMassSecVtx/interface/SmartSelectionMonitor.h"
#include "UserCode/TopMassSecVtx/interface/DataEventSummaryHandler.h"
#include "UserCode/TopMassSecVtx/interface/LxyAnalysis.h"
#include "UserCode/TopMassSecVtx/interface/MuScleFitCorrector.h"

#include "FWCore/FWLite/interface/AutoLibraryLoader.h"
#include "FWCore/PythonParameterSet/interface/MakeParameterSets.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "PhysicsTools/Utilities/interface/LumiReWeighting.h"

#include "TVectorD.h"
#include "TSystem.h"
#include "TFile.h"
#include "TTree.h" 
#include "TGraph2D.h"

#include <fstream>
#include <iostream>

using namespace std;

FactorizedJetCorrector *fJesCor=0;
std::vector<JetCorrectionUncertainty *> fTotalJESUnc;
MuScleFitCorrector *fMuCor=0;

//aggregates all the objects needed for the analysis
enum ControlBoxType { DIJETBOX=1, GAMMABOX=22, WBOX=23, ZBOX=24};
class ControlBox{
public:
  ControlBox() : cat(0), probeFlav(0), probeXb(0), probeFlavStr(""), probe(0), tag(0) { }
  
  void assignBox(Int_t evcat,data::PhysicsObject_t *itag, data::PhysicsObject_t *iprobe)
  {
    cat=evcat;
    tag=itag;
    probe=iprobe;
  }

  void assignProbeFlavour(data::PhysicsObjectCollection_t &gen)
  {
    const data::PhysicsObject_t &genJet=probe->getObject("genJet");
    if(genJet.pt()>0) {
      int jetFlav=genJet.info.find("id")->second;
      if(abs(jetFlav)==5)      { probeFlav=1; probeFlavStr="b";         }
      else if(abs(jetFlav)==4) { probeFlav=3; probeFlavStr="c";         } 
      else                     { probeFlav=2; probeFlavStr="udsg";      }
    }
    else                       { probeFlav=4; probeFlavStr="unmatched"; }
     
    const data::PhysicsObject_t &genParton=probe->getObject("gen");
    int genId=genParton.info.find("id")->second;
    if(abs(genId)==5 && genParton.pt()>0){
      for(size_t imc=0; imc<gen.size(); imc++)
	{
	  int id=gen[imc].get("id");
	  if(abs(id)<500) continue;
	  if(deltaR(gen[imc],genParton)>0.5) continue;
	  probeXb=gen[imc].pt()/genParton.pt();
	  break;
	}
    }
  }
  
  ~ControlBox() { }
  Int_t cat;
  Int_t probeFlav;
  Float_t probeXb;
  TString probeFlavStr;
  data::PhysicsObject_t *probe, *tag;
};

ControlBox assignBox(int reqControlType, 
		     data::PhysicsObjectCollection_t &leptons, 
		     data::PhysicsObjectCollection_t &photons, 
		     data::PhysicsObjectCollection_t &jets, 
		     data::PhysicsObjectCollection_t &met, 
		     data::PhysicsObjectCollection_t &pf)
{
  ControlBox box;
  
  if(reqControlType==DIJETBOX)
    {
      //two jets and now leptons
      if(jets.size()!=2) return box;
      if(leptons.size()) return box;

      //require at least one soft muon
      std::vector<int> nTriggerSoftMuons(jets.size(),0), nSoftMuons(jets.size(),0);
      for(size_t ijet=0; ijet<jets.size(); ijet++){
	size_t pfstart=jets[ijet].get("pfstart");
	size_t pfend=jets[ijet].get("pfend");
	if(pf.size()<pfstart || pf.size()<pfend-1) continue;
	for(size_t ipfn=pfstart; ipfn<=pfend; ipfn++)
	  {
	    int id=pf[ipfn].get("id");
	    if(abs(id)!=13) continue;
		 if(pf[ipfn].pt()<1) continue;
		 nSoftMuons[ijet]++;
		 if(pf[ipfn].pt()<5) continue;
		 nTriggerSoftMuons[ijet]++;
	  }
      }
      if(nTriggerSoftMuons[0]+nTriggerSoftMuons[1]) return box;
     
      //back to back configuration
      float dphijj=deltaPhi(jets[0].phi(),jets[1].phi());
      if(fabs(dphijj)<2.7) return box;
     
      //balancing variable
      float balance=jets[1].pt()/jets[0].pt();
      if(balance<0.9) return box;
	   
      //now decide which one is the tag and which one is the probe (give preference to higher pT jet for tag) 
      int tagJetIdx(0), probeJetIdx(1);
      if( nTriggerSoftMuons[0]==0 ) { tagJetIdx=1; probeJetIdx=0; }
	   
      //require a tag on the tag jet
      bool tagHasCSVL(selJets[tagJetIdx].getVal("csv")>0.405);
      if(!tagHasCSVL) return box;
	   
      //all done here
      box.assignBox(reqControlType, &(jets[tagJetIdx]), &(jets[probeJetIdx]));
    }
  else if(reqControlType==GAMMABOX)
    {
      //gamma+1 jet without leptons
      if(photons.size()!=1 || jets.size()!=1) return box;
      if(leptons.size()) return box;

      //back to back configuration
      float dphijj=deltaPhi(photons[0].phi(),jets[0].phi());
      if(fabs(dphijj)<2.7) return box;
     
      //balancing variable
      float balance=jets[0].pt()/photons[0].pt();
      if(balance<0.8) return box;

      //all done here
      box.assignBox(reqControlType, &(photons[0]), &(jets[0]));
    }
  else if(reqControlType==WBOX)
    {
      //1 lepton + 1 jet
      if(leptons.size()!=1) return box;
      if(jets.size()!=1) return box;
      
      //require significant MET
      float metsig=met[0].pt()/sqrt(jet[0].pt());
      if(metsig<3.5) return box;

      //require minimun transverse mass
      float mt(utils::cmssw::getMT<LorentzVector>( leptons[0], met[0]));
      if(mt<50) return box;
      
      //back-to-back configuration
      LorentzVector lv=leptons[0]+met[0];
      float dphijj=deltaPhi(lv.phi(),jets[0].phi());
      if(fabs(dphijj)<2.7) return box;
      
      //balancing variable
      //float balance=jets[0].pt()/lv.pt();
      //if(balance<0.8) return box;
      
      data::PhysicsObject_t *w=new data::PhysicsObject_t(lv.px(),lv.py(),lv.pz(),lv.energy());
      w->set("id",22);
      box.assignBox(reqControlType, w, &(jets[0]));
    }
  else if(reqControlType==ZBOX)
    {
      //2 leptons + 1 jet
      if(leptons.size()!=2) return box;
      if(jets.size()!=1) return box;

      //require z window
      LorentzVector ll=leptons[0]+leptons[1];
      if(fabs(ll.mass()-91)>15) return box;

      //back to back configuration 
      float dphijj=deltaPhi(ll.phi(),jets[0].phi());
      if(fabs(dphijj)<2.7) return box;
      
      //balancing variable
      float balance=jets[0].pt()/ll.pt();
      if(balance<0.8) return box;
      
      data::PhysicsObject_t *z=new data::PhysicsObject_t(ll.px(),ll.py(),ll.pz(),ll.energy());
      z->set("id",24);
      box.assignBox(reqControlType, z, &(jets[0]));
    }

  //all done
  return box;
}

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
  const edm::ParameterSet &runProcess       = edm::readPSetsFrom(argv[1])->getParameter<edm::ParameterSet>("runProcess");
  std::vector<std::string> urls=runProcess.getParameter<std::vector<std::string> >("input");
  TString url = TString(urls[0]);
  TString baseDir     = runProcess.getParameter<std::string>("dirName");
  TString jecDir      = runProcess.getParameter<std::string>("jecDir");
  bool isMC           = runProcess.getParameter<bool>("isMC");
  double xsec         = runProcess.getParameter<double>("xsec");
  TString out          = runProcess.getParameter<std::string>("outdir");
  bool saveSummaryTree = runProcess.getParameter<bool>("saveSummaryTree");
  std::vector<string>  weightsFile = runProcess.getParameter<std::vector<string> >("weightsFile");

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

  //control the sec vtx analysis  
  LxyAnalysis lxyAn;

  //prepare the output file
  TString proctag=gSystem->BaseName(url);
  Ssiz_t pos=proctag.Index(".root");
  proctag.Remove(pos,proctag.Length());
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
  // check input file
  //
  TFile *inF = TFile::Open(url);
  if(inF==0) return -1;
  if(inF->IsZombie()) return -1;

  //
  // pileup reweighter
  //
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
  while(mcPileupDistribution.size()<dataPileupDistribution.size())  mcPileupDistribution.push_back(0.0);
  while(mcPileupDistribution.size()>dataPileupDistribution.size())dataPileupDistribution.push_back(0.0);
  gROOT->cd();  //THIS LINE IS NEEDED TO MAKE SURE THAT HISTOGRAM INTERNALLY PRODUCED IN LumiReWeighting ARE NOT DESTROYED WHEN CLOSING THE FILE
  edm::LumiReWeighting *LumiWeights= isMC ? new edm::LumiReWeighting(mcPileupDistribution,dataPileupDistribution): 0;

  //book histograms
  SmartSelectionMonitor controlHistos;
  TH1 *Hcutflow=(TH1 *)controlHistos.addHistogram(  new TH1F ("cutflow"    , "cutflow"    ,6,0,6) ) ;
  for(int ibin=1; ibin<=6; ibin++) Hcutflow->SetBinContent(ibin,1);
  controlHistos.addHistogram( new TH1F("pthat", ";#hat{p}_{T} [GeV]; Events",100,0,1500) );
  controlHistos.addHistogram( new TH1F ("nvertices", "; Vertex multiplicity; Events", 50, 0.,50.) );

  //jet control
  TString jetFlavors[]={"","b","udsg","c","unmatched"};
  size_t nJetFlavors=sizeof(jetFlavors)/sizeof(TString);
  for(size_t ijet=1; ijet<=2; ijet++)
    {
      TString jetctr(""); jetctr += ijet;
      controlHistos.addHistogram( new TH1F ("jet"+jetctr, "; Jet #"+jetctr+" transverse momentum [GeV]; Jets", 100, 0.,1000.) );
      controlHistos.addHistogram( new TH1F ("jet"+jetctr+"eta", "; Jet #"+jetctr+" pseudo-rapidity; Jets", 30, 0.,3.) );
      TH1 *hflav=controlHistos.addHistogram( new TH1F ("jet"+jetctr+"flav", "; Jet #"+jetctr+" flavour; Jets", nJetFlavors, 0.,nJetFlavors) );
      for(int xbin=1; xbin<=hflav->GetXaxis()->GetNbins(); xbin++) hflav->GetXaxis()->SetBinLabel(xbin,jetFlavors[xbin-1]);
    }
  
  //tag and probe analysis for Sec Vtx
  const Double_t ptBins[]={30,35,40,45,50,55,60,65,70,80,90,100,120,140,160,180,200,250,350,400,500,750,1000};
  Int_t nPtbins=sizeof(ptBins)/sizeof(Double_t)-1;
  TString svxAlgo="svx"; 
  // TString svxAlgo="ivf";
  for(size_t iflav=0; iflav<nJetFlavors; iflav++)
    {
      size_t nVars(1);
      if(jetFlavors[iflav]=="b") nVars=systVars.size();
      for(size_t ivar=0; ivar<nVars; ivar++)
	{
	  TString prefix(systVars[ivar]+jetFlavors[iflav]);
	  controlHistos.addHistogram( new TH2F (prefix+"recoil"+svxAlgo+"mass",       "; SecVtx Mass [GeV]; Jets",                 50, 0.,10.,  nPtbins,ptBins) );
	  controlHistos.addHistogram( new TH2F (prefix+"recoil"+svxAlgo+"lxy",        "; SecVtx L_{xy} [cm]; Jets",                100, 0.,10., nPtbins,ptBins) );	 
	  controlHistos.addHistogram( new TH2F (prefix+"recoil"+svxAlgo+"lxysig",     "; L_{xy}/sigma;  Jets",                     50, 0.,50.,  nPtbins,ptBins) );	 
	  controlHistos.addHistogram( new TH2F (prefix+"recoil"+svxAlgo+"dr",         "; #Delta R(jet,SecVtx L_{xy}); Jets",       50, 0.,1.0,  nPtbins,ptBins) );	 
	  controlHistos.addHistogram( new TH2F (prefix+"recoil"+svxAlgo+"ptfrac",     "; p_{T}(SecVtx L_{xy})/p_{T}(jet); Jets",   50, 0.,2.0,  nPtbins,ptBins) );	 
	  controlHistos.addHistogram( new TH2F (prefix+"recoil"+svxAlgo+"neutemfrac", "; Neutral EM fraction; Jets",               50, 0.,1.0,  nPtbins,ptBins) );	 
	  controlHistos.addHistogram( new TH2F (prefix+"recoil"+svxAlgo+"chfrac",     "; Charged fraction; Jets",                  50, 0.,1.0,  nPtbins,ptBins) );	 
	  controlHistos.addHistogram( new TH2F (prefix+"recoil"+svxAlgo+"neuthadfrac","; Neutral Had fraction; Jets",              50, 0.,1.0,  nPtbins,ptBins) );	 
	  controlHistos.addHistogram( new TH2F (prefix+"recoil"+svxAlgo+"mufrac",     "; Muon fraction; Jets",                     50, 0.,1.0,  nPtbins,ptBins) );	 
	  controlHistos.addHistogram( new TH2F (prefix+"recoil"+svxAlgo+"ntracks", "; SecVtx track multiplicity; Jets",            10, 0.,10,   nPtbins,ptBins) );	 
	}
    }

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

  //
  // analyze (puf...)
  //
  for (int inum=0; inum < totalEntries; ++inum)
    {
      if(inum%500==0) { printf("\r [ %d/100 ]",int(100*float(inum)/float(totalEntries))); cout << flush; }
      evSummary.getEntry(inum);
      DataEventSummary &ev = evSummary.getEvent();
  
      //pileup weight
      float weightNom(1.0);
      if(LumiWeights) 	weightNom  = LumiWeights->weight(ev.ngenITpu);

      //get the trigger
      float triggerPrescale(1.0),triggerThreshold(0);
      bool dijetTrigger(false), gammaTrigger(false), eTrigger(false), muTrigger(false), eeTrigger(false), mumuTrigger(false);
      if(runDijetControl)
	{
	  for(int itrig=0; itrig<=4; itrig++)
	    {
	      if(!ev.t_bits[itrig]) continue;
	      dijetTrigger=true;
	      triggerPrescale=ev.t_prescale[itrig];
	      break;
	    }
	  triggerThreshold=30;
	  if(isMC) dijetTrigger=true; 
	  if(!dijetTrigger) continue;
	}
      else if(runGammaControl)
	{
	  for(size_t itrig=10; itrig>=7; itrig--)
	    {
	      if(!ev.t_bits[itrig]) continue;
	      gammaTrigger=true;
	      triggerPrescale=ev.t_prescale[itrig];
	      if(itrig==10) triggerThreshold=92; //90   
	      if(itrig==9)  triggerThreshold=77; //75
	      if(itrig==8)  triggerThreshold=50;
	      if(itrig==7)  triggerThreshold=36;
	      break;
	    }
	  if(isMC) gammaTrigger=true;
	  if(!gammaTrigger) continue;
	}
      else if(runWcontrol)
	{
	  eTrigger  = ev.t_bits[13];
	  muTrigger = ev.t_bits[6];
	  if(!eTrigger && !muTrigger) continue;
	}
      else if(runZcontrol)
	{
	  eeTrigger   = ev.t_bits[0];
	  mumuTrigger = ev.t_bits[2] || ev.t_bits[3];
	  if(!eeTrigger && !mumuTrigger) continue;
	}
      
      
      //weight for the event
      float weight(weightNom*triggerPrescale);

      //select the objects
      data::PhysicsObjectCollection_t leptons    = selectLeptons(evSummary.getPhysicsObject(DataEventSummaryHandler::LEPTONS), ev.rho, isMC);
      data::PhysicsObjectCollection_t photons    = selectPhotons(evSummary.getPhysicsObject(DataEventSummaryHandler::PHOTONS), triggerThresholds, ev.rho);
      data::PhysicsObjectCollection_t rawJets    = evSummary.getPhysicsObject(DataEventSummaryHandler::JETS);
      LorentzVector jetDiff                      = utils::cmssw::updateJEC(rawJets, fJesCor, fTotalJESUnc, ev.rho, ev.nvtx, isMC);      
      data::PhysicsObjectCollection_t jets       = selectJets(rawJets,leptons);
      data::PhysicsObjectCollection_t recoMet    = evSummary.getPhysicsObject(DataEventSummaryHandler::MET);
      recoMet[2].SetPxPyPzE(recoMet[2].px()-jetDiff.px(),
			    recoMet[2].py()-jetDiff.py(),
			    0.,
			    sqrt(pow(recoMet[2].px()-jetDiff.px(),2)+pow(recoMet[2].py()-jetDiff.py(),2))
			    );
     std::vector<LorentzVector> met              = utils::cmssw::getMETvariations(recoMet[2], selJets, selLeptons, isMC);
     data::PhysicsObjectCollection_t pf          = evSummary.getPhysicsObject(DataEventSummaryHandler::PFCANDIDATES); 
      
     //build the analysis box
     ControlBox box = assignBox(reqControlType,leptons,photons,jets,met,pf);
     if(box.cat==0) continue;
     data::PhysicsObjectCollection_t gen;
     if(isMC){
       gen=evSummary.getPhysicsObject(DataEventSummaryHandler::GENPARTICLES);
       box.assignProbeFlavour(gen);
     }

     //gen control
     if(isMC) controlHistos.fillHisto("pthat",catsToFill,ev.pthat,weight);
     
     //vertices control
     controlHistos.fillHisto("nvertices",catsToFill,ev.nvtx,weight);

     //tag/probe kinematics
     controlHistos.fillHisto("tagpt",     catsToFill, box.tag->pt(),          weight);
     controlHistos.fillHisto("tageta",    catsToFill, fabs(box.tag->eta()),   weight);
     controlHistos.fillHisto("probept",   catsToFill, box.probe->pt(),        weight);
     controlHistos.fillHisto("probeeta",  catsToFill, fabs(box.probe->eta()), weight);
     if(isMC) controlHistos.fillHisto("probeflav", catsToFill, box.probeFlav,          weight);
     
     //secondary vertex characteristics evaluated for the probe
     float recoilPtNorm(TMath::Min(box.probe[0]->pt(),ptBins[nPtbins-1]));
     const data::PhysicsObject_t &svx = selJets[probeJetIdx].getObject(svxAlgo);
     float lxy=svx.vals.find("lxy")->second;
     if(lxy)
       {
	 float lxyErr=svx.vals.find("lxyErr")->second;
	 int ntrk=svx.info.find("ntrk")->second;
	 catsToFill.clear();
	 catsToFill.push_back("");
	 if(ntrk==2)      catsToFill.push_back("ntrk2");
	 else if(ntrk==3) catsToFill.push_back("ntrk3");
	 else             catsToFill.push_back("ntrk4");
	 controlHistos.fillHisto("recoil"+svxAlgo+"mass",        catsToFill, svx.mass(),                                  recoilPtNorm, weight);
	 controlHistos.fillHisto("recoil"+svxAlgo+"lxy",         catsToFill, lxy,                                         recoilPtNorm, weight);
	 controlHistos.fillHisto("recoil"+svxAlgo+"lxysig",      catsToFill, lxy/lxyErr,                                  recoilPtNorm, weight);
	 controlHistos.fillHisto("recoil"+svxAlgo+"dr",          catsToFill, deltaR(selJets[probeJetIdx],svx),            recoilPtNorm, weight);
	 controlHistos.fillHisto("recoil"+svxAlgo+"ptfrac",      catsToFill, svx.pt()/selJets[probeJetIdx].pt(),          recoilPtNorm, weight);
	 controlHistos.fillHisto("recoil"+svxAlgo+"neutemfrac",  catsToFill, selJets[probeJetIdx].getVal("neutEmFrac"),   recoilPtNorm, weight);
	 controlHistos.fillHisto("recoil"+svxAlgo+"chfrac",      catsToFill, selJets[probeJetIdx].getVal("chHadFrac"),    recoilPtNorm, weight);
	 controlHistos.fillHisto("recoil"+svxAlgo+"neuthadfrac", catsToFill, selJets[probeJetIdx].getVal("neutHadFrac"),  recoilPtNorm, weight);
	 controlHistos.fillHisto("recoil"+svxAlgo+"mufrac",      catsToFill, selJets[probeJetIdx].getVal("muFrac"),       recoilPtNorm, weight);
	 controlHistos.fillHisto("recoil"+svxAlgo+"ntracks",     catsToFill, ntrk,                                        recoilPtNorm, weight);
	 if(isMC)
	   {
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"mass",         catsToFill, svx.mass(),                                  recoilPtNorm, weight);
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"lxy",          catsToFill, lxy,                                         recoilPtNorm, weight);
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"lxysig",       catsToFill, lxy/lxyErr,                                  recoilPtNorm, weight);
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"dr",           catsToFill, deltaR(selJets[probeJetIdx],svx),            recoilPtNorm, weight);
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"ptfrac",       catsToFill, svx.pt()/selJets[probeJetIdx].pt(),          recoilPtNorm, weight);
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"ntracks",      catsToFill, ntrk,                                        recoilPtNorm, weight);
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"nmuons",       catsToFill, nmuons,                                      recoilPtNorm, weight);
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"neutemfrac",   catsToFill, selJets[probeJetIdx].getVal("neutEmFrac"),   recoilPtNorm, weight);
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"chfrac",       catsToFill, selJets[probeJetIdx].getVal("chHadFrac"),    recoilPtNorm, weight);
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"neuthadfrac",  catsToFill, selJets[probeJetIdx].getVal("neutHadFrac"),  recoilPtNorm, weight);
	     controlHistos.fillHisto(box.probeFlavStr+"recoil"+svxAlgo+"mufrac",       catsToFill, selJets[probeJetIdx].getVal("muFrac"),       recoilPtNorm, weight);
	   }
       }
     
     
     //save selected event
     if(!saveSummaryTree) continue;
     lxyAn.resetBeautyEvent();
     BeautyEvent_t &bev=lxyAn.getBeautyEvent();
     bev.evcat=box.cat;
     bev.gevcat=box.cat;
     bev.run=ev.run;
     bev.event=ev.event;
     bev.lumi=ev.lumi;
     bev.nvtx=ev.nvtx;
     bev.rho=ev.rho;
     bev.nw=1;
     bev.w[0]=weight;
     bev.qscale=ev.qscale;  bev.x1=ev.x1; bev.x2=ev.x2; bev.id1=ev.id1; bev.id2=ev.id2;
     std::vector<data::PhysicsObject_t *> boxtag,boxprobe;
     boxtag.push_back( box.tag );
     boxprobe.push_back( box.probe );
     lxyAn.analyze( boxtag, boxprobe, met, pf, gen);
     spyDir->cd();
     lxyAn.save();
    }
  
  inF->Close();
  
  //
  // save histos to local file
  //
  spyFile->cd();
  spyFile->Write();
  TVectorD constVals(2);
  constVals[0] = isMC ? cnorm : 1.0;
  constVals[1] = isMC ? xsec  : 1.0;
  constVals.Write("constVals");
  controlHistos.Write();
  spyFile->Close();
 }
