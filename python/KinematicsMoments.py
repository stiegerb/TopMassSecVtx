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

        #book the vectors/matrices to store the final results
        self.avgX=ROOT.TVectorT('float')(self.maxMomentToReport*self.nObs)
        self.sigmaX=ROOT.TVectorT('float')(self.maxMomentToReport*self.nObs)
        self.avgXY=ROOT.TMatrixT('float')(self.maxMomentToReport*self.nObs,self.maxMomentToReport*self.nObs)
        self.cXY=ROOT.TMatrixT('float')(self.maxMomentToReport*self.nObs,self.maxMomentToReport*self.nObs)
            
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
                ok_i=wgt*ROOT.TMath.Power(val_i,xbin-1)

                ctr_j=0
                for obs_j in observables:

                    val_j=observables[obs_j]
                    ctr_j+=1
                    if ctr_j<ctr_i: continue
                    
                    for ybin in xrange(1,self.maxMoment+1):

                        baseYbin=(ctr_j-1)*(self.maxMoment)
                        ok_j=wgt*ROOT.TMath.Power(val_j,ybin-1)

                        #symmetric matrix
                        self.ObsCorrHisto.Fill(baseXbin+xbin-1,baseYbin+ybin-1,ok_i*ok_j)
                        if ctr_i!=ctr_j:
                            self.ObsCorrHisto.Fill(baseYbin+ybin-1,baseXbin+xbin-1,ok_i*ok_j)
                        

    def finalize(self,report=False):

        if self.N==0: return

        avgX0=self.ObsCorrHisto.GetBinContent(1,1)

        for iobs in xrange(0,self.nObs):

            baseXbin=iobs*self.maxMoment+1
            
            for xbin in xrange(2,self.maxMoment+1):

                #compute average and standard deviation for each observable
                xmomOrder=xbin-1
                if xmomOrder>self.maxMomentToReport: continue
                xxbin=2*xbin-1
                idx=iobs*self.maxMomentToReport+(xbin-2)

                self.avgX[idx]=self.ObsCorrHisto.GetBinContent(baseXbin+xbin-1,baseXbin)/avgX0
                avgXX=self.ObsCorrHisto.GetBinContent(baseXbin+xxbin-1,baseXbin)/avgX0
                sigma2=avgXX-self.avgX[idx]**2
                self.sigmaX[idx]=ROOT.TMath.Sqrt(sigma2) if sigma2>0 else -ROOT.TMath.Sqrt(-sigma2)
            
                #compute the cross average and correlations between observables
                for jobs in xrange(0,self.nObs):
                    baseYbin=jobs*self.maxMoment+1
                    for ybin in xrange(2,self.maxMoment+1):
                        ymomOrder=ybin-1
                        if ymomOrder>self.maxMomentToReport: continue

                        #xlab=self.ObsCorrHisto.GetXaxis().GetBinLabel(baseXbin+xbin-1)
                        #ylab=self.ObsCorrHisto.GetYaxis().GetBinLabel(baseYbin+ybin-1)
                        
                        idy=jobs*self.maxMomentToReport+(ybin-2)
                        self.avgXY[idx][idy]=self.ObsCorrHisto.GetBinContent(baseXbin+xbin-1,baseYbin+ybin-1)/avgX0
                        
                        diff=self.avgXY[idx][idy]-self.avgX[idx]*self.avgX[idy]
                        sxsy=self.sigmaX[idx]*self.sigmaX[idy]
                        self.cXY[idx][idy]=diff/sxsy if sxsy!=0 else 0

        if report is True:
            print '[Average for observables]'
            self.avgX.Print('v')
            print '[Standard deviation for observables]'
            self.sigmaX.Print('v')
            print '[Average for crossed observables]'
            self.avgXY.Print('v')
            print '[Correlation for crossed observables]'
            self.cXY.Print('v')
        
    def save(self,outF):
        #write relevant objects to a sub-directory of the file
        outDir=outF.mkdir(self.name)
        outDir.cd()
        self.avgX.Write('avgX')
        self.sigmaX.Write('sigmaX')
        self.avgXY.Write('avgXY')
        self.cXY.Write('cXY')
        self.ObsCorrHisto.Write()
        outF.cd()
