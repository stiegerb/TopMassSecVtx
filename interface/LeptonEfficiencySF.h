#ifndef LeptonEfficiencySF_h
#define LeptonEfficiencySF_h

// cf.
// https://twiki.cern.ch/twiki/bin/view/Main/EGammaScaleFactors2012#2012_8_TeV_data_53X
//
class LeptonEfficiencySF
{
 public:

  //
  LeptonEfficiencySF() { }

  //
  ~LeptonEfficiencySF() {}

  //electrons : id+iso from Table 6, trigger from Table 9 (leptonic leg) in AN 2012/218
  //muons : inclusive scale factors from AN 2013/248 (averaged for positive/negative eta), a conservative 1% uncertainty is assigned
  std::pair<float,float> getSingleLeptonEfficiencySF(float eta,int id)
  {
    std::pair<float, float> sf(1,0);
    eta=abs(eta);
    id=abs(id);
    switch(id)
      {
      case 11:
	{
	  sf.first=1.00*0.988;
	  sf.second=sqrt(pow(0.02*0.988,2)+pow(0.02*1.00,2));
	  break;
	}
      case 13:
	{
	  sf.second=0.01;
	  if(eta<0.12) sf.first=0.97;
	  if(eta<0.35) sf.first=0.94;
	  if(eta<0.59) sf.first=0.98;
	  if(eta<0.89) sf.first=0.98;
	  if(eta<1.22) sf.first=0.96;
	  if(eta<1.62) sf.first=0.98;
	  else         sf.first=1.0;
	  break;
	}
      }
    return sf;
  }
  
  //AN-2012/389, Figures 4,5,6
  //assumes eta1,eta2 are the leading, trailer lepton eta
  //for emu eta1=eta_e, eta2=eta_mu
  //the selection efficiency is assumed to be perfect (SF=1) which is ok, and a 2% unc. is assigned to it
  std::pair<float,float> getDileptonEfficiencySF(float eta1,float eta2,int id)
  {
    float trigSF(1.0),trigSFUnc(0.0),selSF(1.0),selSFUnc(0.0);
    id=abs(id);
    switch(id)
      {
      case 11*11:
	{
	  selSF=1.0; selSFUnc=0.01;
	  if( fabs(eta1)<1.442 )
	    {
	      if(fabs(eta2)<1.4442) {trigSF=0.978; trigSFUnc=0.012;}
	      else                  {trigSF=0.991; trigSFUnc=0.023;}
	    }
	  else
	    {
	      if(fabs(eta2)<1.4442) {trigSF=0.990; trigSFUnc=0.023;}
	      else                  {trigSF=0.908; trigSFUnc=0.051;}
	    }
	  break;
	}
      case 11*13:
	{
	  selSF=1.0; selSFUnc=0.01;
	  if( fabs(eta1)<1.442 )
	    {
	      if(fabs(eta2)<1.2) {trigSF=0.961; trigSFUnc=0.011;}
	      else               {trigSF=0.930; trigSFUnc=0.015;}
	    }
	  else
	    {
	      if(fabs(eta2)<1.2) {trigSF=0.972; trigSFUnc=0.018;}
	      else               {trigSF=0.922; trigSFUnc=0.032;}
	    }
	  break;
	}
      case 13*13:
	{
	  selSF=1.0; selSFUnc=0.01;
	  if( fabs(eta1)<0.9 )
	    {
	      if( fabs(eta2)<0.9 )     { trigSF=0.969; trigSFUnc=0.010; }
	      else if (fabs(eta2)<1.2) { trigSF=0.977; trigSFUnc=0.025; }
	      else if (fabs(eta2)<2.1) { trigSF=0.975; trigSFUnc=0.011; }
	      else                     { trigSF=0.982; trigSFUnc=0.026; }
	    }
	  else if (fabs(eta1)<1.2)
	    {
	      if( fabs(eta2)<0.9 )     { trigSF=0.978; trigSFUnc=0.011; }
	      else if (fabs(eta2)<1.2) { trigSF=0.972; trigSFUnc=0.015; }
	      else if (fabs(eta2)<2.1) { trigSF=0.963; trigSFUnc=0.014; }
	      else                     { trigSF=0.928; trigSFUnc=0.035; }
	    }
	  else if (fabs(eta1)<2.1)
	    {
	      if( fabs(eta2)<0.9 )     { trigSF=0.968; trigSFUnc=0.011; }
	      else if (fabs(eta2)<1.2) { trigSF=0.978; trigSFUnc=0.014; }
	      else if (fabs(eta2)<2.1) { trigSF=0.969; trigSFUnc=0.012; }
	      else                     { trigSF=0.975; trigSFUnc=0.023; }
	    }
	  else
	    {
	      if( fabs(eta2)<0.9 )     { trigSF=0.960; trigSFUnc=0.028; }
	      else if (fabs(eta2)<1.2) { trigSF=0.949; trigSFUnc=0.035; }
	      else if (fabs(eta2)<2.1) { trigSF=0.973; trigSFUnc=0.026; }
	      else                     { trigSF=1.075; trigSFUnc=0.093; }
	    }
	  break;
	}
      }
    
    return std::pair<float, float>(selSF*trigSF,sqrt(pow(selSF*trigSFUnc,2)+pow(selSFUnc*trigSF,2)));
  }
  
  
 private:
  
};
  

#endif
