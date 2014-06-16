#ifndef _tdrstyle_h_
#define _tdrstyle_h_

//
// TDR style macro for plots in ROOT
//

#include "TString.h"
#include <string>

#include "TROOT.h"
#include "TStyle.h"
#include "TPad.h"

void fixOverlay();
void setTDRStyle();

//round up and show in TeX
std::string toLatexRounded(double value, double error, double systError=-1,bool doPowers=true);

//clean up ROOT version of TeX
void TLatexToTex(TString &expr);

#endif
