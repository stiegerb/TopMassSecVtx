#! /usr/bin/env python
import os
import sys
import json
import pickle
import ROOT
from UserCode.TopMassSecVtx.PlotUtils import setTDRStyle,fixExtremities,Plot

sys.path.append('/afs/cern.ch/cms/caf/python/')
from cmsIO import cmsFile

COLORPALETTE = { # title -> color
    't#bar{t}'       : ROOT.kGray,
    'Single top'     : ROOT.kAzure+5,
    'W+Jets'         : ROOT.kOrange-3,
    'DY+Jets'        : ROOT.kOrange+9,
    'QCD Multijets'  : ROOT.kGray+2,
    'Multiboson'     : ROOT.kSpring-5,
    'other t#bar{t}' : ROOT.kBlue+2,
    ## Original
    # 'VV'             : ROOT.kBlue-9,    # 591
    # 'W'              : ROOT.kOrange+9,  # 809
    # 'other t#bar{t}' : ROOT.kSpring+2,  # 822
    # 'Single top'     : ROOT.kSpring+4,  # 824
    # 'DY'             : ROOT.kTeal-9,    # 831
    # 't#bar{t}'       : ROOT.kMagenta-2, # 614
    # 'Multijets'      : ROOT.kYellow-6,  # 41
}

def getCMSPfn(path, protocol='rfio'):
    cmsf = cmsFile(url, protocol)
    return cmsf.pfn

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

def getNormalization(tfile):
    constVals = tfile.Get('constVals')
    try:
        nevents, xsec = int(constVals[0]), float(constVals[1])
    except:
        print '\033[91m Unable to retrieve const vals \033[0m - check run for............ %s'%tfile.GetName()
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
def getHistogramFromFile(key, tfile, options):
    ihist = tfile.Get(key)
    try:
        if ihist.Integral() <= 0:
            if options.verbose > 1:
                print ("   empty histogram: %s in %s" %
                           (ihist.GetName(), tfile.GetName()))
            return None

    except AttributeError:
        if options.verbose > 1:
            print ("   failed to load: %s from %s" %
                          (key, tfile.GetName()))
        return None
    return ihist

def getListofProcessesFromJSON(procList, chopPrefix=False):
    returnlist = []
    for desc in procList[0][1]:
        for process in desc['data']:
            listitem = process['dtag']
            if chopPrefix:
                listitem = listitem.split('_',1)[1]
            returnlist.append(str(listitem))
    return returnlist
def getAllPlotsFrom(tdir, chopPrefix=False,tagsToFilter=[],
                    filterByProcsFromJSON=None):
    """
    Return a list of all keys deriving from TH1 in a file
    """
    toReturn = []
    allKeys = tdir.GetListOfKeys()
    for tkey in allKeys:
        key = tkey.GetName()

        keepPlot = False
        antifilter = False
        for tag in tagsToFilter:
            if tag == '!':
                antifilter = True
            if tag in key:
                keepPlot = True

        if antifilter: keepPlot = not keepPlot
        if not keepPlot : continue

        obj = tdir.Get(key)
        if obj.InheritsFrom('TDirectory') :
            allKeysInSubdir = getAllPlotsFrom(obj, chopPrefix=chopPrefix,
                                tagsToFilter=tagsToFilter,
                                filterByProcsFromJSON=filterByProcsFromJSON)
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

    if filterByProcsFromJSON:
        jsonFile = open(filterByProcsFromJSON,'r')
        procList = json.load(jsonFile,encoding = 'utf-8').items()
        list_of_processes = getListofProcessesFromJSON(procList,
                                                       chopPrefix=True)

        newlist = []
        for key in toReturn:
            for proc in list_of_processes:
                if key.endswith('_%s'%proc):
                    newkey = key.replace('_%s'%proc,'')
                    newlist.append(newkey)

        return list(set(newlist))

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
    recovered_files = []

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
            isData = desc.get('isdata',False)
            mctruthmode = desc.get('mctruthmode')
            for d in data:
                dtag = d.get('dtag','')
                split = d.get('split',1)

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
                    else:
                        tfile = openTFile(rootFileUrl)
                        try:
                            if tfile.TestBit(ROOT.TFile.kRecovered):
                                recovered_files.append(filename)
                            tfile.Close()
                        except AttributeError:
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
        print "The following files are suspicious (< 1kB size or zombie):"
        print "(%d out of %d expected)"% (len(suspicious_files), total_expected)
        for filename in suspicious_files:
            print filename
        print 20*'-'
    if len(recovered_files):
        print "The following files are recovered:"
        print "(%d out of %d expected)"% (len(recovered_files), total_expected)
        for filename in recovered_files:
            print filename
        print 20*'-'


def makePlot((key, inDir, procList, xsecweights, options, scaleFactors)):
    print "... processing", key
    pName = key.replace('/','')
    newPlot = Plot(pName)
    newPlot.plotformats = ['pdf', 'png']
    newPlot.ratiorange = (0.4,2.3)
    baseRootFile = None

    procsToExclude = options.excludeProcesses.split(',')
    if len(procsToExclude) == 1 and '' in procsToExclude:
        procsToExclude = []

    if inDir.endswith('.root'):
        baseRootFile = openTFile(inDir)
    for proc_tag in procList:
        for desc in proc_tag[1]: # loop on processes
            title = desc.get('tag','unknown')
            isData = desc.get('isdata',False)
            try:
                color = COLORPALETTE[title]
            except KeyError:
                color = int(desc.get('color',1))
            data = desc['data']
            mctruthmode = desc.get('mctruthmode')

            # Exclude processes specified in options.excludeProcesses
            skipproc = False
            for exproc in procsToExclude:
                if exproc in title: skipproc = True
            if skipproc:
                if options.verbose > 0:
                    print '   skipping %s' % title
                continue

            hist = None
            for process in data: # loop on datasets for process
                dtag = process.get('dtag','')

                # Exclude processes specified in options.excludeProcesses
                for exproc in procsToExclude:
                    if exproc in dtag: skipproc = True
                if skipproc:
                    if options.verbose > 0:
                        print '   skipping %s' % dtag
                    continue

                if baseRootFile is None:
                    if options.split: # Files are split
                        split = process.get('split',1)
                        for segment in range(0,split) :
                            eventsFile = dtag
                            if split > 1:
                                eventsFile = dtag + '_' + str(segment)
                            if mctruthmode:
                                eventsFile += '_filt%d' % mctruthmode
                            rootFileUrl = inDir+'/'+eventsFile+'.root'

                            rootFile = openTFile(rootFileUrl)
                            if rootFile is None: continue

                            ihist = getHistogramFromFile(key, rootFile, options)
                            if not ihist:
                                rootFile.Close()
                                continue

                            if not options.cutUnderOverFlow:
                                fixExtremities(ihist,True,True)
                            else:
                                fixExtremities(ihist,False,False)

                            ## Apply xsec weights
                            if xsecweights : ihist.Scale(xsecweights[str(dtag)])

                            ## Apply external scale factor
                            if (key,str(title)) in scaleFactors:
                                print (' ... scaling %s,%s by %5.3f' %
                                         (key, str(title),
                                          scaleFactors[(key, str(title))]))
                                ihist.Scale(scaleFactors[(key,str(title))])

                            if hist is None :
                                hist = ihist.Clone(dtag+'_'+pName)
                                hist.SetDirectory(0)
                            else:
                                hist.Add(ihist)
                            rootFile.Close()
                    else:
                        eventsFile = dtag
                        if mctruthmode:
                            eventsFile += '_filt%d' % mctruthmode
                        rootFileUrl = inDir+'/'+eventsFile+'.root'

                        rootFile = openTFile(rootFileUrl)
                        if rootFile is None: continue

                        ihist = getHistogramFromFile(key, rootFile, options)
                        if not ihist:
                            rootFile.Close()
                            continue

                        if not options.cutUnderOverFlow:
                            fixExtremities(ihist,True,True)
                        else:
                            fixExtremities(ihist,False,False)

                        ## Apply xsec weights
                        if xsecweights : ihist.Scale(xsecweights[str(dtag)])

                        ## Apply external scale factor
                        if (key,str(title)) in scaleFactors:
                            print (' ... scaling %s,%s by %5.3f' %
                                     (key, str(title),
                                      scaleFactors[(key, str(title))]))
                            ihist.Scale(scaleFactors[(key,str(title))])

                        if hist is None :
                            hist = ihist.Clone(dtag+'_'+pName)
                            hist.SetDirectory(0)
                        else:
                            hist.Add(ihist)
                        rootFile.Close()

                else:
                    # ihist = baseRootFile.Get(dtag+'/'+dtag+'_'+pName)
                    histkey = '%s_%s' % (key,dtag.split('_',1)[1])
                    ihist = getHistogramFromFile(histkey, baseRootFile,
                                                 options)
                    if not ihist: continue

                    if not options.cutUnderOverFlow:
                        fixExtremities(ihist,True,True)
                    else:
                        fixExtremities(ihist,False,False)

                    ## Apply xsec weights
                    if xsecweights : ihist.Scale(xsecweights[str(dtag)])

                    ## Apply external scale factor
                    if (key,str(title)) in scaleFactors:
                        print (' ... scaling %s,%s by %5.3f' %
                                 (key, str(title),
                                  scaleFactors[(key, str(title))]))
                        ihist.Scale(scaleFactors[(key,str(title))])


                    if hist is None: ## Check if it is found
                        hist = ihist.Clone(dtag+'_'+pName)
                        hist.SetDirectory(0)
                    else:
                        hist.Add(ihist)

            if hist is None: continue
            if not isData:
                hist.Scale(options.lumi)
            if options.verbose > 0:
                print ("  adding %s (Integral: %s) (Color %d) (Isdata %d)" %
                        (hist.GetName(), hist.Integral(), color, isData))

            newPlot.add(hist,title,color,isData)

    if options.normToData :
        newPlot.normToData()

    if not options.silent :
        if 'flow' in newPlot.name:
            newPlot.savelog = True
        newPlot.show(options.outDir)
        if options.debug or 'flow' in newPlot.name:
            newPlot.showTable(options.outDir)
    newPlot.appendTo(os.path.join(options.outDir, options.outFile))
    newPlot.reset()

def readXSecWeights(jsonfile=None):
    """
    read the pre-stored xsecweights dictionary
    """
    try:
        cachefile = open(".xsecweights.pck", 'r')
        xsecweights = pickle.load(cachefile)
        cachefile.close()
        print '>>> Reading xsec weights from cache (.xsecweights.pck)'
        return xsecweights
    except IOError:
        print '>>> Failed to read .xsecweights.pck file'
        raise RuntimeError

    ## Should check that all the dtags in the given json file are in the dictionary
    if jsonfile:
        jsonFile = open(jsonfile,'r')
        procList = json.load(jsonFile,encoding = 'utf-8').items()

        for proc_tag in procList:
            for desc in proc_tag[1]:
                data = desc['data']
                isData = desc.get('isdata',False)
                for process in data:
                    dtag = process.get('dtag','')
                    if not str(dtag) in xsecweights:
                        print '>>> Missing entry in xsecweights: %s' % str(dtag)

    return xsecweights

def makeXSecWeights(inDir, jsonfiles, options):
    """
    Loop over a list of json files and fill in a xsecweights dictionary
    """
    xsecweights = {}
    tot_ngen = {}
    missing_files = []
    for jfname in jsonfiles:
        ## Rootfiles are in subdirs for the syst and mass_scan samples:
        dirname = inDir
        if 'syst'      in jfname: dirname = os.path.join(inDir,'syst')
        if 'mass_scan' in jfname: dirname = os.path.join(inDir,'mass_scan')
        if 'qcd'       in jfname: dirname = os.path.join(inDir,'qcd_control')
        if 'z_s'       in jfname: dirname = os.path.join(inDir,'z_control')
        if 'photon_samples' in jfname: dirname = os.path.join(inDir,'photon_control')
        jsonFile = open(jfname,'r')
        procList = json.load(jsonFile,encoding = 'utf-8').items()

        # Make a survey of *all* existing plots
        for proc_tag in procList:
            for desc in proc_tag[1]:
                data = desc['data']
                isData = desc.get('isdata',False)
                mctruthmode = desc.get('mctruthmode')
                for process in data:
                    dtag = process.get('dtag','')
                    procKey=dtag
                    if mctruthmode : procKey += '_filt'+str(mctruthmode)
                    print "... processing %s"%procKey

                    if isData:
                        xsecweights[procKey] = 1.0
                        tot_ngen[procKey]    = 0
                        continue

                    split = process.get('split',1)

                    try:
                        ngen = tot_ngen[procKey]
                    except KeyError:
                        ngen = 0

                    for segment in range(0,split):
                        eventsFile = dtag
                        if split > 1:
                            eventsFile = dtag + '_' + str(segment)
                        if mctruthmode:
                            eventsFile += '_filt%d' % mctruthmode
                        rootFileUrl = dirname+'/'+eventsFile+'.root'
                        rootFile = openTFile(rootFileUrl)
                        if rootFile is None:
                            missing_files.append(eventsFile+'.root')
                            continue

                        ngen_seg,_ = getNormalization(rootFile)
                        if not isData: ngen += ngen_seg

                        rootFile.Close()

                    tot_ngen[procKey] = ngen

                # Calculate weights:
                for process in data:
                    dtag = process.get('dtag','')
                    procKey=dtag
                    if mctruthmode : procKey += '_filt'+str(mctruthmode)
                    brratio = process.get('br',[1])
                    xsec = process.get('xsec',1)
                    if procKey not in xsecweights.keys():
                        try:
                            ngen = tot_ngen[procKey]
                            finalBR=1
                            for br in brratio: finalBR *=br
                            xsecweights[procKey] = finalBR*xsec/ngen
                        except ZeroDivisionError:
                            if isData:
                                xsecweights[procKey] = 1.0
                            else:
                                print ">>> ERROR: ngen not set for", procKey


    if len(missing_files) and options.verbose>0:
        print 20*'-'
        print "WARNING: Missing the following files:"
        for filename in missing_files:
            print filename
        print 20*'-'

    cachefile = open(".xsecweights.pck", 'w')
    pickle.dump(xsecweights, cachefile, pickle.HIGHEST_PROTOCOL)
    cachefile.close()
    print '>>> Produced xsec weights and wrote to cache (.xsecweights.pck)'
    return 0

def runPlotter(inDir, options, scaleFactors={}):
    """
    Loop over the inputs and launch jobs
    """
    from ROOT import TFile

    jsonFile = open(options.json,'r')
    procList = json.load(jsonFile,encoding = 'utf-8').items()

    # Make a survey of *all* existing plots
    plots = []

    # Read the xsection weights (from cache or from the input files)
    xsecweights = None
    try :
        xsecweights = readXSecWeights(jsonfile=options.json)
    except:
        print '[WARNING] default normalization as stored in the histos will be used'

    missing_files = []
    tagsToFilter = options.filter.split(',')
    baseRootFile = None

    # Input is a single root file with all histograms
    if inDir.endswith('.root'):
        baseRootFile = TFile.Open(inDir)
        plots = getAllPlotsFrom(tdir=baseRootFile,
                                chopPrefix=True,
                                tagsToFilter=tagsToFilter,
                                filterByProcsFromJSON=options.json)

    # Input is a directory with files for each process containing histograms
    else:
        for proc_tag in procList:
            for desc in proc_tag[1]:
                data = desc['data']
                isData = desc.get('isdata',False)
                mctruthmode = desc.get('mctruthmode')
                for process in data:
                    dtag = process.get('dtag','')
                    dset = process.get('dset',dtag)

                    if options.split: # Files are split
                        split = process.get('split',1)
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
                            rootFile.Close()
                            plots = list(set(plots+iplots))
                    else: # Files are merged by processes
                        eventsFile = dtag
                        if mctruthmode:
                            eventsFile += '_filt%d' % mctruthmode
                        rootFileUrl = inDir+'/'+eventsFile+'.root'
                        rootFile = openTFile(rootFileUrl)
                        if rootFile is None:
                            missing_files.append(eventsFile+'.root')
                            continue

                        iplots = getAllPlotsFrom(tdir=rootFile,tagsToFilter=tagsToFilter)
                        rootFile.Close()
                        plots = list(set(plots+iplots))

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

    if options.verbose > 0:
        print " Processing the following plots:"
        print plots

    # Now plot them
    if options.jobs==0:
        for plot in plots:
            makePlot((plot, inDir, procList,
                      xsecweights, options, scaleFactors))

    else:
        from multiprocessing import Pool
        pool = Pool(options.jobs)

        tasklist = [(p, inDir, procList, xsecweights, options, scaleFactors)
                                                              for p in plots]
        pool.map(makePlot, tasklist)


    if baseRootFile is not None: baseRootFile.Close()

def addPlotterOptions(parser):
    parser.add_option('-j', '--json', dest='json',
                      default='test/topss2014/samples.json',
                      help='A json file with the samples to analyze'
                           '[default: %default]')
    parser.add_option('-c', '--checkMissingFiles', dest='checkMissingFiles',
                      action="store_true",
                      help=('Check a directory for missing files (as '
                            'expected from the json file) and exit.'))
    parser.add_option('--cutUnderOverFlow', dest='cutUnderOverFlow',
                      action="store_true",
                      help=('Do not add under and overflow in the '
                            'first and last bins.'))
    parser.add_option('-d', '--debug', dest='debug', action="store_true",
                      help='Dump the event yields table for each plot')
    parser.add_option('--normToData', dest='normToData', action="store_true",
                      help='Force normalization to data')
    parser.add_option('-f', '--filter', dest='filter', default="",
                      help='csv list of plots to produce')
    parser.add_option('-x', '--excludeProcesses', dest='excludeProcesses',
                      default="",
                      help='csv list of processes to exclude')
    parser.add_option('-v', '--verbose', dest='verbose', action="store",
                      type='int', default=0,
                      help='Verbose mode [default: %default (semi-quiet)]')
    parser.add_option('-m', '--plotMask', dest='plotMask',
                      default='',
                      help='Only process plots matching this mask'
                           '[default: all plots]')
    parser.add_option('-l', '--lumi', dest='lumi', default=19701,
                      type='float',
                      help='Re-scale to integrated luminosity [pb]'
                           ' [default: %default]')
    parser.add_option('-o', '--outDir', dest='outDir', default='plots',
                      help='Output directory [default: %default]')
    parser.add_option('--outFile', dest='outFile', default='plotter.root',
                      help=('Output file (in output directory) '
                            '[default: %default]'))
    parser.add_option('-s', '--silent', dest='silent', action="store_true",
                      help='Silent mode (no plots) [default: %default]')
    parser.add_option('--split', dest='split', action="store_true",
                      help='Run on split files')
    parser.add_option('--rereadXsecWeights', dest='rereadXsecWeights',
                      action="store_true",
                      help='Trigger re-reading of xsec weights')
    parser.add_option("--jobs", default=0,
                      action="store", type="int", dest="jobs",
                      help=("Run N jobs in parallel."
                            "[default: %default]"))

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
    addPlotterOptions(parser)
    (opt, args) = parser.parse_args()

    if len(args) > 0:
        if opt.checkMissingFiles:
            checkMissingFiles(inDir=args[0], jsonUrl=opt.json)
            exit(0)

        if opt.rereadXsecWeights:
            indir = args[0]
            jsonfiles = opt.json.split(',')
            exit(makeXSecWeights(indir, jsonfiles, options=opt))

        setTDRStyle()
        gROOT.SetBatch(True)
        gStyle.SetOptTitle(0)
        gStyle.SetOptStat(0)

        os.system('mkdir -p %s'%opt.outDir)
        os.system('rm %s'%os.path.join(opt.outDir,opt.outFile))
        runPlotter(inDir=args[0], options=opt)
        print 'Plots have been saved to %s' % opt.outDir
        exit(0)

    else:
        parser.print_help()
        exit(-1)

