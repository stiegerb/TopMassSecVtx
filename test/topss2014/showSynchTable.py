import ROOT
import os
dir="%s/src/UserCode/llvv_fwk/test/topss2014/summary/a8b66b1/"%os.environ['CMSSW_BASE']

ctsMap=[]
files=[[ROOT.TFile.Open(dir+"/Synch_ll_ntuple.root"),["ee","mumu","emu"]],
       [ROOT.TFile.Open(dir+"/Synch_ljets_ntuple.root"),["e","mu"]]
       ]
allch=[]

for f in files:
    for ich in xrange(0,len(f[1])):
        ch=f[1][ich]
        allch.append(ch)
        h=f[0].Get(ch+"_synchevtflow")
        if len(ctsMap)==0:
            for xbin in xrange(1,h.GetXaxis().GetNbins()+1):
                ctsMap.append([h.GetXaxis().GetBinLabel(xbin),[]])

        for xbin in xrange(1,h.GetXaxis().GetNbins()+1):
            label=h.GetXaxis().GetBinLabel(xbin)
            cts=h.GetBinContent(xbin)
            ctsMap[xbin-1][1].append(cts)
 

colSize=15
print "-----------------------------------------"
print "Cut".rjust(colSize),
for ch in allch : print ch.rjust(colSize),
print ''
for cut in ctsMap:
    print cut[0].rjust(colSize),
    for cts in cut[1]:
        print ('%d'%cts).rjust(colSize),
    print ''
print "-----------------------------------------"
