## some useful python functions which can be used to handle root stuff
## include this file instead of copying them all the time...

import os
import ROOT
from ROOT import *

import subprocess

######################################################################
## some basic ROOT histogram manipulation stuff
## which one is using over and over...
######################################################################

def openTFile(path, option='r'):
    f =  ROOT.TFile.Open(path,option)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    return f

def GetKeyNames( file, dir = "" ):
        file.cd(dir)
        return [key.GetName() for key in gDirectory.GetListOfKeys()]

def getHist(file, hist):
    h = file.Get(hist)
    if not h.__nonzero__():
        raise NameError('Histogram '+hist+' doesn\'t exist in '+str(file))
    if not h.GetSumw2(): h.Sumw2()
    return h

def getTree(file, tree):
    t = file.Get(tree)
    if not t.__nonzero__():
        raise NameError('Tree '+tree+' doesn\'t exist in '+str(file))
    return t

def getHistFromTree(tree, var, cut, bins=100, low=0, high=300, nEntries=1000000000):
    varexp = var+'>>h('+str(bins)+','+str(low)+','+str(high)+')'
    tree.Draw(varexp,cut,'',nEntries)
    hist = ROOT.gDirectory.Get("h")
    return hist.Clone('h')

def projectFromTree(hist, varname, sel, tree, option=''):
    try:
        tree.Project(hist.GetName(),varname, sel, option)
        return True
    except Exception, e:
        raise e


def scaleHist(hist, scale=1.):
    hist.Scale(scale/hist.Integral(0,hist.GetNbinsX()+1))

def checkKeyInFile(key, filehandle, doraise=True):
    obj = ROOT.TObject()
    try:
        filehandle.GetObject(key, obj)
        return True
    except LookupError, e:
        print ("Error: key %s not found in file %s" %
                  (key, filehandle.GetName()))
        if doraise:
            raise e
        else:
            return False

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


######################################################################
## some more specialized things, but still ROOT related
######################################################################


def cmsPreliminary(x1=0.15, y1=0.9, x2=0.4, y2=1.):
    pave = TPaveText(x1, y1, x2, y2, "NDC")
    pave.SetBorderSize(0);
    pave.SetFillStyle(0);
    pave.SetTextAlign(12);
    pave.SetTextFont(42);
    # pave.SetTextSize(20);
    pave.AddText('CMS Preliminary');
    return pave


## the following ratio function takes a histogram and a list of histograms
## it returns 3 histograms, the ratio, and the error band
def getRatio(data, stacks):
    ratio = data.Clone('ratio')
    ratio.Sumw2()
    ratio.Divide(stacks[0].Clone(''))
    ratio.GetYaxis().SetTitle('Data/MC')
    ratio.GetYaxis().SetNdivisions(5)
    ratio.SetMaximum(1.499)
    ratio.SetMinimum(0.501)

    rup = stacks[0].Clone('rup')
    rdown = stacks[0].Clone('rdown')
    rup.Divide(rup)
    rdown.Divide(rdown)
    for i in xrange(1,rup.GetNbinsX()+1):
        rup.SetBinContent(i,1+max(rup.GetBinError(i),rdown.GetBinError(i)))
        rdown.SetBinContent(i,1-max(rup.GetBinError(i),rdown.GetBinError(i)))

    rup.SetLineStyle(1)
    rup.SetLineStyle(1)
    rup.SetFillColor(16)
    rup.SetLineColor(16)
    rdown.SetLineStyle(1)
    rdown.SetFillColor(10)
    rdown.SetLineColor(16)

    return ratio.Clone('ratio'),rup.Clone('rup'),rdown.Clone('rdown')

def getRatioSimple(hist, reference):
    ratio = hist.Clone("%s_ratio"%hist.GetName())
    ratio.SetDirectory(0)
    ratio.SetLineColor(hist.GetLineColor())
    for xbin in xrange(1,reference.GetNbinsX()+1):
        ref = reference.GetBinContent(xbin)
        val = hist.GetBinContent(xbin);
        if ref==0:
            ratio.SetBinContent(xbin, 1.0)
            continue
        ratio.SetBinContent(xbin, val/ref)
    return ratio


## same as above
def getRatios(data, stacks):
    ratios = []
    data.Sumw2()
    for stack in stacks:
        stack.Sumw2()
        ratio = data.Clone('ratio')
        ratio.Sumw2()
        ratio.SetLineColor(stack.GetLineColor())
        ratio.SetLineStyle(stack.GetLineStyle())
        ratio.SetMarkerStyle(stack.GetMarkerStyle())
        ratio.SetMarkerColor(stack.GetMarkerColor())
        ratio.SetMarkerSize(stack.GetMarkerSize())
        ratio.Divide(stack.Clone(''))
        ratio.GetYaxis().SetTitle('Data/MC')
        ratio.GetYaxis().SetNdivisions(5)
        ratio.SetMaximum(1.499)
        ratio.SetMinimum(0.501)
        ratios.append(ratio.Clone(''))


    rup = data.Clone('rup')
    rdown = data.Clone('rdown')
    rup.Divide(rup)
    rdown.Divide(rdown)
    for i in xrange(1,rup.GetNbinsX()+1):
        rup.SetBinContent(i,1+max(rup.GetBinError(i),rdown.GetBinError(i)))
        rdown.SetBinContent(i,1-max(rup.GetBinError(i),rdown.GetBinError(i)))

    rup.GetYaxis().SetTitle('ratio')
    rup.SetLineStyle(1)
    rup.SetLineStyle(1)
    rup.SetFillColor(16)
    rup.SetLineColor(16)
    rdown.SetLineStyle(1)
    rdown.SetFillColor(10)
    rdown.SetLineColor(16)

    return ratios,rup.Clone('rup'),rdown.Clone('rdown')


def setAxesStyle(hist):
    hist.GetXaxis().SetLabelFont(43)
    hist.GetYaxis().SetLabelFont(43)
    hist.GetXaxis().SetLabelSize(20)
    hist.GetYaxis().SetLabelSize(20)
    hist.GetXaxis().SetTitleFont(43)
    hist.GetYaxis().SetTitleFont(43)
    hist.GetXaxis().SetTitleSize(20)
    hist.GetYaxis().SetTitleSize(20)
    hist.GetXaxis().SetTitleOffset(5)
    hist.GetYaxis().SetTitleOffset(2)
    tag = hist.GetName().split('_')[1]
    try:
        hist.GetXaxis().SetTitle(xtitle_dict[tag])
        hist.GetYaxis().SetTitle(ytitle_dict[tag])
    except:
        KeyError


def prepareLine(x1=-200, y1=1., x2=1000, y2=1.):
    line = ROOT.TGraph()
    line.SetPoint(0,x1,y1)
    line.SetPoint(1,x2,y2)
    line.SetLineWidth(2)
    line.SetLineColor(6)
    line.SetLineStyle(7)
    line.Draw()
    return line


def splitCanvas(border = 0.25,logy=0):
    scale = (1-border)/border
    p_plot = ROOT.TPad('plotpad','Pad containing the actual plot',0.,border,1.,1.,0,0)
    p_plot.SetBottomMargin(0.05)
    p_plot.SetLeftMargin(0.15)
    p_plot.SetLogy(logy)
    p_plot.SetTicks()
    # p_plot.Draw()
    p_ratio = ROOT.TPad('ratiopad','Pad containing the ratio',0.,0.,1.,border,0,0)
    p_ratio.SetTopMargin(0.0)
    p_ratio.SetLeftMargin(0.15)
    p_ratio.SetBottomMargin(0.35)
    p_ratio.SetTicks()
    # p_ratio.Draw()
    return p_plot, p_ratio

######################################################################
## some other useful things
######################################################################

def createDirectory(path):
    if not os.path.exists(path):
        print 'creating output directory '+path
        os.makedirs(path)
    else:
        print 'directory '+path+' already exists'


def getRootPath(directory, tag):
    eos = '/store/cmst3/user/'
    rooteos = 'root://eoscms//eos/cms/store/cmst3/user/'
    cmd = 'cmsLs'
    data = subprocess.Popen([cmd,directory], stdout=subprocess.PIPE)
    a = [f.split()[-1] for f in data.stdout if len(f.split())>0]
    if tag != '':
        b = [s for s in a if tag in s]
        return b
    else:
        return a


def chainFiles(files,name):
    chain = TChain(name)
    for f in files:
        chain.Add(f)
    return chain







