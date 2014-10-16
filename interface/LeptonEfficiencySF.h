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
	  sf.first=1.005*0.988;
	  sf.second=sqrt(pow(0.05*0.988,2)+pow(0.05*1.005,2));
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
	  else sf.first=1.0;
	  break;
	}
      }
    return sf;
  }
  
  //AN-2012/389, Figures 26, 27,28
  //assumes eta1,eta2 are the leading, trailer lepton eta
  //for emu eta1=eta_e, eta2=eta_mu
  //the selection efficiency is assumed to be perfect (SF=1) which is ok, and a 2% unc. is assigned to it
  std::pair<float,float> getDileptonEfficiencySF(float eta1,float eta2,int id)
  {
    float trigSF,trigSFUNC,selSF,selSFUnc;
    id=abs(id);
    switch(id)
      {
      case 11*11:
	{
	  selSF=1.0; selSFUnc=0.02;
	  if( fabs(eta1)<1.442 )
	    {
	      if(fabs(eta2)<1.4442) {trigSF=0.993; trigSFUnc=0.011;}
	      else                  {trigSF=1.007; trigSFUnc=0.014;}
	    }
	  else
	    {
	      if(fabs(eta2)<1.4442) {trigSF=0.987; trigSFUnc=0.015;}
	      else                  {trigSF=0.998; trigSFUnc=0.024;}
	    }
	  break;
	}
      case 11*13:
	{
	  selSF=1.0; selSFUnc=0.02;
	  if( fabs(eta1)<1.442 )
	    {
	      if(fabs(eta2)<1.2) {trigSF=0.984; trigSFUnc=0.010;}
	      else               {trigSF=0.940; trigSFUnc=0.012;}
	    }
	  else
	    {
	      if(fabs(eta2)<1.2) {trigSF=0.978; trigSFUnc=0.013;}
	      else               {trigSF=0.937; trigSFUnc=0.020;}
	    }
	  break;
	}
      case 13*13:
	{
	  selSF=1.0; selSFUnc=0.02;
	  if( fabs(eta1)<0.9 )
	    {
	      if( fabs(eta2)<0.9 )     { trigSF=0.968; trigSFUnc=0.010; }
	      else if (fabs(eta2)<1.2) { trigSF=0.976; trigSFUnc=0.010; }
	      else if (fabs(eta2)<2.1) { trigSF=0.976; trigSFUnc=0.010; }
	      else                     { trigSF=0.975; trigSFUnc=0.021; }
	    }
	  else if (fabs(eta1)<1.2)
	    {
	      if( fabs(eta2)<0.9 )     { trigSF=0.980; trigSFUnc=0.010; }
	      else if (fabs(eta2)<1.2) { trigSF=0.980; trigSFUnc=0.012; }
	      else if (fabs(eta2)<2.1) { trigSF=0.979; trigSFUnc=0.011; }
	      else                     { trigSF=0.980; trigSFUnc=0.023; }
	    }
	  else if (fabs(eta1)<2.1)
	    {
	      if( fabs(eta2)<0.9 )     { trigSF=0.976; trigSFUnc=0.010; }
	      else if (fabs(eta2)<1.2) { trigSF=0.983; trigSFUnc=0.011; }
	      else if (fabs(eta2)<2.1) { trigSF=0.962; trigSFUnc=0.010; }
	      else                     { trigSF=0.957; trigSFUnc=0.015; }
	    }
	  else
	    {
	      if( fabs(eta2)<0.9 )     { trigSF=0.988; trigSFUnc=0.020; }
	      else if (fabs(eta2)<1.2) { trigSF=1.009; trigSFUnc=0.023; }
	      else if (fabs(eta2)<2.1) { trigSF=0.959; trigSFUnc=0.015; }
	      else                     { trigSF=0.961; trigSFUnc=0.032; }
	    }
	  break;
	}
      }
    
    return std::pair<float, float>(selSF*trigSF,sqrt(pow(selSF*trigSFUnc,2)+pow(selSFUnc*trigSF,2)));
  }
  
  
 private:
  
};
  

#endif
