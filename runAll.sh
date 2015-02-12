#!/bin/bash
WHAT=$1; if [[ "$1" == "" ]]; then echo "runAll.sh <TREES/ALLTREES/MERGE/PLOTS/FITS>"; exit 1; fi

tag=Feb12
# tag=Feb6
# tag=Nov14
# tag=Aug28
# tag=Sep18
treedir=/afs/cern.ch/work/s/stiegerb/TopSecVtx/SVLInfo/${tag}/
# treedir=/data/stiegerb/topss2014/hidde/lxyplots_${tag}/

mkdir -p ${treedir}

hash="e1fa735"

echo "Running on "${treedir}

case $WHAT in
	TREES )
		./scripts/runLxyTreeAnalysis.py -p MC8TeV_TTJets_MSDecays_172v5 -o ${treedir} -j 8 /store/cmst3/group/top/summer2014/${hash}/
		./scripts/runLxyTreeAnalysis.py -p Data8TeV -o ${treedir} -j 8 /store/cmst3/group/top/summer2014/${hash}/
		./scripts/runLxyTreeAnalysis.py -p MC8TeV_TTJets_TuneP11_ -o ${treedir} -j 8 /store/cmst3/group/top/summer2014/${hash}/syst/
		./scripts/runLxyTreeAnalysis.py -p MC8TeV_TT_Z2star_powheg_pythia -o ${treedir} -j 8 /store/cmst3/group/top/summer2014/${hash}/syst/
		./scripts/runLxyTreeAnalysis.py -p MC8TeV_TT_AUET2_powheg_herwig -o ${treedir} -j 8 /store/cmst3/group/top/summer2014/${hash}/syst/
		;;
	ALLTREES )
		./scripts/runLxyTreeAnalysis.py -o ${treedir}            -j 8 /store/cmst3/group/top/summer2014/${hash}/
		./scripts/runLxyTreeAnalysis.py -o ${treedir}/mass_scan/ -j 8 /store/cmst3/group/top/summer2014/${hash}/mass_scan/
		./scripts/runLxyTreeAnalysis.py -o ${treedir}/syst/      -j 8 /store/cmst3/group/top/summer2014/${hash}/syst/
		;;
	MERGE )
		./scripts/mergeSVLInfoFiles.py ${treedir}
		./scripts/mergeSVLInfoFiles.py ${treedir}/mass_scan/
		./scripts/mergeSVLInfoFiles.py ${treedir}/syst/
		;;
	SVLPLOTS )
		./scripts/makeSVLControlPlots.py ${treedir} -o svlplots/${tag}
		./scripts/makeSVLDataMCPlots.py ${treedir}  -o svlplots/${tag}
		;;
	FITS )
		./scripts/makeSVLWorkspace.py -i .svlhistos.pck -j 8 -o svlfits/${tag}
		;;
esac
