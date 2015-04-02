#ifndef _bfragweighter_hh_
#define _bfragweighter_hh_

#include "TGraphErrors.h"
#include "TFile.h"
#include "TString.h"
#include "TSystem.h"

#include <iostream>
#include <vector>

class BfragWeighter
{
public:

  /**
     @short CTOR
  */
  BfragWeighter(TString url)
    {
      weights_.resize(3,0);
      gSystem->ExpandPathName( url );
      TFile *wgtsFile = TFile::Open( url );
      if(wgtsFile && !wgtsFile->IsZombie())
	{
	  std::cout << "[BfragWeighter] will use weights stored @ " << url << std::endl;
	  weights_[0] = (TGraphErrors *) wgtsFile->Get("Z2star_rbLEP_weight");
	  weights_[1] = (TGraphErrors *) wgtsFile->Get("Z2star_rbLEPhard_weight");
	  weights_[2] = (TGraphErrors *) wgtsFile->Get("Z2star_rbLEPsoft_weight");
	}
      wgtsFile->Close();
    }
  
  /**
     @short for n b-jets matched in the event, return the overall event weight
   */
  std::vector<float> getEventWeights(float bptratio)
    {
      std::vector<float> toRet(weights_.size(),1.0);
      for(size_t i=0; i<weights_.size(); i++)
	toRet[i] = weights_[i]->Eval( bptratio );
	
      return toRet;
    }
  
  /**
     @short DTOR
  */
  ~BfragWeighter()
    {
    }
  
 private:

  std::vector<TGraphErrors *> weights_;
};

#endif
