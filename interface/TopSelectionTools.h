#ifndef _topseltools_h_
#define _topseltools_h_

#include "UserCode/TopMassSecVtx/interface/DataEventSummaryHandler.h"
#include "UserCode/TopMassSecVtx/interface/MuScleFitCorrector.h"

namespace top
{

//
// PARTICLE SELECTORS
//

//sets the selection flags on the electron
data::PhysicsObject_t getTopSelectionTaggedElectron(data::PhysicsObject_t ele,float rho,bool useAntiID=false)
{
    // Kinematic cuts
    float sceta = ele.getVal("sceta");
    bool isInEB2EE    ( fabs(sceta) > 1.4442 && fabs(sceta) < 1.5660 );
    bool passLLkin    ( ele.pt()>20 && fabs(ele.eta()) < 2.5 && !isInEB2EE);
    bool passLJkin    ( ele.pt()>33 && fabs(ele.eta()) < 2.1 && !isInEB2EE);
    bool passLJvetokin( ele.pt()>20 && fabs(ele.eta()) < 2.5 && !isInEB2EE);

    //id
    bool passIdBaseQualityCuts(true);
    if( ele.getFlag("isconv") )              passIdBaseQualityCuts=false;
    if( fabs(ele.getVal("tk_d0"))>0.04 )     passIdBaseQualityCuts=false;
    if( ele.getVal("tk_lostInnerHits") > 0 ) passIdBaseQualityCuts=false;
    if( fabs(ele.getVal("tk_dz"))>0.5)       passIdBaseQualityCuts=false;
    bool passLLid(     ele.getVal("mvatrig")>0.5 && passIdBaseQualityCuts);
    bool passLJid(     ele.getVal("mvatrig")>0.5 && passIdBaseQualityCuts && fabs(ele.getVal("tk_d0"))<0.02);
    bool passLJvetoid( ele.getVal("mvatrig")>0 );

    // Isolation
    Float_t gIso = ele.getVal("gIso03");
    Float_t chIso = ele.getVal("chIso03");
    Float_t puchIso = ele.getVal("puchIso03");
    Float_t nhIso = ele.getVal("nhIso03");
    float relIso = (TMath::Max(Float_t(nhIso+gIso-rho*utils::cmssw::getEffectiveArea(11,sceta,3)),Float_t(0.))+chIso)/ele.pt();
    bool passLLiso( relIso < 0.15 );
    float relIsoDeltaBeta = (TMath::Max(Float_t(nhIso+gIso-0.5*puchIso),Float_t(0.))+chIso)/ele.pt();
    bool passLJiso( relIsoDeltaBeta < 0.1 );
    bool passLJvetoiso( relIsoDeltaBeta < 0.15 );
    bool passLAntiIso(  relIsoDeltaBeta > 0.20 && relIsoDeltaBeta<1.0 );

    //set the flags
    ele.setVal("reliso",relIso);
    ele.setFlag("passLL",      (passLLkin     && passLLid     && passLLiso));
    ele.setFlag("passLJ",      (passLJkin     && passLJid     && passLJiso));
    ele.setFlag("passLJveto",  (passLJvetokin && passLJvetoid && passLJvetoiso));
    if(useAntiID)
      ele.setFlag("passLAntiIso",(passLLkin     && !passLLid     && passLLiso));
    else
      ele.setFlag("passLAntiIso",(passLLkin     && passLLid     && passLAntiIso));
    
    return ele;
}

//sets the selection flags on the muon
data::PhysicsObject_t getTopSelectionTaggedMuon(data::PhysicsObject_t mu, MuScleFitCorrector *fMuCor, float isMC)
{
    // Muon energy scale and uncertainties
    Int_t id = mu.get("id");
    if( fMuCor ) {
        TLorentzVector p4(mu.px(),mu.py(),mu.pz(),mu.energy());
        fMuCor->applyPtCorrection(p4 , id<0 ? -1 : 1 );
        if( isMC ) fMuCor->applyPtSmearing(p4, id<0 ? -1 : 1, false);
        mu.SetPxPyPzE(p4.Px(),p4.Py(),p4.Pz(),p4.E());
    }

    // Kinematic cuts
    bool passLLkin(     mu.pt()>20 && fabs(mu.eta())<2.4 );
    bool passLJkin(     mu.pt()>26 && fabs(mu.eta())<2.1 );
    bool passLJvetokin( mu.pt()>20 && fabs(mu.eta())<2.4 );

    // ID
    Int_t idbits = mu.get("idbits");
    bool isPF((idbits >> 7) & 0x1);
    bool passLLid(     ((idbits >> 10) & 0x1) && isPF );
    bool passLJid(     ((idbits >> 10) & 0x1) && isPF );
    bool passLJvetoid( ((idbits >> 10) & 0x1) && isPF );

    // Isolation
    Float_t gIso = mu.getVal("gIso04");
    Float_t chIso = mu.getVal("chIso04");
    Float_t puchIso = mu.getVal("puchIso04");
    Float_t nhIso = mu.getVal("nhIso04");
    Float_t relIso = ( TMath::Max(nhIso+gIso-0.5*puchIso,0.)+chIso ) / mu.pt();
    bool passLLiso(     relIso < 0.12 );
    bool passLJiso(     relIso < 0.12 );
    bool passLJvetoiso( relIso < 0.12 );
    bool passLAntiIso(  relIso > 0.20 && relIso<1.0);

    //set the flags
    mu.setVal("reliso",relIso);
    mu.setFlag("passLL",    (passLLkin     && passLLid     && passLLiso));
    mu.setFlag("passLJ",    (passLJkin     && passLJid     && passLJiso));
    mu.setFlag("passLJveto",(passLJvetokin && passLJvetoid && passLJvetoiso));
    mu.setFlag("passLAntiIso",(passLLkin   && passLLid     && passLAntiIso));

    return mu;
}

//
data::PhysicsObjectCollection_t selectLeptons(data::PhysicsObjectCollection_t &leptons, MuScleFitCorrector *fMuCor, float rho, bool isMC)
{
    data::PhysicsObjectCollection_t selLeptons;
    for(size_t ilep=0; ilep<leptons.size(); ilep++) {
        Int_t id=leptons[ilep].get("id");
        data::PhysicsObject_t selLepton(abs(id)==11 ?
                                        getTopSelectionTaggedElectron(leptons[ilep], rho) :
                                        getTopSelectionTaggedMuon    (leptons[ilep], fMuCor, isMC) );
        if( !selLepton.getFlag("passLL") &&
        	!selLepton.getFlag("passLJ") &&
            !selLepton.getFlag("passLJveto") &&
            !selLepton.getFlag("passLAntiIso")) continue;
        selLeptons.push_back(selLepton);
    }

    sort(selLeptons.begin(), selLeptons.end(), data::PhysicsObject_t::sortByPt);

    return selLeptons;
}

//
data::PhysicsObject_t getTopSelectionTaggedJet(data::PhysicsObject_t jet, data::PhysicsObjectCollection_t &leptons,float minpt, float maxeta)
{
    // kin cuts
    bool passKin(true);
    if( jet.pt() < minpt )         passKin=false;
    if( fabs(jet.eta()) > maxeta ) passKin=false;

    //cross-clean with selected leptons
    double minDRlj(9999.);
    for( size_t ilep=0; ilep<leptons.size(); ilep++ )
    {
        if( !(leptons[ilep].getFlag("passLJ")) && !(leptons[ilep].getFlag("passLL")) ) continue;
        minDRlj = TMath::Min( minDRlj, deltaR(jet, leptons[ilep]) );
    }

    // Require to pass the loose id
    Int_t idbits = jet.get("idbits");
    bool passPFloose( ((idbits>>0) & 0x1) );

    jet.setFlag("passGoodJet", (passKin && minDRlj>0.4 && passPFloose) );


    return jet;
}

//select jets
data::PhysicsObjectCollection_t selectJets(data::PhysicsObjectCollection_t &jets, data::PhysicsObjectCollection_t &leptons)
{
    data::PhysicsObjectCollection_t selJets;
    for(size_t ijet=0; ijet<jets.size(); ijet++)
    {
        data::PhysicsObject_t selJet = getTopSelectionTaggedJet(jets[ijet], leptons, 25., 5.0);

        if(!selJet.getFlag("passGoodJet")) continue;

        //here is a trick just to get the leading lxy jet first
        const data::PhysicsObject_t &svx=selJet.getObject("svx");
        selJet.setVal("lxy",svx.vals.find("lxy")->second);
        selJets.push_back(selJet);
    }

    sort(selJets.begin(), selJets.end(), data::PhysicsObject_t::sortByPt);

    return selJets;
}

//select photons
data::PhysicsObjectCollection_t selectPhotons(data::PhysicsObjectCollection_t &photons, float minPt, float rho)
{
    data::PhysicsObjectCollection_t selPhotons;
    for(size_t ipho=0; ipho<photons.size(); ipho++)
    {
        double pt=photons[ipho].pt();
        double eta=photons[ipho].getVal("sceta");

        //if systematics are active loosen the selection to the medium working point
        Int_t idbits( photons[ipho].get("id") );
        bool hasTightPhotonId( (idbits >> 2 ) & 0x1 );
        double gIso    = photons[ipho].getVal("gIso03");
        double gArea   = utils::cmssw::getEffectiveArea(22,eta,3,"gIso");
        double chIso   = photons[ipho].getVal("chIso03");
        double chArea  = utils::cmssw::getEffectiveArea(22,eta,3,"chIso");
        double nhIso   = photons[ipho].getVal("nhIso03");
        double nhArea  = utils::cmssw::getEffectiveArea(22,eta,3,"nhIso");

        //select the photon
        if(pt<minPt || fabs(eta)>1.4442 ) continue;
        bool passId(true);
        if( photons[ipho].getVal("r9")<0.9 ) passId=false;
        if(!hasTightPhotonId) passId=false;
        if(!passId) continue;
        bool passIso(true);
        passIso &= (TMath::Max(chIso-chArea*rho,0.0) < 0.7);
        passIso &= (TMath::Max(nhIso-nhArea*rho,0.0) < 0.4+0.04*pt);
        passIso &= (TMath::Max(gIso-gArea*rho,  0.0) < 0.5+0.005*pt);
        if(!passIso) continue;
        selPhotons.push_back(photons[ipho]);
    }

    return selPhotons;
}

}

#endif
