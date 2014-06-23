
#!/bin/bash

#
# full analysis
#

step=$1
optim_step=$2
outdir="${CMSSW_BASE}/src/UserCode/llvv_fwk/test/topss2014"
indir="/store/cmst3/user/psilva/5311_ntuples"
cfg="$CMSSW_BASE/src/UserCode/llvv_fwk/test/runAnalysis_cfg.py.templ"
queue=8nh
hash=f0599ff

#prepare output directories
mkdir -p ${outdir}/summary/

if [ "$step" == "1" ]; then
    echo "Submitting sample pre-selection"
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/samples.json  -d ${indir} -o ${outdir}/summary/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/syst_samples.json  -d ${indir} -o ${outdir}/summary_systs/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "2" ]; then
    echo "Making pre-selection plots"
    runPlotter.py -l 19736  -j ${outdir}/samples.json -o ${outdir}/summary/${hash}/plots ${outdir}/summary/${hash};
    echo "You can find the summary plots @ ${outdir}/summary/${hash}/plots"
fi
