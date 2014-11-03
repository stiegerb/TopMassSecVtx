
#!/bin/bash

#
# full analysis
#

step=$1
eosdir=$2
outdir="${CMSSW_BASE}/src/UserCode/TopMassSecVtx/test/topss2014"
indir="/store/cmst3/user/psilva/5311_ntuples"
synchdir="/store/cmst3/group/top/summer2014/synchEx"
plotsdir="~`whoami`/public/html/TopMassSecVtx/"
cfg="$CMSSW_BASE/src/UserCode/TopMassSecVtx/test/runAnalysis_cfg.py.templ"
queue=1nd
hash=e1fa735

#prepare output directories
mkdir -p ${outdir}/summary/

if [ "$step" == "0" ]; then
    echo "Submitting selection synchronization"
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/synch_samples.json  -d ${synchdir} -o ${outdir}/summary/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -f ${hash};
    python test/topss2014/showSynchTable.py ${outdir}/summary/${hash} > synch_results.txt;
    cat synch_results.txt;
fi

if [ "$step" == "1" ]; then
    echo "Submitting sample pre-selection"
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/samples.json  -d ${indir} -o ${outdir}/summary/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "2" ]; then
    echo "Making pre-selection plots"
    if [ -z $eosdir ]; then
	runPlotter.py -l 19701  -j ${outdir}/samples.json -o ${plotsdir}/plots ${outdir}/summary/${hash};
    else
	runPlotter.py -l 19701  -j ${outdir}/samples.json -o ${plotsdir}/plots ${eosdir};
    fi
    echo "You can find the summary plots @ ${outdir}/summary/${hash}/plots"
fi

if [ "$step" == "3" ]; then
    echo "Submitting systematic samples"
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/syst_samples.json  -d ${indir} -o ${outdir}/summary_systs/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "4" ]; then
    echo "Submitting mass scan samples"
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/mass_scan_samples.json  -d ${indir} -o ${outdir}/mass_scan/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "5" ]; then
    echo "Submitting control analysis"

    ctrlJsons=("qcd_samples")
    for ijson in ${ctrlJsons[@]}; do
	runLocalAnalysisOverSamples.py -e runControlAnalysis -j ${outdir}/${ijson}.json  -d /store/cmst3/user/psilva/5311_qcd_ntuples -o ${outdir}/${ijson}/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    done

    ctrlJsons=("z_samples" "w_samples" "photon_samples")
    for ijson in ${ctrlJsons[@]}; do
	runLocalAnalysisOverSamples.py -e runControlAnalysis -j ${outdir}/${ijson}.json  -d ${indir} -o ${outdir}/${ijson}/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    done
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "6" ]; then
    ctrlJsons=("qcd_samples" "z_samples" "w_samples" "photon_samples")
    for ijson in ${ctrlJsons[@]}; do
	echo "Making pre-selection plots for ${ijson}"
	runPlotter.py -l 19701  -j ${outdir}/${ijson}.json -o ${plotsdir}/${ijson}_plots ${outdir}/${ijson}/${hash};
    done
fi