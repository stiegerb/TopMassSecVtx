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

  //
  std::pair<float,float> getSingleLeptonEfficiencySF(float eta,int id)
  {
    std::pair<float, float> sf(1,0);
    eta=abs(eta);
    id=abs(id);
    switch(id)
      {
      case 11:
	{
	  //id+iso from Table 6, trigger from Table 9 (leptonic leg) in AN 2012/218
	  //trigger
	  sf.first=1.005*0.988;
	  sf.second=sqrt(pow(0.05*0.988,2)+pow(0.05*1.005,2));
	  break;
	}
      case 13:
	{
	  //inclusive scale factors from AN 2013/248 (averaged for positive/negative eta)
	  //a conservative 1% uncertainty is assigned
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
  
  //AN-2012/389, table 11
  std::pair<float,float> getDileptonEfficiencySF(int id)
  {
    float trigSF(1.0), trigSFUnc(0.0);
    float selSF(1.0), selSFUnc(0.0);
    id=abs(id);
    switch(id)
      {
      case 11*11:
	{
	  selSF=0.982;  selSFUnc=0.006;
	  trigSF=0.979; trigSFUnc=0.012;
	  break;
	}
      case 11*13:
	{
	  selSF=0.990;  selSFUnc=0.004;
	  trigSF=0.948; trigSFUnc=0.010;
	  break;
	}
      case 13*13:
	{
	  selSF=0.999;  selSFUnc=0.006;
	  trigSF=0.966; trigSFUnc=0.011;
	  break;
	}
      }
    
    return std::pair<float, float>(selSF*trigSF,sqrt(pow(selSF*trigSFUnc,2)+pow(selSFUnc*trigSF,2)));
  }
  
  
 private:
  
};
  

#endif
