#!/usr/bin/env python
import os
import math
from array import array
import ROOT
from sys import stdout
from ROOT import THStack, TLatex
from ROOT import TCanvas, TPad, TLegend
from UserCode.TopMassSecVtx.CMS_lumi import *
from UserCode.TopMassSecVtx.rounding import *


class bcolors:
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKGREEN   = '\033[92m'
    YELLOW    = '\033[93m'
    RED       = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

def printProgress(step, total, customstr=''):
    stdout.write("\r%s[%3d %%]" % (customstr, 100*float(step+1)/float(total)) )
    stdout.flush()
    if step==total-1:
        stdout.write("\n")
        stdout.flush()

def getContours(h):
     contours      = array('d',[1,3.84])
     contourTitles = ['68% CL','95% CL']
     colors        = [2,9]
     styles        = [1,2]
     total=h.Integral()
     if total<=10 : return None

     #get contours
     h.SetContour(len(contours),contours)
     h.Draw('cont z list')
     conts = ROOT.gROOT.GetListOfSpecials().FindObject("contours");
     allGr=[]
     for cList in conts:
          for cGr in cList:
               cGr.SetFillStyle(0)
               cGr.SetFillColor(0);
               cGr.SetLineColor(colors[len(allGr)])
               cGr.SetLineStyle(styles[len(allGr)])
               cGr.SetLineWidth(4)
               cGr.SetLineWidth(2)
               cGr.SetTitle( contourTitles[icont] )
               allGr.append( cGr.Clone('cont_%d'%len(allGr) ) )
     return allGr


def getRatio(hist, reference):
    ratio = hist.Clone("%s_ratio"%hist.GetName())
    ratio.SetDirectory(0)
    ratio.SetLineColor(hist.GetLineColor())
    for xbin in xrange(1,reference.GetNbinsX()+1):
        ref = reference.GetBinContent(xbin)
        val = hist.GetBinContent(xbin)

        refE = reference.GetBinError(xbin)
        valE = hist.GetBinError(xbin)

        try:
            ratio.SetBinContent(xbin, val/ref)
            ratio.SetBinError(xbin, math.sqrt( (val*refE/(ref**2))**2 + (valE/ref)**2 ))
        except ZeroDivisionError:
            ratio.SetBinContent(xbin, 1.0)
            ratio.SetBinError(xbin, 0.0)

    return ratio

def setMaximums(histos, margin=1.1, setminimum=None):
    maxy = 0.
    for hist in histos:
        binmax = 0.
        for binx in xrange(1,hist.GetNbinsX()+1):
            binmax = max(binmax, hist.GetBinContent(binx))
        maxy = max(maxy,margin*binmax)
    for hist in histos: hist.SetMaximum(maxy)
    if setminimum is not None:
        for hist in histos: hist.SetMinimum(setminimum)

def customChi2(hist1, hist2):
    if hist1.GetNbinsX() != hist2.GetNbinsX():
        print "customChi2::Error ==> Histograms not compatible"
        return -1
    chi2 = 0
    for ibin in xrange(1,hist1.GetNbinsX()):
        binc1 = hist1.GetBinContent(ibin)
        binc2 = hist2.GetBinContent(ibin)
        chi2 += (binc1-binc2)**2
    return chi2

def redrawBorder(pad):
    # this little macro redraws the axis tick marks and the pad border lines.
    pad.Update()
    pad.RedrawAxis()
    l = ROOT.TLine()
    l.DrawLine(pad.GetUxmin(), pad.GetUymax(), pad.GetUxmax(), pad.GetUymax())
    l.DrawLine(pad.GetUxmax(), pad.GetUymin(), pad.GetUxmax(), pad.GetUymax())


class RatioPlot(object):
    """Wrapper class for making ratio plots"""

    def __init__(self, name):
        super(RatioPlot, self).__init__()
        self.name = name
        self.histos = []
        self.rebin = 1
        self.histsforratios = []
        self.legentries = []
        self.drawoptions = None
        self.markerstyles = []
        self.markersizes = []
        self.titlex = None
        self.titley = None
        self.reference = []
        self.normalized = True
        self.ratiotitle = None
        self._garbageList = []
        self.tag = None
        self.subtag = None
        self.tagpos = (0.85,0.85)
        self.subtagpos = (0.85,0.78)
        self.legpos = (0.60, 0.15)
        self.extratext = 'Simulation'
        self.plotformats = ['.pdf', '.png', '.C']
        self.canvassize = (800, 800) # default is 800,800, don't go below 600
        self.colors1 = [ ## rainbow ('gay flag')
            ROOT.kViolet-6,
            ROOT.kBlue+2,
            ROOT.kAzure-2,
            ROOT.kGreen+3,
            ROOT.kGreen-3,
            ROOT.kSpring-9,
            ROOT.kOrange+8,
            ROOT.kRed+1,
            ROOT.kRed+3,
        ]
        self.colors2 = [ ## reduced rainbow ('gay flag')
            # ROOT.kViolet-6,
            ROOT.kBlue+2,
            ROOT.kAzure-2,
            ROOT.kGreen+3,
            ROOT.kGreen-3,
            # ROOT.kSpring-9,
            ROOT.kOrange+8,
            ROOT.kRed+1,
            # ROOT.kRed+3,
        ]
        # self.colors = [ ## shades of blue
        #     ROOT.kViolet-7,
        #     ROOT.kViolet-6,
        #     ROOT.kViolet+4,
        #     ROOT.kViolet+9,
        #     ROOT.kBlue,
        #     ROOT.kBlue-7,
        #     ROOT.kAzure+1,
        #     ROOT.kAzure+8,
        # ]
        self.ratiorange = None

    def reset(self):
        for o in self._garbageList:
            try:
                o.Delete()
            except AttributeError:
                pass
            except Exception, e:
                print e
                raise e
        self.histos = []
        self.histsforratios = []
        self.legentries = []

    def add(self, hist, tag, includeInRatio=True):
        if hist.GetEntries() == 0:
            print "Skipping empty histogram", hist.GetName()
            return

        histtoadd = hist.Clone(hist.GetName())
        if self.rebin>1:
            histtoadd.Rebin(self.rebin)
        self.histos.append(histtoadd)
        if includeInRatio: self.histsforratios.append(histtoadd)
        self._garbageList.append(histtoadd)
        self.legentries.append(tag)

    def getChiSquares(self, rangex=None):
        if len(self.reference):
            reference = self.reference[0]
        else:
            reference = self.histos[0]
        chisquares = {}

        # make copies of the histograms
        histocopies = []
        for hist in self.histos:
            histocopies.append(hist.Clone("%s_copy" % hist.GetName()))
            reference = reference.Clone("%s_copy" % reference.GetName())

        for hist in histocopies:
            if rangex is not None:
                hist.GetXaxis().SetRangeUser(rangex[0], rangex[1])
                reference.GetXaxis().SetRangeUser(rangex[0], rangex[1])
                bin1 = hist.GetXaxis().FindBin(rangex[0])
                bin2 = hist.GetXaxis().FindBin(rangex[1])

                hist.Scale(1./hist.Integral(bin1, bin2))
                reference.Scale(1./reference.Integral(bin1, bin2))

            else:
                hist.Scale(1./hist.Integral())

        for legentry,hist in zip(self.legentries, histocopies):
            # chisquares[legentry] = hist.Chi2Test(reference,"WW CHI2/NDF")
            # chisquares[legentry] = hist.KolmogorovTest(reference,"")
            chisquares[legentry] = customChi2(hist, reference)

        return chisquares

    def saveRatios(self, outname, outdir, histnames=[]):
        if not len(self.ratios):
            print "RatioPlot::saveRatio only works after .show has been called!"
            return

        if len(histnames):
            assert(len(histnames) == len(self.ratios))
        else:
            histnames = [h.GetName() for h in self.ratios]

        if not len(set(histnames)) == len(histnames):
            print "RatioPlot >> WARNING Non-unique names for ratio histograms!"

        if not outname.endswith('.root'): outname += '.root'
        ofile = ROOT.TFile.Open(os.path.join(outdir,outname), "RECREATE")
        ofile.cd()
        for rathist,hname in zip(self.ratios,histnames):
            rathist.Write(hname)

        ofile.Write()
        ofile.Close()

        print "RatioPlot >> wrote ratio histograms to %s"%os.path.join(outdir,outname)
        return



    def show(self, outname, outdir):
        if not os.path.isdir(outdir):
            os.system('mkdir -p %s' % outdir)

        # Scaling with canvas size
        canv_scalex = 800./self.canvassize[0]
        canv_scaley = 800./self.canvassize[1]

        # Automatic coloring
        colors = self.colors1
        if len(self.histos) <= 6:
            colors = self.colors2
        # Custom coloring
        if hasattr(self, 'colors'):
            colors = self.colors

        for hist,color in zip(self.histos, colors):
            hist.SetLineColor(color)
            hist.SetMarkerColor(color)
            hist.SetLineWidth(2)

        # Marker styles
        for hist,mstyle,msize in zip(self.histos, self.markerstyles, self.markersizes):
            hist.SetMarkerStyle(mstyle)
            hist.SetMarkerSize(msize)

        # Draw options
        if not self.drawoptions:
            self.drawoptions = len(self.histos)*['hist']
        assert(len(self.drawoptions) == len(self.histos))

        if self.normalized:
            for hist in self.histos:
                hist.Scale(1./hist.Integral())

        setMaximums(self.histos, setminimum=0)

        tc = ROOT.TCanvas(outname, "ratioplots", 800, 800)
        # self._garbageList.append(tc)
        tc.cd()
        tc.SetCanvasSize(self.canvassize[0], self.canvassize[1])
        p2 = ROOT.TPad("pad2","pad2",0,0,1,0.31);
        self._garbageList.append(p2)
        p2.SetTopMargin(0);
        p2.SetBottomMargin(0.3);
        p2.SetLeftMargin(0.15)
        p2.SetRightMargin(0.03)
        p2.SetFillStyle(0);
        p2.Draw();
        p1 = ROOT.TPad("pad1","pad1",0,0.31,1,1);
        self._garbageList.append(p1)
        p1.SetBottomMargin(0);
        p1.SetLeftMargin(p2.GetLeftMargin())
        p1.SetRightMargin(p2.GetRightMargin())
        p1.Draw();
        p1.cd();

        # tl = ROOT.TLegend(0.66, 0.75-0.040*max(len(self.histos)-3,0), .89, .89)
        # tl = ROOT.TLegend(0.66, 0.15, .89, .30+0.040*max(len(self.histos)-3,0))
        tleg = ROOT.TLegend(self.legpos[0], self.legpos[1],
                            min(self.legpos[0]+0.30,0.89),
                            min(self.legpos[1]+0.15+canv_scaley*0.042*max(len(self.histos)-3,0), 0.89))
        self._garbageList.append(tleg)
        tleg.SetBorderSize(0)
        tleg.SetFillColor(0)
        tleg.SetFillStyle(0)
        tleg.SetShadowColor(0)
        tleg.SetTextFont(43)
        tleg.SetTextSize(20)
        if len(self.histos)>30 :
            tleg.SetTextSize(10)
            tleg.SetNColumns(3)

        mainframe = self.histos[0].Clone('mainframe')
        self._garbageList.append(mainframe)
        mainframe.Reset('ICE')
        mainframe.GetXaxis().SetTitleFont(43)
        mainframe.GetXaxis().SetLabelFont(43)
        mainframe.GetYaxis().SetTitleFont(43)
        mainframe.GetYaxis().SetLabelFont(43)

        if not self.titley:
            if self.normalized:
                mainframe.GetYaxis().SetTitle('a.u.')
            else:
                if "GeV" in mainframe.GetXaxis().GetTitle():
                    if mainframe.GetBinWidth(1) > 0.1:
                        ytit = "Events / %3.1f GeV" %mainframe.GetBinWidth(1)
                    elif mainframe.GetBinWidth(1) > 0.001:
                        ytit = "Events / %.0f MeV" % (mainframe.GetBinWidth(1)*1000)
                    else:
                        ytit = "Events / %.0f keV" % (mainframe.GetBinWidth(1)*1000000)
                else:
                    ytit = "Events / %3.1f" % h.GetBinWidth(1)
                mainframe.GetYaxis().SetTitle(ytit)
        else:
            mainframe.GetYaxis().SetTitle(self.titley)
        mainframe.GetYaxis().SetLabelSize(22)
        mainframe.GetYaxis().SetTitleSize(26)
        mainframe.GetYaxis().SetTitleOffset(2.0/canv_scalex)

        mainframe.GetXaxis().SetTitle('')
        mainframe.GetXaxis().SetLabelSize(0)
        mainframe.GetXaxis().SetTitleSize(0)
        mainframe.GetXaxis().SetTitleOffset(1.5/canv_scaley)
        mainframe.GetYaxis().SetNoExponent()
        mainframe.Draw()

        # self.histos[0].GetYaxis().SetTitle('a.u.')
        # self.histos[0].Draw("axis")
        for hist,legentry,dopt in zip(self.histos,self.legentries,self.drawoptions):
            if dopt=='hist':
                tleg.AddEntry(hist, legentry, 'l')
            else:
                tleg.AddEntry(hist, legentry, 'p')
        for hist,dopt in reversed(zip(self.histos,self.drawoptions)):
            hist.Draw("%s same"%dopt)

        tleg.Draw()

        tlat = TLatex()
        tlat.SetTextFont(43)
        tlat.SetNDC(1)
        if self.tag:
            tlat.SetTextAlign(33) # right aligned
            if self.tagpos[0] < 0.50:
                # left aligned if on the left side
                tlat.SetTextAlign(13)
            tlat.SetTextSize(22)
            tlat.DrawLatex(self.tagpos[0], self.tagpos[1], self.tag)
            # tlat.DrawLatex(0.85, 0.85, self.tag)
        if self.subtag:
            tlat.SetTextAlign(33) # right aligned
            if self.subtagpos[0] < 0.50:
                # left aligned if on the left side
                tlat.SetTextAlign(13)
            tlat.SetTextSize(20)
            tlat.DrawLatex(self.subtagpos[0], self.subtagpos[1], self.subtag)
            # tlat.DrawLatex(0.85, 0.78, self.subtag)

        CMS_lumi(pad=p1,iPeriod=2,iPosX=0,extraText=self.extratext)

        redrawBorder(p1)
        p2.cd()

        try:
            if not len(self.reference): # no reference given
                self.reference = len(self.histsforratios)*[self.histos[0]]
                # No rebinning needed, was already done when adding the histo

            elif len(self.reference) == 1: # only one reference given
                refhist = self.reference[0].Clone("%s_reference"%self.name)
                # Need to rebin since the ref histo is external
                refhist.Rebin(self.rebin)
                self.reference = len(self.histsforratios)*[refhist]
            else:
                self.reference = [h.Rebin(self.rebin) for h in self.reference[:]]

        except TypeError:
            # Backwards compatibility
            refhist = self.reference.Clone("%s_reference"%self.name)
            if refhist.GetNbinsX() != self.histos[0].GetNbinsX():
                refhist.Rebin(self.rebin)
            self.reference = len(self.histsforratios)*[refhist]

        assert(len(self.reference) == len(self.histsforratios))


        ratioframe = mainframe.Clone('ratioframe')
        self._garbageList.append(ratioframe)
        ratioframe.Reset('ICE')
        ratioframe.GetYaxis().SetRangeUser(0.50,1.50)
        if not self.ratiotitle:
            ratioframe.GetYaxis().SetTitle('Ratio')
        else:
            ratioframe.GetYaxis().SetTitle(self.ratiotitle)
        if not self.titlex:
            ratioframe.GetXaxis().SetTitle(self.histos[0].GetXaxis().GetTitle())
        else:
            ratioframe.GetXaxis().SetTitle(self.titlex)
        ratioframe.GetXaxis().SetLabelSize(22)
        ratioframe.GetXaxis().SetTitleSize(26)
        ratioframe.GetYaxis().SetNdivisions(5)
        ratioframe.GetYaxis().SetNoExponent()
        ratioframe.GetYaxis().SetTitleOffset(mainframe.GetYaxis().GetTitleOffset())
        ratioframe.GetXaxis().SetTitleOffset(3.0)
        ratioframe.Draw()

        ## Calculate Ratios
        self.ratios = []
        for hist,ref in zip(self.histsforratios,self.reference):
            if self.normalized:
                ref_norm = ref.Clone("%s_norm"%ref.GetName())
                ref_norm.Scale(1./ref_norm.Integral())
                self.ratios.append(getRatio(hist, ref_norm))
                self._garbageList.append(ref_norm)
            else:
                self.ratios.append(getRatio(hist, ref))
        if self.ratiorange:
            ratmin, ratmax = self.ratiorange
            for ratio in self.ratios:
                ratio.SetMinimum(ratmin)
                ratio.SetMaximum(ratmax)
                ratioframe.GetYaxis().SetRangeUser(ratmin, ratmax)

        else:
            setMaximums(self.ratios)

        line = ROOT.TLine(self.ratios[0].GetXaxis().GetXmin(), 1.0,
                          self.ratios[0].GetXaxis().GetXmax(), 1.0)
        line.SetLineColor(ROOT.kGray)
        # line.SetLineStyle(2)
        line.Draw()

        for ratio,dopt in reversed(zip(self.ratios,self.drawoptions)):
            ratio.Draw("%s same"%dopt)

        redrawBorder(p2)

        tc.cd()
        tc.Modified()
        tc.Update()
        for ext in self.plotformats:
            tc.SaveAs(os.path.join(outdir,"%s%s"%(outname,ext)))
        tc.Close()


class Plot(object):
    """
    A wrapper to store data and MC histograms for comparison
    """

    def __init__(self,name,usePoissonStatsForData=True):
        self.name = name
        self.usePoissonStatsForData=usePoissonStatsForData
        self.mc = []
        self.dataH = None
        self.data = None
        self._garbageList = []
        self.normalizedToData=False
        self.plotformats = ['pdf','png']
        self.savelog = False
        self.ratiorange = (0.62, 1.36)

    def info(self):
        print self.name
        print len(self.mc),' mc processes', ' data=', self.data

    def add(self, h, title, color, isData):
        self._garbageList.append(h)
        h.SetTitle(title)

        if "GeV" in h.GetXaxis().GetTitle():
            if h.GetBinWidth(1) > 0.1:
                h.GetYaxis().SetTitle("Events / %3.1f GeV" %h.GetBinWidth(1))
            elif h.GetBinWidth(1) > 0.001:
                h.GetYaxis().SetTitle("Events / %.0f MeV" %
                                                 (h.GetBinWidth(1)*1000))
            else:
                h.GetYaxis().SetTitle("Events / %.0f keV" %
                                                 (h.GetBinWidth(1)*1000000))
        else:
            h.GetYaxis().SetTitle("Events / %3.1f" % h.GetBinWidth(1))

        if isData:
            h.SetMarkerStyle(20)
            h.SetMarkerSize(1.4)
            h.SetMarkerColor(color)
            h.SetLineColor(ROOT.kBlack)
            h.SetLineWidth(2)
            h.SetFillColor(0)
            h.SetFillStyle(0)
            self.dataH = h
            if self.usePoissonStatsForData:
                self.data = convertToPoissonErrorGr(h)
        else:
            h.SetMarkerStyle(1)
            h.SetMarkerColor(color)
            h.SetLineColor(ROOT.kBlack)
            h.SetLineWidth(1)
            h.SetFillColor(color)
            h.SetFillStyle(1001)
            self.mc.append(h)

    def appendTo(self,outUrl):
        # If file does not exist it is created
        outF = ROOT.TFile.Open(outUrl,'UPDATE')
        if not outF.cd(self.name):
            outDir = outF.mkdir(self.name)
            outDir.cd()

        for m in self.mc :
            if m :
                m.Write(m.GetName(), ROOT.TObject.kOverwrite)
        if self.data :
            self.data.Write(self.data.GetName(), ROOT.TObject.kOverwrite)
        if self.dataH :
            self.dataH.Write(self.dataH.GetName(), ROOT.TObject.kOverwrite)
        outF.Close()

    def normToData(self):
        totalMC=0
        for m in self.mc:
            totalMC+=m.Integral()
        if totalMC==0 : return
        if self.dataH is None: return
        totalData=self.dataH.Integral()
        if totalData==0 : return
        scaleFactor=totalData/totalMC
        for m in self.mc:
            m.Scale(scaleFactor)
        self.normalizedToData=True

    def reset(self):
        self.normalizedToData=False
        for o in self._garbageList:
            try:
                o.Delete()
            except:
                pass

    def showTable(self, outDir, firstBin=1, lastBin=-1):
        if len(self.mc)==0:
            print '%s is empty' % self.name
            return

        if firstBin<1: firstBin = 1

        f = open(outDir+'/'+self.name+'.dat','w')
        f.write('------------------------------------------\n')
        f.write("Process".ljust(20),)
        f.write("Events after each cut\n")
        f.write('------------------------------------------\n')

        tot ={}
        err = {}
        f.write(' '.ljust(20),)
        try:
            for xbin in xrange(1,self.mc[0].GetXaxis().GetNbins()+1):
                pcut=self.mc[0].GetXaxis().GetBinLabel(xbin)
                f.write(pcut.ljust(40),)
                tot[xbin]=0
                err[xbin]=0
        except:
            pass
        f.write('\n')
        f.write('------------------------------------------\n')

        for h in self.mc:
            pname = h.GetTitle()
            f.write(pname.ljust(20),)

            for xbin in xrange(1,h.GetXaxis().GetNbins()+1):
                itot=h.GetBinContent(xbin)
                ierr=h.GetBinError(xbin)
                pval=' & %s'%toLatexRounded(itot,ierr)
                f.write(pval.ljust(40),)
                tot[xbin] = tot[xbin]+itot
                err[xbin] = err[xbin]+ierr*ierr
            f.write('\n')

        f.write('------------------------------------------\n')
        f.write('Total'.ljust(20),)
        for xbin in tot:
            pval=' & %s'%toLatexRounded(tot[xbin],math.sqrt(err[xbin]))
            f.write(pval.ljust(40),)
        f.write('\n')

        if self.dataH is None: return
        f.write('------------------------------------------\n')
        f.write('Data'.ljust(20),)
        for xbin in xrange(1,self.dataH.GetXaxis().GetNbins()+1):
            itot=self.dataH.GetBinContent(xbin)
            pval=' & %d'%itot
            f.write(pval.ljust(40))
        f.write('\n')
        f.write('------------------------------------------\n')
        f.close()

    def show(self, outDir):
        if len(self.mc)==0:
            print '%s has no MC!' % self.name
            return

        htype=self.mc[0].ClassName()
        if htype.find('TH2')>=0:
            print 'Skipping TH2'
            return

        ROOT.gStyle.SetOptTitle(0)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gROOT.SetBatch(1)

        canvas = TCanvas('c_'+self.name,'C',800,800)
        canvas.cd()
        t1 = TPad("t1","t1", 0.0, 0.20, 1.0, 1.0)
        t1.SetBottomMargin(0)
        t1.Draw()
        t1.cd()
        self._garbageList.append(t1)

        frame = None
        # Decide which backgrounds are visible
        maxint = max([x.Integral() for x in self.mc])
        hists_to_add = [h for h in self.mc if h.Integral() > 0.005*maxint]

        # Make the legend with the correct size
        leg = TLegend(0.75, 0.74-0.04*max(len(hists_to_add)-2,0), .89, 0.89)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetTextFont(43)
        leg.SetTextSize(20)
        nlegCols = 0

        maxY = 1.0
        if self.data is not None:
            leg.AddEntry( self.data, self.data.GetTitle(),'p')
            frame = self.dataH.Clone('frame')
            self._garbageList.append(frame)
            maxY = self.dataH.GetMaximum()
            frame.Reset('ICE')
        elif self.dataH is not None:
            leg.AddEntry( self.dataH, self.dataH.GetTitle(),'p')
            frame = self.dataH.Clone('frame')
            self._garbageList.append(frame)
            maxY = self.dataH.GetMaximum()
            frame.Reset('ICE')

        # Add the legend entries for the visible backgrounds
        for h in sorted(hists_to_add, key=lambda x: x.Integral(), reverse=True):
            leg.AddEntry(h, h.GetTitle(), 'f')
            nlegCols = nlegCols+1

        # Build the stack to plot from all backgrounds
        totalMC = None
        stack = THStack('mc','mc')
        for h in sorted(self.mc, key=lambda x: x.Integral()):
            stack.Add(h,'hist')
            if totalMC is None:
                totalMC = h.Clone('totalmc')
                self._garbageList.append(totalMC)
                totalMC.SetDirectory(0)
            else:
                totalMC.Add(h)

        if totalMC is not None:
            maxY = max(totalMC.GetMaximum(),maxY)
            if frame is None:
                frame = totalMC.Clone('frame')
                frame.Reset('ICE')
                self._garbageList.append(frame)

        if self.data is not None or self.dataH is not None: nlegCols = nlegCols+1
        if nlegCols == 0:
            print '%s is empty'%self.name
            return

        frame.GetYaxis().SetTitleSize(0.045)
        frame.GetYaxis().SetLabelSize(0.04)
        frame.GetYaxis().SetRangeUser(0.5, 1.2*maxY)
        frame.GetYaxis().SetNoExponent()
        frame.SetDirectory(0)
        frame.Draw()
        frame.GetYaxis().SetTitleOffset(1.6)
        stack.Draw('hist same')
        if self.data is not None:
            self.data.Draw('P')
        elif self.dataH is not None:
            self.dataH.Draw('e1same')

        # leg.SetNColumns(nlegCols)
        leg.Draw()
        redrawBorder(t1)


        ## Draw CMS Preliminary label
        CMS_lumi(pad=t1,iPeriod=2,iPosX=0,extraText='Work in Progress')

        if self.normalizedToData:
            txt=TLatex()
            txt.SetNDC(True)
            txt.SetTextFont(42)
            txt.SetTextColor(ROOT.kGray+1)
            txt.SetTextSize(0.035)
            txt.SetTextAngle(90)
            txt.SetTextAlign(12)
            txt.DrawLatex(0.05,0.05,'#it{Normalized to data}')

        if totalMC is None or (self.data is None and self.dataH is None):
            t1.SetPad(0,0,1,1)
            t1.SetBottomMargin(0.12)
        else:
            canvas.cd()
            t2 = TPad("t2","t2", 0.0, 0.0, 1.0, 0.2)
            self._garbageList.append(t2)
            t2.SetTopMargin(0)
            t2.SetBottomMargin(0.4)
            t2.SetGridy()
            t2.Draw()
            t2.cd()

            ratioframe=self.dataH.Clone('ratioframe')
            ratioframe.Reset('ICE')
            ratioframe.Draw()
            ratioframe.GetYaxis().SetRangeUser(self.ratiorange[0], self.ratiorange[1])
            ratioframe.GetYaxis().SetTitle('Obs./Exp.')
            ratioframe.GetYaxis().SetNdivisions(5)
            ratioframe.GetYaxis().SetLabelSize(0.15)
            ratioframe.GetXaxis().SetLabelSize(0.15)
            ratioframe.GetYaxis().SetTitleSize(0.18)
            ratioframe.GetXaxis().SetLabelSize(0.18)
            ratioframe.GetXaxis().SetTitleSize(0.18)
            ratioframe.GetYaxis().SetTitleOffset(0.4)
            ratioframe.GetXaxis().SetTitleOffset(0.9)

            gr=ROOT.TGraphAsymmErrors()
            gr.SetName("data2bkg")
            gr.SetMarkerStyle(self.dataH.GetMarkerStyle())
            gr.SetMarkerSize(0.7*self.dataH.GetMarkerSize())
            gr.SetMarkerColor(self.dataH.GetMarkerColor())
            gr.SetLineColor(self.dataH.GetLineColor())
            gr.SetLineWidth(self.dataH.GetLineWidth())
            bkgUncGr=ROOT.TGraphErrors()
            bkgUncGr.SetName('bkgunc')
            bkgUncGr.SetMarkerColor(920)
            bkgUncGr.SetMarkerStyle(1)
            bkgUncGr.SetLineColor(920)
            bkgUncGr.SetFillColor(920)
            bkgUncGr.SetFillStyle(3001)
            for xbin in xrange(1,self.dataH.GetXaxis().GetNbins()+1):
                x            = self.dataH.GetXaxis().GetBinCenter(xbin)
                dx           = self.dataH.GetXaxis().GetBinWidth(xbin)
                dataCts      = self.dataH.GetBinContent(xbin)
                if self.data:
                    data_err_low = self.data.GetErrorYlow(xbin-1) #get errors from the graph
                    data_err_up  = self.data.GetErrorYhigh(xbin-1)
                else:
                    data_err_low=self.dataH.GetBinError(xbin)
                    data_err_up=data_err_low
                bkgCts       = totalMC.GetBinContent(xbin);
                bkgCts_err   = totalMC.GetBinError(xbin);
                if bkgCts==0 : continue
                errLo=math.sqrt(math.pow(data_err_low*bkgCts,2) + math.pow(dataCts*bkgCts_err,2))/math.pow(bkgCts,2)
                errHi=math.sqrt(math.pow(data_err_up*bkgCts,2)  + math.pow(dataCts*bkgCts_err,2))/math.pow(bkgCts,2)
                np=gr.GetN()
                gr.SetPoint(np,x,dataCts/bkgCts)
                gr.SetPointError(np,0,0,errLo,errHi)
                bkgUncGr.SetPoint(np,x,1)
                bkgUncGr.SetPointError(np,dx,bkgCts_err/bkgCts)
            bkgUncGr.Draw('2')
            gr.Draw('p')
            redrawBorder(t2)


        canvas.cd()
        canvas.Modified()
        canvas.Update()



        for ext in self.plotformats : canvas.SaveAs(os.path.join(outDir, self.name+'.'+ext))
        if self.savelog:
            t1.cd()
            t1.SetLogy()
            frame.GetYaxis().SetRangeUser(1000,10*maxY)
            canvas.cd()
            for ext in self.plotformats : canvas.SaveAs(os.path.join(outDir, self.name+'_log.'+ext))



"""
converts a histogram to a graph with Poisson error bars
"""
def convertToPoissonErrorGr(h):

    htype=h.ClassName()
    if htype.find('TH1')<0 : return None

    #check https://twiki.cern.ch/twiki/bin/view/CMS/PoissonErrorBars
    alpha = 1 - 0.6827;
    grpois = ROOT.TGraphAsymmErrors(h);
    for i in xrange(0,grpois.GetN()+1) :
        N = grpois.GetY()[i]
        if N<200 :
            L = 0
            if N>0 : L = ROOT.Math.gamma_quantile(alpha/2,N,1.)
            U = ROOT.Math.gamma_quantile_c(alpha/2,N+1,1)
            grpois.SetPointEYlow(i, N-L)
            grpois.SetPointEYhigh(i, U-N)
        else:
            grpois.SetPointEYlow(i, math.sqrt(N))
            grpois.SetPointEYhigh(i,math.sqrt(N))
    return grpois


"""
increments the first and the last bin to show the under- and over-flows
"""
def fixExtremities(h,addOverflow=True,addUnderflow=True):
    if addUnderflow :
        fbin  = h.GetBinContent(0) + h.GetBinContent(1)
	fbine = ROOT.TMath.Sqrt(h.GetBinError(0)*h.GetBinError(0) + h.GetBinError(1)*h.GetBinError(1))
	h.SetBinContent(1,fbin)
	h.SetBinError(1,fbine)
	h.SetBinContent(0,0)
	h.SetBinError(0,0)
    if addOverflow:
        nbins = h.GetNbinsX();
	fbin  = h.GetBinContent(nbins) + h.GetBinContent(nbins+1)
	fbine = ROOT.TMath.Sqrt(h.GetBinError(nbins)*h.GetBinError(nbins)  + h.GetBinError(nbins+1)*h.GetBinError(nbins+1))
	h.SetBinContent(nbins,fbin)
	h.SetBinError(nbins,fbine)
	h.SetBinContent(nbins+1,0)
	h.SetBinError(nbins+1,0)


def setTDRStyle():
    """
    Loads TDR style
    """
    tdrStyle = ROOT.TStyle("tdrStyle","Style for P-TDR")
    # For the canvas:
    tdrStyle.SetCanvasBorderMode(0)
    tdrStyle.SetCanvasColor(ROOT.kWhite)
    tdrStyle.SetCanvasDefH(928) #Height of canvas
    tdrStyle.SetCanvasDefW(904) #Width of canvas
    tdrStyle.SetCanvasDefX(1320)   #POsition on screen
    tdrStyle.SetCanvasDefY(0)

    # For the Pad:
    tdrStyle.SetPadBorderMode(0)
    # tdrStyle.SetPadBorderSize(Width_t size = 1)
    tdrStyle.SetPadColor(ROOT.kWhite)
    tdrStyle.SetPadGridX(False)
    tdrStyle.SetPadGridY(False)
    tdrStyle.SetGridColor(0)
    tdrStyle.SetGridStyle(3)
    tdrStyle.SetGridWidth(1)

    # For the frame:
    tdrStyle.SetFrameBorderMode(0)
    tdrStyle.SetFrameBorderSize(1)
    tdrStyle.SetFrameFillColor(0)
    tdrStyle.SetFrameFillStyle(0)
    tdrStyle.SetFrameLineColor(1)
    tdrStyle.SetFrameLineStyle(1)
    tdrStyle.SetFrameLineWidth(1)

    # For the histo:
    # tdrStyle.SetHistFillColor(1)
    # tdrStyle.SetHistFillStyle(0)
    tdrStyle.SetHistLineColor(1)
    tdrStyle.SetHistLineStyle(0)
    tdrStyle.SetHistLineWidth(1)
    # tdrStyle.SetLegoInnerR(Float_t rad = 0.5)
    # tdrStyle.SetNumberContours(Int_t number = 20)

    tdrStyle.SetEndErrorSize(2)
    #  tdrStyle.SetErrorMarker(20)
    tdrStyle.SetErrorX(0.)

    tdrStyle.SetMarkerStyle(20)

    # For the fit/function:
    tdrStyle.SetOptFit(1)
    tdrStyle.SetFitFormat("5.4g")
    tdrStyle.SetFuncColor(2)
    tdrStyle.SetFuncStyle(1)
    tdrStyle.SetFuncWidth(1)

    #For the date:
    tdrStyle.SetOptDate(0)
    # tdrStyle.SetDateX(Float_t x = 0.01)
    # tdrStyle.SetDateY(Float_t y = 0.01)

    # For the statistics box:
    tdrStyle.SetOptFile(0)
    tdrStyle.SetOptStat(0) # To display the mean and RMS:   SetOptStat("mr")
    tdrStyle.SetStatColor(ROOT.kWhite)
    tdrStyle.SetStatFont(42)
    tdrStyle.SetStatFontSize(0.025)
    tdrStyle.SetStatTextColor(1)
    tdrStyle.SetStatFormat("6.4g")
    tdrStyle.SetStatBorderSize(1)
    tdrStyle.SetStatH(0.1)
    tdrStyle.SetStatW(0.15)
    # tdrStyle.SetStatStyle(Style_t style = 1001)
    # tdrStyle.SetStatX(Float_t x = 0)
    # tdrStyle.SetStatY(Float_t y = 0)

    # Margins:
    tdrStyle.SetPadTopMargin(0.07)
    tdrStyle.SetPadBottomMargin(0.13)
    tdrStyle.SetPadLeftMargin(0.17)
    tdrStyle.SetPadRightMargin(0.03)

    # For the Global title:
    tdrStyle.SetOptTitle(0)
    tdrStyle.SetTitleFont(42)
    tdrStyle.SetTitleColor(1)
    tdrStyle.SetTitleTextColor(1)
    tdrStyle.SetTitleFillColor(10)
    tdrStyle.SetTitleFontSize(0.065)
    tdrStyle.SetTitleH(0.07) # Set the height of the title box
    tdrStyle.SetTitleW(0.80) # Set the width of the title box
    tdrStyle.SetTitleX(0.15) # Set the position of the title box
    tdrStyle.SetTitleY(1.00) # Set the position of the title box
    # tdrStyle.SetTitleStyle(Style_t style = 1001)
    tdrStyle.SetTitleBorderSize(1)

    # For the axis titles:
    tdrStyle.SetTitleColor(1, "XYZ")
    tdrStyle.SetTitleFont(42, "XYZ")
    tdrStyle.SetTitleSize(0.06, "XYZ")
    # tdrStyle.SetTitleXSize(Float_t size = 0.02) # Another way to set the size?
    # tdrStyle.SetTitleYSize(Float_t size = 0.02)
    tdrStyle.SetTitleXOffset(0.95)
    tdrStyle.SetTitleYOffset(1.3)
    # tdrStyle.SetTitleOffset(1.1, "Y") # Another way to set the Offset

    # For the axis labels:
    tdrStyle.SetLabelColor(1, "XYZ")
    tdrStyle.SetLabelFont(42, "XYZ")
    tdrStyle.SetLabelOffset(0.007, "XYZ")
    tdrStyle.SetLabelSize(0.044, "XYZ")

    # For the axis:
    tdrStyle.SetAxisColor(1, "XYZ")
    tdrStyle.SetStripDecimals(True)
    tdrStyle.SetTickLength(0.03, "XYZ")
    tdrStyle.SetNdivisions(510, "XYZ")
    tdrStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
    tdrStyle.SetPadTickY(1)

    # Change for log plots:
    tdrStyle.SetOptLogx(0)
    tdrStyle.SetOptLogy(0)
    tdrStyle.SetOptLogz(0)

    # Postscript options:
    tdrStyle.SetPaperSize(20.,20.)
    # tdrStyle.SetLineScalePS(Float_t scale = 3)
    # tdrStyle.SetLineStyleString(Int_t i, const char* text)
    # tdrStyle.SetHeaderPS(const char* header)
    # tdrStyle.SetTitlePS(const char* pstitle)

    # tdrStyle.SetBarOffset(Float_t baroff = 0.5)
    # tdrStyle.SetBarWidth(Float_t barwidth = 0.5)
    # tdrStyle.SetPaintTextFormat(const char* format = "g")
    # tdrStyle.SetPalette(Int_t ncolors = 0, Int_t* colors = 0)
    # tdrStyle.SetTimeOffset(Double_t toffset)
    # tdrStyle.SetHistMinimumZero(True)

    tdrStyle.cd()

