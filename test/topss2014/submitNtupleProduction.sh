#!/bin/bash

#
# full analysis
#

step=$1
eosdir=$2
outdir="${CMSSW_BASE}/src/UserCode/TopMassSecVtx/test/topss2014"
indir="/store/cmst3/user/psilva/5311_ntuples"
synchdir="/store/cmst3/group/top/summer2014/synchEx"
plotsdir="${HOME}/public/html/TopMassSecVtx/"
cfg="$CMSSW_BASE/src/UserCode/TopMassSecVtx/test/runAnalysis_cfg.py.templ"
queue=1nd
hash=bbbcb36

#prepare output directories
mkdir -p ${outdir}/summary/

if [ "$step" == "synch" ]; then
    echo "Submitting selection synchronization"
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/synch_samples.json  -d ${synchdir} -o ${outdir}/summary/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -f ${hash};
    python test/topss2014/showSynchTable.py ${outdir}/summary/${hash} > synch_results.txt;
    cat synch_results.txt;
fi

if [ "$step" == "presel" ]; then
    echo "Submitting sample pre-selection"
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/samples.json  -d ${indir} -o ${outdir}/summary/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "syst" ]; then
    echo "Submitting systematic samples"
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/syst_samples.json  -d ${indir} -o ${outdir}/summary_systs/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash} -t Full;
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "mass" ]; then
    echo "Submitting mass scan samples"
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/mass_scan_samples.json  -d ${indir} -o ${outdir}/mass_scan/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "${step}" == "pdf" ]; then
    MCTREEDIR=/store/cmst3/group/top/summer2015/${hash};
    echo "WARNING: Using MC trees stored at ${MCTREEDIR}";
    runLocalAnalysisOverSamples.py -e computePDFvariations -j ${outdir}/samples.json -o ${outdir}/summary/${hash} -d ${MCTREEDIR} -c ${cfg} -t MC -s 2nw;
fi

if [ "$step" == "control" ]; then
    echo "Submitting control analysis"

    #ctrlJsons=("qcd_samples")
    #for ijson in ${ctrlJsons[@]}; do
    #runLocalAnalysisOverSamples.py -e runControlAnalysis -j ${outdir}/${ijson}.json  -d /store/cmst3/user/psilva/5311_qcd_ntuples -o ${outdir}/${ijson}/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    #done

    ctrlJsons=("z_syst_samples" "z_samples") #"z_samples"  "photon_samples" "w_samples")
    for ijson in ${ctrlJsons[@]}; do
	runLocalAnalysisOverSamples.py -e runControlAnalysis -j ${outdir}/${ijson}.json  -d ${indir} -o ${outdir}/${ijson}/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    done
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi
