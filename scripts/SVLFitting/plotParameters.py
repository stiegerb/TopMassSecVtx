"""
"""
def plotParameters(ws):
    ROOT.gROOT.SetBatch(1)
    pars_to_plot = ["sig_agauss_mean", "sig_agauss_sigmaL",
                    "sig_agauss_sigmaR","sig_ngauss_beta",
                    "sig_ngauss_gamma", "sig_ngauss_mu"]

    colors = [51, 62, 83, 93, 100, 68]

    for np,param in enumerate(pars_to_plot):
        par1 = ws.var("b_%s"% param).getVal()
        par2 = ws.var("a_%s"% param).getVal()
        par1E = ws.var("b_%s"% param).getError()
        par2E = ws.var("a_%s"% param).getError()

        canv = ROOT.TCanvas('C_%s'%param,'c',800,800)
        canv.cd()
        axes = ROOT.TH2D("axes_%s"%param, "axes",
                          1, -15., 15,
                          1, (1-0.23)*par1, (1+0.23)*par1)
        axes.GetXaxis().SetTitle("#Delta m_{top} [GeV]")
        axes.Draw("axis")

        nom = ROOT.TF1("nom_%s"%param, "pol1", -20., 20.)
        nom.SetParameters(par1, par2)

        upup = ROOT.TF1("upup_%s"%param, "pol1", -20., 20.)
        upup.SetParameters(par1+par1E, par2+par2E)
        dndn = ROOT.TF1("dndn_%s"%param, "pol1", -20., 20.)
        dndn.SetParameters(par1-par1E, par2-par2E)
        updn = ROOT.TF1("updn_%s"%param, "pol1", -20., 20.)
        updn.SetParameters(par1+par1E, par2-par2E)
        dnup = ROOT.TF1("dnup_%s"%param, "pol1", -20., 20.)
        dnup.SetParameters(par1-par1E, par2+par2E)

        nom.SetLineWidth(3)
        for x in [nom, upup, updn, dndn, dnup]:
            x.SetLineColor(colors[np])
        for x in [upup,dnup,updn,dndn]:
            x.SetLineWidth(1)
            x.SetLineStyle(2)
        upup.DrawCopy("same")
        dndn.DrawCopy("same")
        updn.DrawCopy("same")
        dnup.DrawCopy("same")
        nom.DrawCopy("same")

        label=ROOT.TLatex()
        label.SetNDC()
        label.SetTextFont(42)
        label.SetTextSize(0.03)
        label.DrawLatex(0.15,0.83, param)

        canv.SaveAs("calib_%s.pdf"%param)
