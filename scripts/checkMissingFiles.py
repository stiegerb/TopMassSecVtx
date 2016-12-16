#! /usr/bin/env python
import sys
import os
import json
from ROOT import TFile

from optparse import OptionParser

def eos_ls(directory):
    from subprocess import Popen, PIPE
    '''Takes a directory on eos (starting from /store/...) and returns
    a list of all files with root://eoscms//eos/cms/ prepended'''

    eos_cmd = '/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select'
    data = Popen([eos_cmd, 'ls', directory], stdout=PIPE, shell=False)
    out,err = data.communicate()
    return [f for f in out.split('\n') if not len(f.strip()) == 0]


def checkMissingFiles(inDir, jsonUrl):
    """
    Loop over json inputs and check existence of files.
    If existing, attempts to open files in ROOT.

    Returns a list of missing or bad files
    """

    file_list = []
    remote = False
    try:
        file_list = os.listdir(inDir)
    except OSError:
        remote = True
        file_list = eos_ls(inDir)

    if file_list == []:
        print "Directory does not exist or is empty!"
        return []

    total_expected = 0
    missing_files = []
    suspicious_files = []
    recovered_files = []

    print 'Found %d files in input directory' % len(file_list)
    print 20*'-'

    jsonFile = open(jsonUrl,'r')
    procList = json.load(jsonFile,encoding = 'utf-8').items()

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

                    sys.stdout.write('... checking %s' % filename)
                    sys.stdout.flush()

                    total_expected += 1

                    if not filename in file_list:
                        missing_files.append(filename)
                        sys.stdout.write('\033[91m MISSING \033[0m \n')
                        # sys.stdout.flush()
                        continue

                    rootFileUrl = os.path.join(inDir, filename)
                    if remote:
                        rootFileUrl = ('root://eoscms//eos/cms/store' +
                                        rootFileUrl.split('store',1)[1])

                    recovered, suspicious = False, False
                    tfile = TFile.Open(rootFileUrl)
                    try:
                        if tfile.TestBit(TFile.kRecovered):
                            recovered = True
                        if tfile.IsZombie():
                            suspicious = True
                        tfile.Close()
                    except AttributeError, ReferenceError:
                        suspicious = True

                    if recovered:
                        sys.stdout.write('\033[93m Recovered \033[0m \n')
                        recovered_files.append(filename)
                    if suspicious:
                        sys.stdout.write('\033[93m Failed to open \033[0m \n')
                        suspicious_files.append(filename)

                    sys.stdout.write('\033[92m OK \033[0m \n')
                    sys.stdout.flush()

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
        print "Failed to open the following files:"
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

    return missing_files+suspicious_files+recovered_files


if __name__ == "__main__":
    usage = """
    usage: %prog [options] input_directory
    """
    parser = OptionParser(usage=usage)
    parser.add_option('-j', '--json', dest='json',
                      default='test/topss2014/samples.json',
                      help='A json file with the samples to analyze'
                           '[default: %default]')
    (opt, args) = parser.parse_args()

    bad_files = checkMissingFiles(inDir=args[0], jsonUrl=opt.json)

    sys.exit(len(bad_files))

