import FWCore.ParameterSet.Config as cms

import os,commands

def getMarkusSherpaSamplesFor(hadr='Lund'):
    
    fileList=cms.untracked.vstring()
    for i in xrange(0,1500,250):
        files=commands.getstatusoutput('lcg-ls -D srmv2 -b srm://dcache-se-cms.desy.de:8443/srm/managerv2?SFN=/pnfs/desy.de/cms/tier2/store/user/mseidel/TT_%s_8TeV-sherpa2 -c 250 -o %d'
                                       %(hadr,i))[1].split()
        files=[f.replace('/pnfs/desy.de/cms/tier2/','root://dcache-cms-xrootd.desy.de//') for f in files]
        fileList.extend(files)
    print len(fileList),' files to process for %s model'%hadr
    return fileList
