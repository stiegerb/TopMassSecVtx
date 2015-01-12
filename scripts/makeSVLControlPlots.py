#! /usr/bin/env python
import os, sys
import ROOT
import pickle
from UserCode.TopMassSecVtx.PlotUtils import Plot, getRatio
from UserCode.TopMassSecVtx.CMS_lumi import CMS_lumi
from runPlotter import openTFile

TREENAME = 'SVLInfo'
SELECTIONS = [
	('mrankinc',  'SVLMassRank==1'),
	('mrank',     'SVLDeltaR<2.0&&SVLMassRank==1'),
	('drrankinc', 'SVLDeltaRRank==1'),
	('drrank',    'SVLDeltaR<2.0&&SVLDeltaRRank==1')
]

NBINS = 100
XMAX = 200.

class NormPlot(Plot):
	def __init__(self,name):
		super(NormPlot, self).__init__(name)

	def show(self, outDir):
		if len(self.mc)==0:
			print '%s is empty' % self.name
			return

		htype=self.mc[0].ClassName()
		if htype.find('TH2')>=0:
			print 'Skipping TH2'
			return

		ROOT.gStyle.SetOptTitle(0)
		ROOT.gStyle.SetOptStat(0)

		canvas = ROOT.TCanvas('c_'+self.name,'C',600,600)
		canvas.cd()
		t1 = ROOT.TPad("t1","t1", 0.0, 0.20, 1.0, 1.0)
		t1.SetBottomMargin(0)
		t1.Draw()
		t1.cd()
		self.garbageList.append(t1)

		frame = None
		# leg = ROOT.TLegend(0.15,0.9,0.9,0.95)
		leg = ROOT.TLegend(0.5,0.7,0.9,0.89)
		leg.SetBorderSize(0)
		leg.SetFillStyle(0)
		leg.SetTextFont(42)
		leg.SetTextSize(0.04)
		nlegCols = 0

		maxY = 1.0
		if self.data is not None:
			leg.AddEntry( self.data, self.data.GetTitle(),'p')
			frame = self.dataH.Clone('frame')
			self.garbageList.append(frame)
			maxY = self.data.GetMaximum()*1.1
			frame.Reset('ICE')

		totalMC = None

		if self.data is not None: nlegCols = nlegCols+1
		if nlegCols == 0:
			print '%s is empty'%self.name
			return

		frame.GetYaxis().SetTitleSize(0.045)
		frame.GetYaxis().SetLabelSize(0.04)
		frame.GetYaxis().SetRangeUser(0.5,1.3*maxY)
		frame.SetDirectory(0)
		frame.Draw()
		frame.GetYaxis().SetTitleOffset(1.6)

		for h in self.mc:
			h.DrawNormalized('hist same')

		if self.data is not None: self.data.Draw('P same')
		# leg.SetNColumns(nlegCols)
		leg.SetNColumns(2)
		leg.Draw()

		## Draw CMS Preliminary label
		CMS_lumi(t1,2,0)

		if self.normalizedToData:
			txt=TLatex()
			txt.SetNDC(True)
			txt.SetTextFont(42)
			txt.SetTextColor(ROOT.kGray+1)
			txt.SetTextSize(0.035)
			txt.SetTextAngle(90)
			txt.SetTextAlign(12)
			txt.DrawLatex(0.05,0.05,'#it{Normalized to data}')

		if totalMC is None or self.data is None:
			t1.SetPad(0,0,1,1)
			t1.SetBottomMargin(0.12)
		else:
			canvas.cd()
			t2 = ROOT.TPad("t2","t2", 0.0, 0.0, 1.0, 0.2)
			self.garbageList.append(t2)
			t2.SetTopMargin(0)
			t2.SetBottomMargin(0.4)
			t2.SetGridy()
			t2.Draw()
			t2.cd()

			ratioframe=self.dataH.Clone('ratioframe')
			ratioframe.Reset('ICE')
			ratioframe.Draw()
			ratioframe.GetYaxis().SetRangeUser(0.62,1.36)
			ratioframe.GetYaxis().SetTitle('Data/#SigmaBkg')
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
			gr.SetMarkerStyle(20)
			gr.SetMarkerColor(1)
			gr.SetLineColor(1)
			gr.SetLineWidth(2)
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
				data_err_low = self.data.GetErrorYlow(xbin-1) #get errors from the graph
				data_err_up  = self.data.GetErrorYhigh(xbin-1)
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


		canvas.cd()
		canvas.Modified()
		canvas.Update()
		for ext in ['pdf','png'] : canvas.SaveAs(outDir+'/'+self.name+'.'+ext)
		t1.cd()
		t1.SetLogy()
		frame.GetYaxis().SetRangeUser(0.5,4*maxY)
		canvas.cd()
		for ext in ['pdf','png'] : canvas.SaveAs(outDir+'/'+self.name+'_log.'+ext)

def projectFromTree(hist, varname, sel, tree, option=''):
	try:
		# tree.Draw(">>evlist", sel)
		# evlist = ROOT.gDirectory.Get("evlist")
		# tree.SetEventList(evlist)
		tree.Project(hist.GetName(),varname, sel, option)
		return True
	except Exception, e:
		raise e

def makeControlPlot(tree, opt):
	sel = 'SVLDeltaR<2.0'
	# newPlot = NormPlot("Control")
	h_tot = ROOT.TH1D("total"    , "total"    , NBINS, 0, XMAX)
	h_cor = ROOT.TH1D("correct"  , "correct"  , NBINS, 0, XMAX)
	h_wro = ROOT.TH1D("wrong"    , "wrong"    , NBINS, 0, XMAX)
	h_unm = ROOT.TH1D("unmatched", "unmatched", NBINS, 0, XMAX)

	projectFromTree(h_tot, "SVLMass", sel,                  tree)
	projectFromTree(h_cor, "SVLMass", sel+'&&CombInfo==1',  tree)
	projectFromTree(h_wro, "SVLMass", sel+'&&CombInfo==0',  tree)
	projectFromTree(h_unm, "SVLMass", sel+'&&CombInfo==-1', tree)

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	tc = ROOT.TCanvas("control", "Control", 800, 800)
	tc.cd()

	h_tot.SetLineColor(ROOT.kBlack)
	h_cor.SetLineColor(ROOT.kBlue)
	h_wro.SetLineColor(ROOT.kRed)
	h_unm.SetLineColor(ROOT.kSpring-5)

	for x in [h_tot, h_cor, h_wro, h_unm]:
		x.SetLineWidth(2)

	CMS_lumi(tc,2,0)

	h_tot.Draw("hist")
	h_wro.Draw("hist same")
	h_unm.Draw("hist same")

	tc.SaveAs(os.path.join(opt.outDir,"control.pdf"))

	# newPlot.add(h_tot, h_tot.GetTitle(), ROOT.kBlack,    False)
	# newPlot.add(h_cor, h_cor.GetTitle(), ROOT.kBlue,     False)
	# newPlot.add(h_wro, h_wro.GetTitle(), ROOT.kRed,      False)
	# newPlot.add(h_unm, h_unm.GetTitle(), ROOT.kSpring-5, False)

	# newPlot.info()

	# newPlot.show(opt.outDir)
	# newPlot.appendTo(os.path.join(opt.outDir,'svlplots.root'))

def getSVLMassHistos(tree, sel, tag=''):
	h_tot = ROOT.TH1D("msvl_tot_%s"%tag, "total"    , NBINS, 0, XMAX)
	h_cor = ROOT.TH1D("msvl_cor_%s"%tag, "correct"  , NBINS, 0, XMAX)
	h_wro = ROOT.TH1D("msvl_wro_%s"%tag, "wrong"    , NBINS, 0, XMAX)
	h_unm = ROOT.TH1D("msvl_unm_%s"%tag, "unmatched", NBINS, 0, XMAX)

	projectFromTree(h_tot, "SVLMass", sel,                  tree)
	projectFromTree(h_cor, "SVLMass", sel+'&&CombInfo==1',  tree)
	projectFromTree(h_wro, "SVLMass", sel+'&&CombInfo==0',  tree)
	projectFromTree(h_unm, "SVLMass", sel+'&&CombInfo==-1', tree)

	h_tot.SetLineColor(ROOT.kBlack)
	h_cor.SetLineColor(ROOT.kBlue)
	h_wro.SetLineColor(ROOT.kRed)
	h_unm.SetLineColor(ROOT.kSpring-5)

	for x in [h_tot, h_cor, h_wro, h_unm]:
		x.SetLineWidth(2)
		x.Sumw2()
		x.Scale(1./h_tot.Integral())

	return h_tot, h_cor, h_wro, h_unm

def setMaximums(histos, margin=1.2):
	maxy = 0.
	for hist in histos:
		binmax = 0.
		for binx in xrange(1,hist.GetNbinsX()+1):
			binmax = max(binmax, hist.GetBinContent(binx))
		maxy = max(maxy,margin*binmax)
	for hist in histos:
		hist.SetMaximum(maxy)

def makeSVLMassvsmtPlots(histos, tag):
	colors = [100, 91, 85, 78, 67, 61, 57, 51]
	for n,mass in enumerate(sorted(histos.keys())):
		histos[mass].SetLineColor(colors[n])

	for hist in histos.values():
		hist.Scale(1./hist.Integral())

	setMaximums(histos.values())

	ROOT.gStyle.SetOptTitle(0)
	ROOT.gStyle.SetOptStat(0)
	ROOT.gROOT.SetBatch(1)

	tc = ROOT.TCanvas("massscan_%s"%tag, "massscan", 800, 800)
	tc.cd()

	tc.SetWindowSize(800 + (800 - tc.GetWw()), (800 + (800 - tc.GetWh())));
	p2 = ROOT.TPad("pad2","pad2",0,0,1,0.31);
	p2.SetTopMargin(0);
	p2.SetBottomMargin(0.3);
	p2.SetFillStyle(0);
	p2.Draw();
	p1 = ROOT.TPad("pad1","pad1",0,0.31,1,1);
	p1.SetBottomMargin(0);
	p1.Draw();
	p1.cd();

	tl = ROOT.TLegend(0.74, 0.75-0.035*max(len(histos)-3,0), .89, .89)
	tl.SetBorderSize(0)
	tl.SetFillColor(0)
	tl.SetShadowColor(0)
	tl.SetTextFont(42)
	tl.SetTextSize(0.035)

	histos.values()[0].Draw("axis")

	for mass in sorted(histos.keys()):
		tl.AddEntry(histos[mass], '%5.1f GeV'%mass, 'l')
		histos[mass].Draw("hist same")

	tl.Draw()


	p2.cd()

	ratioframe = histos[172.5].Clone('ratioframe')
	ratioframe.Reset('ICE')
	ratioframe.GetYaxis().SetRangeUser(0.50,1.50)
	ratioframe.GetYaxis().SetTitle('Ratio w.r.t. 172.5 GeV')
	# ratioframe.GetYaxis().SetNdivisions(5)
	ratioframe.GetYaxis().SetLabelSize(0.08)
	ratioframe.GetXaxis().SetLabelSize(0.08)
	ratioframe.GetYaxis().SetTitleSize(0.10)
	ratioframe.GetXaxis().SetTitleSize(0.10)
	ratioframe.GetYaxis().SetTitleOffset(0.5)
	ratioframe.GetXaxis().SetTitleOffset(0.5)
	ratioframe.Draw()

	ratios = {}
	# f = ROOT.TFile(os.path.join(opt.outDir,"histos.root"), "RECREATE")
	# f.cd()
	for mass,hist in histos.iteritems():
		ratios[mass] = getRatio(hist, histos[172.5])
		# ratios[mass].Write(ratios[mass].GetName())
	setMaximums(ratios.values())

	for ratio in ratios.values():
		ratio.Draw("hist same")

	tc.cd()
	tc.Modified()
	tc.Update()
	tc.SaveAs(os.path.join(opt.outDir,"masscan_%s.pdf"%tag))
	tc.Close()
	# f.Write()
	# f.Close()



def main(args, opt):
	try:
		os.system('mkdir -p %s'%opt.outDir)

		massfiles = {} # mass -> filename
		# find mass scan files
		for filename in os.listdir(os.path.join(args[0],'mass_scan')):
			if not os.path.splitext(filename)[1] == '.root': continue
			masspos = 3 if 'MSDecays' in filename else 2
			mass = float(filename.split('_')[masspos][:3]) + 0.5
			if mass == 172.5: continue
			massfiles[mass] = os.path.join(args[0],'mass_scan',filename)

		## nominal file
		massfiles[172.5] = os.path.join(args[0],
										'MC8TeV_TTJets_MSDecays_172v5.root')

		masstrees = {} # mass -> tree
		for mass in sorted(massfiles.keys()):
			file = ROOT.TFile.Open(massfiles[mass],'READ')
			tree = file.Get(TREENAME)
			masstrees[mass] = tree

		# makeControlPlot(masstrees[172.5], opt)
		histos = {} # (tag, mass) -> h_tot, h_cor, h_wro, h_unm
		for mass, tree in masstrees.iteritems():
			for tag,sel in SELECTIONS:
				print ' ... processing %5.1f GeV %s' % (mass, sel)
				htag = ("%s_%5.1f"%(tag,mass)).replace('.','')
				histos[(tag, mass)] = getSVLMassHistos(tree, sel, htag)

	    cachefile = open(".svlhistos.pck", 'w')
	    pickle.dump(histos, cachefile, pickle.HIGHEST_PROTOCOL)
	    cachefile.close()

		for tag,sel in SELECTIONS:
			print tag, sel
			for mass in sorted(masstrees.keys()):
				hists = histos[(tag, mass)]
				n_tot, n_cor, n_wro, n_unm = (x.GetEntries() for x in hists)
				p_cor = 100.*(n_cor/float(n_tot))
				p_wro = 100.*(n_wro/float(n_tot))
				p_unm = 100.*(n_unm/float(n_tot))
				print ('  %5.1f GeV: %7d entries '
					   '(%2.0f%% corr, %2.0f%% wrong, %2.0f%% unmatched)' %
					   (mass, n_tot, p_cor, p_wro, p_unm))

			makeSVLMassvsmtPlots(dict((mass, histos[(tag, mass)][0])
									   for mass in sorted(masstrees.keys())),
								 "%s_tot"%tag)
			makeSVLMassvsmtPlots(dict((mass, histos[(tag, mass)][1])
									   for mass in sorted(masstrees.keys())),
								 "%s_cor"%tag)
			makeSVLMassvsmtPlots(dict((mass, histos[(tag, mass)][2])
									   for mass in sorted(masstrees.keys())),
								 "%s_wro"%tag)
			makeSVLMassvsmtPlots(dict((mass, histos[(tag, mass)][3])
									   for mass in sorted(masstrees.keys())),
								 "%s_unm"%tag)



		exit(0)

	except IndexError:
		print "Please provide a valid input directory"
		exit(-1)


if __name__ == "__main__":
	import sys
	tmpargv  = sys.argv[:]     # [:] for a copy, not reference
	sys.argv = []
	from ROOT import gROOT, gStyle
	sys.argv = tmpargv
	from optparse import OptionParser
	usage = """
	usage: %prog [options] input_directory
	"""
	parser = OptionParser(usage=usage)
	parser.add_option('-v', '--verbose', dest='verbose', action="store",
					  type='int', default=1,
					  help='Verbose mode [default: %default (semi-quiet)]')
	parser.add_option('-l', '--lumi', dest='lumi', default=17123,
					  type='float',
					  help='Re-scale to integrated luminosity [pb]'
						   ' [default: %default]')
	parser.add_option('-o', '--outDir', dest='outDir', default='svlplots',
					  help='Output directory [default: %default]')
	parser.add_option("--jobs", default=0,
					  action="store", type="int", dest="jobs",
					  help=("Run N jobs in parallel."
							"[default: %default]"))
	(opt, args) = parser.parse_args()

	main(args, opt)
	exit(-1)




