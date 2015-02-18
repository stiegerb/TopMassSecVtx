#!/bin/bash
WHAT=$1; if [[ "$1" == "" ]]; then echo "runAll.sh <TREES/ALLTREES/MERGE/PLOTS/FITS>"; exit 1; fi
TAG=$2

treedir=/afs/cern.ch/work/s/stiegerb/TopSecVtx/SVLInfo/${TAG}/

mkdir -p ${treedir}

# hash="a176401"
hash="e1fa735"

echo "Running on "${treedir}

case $WHAT in
	TREES )
		./scripts/runLxyTreeAnalysis.py -o ${treedir} -p MC8TeV   -j 8 /store/cmst3/group/top/summer2014/${hash}/
		hash="a176401"
		./scripts/runLxyTreeAnalysis.py -o ${treedir} -p Data8TeV -j 8 /store/cmst3/group/top/summer2014/${hash}/
		;;
	DATATREES )
		hash="a176401"
		./scripts/runLxyTreeAnalysis.py -o ${treedir} -p Data8TeV -j 8 /store/cmst3/group/top/summer2014/${hash}/
		;;
	ALLTREES )
		./scripts/runLxyTreeAnalysis.py -o ${treedir}            -j 8 /store/cmst3/group/top/summer2014/${hash}/
		./scripts/runLxyTreeAnalysis.py -o ${treedir}/mass_scan/ -j 8 /store/cmst3/group/top/summer2014/${hash}/mass_scan/
		./scripts/runLxyTreeAnalysis.py -o ${treedir}/syst/      -j 8 /store/cmst3/group/top/summer2014/${hash}/syst/
		;;
	MERGE )
		# ./scripts/mergeSVLInfoFiles.py ${treedir}
		./scripts/mergeSVLInfoFiles.py ${treedir}/mass_scan/
		./scripts/mergeSVLInfoFiles.py ${treedir}/syst/
		;;
	PLOTS )
		./scripts/makeSVLDataMCPlots.py ${treedir}  -o svlplots/${TAG}
		./scripts/makeSVLControlPlots.py ${treedir} -o svlplots/${TAG}
		;;
	FITS )
		./scripts/makeSVLWorkspace.py -i .svlhistos.pck -j 8 -o svlfits/${TAG}
		;;
esac
