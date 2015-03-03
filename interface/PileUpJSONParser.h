#ifndef _pileupjsonparser_hh_
#define _pileupjsonparser_hh_

#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <utility>

#include "TString.h"

struct lumiInfo {
    double lum;
    double muavg;
    double murms;
    lumiInfo(double lum_=0, double muavg_=0, double murms_=0)
        : lum(lum_), muavg(muavg_), murms(murms_) {};
};

/************************************************************
Copied from parsePileUpJSON.C from Mikko Voutilainen
(email from March 2 2015)

This reads three text files with: good runs (JSON), pixel, and
HF instantaneous luminosities, and for each run/lumisecion
calculates the true number of pileup (mu). (I.e. the target
variable in the pileup reweighting.)

Observations by Mikko:

    1.85<mpx/mhf<2.0 =>
    runs: 190738, 194735, 196203, 198969, 199356, 200532, 203830, 203832,
          203833, 203834, 203835, 206210, 206575
    but only these have more than 1 LS in the range:
    203830, 203832, 203833, 203834, 203835

    Cut |mpx/mpf-0.975|<0.055 removes 6.6% of LS, 2.4% of PXlum, 1.2% of HFlum
    Other good alternative is |mpx/mpf-1|<0.08

    These runs are missing from the HF file:
    Run 194051 of 18 LS (lpx=0.003%)
    Run 206066 of 68 LS (lpx=0.04%)
    Run 207372 of 501 LS (lpx=0.27%)
    The PX file has everything it seems
    4.9% of HF LS and 3.4% of PX LS are empty or missing
************************************************************/
using namespace std;
class PileUpJSONParser
{
	public:

	PileUpJSONParser(TString filename="pileup.txt",
                     TString filename2="",
                     TString json="",
                     double minbXsec = 69400){
	    cout << Form("PileUpJSONParser(minbXsec=%5.1f):",minbXsec) << endl;
	    cout << "Opening " << filename << "...";
	    ifstream f(filename.Data(),ios::in);
	    if (f.is_open()) cout << "ok" << endl;
	    else {
	        cout << "failure" << endl;
	        return;
	    }

	    if (filename2!="") cout << "Opening " << filename2 << "...";
	    ifstream f2(filename2.Data(),ios::in);
	    if (f2.is_open()) cout << "ok" << endl;
	    else if (filename2!="") {
	        cout << "failure" << endl;
	        return;
	    }

	    if (json!="") cout << "Opening " << json << "...";
	    ifstream fj(json.Data(),ios::in);
	    if (fj.is_open()) cout << "ok" << endl;
	    else if (json!="") {
	        cout << "failure" << endl;
	        return;
	    }

	    set<int> hiruns;
	    hiruns.insert(199703); // part
	    hiruns.insert(200190); // part
	    hiruns.insert(203830);
	    hiruns.insert(203832);
	    hiruns.insert(203833);
	    hiruns.insert(203834);
	    hiruns.insert(203835); // part
	    hiruns.insert(208509); // part

	    // Load list of good LS from re-reco JSON
	    set<pair<int, int> > goodls;
	    if (fj.is_open()) {
	        int run, ls1, ls2;
	        while (fj >> run >> ls1 >> ls2) {

	            for (int i = ls1; i != ls2+1; ++i) {
	                goodls.insert(make_pair<int,int>(int(run), int(i)));
	            }
	        }
	    }

	    // Read pixel lumi information from file
	    if (f.is_open()) {
	        int run, ls, cnt(0), cntMax(-1);
	        double lum, xsavg, xsrms;
	        while ( f >> run >> ls >> lum >> xsrms >> xsavg && ++cnt!=cntMax) {

	            if (json=="" || goodls.find(make_pair<int,int>(int(run),int(ls)))!=goodls.end()) {

	                double mu = xsavg * minbXsec;
	                double murms = xsrms * minbXsec;

	                fMupx_[run][ls] = lumiInfo(lum, mu, murms);
	            }
	        }
	    }


	    // Read HF lumi information from file
	    if (f2.is_open()) {

	        int run, ls, cnt(0), cntMax(-1);
	        double lum, xsavg, xsrms;
	        while ( f2 >> run >> ls >> lum >> xsrms >> xsavg && ++cnt!=cntMax) {

	            if (json=="" || goodls.find(make_pair<int,int>(int(run),int(ls)))!=goodls.end()) {

	                double mu = xsavg * minbXsec;
	                double murms = xsrms * minbXsec;

	                fMuhf_[run][ls] = lumiInfo(lum, mu, murms);
	            }
	        }
	    }
	}

	inline double getPxLumi( int run, int ls){ return fMupx_[run][ls].lum; }
	inline double getHFLumi( int run, int ls){ return fMuhf_[run][ls].lum; }
	inline double getMuPx(   int run, int ls){ return fMupx_[run][ls].muavg; }
	inline double getMuRMSPx(int run, int ls){ return fMupx_[run][ls].murms; }
	inline double getMuHF(   int run, int ls){ return fMuhf_[run][ls].muavg; }
	inline double getMuRMSHF(int run, int ls){ return fMuhf_[run][ls].murms; }

	~PileUpJSONParser()
	{
	}

	private:
	map<int, map<int, lumiInfo> > fMupx_;
	map<int, map<int, lumiInfo> > fMuhf_;

   };

#endif
