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


    def save(self,outF):
        #write relevant objects to a sub-directory of the file
        outDir=outF.mkdir(self.name)
        outDir.cd()
        self.ObsCorrHisto.Write()
        outF.cd()

                        
"""
analyze correlation histogram
"""
def analyzeCorrelationOfMoments(ObsCorrHisto,nObs,maxMomentToReport,report=False):

    avgX0=ObsCorrHisto.GetBinContent(1,1)

    if avgX0==0: return

    #book the vectors/matrices to store the final results
    avgX=ROOT.TVectorT('float')(maxMomentToReport*nObs)
    sigmaX=ROOT.TVectorT('float')(maxMomentToReport*nObs)
    avgXY=ROOT.TMatrixT('float')(maxMomentToReport*nObs,maxMomentToReport*nObs)
    cXY=ROOT.TMatrixT('float')(maxMomentToReport*nObs,maxMomentToReport*nObs)

    maxMoment=ObsCorrHisto.GetNbinsX()/nObs
    for iobs in xrange(0,nObs):

        baseXbin=iobs*maxMoment+1
            
        for xbin in xrange(2,maxMoment+1):

            #compute average and standard deviation for each observable
            xmomOrder=xbin-1
            if xmomOrder>maxMomentToReport: continue
            xxbin=2*xbin-1
            idx=iobs*maxMomentToReport+(xbin-2)

            avgX[idx]=ObsCorrHisto.GetBinContent(baseXbin+xbin-1,baseXbin)/avgX0
            avgXX=ObsCorrHisto.GetBinContent(baseXbin+xxbin-1,baseXbin)/avgX0
            sigma2=avgXX-avgX[idx]**2
            sigmaX[idx]=ROOT.TMath.Sqrt(sigma2) if sigma2>0 else -ROOT.TMath.Sqrt(-sigma2)
            
            #compute the cross average and correlations between observables
            for jobs in xrange(0,nObs):
                baseYbin=jobs*maxMoment+1
                for ybin in xrange(2,maxMoment+1):
                    ymomOrder=ybin-1
                    if ymomOrder>maxMomentToReport: continue

                    #xlab=ObsCorrHisto.GetXaxis().GetBinLabel(baseXbin+xbin-1)
                    #ylab=ObsCorrHisto.GetYaxis().GetBinLabel(baseYbin+ybin-1)
                        
                    idy=jobs*maxMomentToReport+(ybin-2)
                    avgXY[idx][idy]=ObsCorrHisto.GetBinContent(baseXbin+xbin-1,baseYbin+ybin-1)/avgX0
                        
                    diff=avgXY[idx][idy]-avgX[idx]*avgX[idy]
                    sxsy=sigmaX[idx]*sigmaX[idy]
                    cXY[idx][idy]=diff/sxsy if sxsy!=0 else 0

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
