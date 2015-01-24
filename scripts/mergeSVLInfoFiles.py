#! /usr/bin/env python
import os, sys
counters = {}

def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def getBaseNames(dirname):
    names = set()
    for item in os.listdir(dirname):
        filename, ext = os.path.splitext(item)
        if not ext == '.root': continue
        try:
            sfilename = filename.split('_',1)
            header = sfilename[0]
            if not header in ['MC8TeV','Data8TeV']: continue
            basename, number = sfilename[1].rsplit('_',1)
            if not number == 'missing' and not isint(number):
                raise ValueError
            key = '_'.join([header,basename])
            try:
                counters[key].append(number)
            except KeyError:
                counters[key] = [number]
            names.add(key)


        except ValueError:
            print filename,'is single'
            names.add(filename)
    return names

try:
    inputdir = sys.argv[1]
    if not os.path.isdir(inputdir):
        print "Input directory not found:", inputdir
        exit(-1)
except IndexError:
    print "Need to provide an input directory."
    exit(-1)

basenames = getBaseNames(inputdir)
print '-----------------------'
print 'Will process the following samples:', basenames

outputdir = os.path.join(inputdir)
chunkdir = os.path.join(inputdir, 'Chunks')

os.system('mkdir -p %s' % chunkdir)

for basename, numbers in counters.iteritems():
    files = [os.path.join(inputdir,"%s_%s.root" % (basename, number)) for number in numbers]
    filenames = " ".join(files)
    target = os.path.join(outputdir,"%s.root" % basename)

    # merging:
    print '... processing', basename
    cmd = 'hadd %s %s' % (target, filenames)
    os.system(cmd)

    # cleanup:
    cmd = '/bin/mv %s %s' % (filenames, chunkdir)
    os.system(cmd)

# merge also the nominal sample
basenames = getBaseNames(inputdir)
nomname = 'MC8TeV_TTJets_MSDecays_172v5'
if (nomname in basenames and nomname+"_v2" in basenames):
    files = [os.path.join(inputdir,"%s.root"%nomname),
             os.path.join(inputdir,"%s_v2.root"%nomname)]
    filenames = " ".join(files)

    target = os.path.join(outputdir,"%s_nom.root" % nomname)
    cmd = 'hadd %s %s' % (target, filenames)
    os.system(cmd)

    cmd = '/bin/mv %s %s' % (filenames, chunkdir)
    os.system(cmd)

    target2 = os.path.join(outputdir,"%s.root" % nomname)
    cmd = '/bin/mv %s %s' % (target, target2)
    os.system(cmd)




