#!/usr/bin/env python

import ROOT

def plotFragmentationVersusMtop(fitResults,outName,ref='bfrag'):
    
    #hardcoded values, from simulation
    fragModels={'bfrag'    :("Z2*LEP r_{b}",    ROOT.kBlack,     0.7616,0.0002),
                'bfragdn'  :("Z2*LEP r_{b}-",   ROOT.kMagenta,   0.7481,0.0003),
                'bfragup'  :("Z2*LEP r_{b}+",   ROOT.kMagenta+2, 0.7729,0.0003),
                'bfragpete':("Z2*LEP Peterson", ROOT.kRed+1,     0.7189,0.0007),
                'bfraglund':("Z2*LEP Lund",     ROOT.kAzure+7,   0.7670,0.0007),
                '172.5'    :('Z2*',             ROOT.kMagenta-9, 0.73278,0.00009),
    }

    #get the fitted values
    fitVals={}
    for key in fragModels:
        if key in fitResults:
            fitVals[key]=(fitResults[key][0],fitResults[key][1])

    #put all into a graph
    mg=ROOT.TMultiGraph()
    for key in fitVals:
        gr=ROOT.TGraphErrors()
        gr.SetLineColor(fragModels[key][1])
        gr.SetMarkerColor(fragModels[key][1])
        gr.SetMarkerSize(1.0)
        gr.SetMarkerStyle(20)
        gr.SetFillStyle(0)
        gr.SetFillColor(0)
        gr.SetTitle(fragModels[key][0])
        gr.SetName(key+'_'+outName)
        gr.SetPoint(0,fragModels[key][2],fitVals[key][0]-fitVals[ref][0])
        gr.SetPointError(0,fragModels[key][3],fitVals[key][1])
        mg.Add(gr)

    c=ROOT.TCanvas('c','c',500,500)
    c.SetTopMargin(0.05)
    c.SetRightMargin(0.05)
    mg.Draw('ap')
    mg.GetXaxis().SetTitle('Average p_{T}(B)/p_{T}(b)')
    mg.GetYaxis().SetTitle('#Delta m_{t} [GeV]')
    mg.GetXaxis().SetTitleOffset(1.2)
    mg.GetYaxis().SetTitleOffset(1.2)
    leg=c.BuildLegend(0.12,0.5,0.4,0.8)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    line=ROOT.TLine()
    line.SetLineColor(ROOT.kGray)
    line.SetLineStyle(9)
    line.DrawLine(mg.GetXaxis().GetXmin(),0,mg.GetXaxis().GetXmax(),0)
    line.DrawLine(fragModels[ref][2],mg.GetYaxis().GetXmin(),fragModels[ref][2],mg.GetYaxis().GetXmax())
    mg.Fit('pol1')
    pol1=mg.GetFunction('pol1')
    pt=ROOT.TPaveText(0.1,0.8,0.6,0.94,'brNDC')
    pt.SetBorderSize(0)
    pt.SetTextFont(42)
    pt.SetFillStyle(0)
    pt.SetTextAlign(12)
    pt.SetTextSize(0.04)
    pol1.Print('v')
    pt.AddText('#bf{CMS} #it{preliminary}')
    pt.AddText('#scale[0.8]{#Delta m_{t}=%0.1f+%0.1fx#Delta<p_{T}(B)/p_{T}(b)>|_{Z2*LEP rb}}'%(pol1.GetParameter(0),pol1.GetParameter(1)))
    pt.Draw()
    c.Modified()
    c.Update()
    for ext in ['.C','.png','.pdf']: c.SaveAs('fragvsmtop_%s%s' % (outName,ext))
