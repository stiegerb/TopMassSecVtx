import os
import sys
import optparse
import ROOT
import pickle
import json

"""
Get data and sum of MC from file
"""
def getTemplates(fIn,dist,tag,refName='QCD'):
    data,refH,sumMC=None,None,None
    for key in fIn.Get(dist).GetListOfKeys():

        keyName=key.GetName()
        if 'Graph' in keyName : continue

        h=fIn.Get('%s/%s'%(dist,keyName))

        #reference
        if refName in keyName : 
            #print keyName,'is qcd'
            if refH:
                refH.Add(h)
            else:
                refH=h.Clone('%s_%s'%(refName,tag))
                refH.SetDirectory(0)
        #data
        elif 'Data' in keyName:
            #print keyName,'is data'
            data=h.Clone('data_'+tag)
            data.SetDirectory(0)

        #other processes
        else:
            #print keyName,'is other procs'
            if sumMC:
                sumMC.Add(h)
            else:
                sumMC=h.Clone('mcsum_'+tag)
                sumMC.SetDirectory(0)

    return data,sumMC,refH


"""
"""
def main():

    #configuration
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('--in',           dest='input',        help='plotter file',        default=None,       type='string')
    parser.add_option('--out',          dest='outdir',       help='output directory',    default='./',       type='string')
    parser.add_option('--noniso',       dest='noniso',       help='noniso name',         default='qcd',      type='string')
    (opt, args) = parser.parse_args()

    #prepare output
    os.system('mkdir -p %s'%opt.outdir)

    #prepare fitter
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
        
    #open inputs
    fIn=ROOT.TFile.Open(opt.input)

    #perform a fit to a variable of interest
    nonIsoTemplateSF={}
    qcdNormUnc={}
    for ch in ['e','mu']:
        for cat in ['',
                    '2j0b','2j1b','2j2b',
                    '3j0b','3j1b','3j2b',
                    '4j0b','4j1b','4j2b']:
           
            nonIsoSF=[]
            for dist in ['met','mt']:
                dataNonIso, sumMCNonIso, _  = getTemplates(fIn=fIn, dist='%s%s%s_%s'%(ch,opt.noniso,cat,dist), tag='noniso')
                dataIso,    sumMCIso, _     = getTemplates(fIn=fIn, dist='%s%s_%s'%(ch,cat,dist),              tag='iso')

                #normalized QCD template below the MET cut
                bin0           = 1
                binN           = dataNonIso.GetXaxis().FindBin(40.)
                niso           = dataIso.Integral(bin0,binN)
                nmciso         = sumMCIso.Integral(bin0,binN)
                nnoniso        = dataNonIso.Integral(bin0,binN)
                nmcnoniso      = sumMCNonIso.Integral(bin0,binN)
            
                #scale factors to apply and relative uncertainty (maximised)
                nonIsoSF.append( ROOT.TMath.Max((niso-nmciso)/(nnoniso-nmcnoniso),0.) )
                #nonIsoSFUnc=ROOT.TMath.Sqrt(((niso+nmciso)*((nnoniso-nmcnoniso)**2)+(nnoniso+nmcnoniso)*((niso-nmciso)**2))/((nnoniso-nmcnoniso)**4)+0.3**2)
                

            nonIsoTemplateSF[ch+cat]=(
                nonIsoSF[1],
                ROOT.TMath.Sqrt( (nonIsoSF[0]-nonIsoSF[1])**2 + 0.3*nonIsoSF[1]) 
                )

            #free mem
            dataNonIso.Delete()
            sumMCNonIso.Delete()
            dataIso.Delete()
            sumMCIso.Delete()


    #produce the QCD templates
    fOut=ROOT.TFile.Open('%s/Data_QCDMultijets.root'%(opt.outdir),'RECREATE')
    for distKey in fIn.GetListOfKeys():
        dist=distKey.GetName()
        if not opt.noniso in dist : continue
        if 'iso' in dist or 'ratevsrun' in dist: continue

        normCateg=dist.split('_')[0].replace(opt.noniso,'')
        #if normCateg[-1]=='b' : normCateg=normCateg[:-2]
        dataNonIso, sumMCNonIso,_ = getTemplates(fIn=fIn, dist=dist, tag=dist)

        try:
            #print dist,normCateg,dataNonIso, sumMCNonIso

            #do not subtract anything in the CR
            dataNonIsoUp=dataNonIso.Clone('%s_QCDUp'%(dist))
            dataNonIsoUp.SetTitle('QCD multijets')

            #subtract 2xMC in the CR
            dataNonIsoDown=dataNonIso.Clone('%s_QCDDown'%(dist))
            dataNonIsoDown.Add(sumMCNonIso,-2)       
            dataNonIsoDown.SetTitle('QCD multijets')

            #subtract 1xMC in the CR
            dataNonIso.Add(sumMCNonIso,-1)  
            dataNonIso.SetName(dist)
            dataNonIso.SetTitle('QCD multijets')

            try:
                dataNonIso.Scale( nonIsoTemplateSF[normCateg][0] )
                totalQCD=dataNonIso.Integral()
                for xbin in xrange(1,dataNonIso.GetNbinsX()+1):
                    scaledUnc=dataNonIso.GetBinError(xbin)
                    scaledYieldUnc=dataNonIso.GetBinContent(xbin)*nonIsoTemplateSF[normCateg][1]/nonIsoTemplateSF[normCateg][0]
                    dataNonIso.SetBinError(xbin,
                                           ROOT.TMath.Sqrt(scaledUnc**2+scaledYieldUnc**2))
                            
                if totalQCD>0:
                    for xbin in xrange(0,dataNonIsoUp.GetNbinsX()):
                        val=dataNonIsoUp.GetBinContent(xbin+1)
                        if val<0 : dataNonIsoUp.SetBinContent(xbin+1,1e-5)
                        val=dataNonIsoDown.GetBinContent(xbin+1)
                        if val<0 : dataNonIsoDown.SetBinContent(xbin+1,1e-5)
                    dataNonIsoUp.Scale(totalQCD/dataNonIsoUp.Integral())
                    dataNonIsoDown.Scale(totalQCD/dataNonIsoDown.Integral())
            except:            
                print 'unable to normalize ',dist,' with normCateg=',normCateg
            sumMCNonIso.Delete()

            #dump to file
            fOut.cd()
            for h in [dataNonIso,dataNonIsoUp,dataNonIsoDown]:
                hname=h.GetName().replace('qcd','')
                h.SetName(hname)
                h.SetDirectory(fOut)
                h.Write()

        except:
            pass
        
    #dump to file    
    print 'QCD scale factors CR->SR'
    print nonIsoTemplateSF
    cachefile=open('%s/.qcdscalefactors.pck'%opt.outdir,'w')
    pickle.dump(nonIsoTemplateSF, cachefile, pickle.HIGHEST_PROTOCOL)
    cachefile.close()

    #all done
    print 'QCD templates and systematic variations stored in %s'%fOut.GetName()
    fOut.Close()
    
    fIn.Close()

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())
