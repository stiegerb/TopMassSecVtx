#ifndef _roofit_utils_h_
#define _roofit_utils_h_

#include <map>
#include <string>
#include "RooDataHist.h"

class MappedRooDataHist
{
 public:
  MappedRooDataHist() {}
  inline void add(std::string cat, RooDataHist *h) { myMap_[cat]=h; }
  inline std::map<std::string, RooDataHist *> &get() { return myMap_; }
  inline std::vector<std::string> getCategories()
  {
    std::vector<std::string> toRet;
    for(std::map<std::string,RooDataHist *>::iterator it=myMap_.begin();
	it!=myMap_.end();
	it++)
      {
	toRet.push_back(it->first);
      }
    return toRet;
  }
 private:
  std::map<std::string,RooDataHist *> myMap_;
};

//
void shushRooFit()
{
  using namespace RooFit;

  RooMsgService::instance().setSilentMode(true);
  RooMsgService::instance().getStream(0).removeTopic(Minimization);
  RooMsgService::instance().getStream(1).removeTopic(Minimization);
  RooMsgService::instance().getStream(1).removeTopic(ObjectHandling);
  RooMsgService::instance().getStream(1).removeTopic(DataHandling);
  RooMsgService::instance().getStream(1).removeTopic(Fitting);
  RooMsgService::instance().getStream(1).removeTopic(Plotting);
  RooMsgService::instance().getStream(0).removeTopic(InputArguments);
  RooMsgService::instance().getStream(1).removeTopic(InputArguments);
  RooMsgService::instance().getStream(0).removeTopic(Eval);
  RooMsgService::instance().getStream(1).removeTopic(Eval);
  RooMsgService::instance().getStream(1).removeTopic(Integration);
  RooMsgService::instance().getStream(1).removeTopic(NumIntegration);
  RooMsgService::instance().getStream(1).removeTopic(NumIntegration);
}

#endif
