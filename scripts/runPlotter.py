#! /usr/bin/env python
import os
import json
import commands
from ROOT import TFile,gROOT,gStyle

def getByLabel(desc, key, defaultVal=None) :
    """
    Gets the value of a given item
    (if not available a default value is returned)
    """
    try :
        return desc[key]
    except KeyError:
        return defaultVal

def getCMSPfn(path):
    from subprocess import Popen, PIPE
    output = Popen(["cmsPfn", path], stdout=PIPE).communicate()[0]
    return output.strip()

def getNormalization(path):
    infile = TFile.Open(path, 'read')
    constVals = infile.Get('constVals')
    nevents, xsec = constVals[0], constVals[1]
    return nevents, xsec

def openTFile(url):
    ## File on eos
    if url.startswith('/store/'):
        url = getCMSPfn(url)
        ## Should add a check here for existence

    ## If it's a local file, check it actually exists
    elif not os.path.exists(url):
        return None

    rootFile = TFile.Open(url)
    try:
        if rootFile.IsZombie(): return None
    except ReferenceError:
        ## Failed to open url (file doesn't exist)
        return None
    return rootFile

def getAllPlotsFrom(tdir, chopPrefix=False):
    """
    Return a list of all keys deriving from TH1 in a file
    """
    toReturn = []
    allKeys = tdir.GetListOfKeys()
    for tkey in allKeys:
        key = tkey.GetName()
        obj = tdir.Get(key)
        if obj.InheritsFrom('TDirectory') :
            allKeysInSubdir = getAllPlotsFrom(obj,chopPrefix)
            for subkey in allKeysInSubdir :
                if not chopPrefix:
                    toReturn.append( key +'/'+subkey )
                else:
                    newObj = obj.Get(subkey)
                    try:
                        if newObj.InheritsFrom('TDirectory'):
                            toReturn.append( key +'/'+subkey )
                    except:
                        subkey = subkey.split('/')[-1]
                        toReturn.append(subkey)
        elif obj.InheritsFrom('TH1') :
            if chopPrefix:
                key = key.replace(tdir.GetName()+'_','')
            toReturn.append(key)
    return toReturn


def runPlotter(inDir, jsonUrl, lumi, debug, outDir):
    """
    Loop over the inputs and launch jobs
    """
    from UserCode.llvv_fwk.PlotUtils import Plot

    jsonFile = open(jsonUrl,'r')
    procList = json.load(jsonFile,encoding = 'utf-8').items()

    # Make a survey of *all* existing plots
    plots = []
    baseRootFile = None
    if inDir.endswith('.root'):
        baseRootFile = TFile.Open(inDir)
        plots = list(set(getAllPlotsFrom(tdir=baseRootFile,chopPrefix=True)))
    else:
        for proc in procList:
            for desc in proc[1]:
                data = desc['data']
                mctruthmode = getByLabel(desc,'mctruthmode')
                for d in data:
                    dtag = getByLabel(d,'dtag','')
                    split = getByLabel(d,'split',1)

                    for segment in range(0,split):
                        eventsFile = dtag
                        if split > 1:
                            eventsFile = dtag + '_' + str(segment)
                        if mctruthmode:
                            eventsFile += '_filt%d' % mctruthmode
                        rootFileUrl = inDir+'/'+eventsFile+'.root'
                        rootFile = openTFile(rootFileUrl)
                        if rootFile is None: continue

                        iplots = getAllPlotsFrom(tdir=rootFile)
                        rootFile.Close()
                        plots = list(set(plots+iplots))

    plots.sort()

    # Now plot them
    for plot in plots:
        print plot
        pName = plot.replace('/','')
        newPlot = Plot(pName)

        for proc in procList:
            for desc in proc[1]: # loop on processes
                title = getByLabel(desc,'tag','unknown')
                isData = getByLabel(desc,'isdata',False)
                color = int(getByLabel(desc,'color',1))
                data = desc['data']
                mctruthmode = getByLabel(desc,'mctruthmode')

                hist = None
                for dset in data: # loop on datasets for process
                    dtag = getByLabel(dset,'dtag','')
                    split = getByLabel(dset,'split',1)

                    if baseRootFile is None:
                        for segment in range(0,split) :
                            eventsFile = dtag
                            if split > 1:
                                eventsFile = dtag + '_' + str(segment)
                            if mctruthmode:
                                eventsFile += '_filt%d' % mctruthmode
                            rootFileUrl = inDir+'/'+eventsFile+'.root'

                            rootFile = openTFile(rootFileUrl)
                            if rootFile is None: continue

                            ihist = rootFile.Get(plot)
                            try:
                                if ihist.Integral() <= 0:
                                    rootFile.Close()
                                    continue
                            except AttributeError:
                                continue
                            if hist is None :
                                hist = ihist.Clone(dtag+'_'+pName)
                                hist.SetDirectory(0)
                            else:
                                hist.Add(ihist)
                            rootFile.Close()

                    else:
                        ihist = baseRootFile.Get(dtag+'/'+dtag+'_'+pName)
                        try:
                            if ihist.Integral() <= 0: continue
                        except:
                            continue
                        if h is None:
                            h = ihist.Clone(dtag+'_'+pName)
                            h.SetDirectory(0)
                        else:
                            h.Add(ihist)

                if hist is None: continue
                if not isData: hist.Scale(lumi)
                newPlot.add(hist,title,color,isData)

        newPlot.show(outDir)
        if(debug):
            newPlot.showTable(outDir)
        newPlot.reset()

    if baseRootFile is not None: baseRootFile.Close()


if __name__ == "__main__":
    import sys
    from optparse import OptionParser
    usage = """
    usage: %prog [options] input_directory
    """
    parser = OptionParser(usage=usage)
    parser.add_option('-j', '--json', dest='json',
                      default='test/topss2014/samples.json',
                      help='A json file with the samples to analyze'
                           '[default: %default]')
    parser.add_option('-d', '--debug', dest='debug', action="store_true",
                      help='Dump the event yields table for each plot')
    parser.add_option('-l', '--lumi', dest='lumi', default=19700,
                      type='float',
                      help='Re-scale to integrated luminosity [pb]'
                           ' [default: %default]')
    parser.add_option('-o', '--outDir', dest='outDir', default='plots',
                      help='Output directory [default: %default]')
    (opt, args) = parser.parse_args()
    sys.argv = [] ## clean up arguments to stop pyROOT from messing with -h

    if len(args) > 0:
        from UserCode.llvv_fwk.PlotUtils import customROOTstyle
        customROOTstyle()
        gROOT.SetBatch(True)
        gStyle.SetOptTitle(0)
        gStyle.SetOptStat(0)
        
        os.system('mkdir -p %s'%opt.outDir)
        runPlotter(inDir=args[0],
                   jsonUrl=opt.json,
                   lumi=opt.lumi,
                   debug=opt.debug,
                   outDir=opt.outDir)
        print 'Plots have been saved to %s' % opt.outDir
        exit(0)

    else:
        parser.print_help()
        exit(-1)

