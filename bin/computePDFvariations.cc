#include <iostream>
#include <boost/shared_ptr.hpp>

#include "UserCode/TopMassSecVtx/interface/PDFInfo.h"
#include "UserCode/TopMassSecVtx/interface/LxyAnalysis.h"

#include "FWCore/FWLite/interface/AutoLibraryLoader.h"
#include "FWCore/PythonParameterSet/interface/MakeParameterSets.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

#include "TSystem.h"
#include "TFile.h"
#include "TTree.h"
#include "TEventList.h"
#include "TROOT.h"
#include "TH1F.h"
#include "TGraph.h"

using namespace std;

namespace LHAPDF {
  void initPDFSet(int nset, const std::string& filename, int member=0);
  int numberPDF(int nset);
  void usePDFMember(int nset, int member);
  double xfx(int nset, double x, double Q, int fl);
  double getXmin(int nset, int member);
  double getXmax(int nset, int member);
  double getQ2min(int nset, int member);
  double getQ2max(int nset, int member);
  void extrapolate(bool extrapolate=true);
}

struct stPDFval{
  stPDFval() {}
  stPDFval(const stPDFval& arg) : 
    qscale(arg.qscale),
    x1(arg.x1),
    x2(arg.x2),
    id1(arg.id1),
    id2(arg.id2){
  }

   Float_t qscale;
   Float_t x1;
   Float_t x2;
   Int_t id1;
   Int_t id2;
};



//
int main(int argc, char* argv[])
{
  // load framework libraries
  gSystem->Load( "libFWCoreFWLite" );
  AutoLibraryLoader::enable();
  
  //check arguments
  if ( argc < 2 ){
      std::cout << "Usage : " << argv[0] << " parameters_cfg.py" << std::endl;
      return 0;
  }
  
  //get configuration
  const edm::ParameterSet &runProcess = edm::readPSetsFrom(argv[1])->getParameter<edm::ParameterSet>("runProcess");
  bool isMC = runProcess.getParameter<bool>("isMC");
  if(!isMC) {
    cout << "Sample is data...nothing to be done here" << endl;
    return -1;
  }
  std::vector<std::string> urls=runProcess.getParameter<std::vector<std::string> >("input");
  TString url = TString(urls[0]);
  //if(url.Contains("/store")) url="root://eoscms//eos/cms/"+url; //not needed

  //prepare output
  TString outFileUrl(gSystem->BaseName(url));
  outFileUrl.ReplaceAll(".root","");
  

  //INITIALIZE THE PDF TOOL
  //notice cteq66.LHgrid and CT10, yields 90% CI so the final uncertainty is obtained after re-scaling by 1/C90=1/1.64485
  //see http://www.hep.ucl.ac.uk/pdf4lhc/PDF4LHC_practical_guide.pdf
  string pdfSets[]   = {"CT10.LHgrid"}; //"cteq66.LHgrid",, "MSTW2008nlo68cl.LHgrid","NNPDF20_100.LHgrid"};
  std::vector<Int_t>   nPdfVars;
  const size_t nPdfSets=sizeof(pdfSets)/sizeof(string);
  //const size_t nPdfSets=1;
  for(size_t ipdf=0; ipdf<nPdfSets; ipdf++)  
    {
      LHAPDF::initPDFSet(ipdf+1, pdfSets[ipdf]);
      nPdfVars.push_back( LHAPDF::numberPDF(ipdf+1) );
    }

  //open the INPUT file and get events tree
  TFile *file = TFile::Open(url);
  if(file==0) return -1;
  if(file->IsZombie()) return -1;
  TTree *t=(TTree *)file->Get("dataAnalyzer/lxy");
  if(t==0)
    {
      cout << "No tree has been found...quitting" << endl;
      file->Close();
      return -1;
    }
  stPDFval valForPDF;
  t->SetBranchAddress("qscale",&valForPDF.qscale);
  t->SetBranchAddress("x1",&valForPDF.x1);
  t->SetBranchAddress("x2",&valForPDF.x2);
  t->SetBranchAddress("id1",&valForPDF.id1);
  t->SetBranchAddress("id2",&valForPDF.id2);

  gROOT->cd();

  //create the OUTPUTFILE AND TREE
  TString outdir=runProcess.getParameter<std::string>("outdir");
  TString outUrl( outdir );
  gSystem->Exec("mkdir -p " + outUrl);
  outUrl += "/";
  outUrl += outFileUrl + "_pdf.root";
  printf("PDF weights will be saved in %s\n", outUrl.Data());
  TFile *ofile=TFile::Open(outUrl, "recreate");  
  TH1F *qscale=new TH1F("qscale",";Q^{2};Events",1000,0.,1000.); 
  qscale->SetDirectory(ofile);
  gROOT->cd(); 


  //loop over events
  std::vector<stPDFval> pdfvals;
  int evStart(0),evEnd(t->GetEntriesFast());
  //loop on all the events
  printf("Progressing Bar     :0%%       20%%       40%%       60%%       80%%       100%%\n");
  printf("Scanning the ntuple :");
  int treeStep = (evEnd-evStart)/50;if(treeStep==0)treeStep=1;
  for( int iev=evStart; iev<evEnd; iev++){
      if((iev-evStart)%treeStep==0){printf(".");fflush(stdout);}
      t->GetEntry(iev);
      pdfvals.push_back(valForPDF);
      qscale->Fill(valForPDF.qscale);
  }printf("\n\n\n");
  //all done with the events file
  file->Close();

  //
  printf("Loop on PDF sets and variations\n");   
  for(size_t ipdf=0; ipdf<nPdfSets; ipdf++){

    std::cout << pdfSets[ipdf] << " has " << nPdfVars[ipdf] << " variations" << std::endl;
    for(int i=0; i <(nPdfVars[ipdf]+1); ++i){
      std::cout << ".";
      LHAPDF::usePDFMember(ipdf+1,i);
      char nameBuf[256];sprintf(nameBuf,"%s_var%d", pdfSets[ipdf].c_str(), i);
      //printf("%30s:", nameBuf);
     
      //create the output tree
      float pdfWgt(0);
      TTree *pdfT = new TTree(nameBuf,"pdf");
      pdfT->Branch("w", &pdfWgt, "w/F");
      pdfT->SetDirectory(ofile);
      
      for(unsigned int v=0; v<pdfvals.size(); v++){ 
	double xpdf1 = LHAPDF::xfx(ipdf+1, pdfvals[v].x1, pdfvals[v].qscale, pdfvals[v].id1)/pdfvals[v].x1;
	double xpdf2 = LHAPDF::xfx(ipdf+1, pdfvals[v].x2, pdfvals[v].qscale, pdfvals[v].id2)/pdfvals[v].x2;
	pdfWgt = xpdf1 * xpdf2;
	pdfT->Fill();
      }
      ofile->cd();
      pdfT->Write();
    }
    std::cout << std::endl;
  }
  qscale->Write();
  ofile->Close();
  printf("All done\n");fflush(stdout);
}  


