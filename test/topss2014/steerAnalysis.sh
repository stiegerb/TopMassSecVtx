
#!/bin/bash

#
# full analysis
#

step=$1
optim_step=$2
outdir="${CMSSW_BASE}/src/UserCode/TopMassSecVtx/test/topss2014"
indir="/store/cmst3/user/psilva/5311_ntuples"
synchdir="/store/cmst3/group/top/summer2014/synchEx"
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
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/syst_samples.json  -d ${indir} -o ${outdir}/summary_systs/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "2" ]; then
    echo "Making pre-selection plots"
    runPlotter.py -l 19701  -j ${outdir}/samples.json -o ${outdir}/summary/${hash}/plots ${outdir}/summary/${hash} --f vertices;
    echo "You can find the summary plots @ ${outdir}/summary/${hash}/plots"
fi
