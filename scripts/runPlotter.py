#! /usr/bin/env python
import os
import sys
import json

sys.path.append('/afs/cern.ch/cms/caf/python/')
from cmsIO import cmsFile


def getByLabel(desc, key, defaultVal=None) :
    """
    Gets the value of a given item
    (if not available a default value is returned)
    """
    try :
        return desc[key]
    except KeyError:
        return defaultVal

def getCMSPfn(path, protocol='rfio'):
    cmsf = cmsFile(url, protocol)
    return cmsf.pfn

def getNormalization(tfile):
    constVals = tfile.Get('constVals')
    try:
        nevents, xsec = int(constVals[0]), float(constVals[1])
    except:
        nevents, xsec = 0, 0
    return nevents, xsec

def openTFile(url):
    from ROOT import TFile
    ## File on eos
    if url.startswith('/store/'):
        cmsf = cmsFile(url, 'rfio')
        if not cmsf.isfile(): ## check existence
            return None
        url = cmsf.pfn

    elif not os.path.exists(url): ## check existence
        return None

    rootFile = TFile.Open(url)
    try:
        if rootFile.IsZombie(): return None
    except ReferenceError:
        ## Failed to open url (file doesn't exist)
        return None
    return rootFile

def getAllPlotsFrom(tdir, chopPrefix=False,tagsToFilter=[]):
    """
    Return a list of all keys deriving from TH1 in a file
    """
    toReturn = []
    allKeys = tdir.GetListOfKeys()
    for tkey in allKeys:
        key = tkey.GetName()
        keepPlot=False
        for tag in tagsToFilter:
            if key.find(tag)>=0 : 
                keepPlot=True
        if not keepPlot : continue
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

def checkMissingFiles(inDir, jsonUrl):
    """
    Loop over json inputs and check existence of files.
    Also checks if files have a reasonable size (> 1kB)
    """

    jsonFile = open(jsonUrl,'r')
    procList = json.load(jsonFile,encoding = 'utf-8').items()

    # Make a survey of *all* existing plots
    total_expected = 0
    missing_files = []
    suspicious_files = []

    protocol = 'local'
    if inDir.startswith('/store/'):
        protocol = 'rfio'

    cmsInDir = cmsFile(inDir, protocol)

    if not cmsInDir.isdir():
        print inDir, "is not a directory"
        return False

    for proc in procList:
        for desc in proc[1]:
            data = desc['data']
            isData = getByLabel(desc,'isdata',False)
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
                    filename = eventsFile+'.root'
                    rootFileUrl = inDir+'/'+filename
                    total_expected += 1
                    cmsInRootFile = cmsFile(rootFileUrl, protocol)
                    if not cmsInRootFile.isfile():
                        missing_files.append(filename)
                    elif (cmsInRootFile.size() < 1024):
                        suspicious_files.append(filename)
                    continue

    print 20*'-'
    if len(missing_files):
        print "Missing the following files:"
        print "(%d out of %d expected)"% (len(missing_files), total_expected)
        for filename in missing_files:
            print filename
    else:
        print "NO MISSING FILES!"
    print 20*'-'
    if len(suspicious_files):
        print "The following files are suspicious (< 1kB size):"
        print "(%d out of %d expected)"% (len(suspicious_files), total_expected)
        for filename in suspicious_files:
            print filename
        print 20*'-'

def makePlotPacked(packedargs):
    key, inDir, procList, xsecweights, options = packedargs
    return makePlot(key, inDir, procList, xsecweights, options)

def makePlot(key, inDir, procList, xsecweights, options):
    from UserCode.TopMassSecVtx.PlotUtils import Plot
    print "... processing", key
    pName = key.replace('/','')
    newPlot = Plot(pName)
    baseRootFile = None ## FIXME
    for proc_tag in procList:
        for desc in proc_tag[1]: # loop on processes
            title = getByLabel(desc,'tag','unknown')
            isData = getByLabel(desc,'isdata',False)
            color = int(getByLabel(desc,'color',1))
            data = desc['data']
            mctruthmode = getByLabel(desc,'mctruthmode')

            hist = None
            for process in data: # loop on datasets for process
                dtag = getByLabel(process,'dtag','')
                split = getByLabel(process,'split',1)

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

                        ihist = rootFile.Get(key)
                        try: ## Check if it is found
                            if ihist.Integral() <= 0:
                                rootFile.Close()
                                continue
                        except AttributeError:
                            rootFile.Close()
                            continue

                        ihist.Scale(xsecweights[dtag])
                        # print dtag,xsecweights[dtag]

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
                    except AttributeError:
                        continue

                    ihist.Scale(xsecweights[dtag])

                    if hist is None: ## Check if it is found
                        hist = ihist.Clone(dtag+'_'+pName)
                        hist.SetDirectory(0)
                    else:
                        hist.Add(ihist)

            if hist is None: continue
            if not isData:
                hist.Scale(options.lumi)
            newPlot.add(hist,title,color,isData)

    newPlot.show(options.outDir)
    if(options.debug or newPlot.name.find('flow')>=0 ) : newPlot.showTable(options.outDir)
    newPlot.appendTo(options.outDir+'/plotter.root')
    newPlot.reset()

def runPlotter(inDir, options):
    """
    Loop over the inputs and launch jobs
    """
    from ROOT import TFile

    jsonFile = open(options.json,'r')
    procList = json.load(jsonFile,encoding = 'utf-8').items()

    # Make a survey of *all* existing plots
    plots = []
    xsecweights = {}
    tot_ngen = {}
    missing_files = []
    baseRootFile = None
    tagsToFilter=opt.filter.split(',')
    if inDir.endswith('.root'):
        baseRootFile = TFile.Open(inDir)
        plots = list(set(getAllPlotsFrom(tdir=baseRootFile,chopPrefix=True,tagsToFilter=tagsToFilter)))
    else:
        for proc_tag in procList:
            for desc in proc_tag[1]:
                data = desc['data']
                isData = getByLabel(desc,'isdata',False)
                mctruthmode = getByLabel(desc,'mctruthmode')
                for process in data:
                    dtag = getByLabel(process,'dtag','')
                    split = getByLabel(process,'split',1)
                    dset = getByLabel(process,'dset',dtag)

                    try:
                        ngen = tot_ngen[dset]
                    except KeyError:
                        ngen = 0

                    for segment in range(0,split):
                        eventsFile = dtag
                        if split > 1:
                            eventsFile = dtag + '_' + str(segment)
                        if mctruthmode:
                            eventsFile += '_filt%d' % mctruthmode
                        rootFileUrl = inDir+'/'+eventsFile+'.root'
                        rootFile = openTFile(rootFileUrl)
                        if rootFile is None:
                            missing_files.append(eventsFile+'.root')
                            continue

                        iplots = getAllPlotsFrom(tdir=rootFile,tagsToFilter=tagsToFilter)
                        if not isData:
                            ngen_seg,_ = getNormalization(rootFile)
                            ngen += ngen_seg

                        rootFile.Close()
                        plots = list(set(plots+iplots))

                    tot_ngen[dset] = ngen


                # Calculate weights:
                for process in data:
                    dtag = getByLabel(process,'dtag','')
                    dset = getByLabel(process,'dset',dtag)
                    brratio = getByLabel(process,'br',[1])
                    xsec = getByLabel(process,'xsec',1)
                    if dtag not in xsecweights.keys():
                        try:
                            ngen = tot_ngen[dset]
                            xsecweights[str(dtag)] = brratio[0]*xsec/ngen
                        except ZeroDivisionError:
                            if isData:
                                xsecweights[str(dtag)] = 1.0
                            else:
                                print "ngen not properly set for", dtag


        if len(missing_files) and options.verbose>0:
            print 20*'-'
            print "WARNING: Missing the following files:"
            for filename in missing_files:
                print filename
            print 20*'-'

    # Apply mask:
    if len(options.plotMask)>0:
        masked_plots = [_ for _ in plots if options.plotMask in _]
        plots = masked_plots

    plots.sort()

    # Now plot them
    if options.jobs==0:
        for plot in plots:
            makePlot(plot, inDir, procList, xsecweights, options)

    else:
        from multiprocessing import Pool
        pool = Pool(options.jobs)

        tasklist = [(p, inDir, procList, xsecweights, options) for p in plots]
        pool.map(makePlotPacked, tasklist)


    if baseRootFile is not None: baseRootFile.Close()


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
    parser.add_option('-j', '--json', dest='json',
                      default='test/topss2014/samples.json',
                      help='A json file with the samples to analyze'
                           '[default: %default]')
    parser.add_option('-c', '--checkMissingFiles', dest='checkMissingFiles',
                      action="store_true",
                      help=('Check a directory for missing files (as '
                            'expected from the json file) and exit.'))
    parser.add_option('-d', '--debug', dest='debug', action="store_true",
                      help='Dump the event yields table for each plot')
    parser.add_option('-f', '--filter', dest='filter', default="",
                      help='csv list of plots to produce')
    parser.add_option('-v', '--verbose', dest='verbose', action="store",
                      type='int', default=1,
                      help='Verbose mode [default: %default (semi-quiet)]')
    parser.add_option('-m', '--plotMask', dest='plotMask',
                      default='',
                      help='Only process plots matching this mask'
                           '[default: all plots]')
    parser.add_option('-l', '--lumi', dest='lumi', default=17123,
                      type='float',
                      help='Re-scale to integrated luminosity [pb]'
                           ' [default: %default]')
    parser.add_option('-o', '--outDir', dest='outDir', default='plots',
                      help='Output directory [default: %default]')
    parser.add_option("--jobs", default=0,
                      action="store", type="int", dest="jobs",
                      help=("Run N jobs in parallel."
                            "[default: %default]"))
    (opt, args) = parser.parse_args()

    if len(args) > 0:
        if opt.checkMissingFiles:
            checkMissingFiles(inDir=args[0], jsonUrl=opt.json)
            exit(0)

        from UserCode.TopMassSecVtx.PlotUtils import setTDRStyle
        setTDRStyle()
        gROOT.SetBatch(True)
        gStyle.SetOptTitle(0)
        gStyle.SetOptStat(0)

        os.system('mkdir -p %s'%opt.outDir)
        os.system('rm %s/plotter.root'%opt.outDir)
        runPlotter(inDir=args[0], options=opt)
        print 'Plots have been saved to %s' % opt.outDir
        exit(0)

    else:
        parser.print_help()
        exit(-1)

