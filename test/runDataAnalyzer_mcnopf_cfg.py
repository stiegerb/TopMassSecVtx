import FWCore.ParameterSet.Config as cms
import os,sys

isMC=True
isTauEmbed=False
storeAllPF=False
gtag="START53_V29A::All"

from UserCode.TopMassSecVtx.storeTools_cff import configureSourceFromCommandLine
outFile, inputListArray = configureSourceFromCommandLine()
inputList=cms.untracked.vstring(inputListArray)
tfsOutputFile=outFile
outFile=os.path.dirname(outFile)+'/edm_'+os.path.basename(outFile)

execfile( os.path.expandvars('${CMSSW_BASE}/src/UserCode/TopMassSecVtx/test/runDataAnalyzer_cfg.py'))

