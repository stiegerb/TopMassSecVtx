#!/usr/bin/env python

import math
import ROOT
from ROOT import THStack, TLatex
from ROOT import TCanvas, TPad, TLegend

class Plot:
    """
    A wrapper to store data and MC histograms for comparison
    """

    def __init__(self,name):
        self.name = name
        self.mc = []
        self.data = None
        self.garbageList = []

    def info(self):
        print self.name
        print len(self.mc),' mc processes', ' data=', self.data

    def add(self, h, title, color, isData):
        self.garbageList.append(h)
        h.SetTitle(title)

        if isData:
            h.SetMarkerStyle(20)
            h.SetMarkerColor(color)
            h.SetLineColor(color)
            h.SetLineWidth(2)
            h.SetFillColor(0)
            h.SetFillStyle(0)
            self.data = h
        else:
            h.SetMarkerStyle(1)
            h.SetMarkerColor(color)
            h.SetLineColor(color)
            h.SetLineWidth(1)
            h.SetFillColor(color)
            h.SetFillStyle(1001)
            self.mc.append(h)

    def reset(self):
        for o in self.garbageList: o.Delete()

    def showTable(self, outDir, firstBin=1, lastBin=-1):

        if firstBin<1: firstBin = 1

        f = open(outDir+'/'+self.name+'.dat','w')
        f.write('------------------------------------------\n')
        f.write("Process".ljust(20),)
        f.write("Events\n")
        f.write('------------------------------------------\n')

        tot = 0
        err = 0
        for h in self.mc:
            maxBins = h.GetXaxis().GetNbins()
            if lastBin<1 : lastBin = maxBins
            if lastBin>maxBins : lastBin = maxBins
            if firstBin>maxBins: firstBin = maxBins
            ierr = ROOT.Double(0)
            itot = h.IntegralAndError(firstBin,lastBin,ierr)
            pname = h.GetTitle()
            f.write(pname.ljust(20),)
            f.write('%3.3f +/- %3.3f\n'%(itot,ierr))
            tot = tot+itot
            err = err+ierr*ierr
        f.write('------------------------------------------\n')
        f.write('Total'.ljust(20),)
        f.write('%3.3f +/- %3.3f\n'%(tot,math.sqrt(err)))

        if self.data is None : return
        f.write('------------------------------------------\n')
        f.write('Data'.ljust(20),)
        f.write('%d\n'%(self.data.Integral(firstBin,lastBin)))
        f.close()


    def show(self, outDir):
        canvas = TCanvas('c_'+self.name,'C',800,800)
        canvas.cd()
        t1 = TPad("t1","t1", 0.0, 0.20, 1.0, 1.0)
        t1.Draw()
        t1.cd()
        self.garbageList.append(t1)

        frame = None
        # leg = TLegend(0.15,0.9,0.9,0.95)
        leg = TLegend(0.65,0.75,0.92,0.89)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetTextFont(42)
        leg.SetTextSize(0.03)
        nlegCols = 0

        maxY = 1.0
        if self.data is not None:
            leg.AddEntry( self.data, self.data.GetTitle(),'p')
            frame = self.data.Clone('frame')
            self.garbageList.append(frame)
            maxY = self.data.GetMaximum()*1.1
            frame.Reset('ICE')

        totalMC = None
        stack = THStack('mc','mc')
        for h in self.mc :
            stack.Add(h,'hist')
            leg.AddEntry(h,h.GetTitle(),'f')
            nlegCols = nlegCols+1
            if totalMC is None:
                totalMC = h.Clone('totalmc')
                self.garbageList.append(totalMC)
                totalMC.SetDirectory(0)
            else:
                totalMC.Add(h)

        if totalMC is not None:
            maxY = max(totalMC.GetMaximum(),maxY)
            if frame is None:
                frame = totalMC.Clone('frame')
                frame.Reset('ICE')
                self.garbageList.append(frame)

        if self.data is not None: nlegCols = nlegCols+1
        if nlegCols == 0:
            print '%s is empty'%self.name
            return

        frame.GetYaxis().SetRangeUser(1e-2,1.2*maxY)
        frame.SetDirectory(0)
        frame.Draw()
        frame.GetYaxis().SetTitleOffset(1.6)
        stack.Draw('hist same')
        if self.data is not None: self.data.Draw('P same')
        # leg.SetNColumns(nlegCols)
        leg.SetNColumns(2)
        leg.Draw()
        ## Draw CMS Preliminary label
        tlat = TLatex()
        tlat.SetNDC()
        tlat.SetTextFont(62)
        tlat.SetTextSize(0.04)
        tlat.SetTextAlign(31)
        prelim_text = 'CMS Preliminary, #sqrt{s} = 8 TeV'
        tlat.DrawLatex(0.92, 0.92, prelim_text)
        if totalMC is None or self.data is None:
            t1.SetPad(0,0,1,1)
        else :
            canvas.cd()
            t2 = TPad("t2","t2", 0.0, 0.0, 1.0, 0.2)
            self.garbageList.append(t2)
            t2.SetTopMargin(0)
            t2.SetBottomMargin(0.2)
            t2.Draw()
            t2.cd()
            ratio = self.data.Clone('ratio')
            self.garbageList.append(ratio)
            ratio.Divide(totalMC)
            ratio.SetDirectory(0)
            ratio.Draw('e1')
            ratio.GetYaxis().SetRangeUser(0.62,1.38)
            ratio.GetYaxis().SetTitle('Data/#SigmaBkg')
            ratio.GetXaxis().SetTitle('')
            ratio.GetYaxis().SetNdivisions(5)
            ratio.GetYaxis().SetTitleOffset(0.5)
            ratio.GetYaxis().SetLabelSize(0.12)
            ratio.GetYaxis().SetTitleSize(0.12)
            ratio.GetXaxis().SetLabelSize(0.12)
            ratio.GetXaxis().SetTitleSize(0.12)

        canvas.cd()
        canvas.Modified()
        canvas.Update()
        canvas.SaveAs(outDir+'/'+self.name+'.pdf')
        # canvas.SaveAs(outDir+'/'+self.name+'.png')

"""
Loads TDR style
"""
def customROOTstyle() :
    ROOT.gSystem.Load("libUserCodellvv_fwk.so")
    ROOT.setTDRStyle()

