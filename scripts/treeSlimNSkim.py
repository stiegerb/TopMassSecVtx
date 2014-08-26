#! /usr/bin/env python

########################################
# Slims and skims trees
#
# Original authour: Duc Bao Ta duct@nikhef.nl
########################################

import ROOT
import sys
import re
import time
from optparse import OptionParser

STARTTIME=time.time()

in_ex_branch=[]
def include_list (option, opt_str, value, parser):
	in_ex_branch.append(value+"+")

def exclude_list (option, opt_str, value, parser):
	in_ex_branch.append(value+"-")

def include_file (option, opt_str, value, parser):
	for l in file(value):
		in_ex_branch.append(l.strip()+"+")

def exclude_file (option, opt_str, value, parser):
	for l in file(value):
		in_ex_branch.append(l.strip()+"-")

def in_file (option, opt_str, value, parser):
	for l in file(value):
		in_ex_branch.append(l.strip())

def outputtime():
	print "-"*5,round(time.time()-STARTTIME,3),time.asctime(),"-"*5

def slimAndSkim(files,
	            cut,
	            in_ex_branch,
	            output,
	            treeloc='dataAnalyzer/lxy'):
	print "-"*40
	print "Using input files:"
	print files
	print "Writing to", output

	outputtime()

	## Get input files
	mainchain = ROOT.TChain(treeloc)
	print "chain", treeloc
	for filename in files:
		mainchain.Add(filename)
		print " ... adding file",filename

	outputtime()

	## Apply cut and get entrylist to loop over
	if cut:
		outputtime()
		print " ... creating cut", cut
		cut = ROOT.TCut(cut)
		cutnumber = mainchain.Draw(">>cutlist",cut,"entrylist")
		cutlist = ROOT.gDirectory.Get("cutlist")
		mainchain.SetEntryList(cutlist)
		print (" Cut reduced number of events from %d to %d" %
			    (mainchain.GetEntries(), cutnumber))

	outputtime()

	## Get list of branches to activate
	brancheslist = []
	allbranches = [br.GetName() for br in mainchain.GetListOfBranches()]

	if len(in_ex_branch)==0 or (in_ex_branch[0][-1])=="-":
		brancheslist=allbranches[:]

	print (" Starting with %d (%d) branches" %
		     (len(brancheslist), len(allbranches)) )
	for branch in in_ex_branch:
		if branch[-1]=="+":
			brancheslist += [b for b in allbranches if
			                         re.match(branch[:-1],b)!=None]
		if branch[-1]=="-":
			brancheslist = [b for b in brancheslist if
			                         re.match(branch[:-1],b)==None ]
		print " ... after",branch,"have",len(brancheslist),"branches"

	outputtime()

	## Activate necessary branches
	print " ... activate branches", len(brancheslist)
	mainchain.SetBranchStatus("*", 0)
	for branch in brancheslist:
		mainchain.SetBranchStatus(branch,1)

	outputtime()

	## Create output file
	print "new file",output
	newfile = ROOT.TFile(output,"recreate")

	## Copy the tree
	print "copy main tree",treeloc
	newtree = mainchain.CopyTree("")

	## Write out new tree
	if '/' in treeloc:
		newdir = newfile.mkdir(treeloc.split('/',1)[0])
		newdir.cd()
	newtree.Write()
	newfile.Close()

	outputtime()
	print "DONE"
	print '-'*40

def main(options, args):
	## Get input files
	files = []
	for arg in args:
		if "," in arg:
			files += arg.split(",")
		else:
			files.append(arg)
	slimAndSkim(files=files,
	            cut=options.cut,
	            in_ex_branch=in_ex_branch,
	            output=options.output,
	            treeloc=options.maintree)
	exit(0)


def addOptions(parser):
	parser.add_option("-t", "--maintree", action="store",
	                  type="str", dest="maintree",
	                  default="dataAnalyzer/lxy",
	                  help=("tree name whose branches are removed and on "
                            "which the cuts are applied, default=%default"))
	parser.add_option("-i", "--include", action="callback", type="str",
                      callback=include_list, help="branches to include")
	parser.add_option("-e", "--exclude", action="callback", type="str",
                      callback=exclude_list, help="branches to exclude")
	parser.add_option("-f", "--fileinclude", action="callback", type="str",
                      callback=include_file,
                      help="file with branch names to include")
	parser.add_option("-F", "--fileexclude", action="callback", type="str",
                      callback=exclude_file,
                      help="file with branch names to exclude")
	parser.add_option("-I", "--includefromfile", action="callback",
	                  type="str", callback=in_file,
                      help=("file with branch name to in- and exclude, add "
                      	    "+ or - at the end of the name"))
	parser.add_option("-c", "--cut", action="store", type="str", dest="cut",
                      help="cut on tree")
	parser.add_option("-o", "--output", action="store", type="str",
		              dest="output", default="output.root",
	                  help="output filename, default=%default")

if __name__ == '__main__':
	usage = """
	usage: %prog [options] input_filename
	Use to slim and skim trees on the command line.
	Branches are included or excluded by using -i or -e.
	The branch names are interpreted as regular expressions (python style),
	i.e. -i \"jet\" means to include all branches starting with \"jet\".
	Note that the order of in- and exclusion matters.
	If you start with an exclusion, the branches are excluded
	from a list of all branches.
	The CollectionTree is automatically copied to the new file.
	It is merged to the physics tree if you apply a cut.
	Branches from the CollectionTree cannot be excluded.
	You can in-/exclude branches from a files with -f/-F.
	You can also use one file with -I,
	add +/- at the end of the branch name for in/-exclusion.
	"""
	parser = OptionParser(usage=usage)
	addOptions(parser)
	(options, args) = parser.parse_args()

	if len(args)<1:
		parser.print_help()
		exit(-1)

	main(options, args)
	exit(0)

