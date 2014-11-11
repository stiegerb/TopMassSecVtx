#! /usr/bin/env python
import os,re
import pprint

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
    _,filename = os.path.split(path)
    barename, ext = os.path.splitext(filename)
    return barename

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
    if os.path.isdir(directory):
        for file_path in os.listdir(directory):
            if file_path.endswith('.root'):
                file_list.append(os.path.join(directory,file_path))

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
        task_list = [(name,task) for name,task in task_list if mask in name]

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
    name, location, treeloc, maxevents = args
    try:
        return runLxyTreeAnalysis(name, location, treeloc, maxevents)
    except ReferenceError:
        print 50*'<'
        print "  Problem with", name, "continuing without"
        print 50*'<'
        return False

def runLxyTreeAnalysis(name, location, treeloc, maxevents=-1):
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

    ana = LxyTreeAnalysis(ch)
    if maxevents > 0:
        ana.setMaxEvents(maxevents)

    ## Add the plots to LxyTreeAnalysis
    for varname, branch, selection, nbins, minx, maxx in PLOTS:
        ana.AddPlot(varname, branch, selection, nbins, minx, maxx)

    ## Handle output file
    makeDir(opt.outDir)
    output_file = os.path.join(opt.outDir, name+".root")

    ## Run the loop
    ana.RunJob(output_file)

    copyObject('constVals', location, output_file)

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
        if len(args) == 1:
            tasks = getListOfTasks(args[0], mask=opt.processOnly)
        else:
            tasks = [(getBareName(x), x) for x in args]

        if opt.jobs == 0:
            for name, task in tasks:
                runLxyTreeAnalysis(name=name,
                                   location=task,
                                   treeloc=opt.treeLoc,
                                   maxevents=opt.maxEvents)
        else:
            from multiprocessing import Pool
            pool = Pool(opt.jobs)

            tasklist = [(name, task, opt.treeLoc, opt.maxEvents) for name,
                                                                     task in tasks]
            pool.map(runLxyTreeAnalysisPacked, tasklist)

        exit(0)

    else:
        parser.print_help()
        exit(-1)
