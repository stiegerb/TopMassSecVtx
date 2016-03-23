#!/usr/bin/env python

import ROOT

"""         
Implements the method proposed to measure the moments and correlations of different variables                                   
from http://arxiv.org/pdf/1407.2763.pdf (App. A and B)                             
"""
class KinematicsMoments:

    def __init__(self, observables,name='',maxMoment=3):

        self.N=0
        self.maxMomentToReport=maxMoment
        self.maxMoment=maxMoment*2+1        
        self.nObs=len(observables)
        self.name=name

        #book an histogram to store the weighted sums
        self.ObsCorrHisto=ROOT.TH2D('obscorr'+self.name,'obscorr%s;Observable;Observable'%self.name,
                                    self.nObs*(self.maxMoment),0,self.nObs*(self.maxMoment),
                                    self.nObs*(self.maxMoment),0,self.nObs*(self.maxMoment))
        iobs=0
        for obs in observables:
            baseXbin=iobs*self.maxMoment
            for xbin in xrange(baseXbin,baseXbin+self.maxMoment):
                self.ObsCorrHisto.GetXaxis().SetBinLabel(xbin+1,'#splitline{#scale[0.6]{%s}}{O^{%d}}'%(obs,xbin-baseXbin))
                self.ObsCorrHisto.GetYaxis().SetBinLabel(xbin+1,'#splitline{#scale[0.6]{%s}}{O^{%d}}'%(obs,xbin-baseXbin))
            iobs+=1
        self.ObsCorrHisto.Sumw2()
        self.ObsCorrHisto.SetDirectory(0)

            
    def measure(self,observables,wgt):

        #increment event counter
        self.N+=1

        # loop over the observables and fill the histogram with the weighted sum
        # of the momenta of the observables
        ctr_i=0
        for obs_i in observables:
            
            val_i=observables[obs_i]
            ctr_i+=1

            for xbin in xrange(1,self.maxMoment+1):

                baseXbin=(ctr_i-1)*(self.maxMoment)
                ok_i=wgt*ROOT.TMath.Power(val_i,xbin-1) if val_i else None

                ctr_j=0
                for obs_j in observables:

                    val_j=observables[obs_j]
                    ctr_j+=1
                    if ctr_j<ctr_i: continue

                    for ybin in xrange(1,self.maxMoment+1):

                        baseYbin=(ctr_j-1)*(self.maxMoment)
                        ok_j=wgt*ROOT.TMath.Power(val_j,ybin-1) if val_j else None

                        if ok_i is None or ok_j is None : continue

                        #symmetric matrix
                        self.ObsCorrHisto.Fill(baseXbin+xbin-1,baseYbin+ybin-1,ok_i*ok_j)
                        if ctr_i!=ctr_j:
                            self.ObsCorrHisto.Fill(baseYbin+ybin-1,baseXbin+xbin-1,ok_i*ok_j)


    def save(self,outF):
        #write relevant objects to a sub-directory of the file
        outDir=outF.mkdir(self.name)
        outDir.cd()
        self.ObsCorrHisto.Write()
        outF.cd()

"""
define bins of interest returning a list of pairs [bin_for_mean,bin_for_std]
"""
def defineBinsOfInterest(ObsCorrHisto,OBSERVABLES):

    binsOfInterest=[]

    for obsTitle,obsLabels in OBSERVABLES:             
        obsBins=[obsTitle,0,0,0]
        for xbin in xrange(1,ObsCorrHisto.GetNbinsX()+1):
            label=ObsCorrHisto.GetXaxis().GetBinLabel(xbin)
            if label==obsLabels[0] : obsBins[1]=xbin
            if label==obsLabels[1] : obsBins[2]=xbin
            if label==obsLabels[2] : obsBins[3]=xbin
        if obsBins[1]==0 or obsBins[2]==0 or obsBins[3]==0 : continue
        binsOfInterest.append(obsBins)

    return binsOfInterest
            

                        
"""
analyze correlation histogram
"""
def analyzeCorrelationOfMoments(ObsCorrHisto,binsOfInterest,report=False):

    avgX0=ObsCorrHisto.GetBinContent(1,1)
    
    if avgX0==0: return

    #book the vectors/matrices to store the final results
    avgX=ROOT.TVectorT('float')(len(binsOfInterest))
    sigmaX=ROOT.TVectorT('float')(len(binsOfInterest))
    avgXY=ROOT.TMatrixT('float')(len(binsOfInterest),len(binsOfInterest))
    cXY=ROOT.TMatrixT('float')(len(binsOfInterest),len(binsOfInterest))

    for ix in xrange(0,len(binsOfInterest)):
        xbin,xxbin=binsOfInterest[ix]

        #print ObsCorrHisto.GetXaxis().GetBinLabel(xbin),ObsCorrHisto.GetXaxis().GetBinLabel(xbin+1)
        avgX[ix]=ObsCorrHisto.GetBinContent(xbin,xbin-1)/avgX0
        avgXX=ObsCorrHisto.GetBinContent(xxbin,xbin-1)/avgX0
        sigma2=avgXX-avgX[ix]**2
        sigmaX[ix]=ROOT.TMath.Sqrt(sigma2) if sigma2>0 else -ROOT.TMath.Sqrt(-sigma2)
            
        #compute the cross average and correlations between observables
        for iy in xrange(ix+1,len(binsOfInterest)):
            ybin,_=binsOfInterest[iy]

            #print ObsCorrHisto.GetXaxis().GetBinLabel(xbin),ObsCorrHisto.GetXaxis().GetBinLabel(ybin)
            avgXY[ix][iy]=ObsCorrHisto.GetBinContent(xbin,ybin)/avgX0
            diff=avgXY[ix][iy]-avgX[ix]*avgX[iy]
            sxsy=sigmaX[ix]*sigmaX[iy]
            cXY[ix][iy]=diff/sxsy if sxsy!=0 else 0

    if report is True:
        print '[Average for observables]'
        avgX.Print('v')
        print '[Standard deviation for observables]'
        sigmaX.Print('v')
        print '[Average for crossed observables]'
        avgXY.Print('v')
        print '[Correlation for crossed observables]'
        cXY.Print('v')

    return avgX,sigmaX,cXY,avgX0        
