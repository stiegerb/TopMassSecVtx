#! /usr/bin/env python
import sys,os,re
import os.path as osp
import pprint

from runPlotter import readXSecWeights
from UserCode.TopMassSecVtx.PlotUtils import bcolors

PLOTS = [
##  ('name',  'branch', 'selection/weight', nbins, minx, maxx)
    # ('jpt',    'jpt[0]',
    #     'w[0]*(abs(evcat)==11&&metpt>30&&nj>3)', 100, 30., 300.),
    # ('met',    'metpt',
    #     'w[0]*(abs(evcat)==11*13&&nj>1)', 100, 0., 200.),
    # ('avpfpt', 'Sum$(pfpt)/Length$(pfpt)',
    #     'w[0]*(abs(evcat)==11&&metpt>30&&nj>3)', 100, 0., 20.)
]

def makeDir(dirname):
    from subprocess import call
    call(['mkdir', '-p', dirname])

def getBareName(path):
    _,filename = osp.split(path)
    barename, ext = osp.splitext(filename)
    return barename

def getProcessNormalization(procname, xsecweights):
    if procname.startswith('Data8TeV'): return 1.0
    searchtag = procname
    if 'filt' in searchtag :
        tkns=procname.split('_')
        searchtag='_'.join(tkns[:-2])+'_'+tkns[-1]
    elif(re.search(r'.*_[0-9]{1,2}?$', procname)): ## ends with a split number
        searchtag = procname.rsplit('_', 1)[0] ## corresponds to dtag in json

    try:
        return xsecweights[searchtag]
    except KeyError:
        print (">>> WARNING: Failed to extract normalization for %s "
               "(setting to 1.0)"%procname)

    return 1.0

def getEOSlslist(directory, mask='', prepend='root://eoscms//eos/cms'):
    from subprocess import Popen, PIPE
    '''Takes a directory on eos (starting from /store/...) and returns
    a list of all files with root://eoscms//eos/cms/ prepended'''
    print 'looking into: '+directory+'...'

    eos_cmd = '/afs/cern.ch/project/eos/installation/0.2.41/bin/eos.select'
    data = Popen([eos_cmd, 'ls', '/eos/cms/'+directory],
                stdout=PIPE)
    out,err = data.communicate()

    full_list = []

    ## if input file was single root file:
    if directory.endswith('.root'):
        if len(out.split('\n')[0]) > 0:
            return [prepend + directory]

    for line in out.split('\n'):
        if len(line.split()) == 0: continue
        ## instead of only the file name append the the string
        ## to open the file in ROOT
        full_list.append(prepend + directory + '/' + line)

    ## strip the list of files
    if mask != '':
        stripped_list = [x for x in full_list if mask in x]
        return stripped_list
    ## if no mask given, run over all files
    else:
        return full_list

def getListOfTasks(directory, mask=''):
    #########################
    ## Single .root file:
    if directory.endswith('.root'):
        if directory.startswith('/store/'):
            # print directory
            # print getEOSlslist(directory)
            return [(getBareName(directory), getEOSlslist(directory)[0])]
        return [(getBareName(directory), directory)]

    #########################
    ## Multiple files
    ## First collect all the files
    file_list = []

    ## Local directory
    if osp.isdir(directory):
        for file_path in os.listdir(directory):
            if file_path.endswith('.root'):
                file_list.append(osp.join(directory,file_path))

    ## Directory on eos
    elif directory.startswith('/store/'):
        file_list = getEOSlslist(directory)

    # pprint.pprint(file_list)


    #########################
    ## Make them into unique tasks
    task_list = []
    for filename in file_list:
        ## Skip toppt weight files
        if filename.endswith('_toppt.root'): continue
        ## Skip pdf weight files
        if filename.endswith('_pdf.root'): continue
        ## Skip anything non-root
        if not filename.endswith('.root'): continue
        task_list.append((getBareName(filename), filename))

    # task_list = []
    # for filename in file_list:
    #     ## Skip toppt weight files
    #     if filename.endswith('_toppt.root'): continue

    #     ## See if the file ends with an index, e.g. filename_2.root
    #     try:
    #         basename,index = re.match("(\S*?)_([\d]*).root$",
    #                                   filename).groups()
    #         task = "%s_*.root" % basename
    #         task_list.append((getBareName(basename),task))
    #     except AttributeError:
    #         ## See if the file has the form filename_3_appendix.root
    #         try:
    #             basename,index,appendix = re.match(
    #                                       "(\S*?)_([\d]*)_(\S*?).root$",
    #                                       filename).groups()
    #             task = "%s_*_%s" %(basename, appendix)
    #             task_name = "%s_%s" % (getBareName(basename), appendix)
    #             task_list.append((task_name, task))
    #         except AttributeError:
    #             ## If neither of the above, and it's a .root file,
    #             ## just add it:
    #             if filename.endswith('.root'):
    #                 task_list.append((getBareName(filename), filename))
    #             ## If not a .root file, skip it and notify us
    #             else:
    #                 print "Skipping", filename

    ## Remove duplicates
    task_list = list(set(task_list))

    ## Apply mask:
    if len(mask) > 0:
        task_list = [(name,fname) for name,fname in task_list if mask in name]

    # pprint.pprint(task_list)
    return task_list

def copyObject(keyname, from_here, to_here):
    from ROOT import TFile
    infile = TFile.Open(from_here, 'read')
    object_ = infile.Get(keyname)
    infile.Close()
    # print 'nevents:', object_[0], 'xsec:', object_[1]
    outfile = TFile.Open(to_here, 'update')
    outfile.cd()
    object_.Write(keyname)
    outfile.Write()
    outfile.Close()
    infile.Close()

def runLxyTreeAnalysisPacked(args):
    name, location, treeloc, xsecweights, maxevents = args
    try:
        return runLxyTreeAnalysis(name, location, treeloc,
                                  xsecweights, maxevents)
    except ReferenceError:
        print 50*'<'
        print "  Problem with", name, "continuing without"
        print 50*'<'
        return False

def runLxyTreeAnalysis(name, location, treeloc, xsecweights=None, maxevents=-1):
    from ROOT import gSystem, TChain

    ## Load the previously compiled shared object library into ROOT
    gSystem.Load("libUserCodeTopMassSecVtx.so")
    ## Load it into PyROOT (this is where the magic happens)
    from ROOT import LxyTreeAnalysis

    print '  ... processing', location

    ## Handle input files
    ch = TChain(treeloc)
    if not location.endswith('.root'):
        ## add all the files in the directory and chain them
        ch.Add(("%s*.root") % location)
    elif location.endswith('.root'):
        ## add a single file
        ch.Add(location)

    # Check tree
    entries = ch.GetEntries()
    if entries<1:
        print 50*'<'
        print "  Problem with", name, "continuing without"
        print 50*'<'
        return False

    weightsDir=os.path.abspath(os.path.join(os.environ['CMSSW_BASE'],
                              'src/UserCode/TopMassSecVtx/data/weights'))
    if 'Data' in name: weightsDir=''
    ana = LxyTreeAnalysis(ch,weightsDir)
    if maxevents > 0:
        ana.setMaxEvents(maxevents)

    ## Get the branching ratio from the json file(s):
    if xsecweights:
        ana.setProcessNormalization(
            getProcessNormalization(name, xsecweights))

    ## Add the plots to LxyTreeAnalysis
    for varname, branch, selection, nbins, minx, maxx in PLOTS:
        ana.AddPlot(varname, branch, selection, nbins, minx, maxx)

    ## Handle output file
    makeDir(opt.outDir)
    output_file = osp.join(opt.outDir, name+".root")

    ## Run the loop
    ana.RunJob(output_file)

    copyObject('constVals', location, output_file)

    print '  ... %s DONE' % name
    return True

def submitBatchJobs(tasks, options, queue='8nh'):
    import time, subprocess, shlex
    cmsswBase = os.environ['CMSSW_BASE']
    baseJobsDir='svlBatchJobs'
    jobsDir = osp.join(cmsswBase,'src/UserCode/TopMassSecVtx/%s'%(baseJobsDir),time.strftime('%b%d'))
    if not osp.exists(jobsDir): os.makedirs(jobsDir)

    print 'Single job scripts stored in %s' % jobsDir

    odirpath = osp.abspath(options.outDir)

    ## Feedback before submitting the jobs
    raw_input('This will submit %d jobs to batch. %s '
              'Did you remember to run scram b?%s \n '
              'Continue?'%(len(tasks), bcolors.RED, bcolors.ENDC))

    for n,task in enumerate(tasks):
        name, url = task
        sys.stdout.write(' ... processing job %3d - %-50s' % (n+1, name))
        sys.stdout.flush()

        scriptFileN = '%s/runLxyTreeAnalysis_%s.sh'%(jobsDir,name)
        scriptFile = open(scriptFileN, 'w')
        scriptFile.write('#!/bin/bash\n')
        scriptFile.write('cd %s/src\n'%cmsswBase)
        scriptFile.write('eval `scram r -sh`\n')
        scriptFile.write('cd %s\n'%jobsDir)
        command = ('runLxyTreeAnalysis.py %s -o %s -t %s -n %d' %
                        (url, odirpath, options.treeLoc, options.maxEvents))
        scriptFile.write('%s\n'%command)
        scriptFile.close()
        os.system('chmod u+rwx %s'%scriptFileN)
        submitcmd = "bsub -q %s -J LxyTA_%s -oo %s \'%s\'"% (
                     queue, name, osp.join(jobsDir,'%s.out'%name), scriptFileN)
        ## FIXME the -oo thing might fail, not tested yet
        os.system(submitcmd)

    sys.stdout.write('%sALL JOBS SUBMITTED %s\n' % (bcolors.OKGREEN, bcolors.ENDC))
    return 0

if __name__ == "__main__":
    from optparse import OptionParser
    usage = """
    Give a directory on eos or a root file as input, e.g.
    \t %prog /store/cmst3/user/psilva/5311_ntuples/summary/
    \t %prog input_dir/
    \t %prog input_dir/MC8TeV_TTJets_MSDecays_173v5_*_filt2.root
    \t %prog MC8TeV_TTJets_MSDecays_173v5_0_filt2.root

    Will then loop on the tree in that file or the trees in
    that directory and run a LxyTreeAnalysis instance on it.

    """
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--outDir", default="lxyplots",
                      action="store", type="string", dest="outDir",
                      help=("Output directory for histogram files "
                            "[default: lxyplots/]"))
    parser.add_option("-l", "--sharedLib", default="libUserCodeTopMassSecVtx.so",
                      action="store", type="string", dest="sharedLib",
                      help=("Shared library for LxyTreeAnalysis class "
                            "[default: %default]"))
    parser.add_option("-t", "--treeLoc", default="dataAnalyzer/lxy",
                      action="store", type="string", dest="treeLoc",
                      help=("Location of tree within file"
                            "[default: %default]"))
    parser.add_option("-p", "--processOnly", default="",
                      action="store", type="string", dest="processOnly",
                      help=("Process only input files matching this"
                            "[default: %default]"))
    parser.add_option("--processOnlyNonExistent", action="store_true",
                      dest="processOnlyNonExistent",
                      help=("Process only input files that are not already"
                            "in the output directory"))
    parser.add_option("-b", "--batch", action="store_true",
                      dest="batch", help="Run jobs on lxbatch")
    parser.add_option("-j", "--jobs", default=0,
                      action="store", type="int", dest="jobs",
                      help=("Run N jobs in parallel."
                            "[default: %default]"))
    parser.add_option("-n", "--maxEvents", default=-1,
                      action="store", type="int", dest="maxEvents",
                      help=("Maximum number of events to process"
                            "[default: %default (all)]"))
    (opt, args) = parser.parse_args()

    if len(args)>0:
        try: xsecweights = readXSecWeights(jsonfile=None)
        except RuntimeError: xsecweights = None

        if len(args) == 1:
            tasks = getListOfTasks(args[0], mask=opt.processOnly)
        else:
            tasks = [(getBareName(x), x) for x in args]

        ## Check for existing output files:
        if opt.processOnlyNonExistent:
            existing = [osp.splitext(osp.basename(f))[0] for f in
                                      os.listdir(opt.outDir) if
                                          osp.splitext(f)[1] == '.root']
            if existing:
                print "Found %d existing files." % len(existing)
                # for fname in existing: print '    %-35s'%fname
            reducedtasks = [(n,f) for n,f in tasks if not n in existing]
            tasks = reducedtasks

        if opt.batch:
            exit(submitBatchJobs(tasks, options=opt))

        if len(tasks)>1:
            print 'Will process the following %d files:'%len(tasks)
            for n,f in tasks:
                print '    %-35s %s' %(n,f)
            if opt.processOnlyNonExistent:
                print (">>> Processing only files that are not found already in "
                       "output directory.")
                print ("     Note that this does not check if those files are "
                       "actually valid.")
                print ("     Make sure you check yourself! "
                       "E.g. with runPlotter.py -c")
            raw_input("Press any key to run on %d files..."%len(tasks))

        if opt.jobs == 0:
            for name, url in tasks:
                runLxyTreeAnalysis(name=name,
                                   location=url,
                                   treeloc=opt.treeLoc,
                                   xsecweights=xsecweights,
                                   maxevents=opt.maxEvents)
        elif opt.jobs > 0:
            from multiprocessing import Pool
            pool = Pool(opt.jobs)

            tasklist = [(name, url, opt.treeLoc, xsecweights, opt.maxEvents)
                               for name,url in tasks]
            pool.map(runLxyTreeAnalysisPacked, tasklist)
            pool.close()
            pool.join()
            print "ALL DONE"
        exit(0)

    else:
        parser.print_help()
        exit(-1)
