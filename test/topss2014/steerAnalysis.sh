#!/bin/bash

#
# full analysis
#

step=$1
optim_step=$2
outdir="${CMSSW_BASE}/src/UserCode/llvv_fwk/test/topss2014"
indir="/store/cmst3/user/psilva/5311_ntuples"
cfg="$CMSSW_BASE/src/UserCode/llvv_fwk/test/runAnalysis_cfg.py.templ"
queue=2nw

#prepare output directories
mkdir -p ${outdir}/summary/

if [ "$step" == "1" ]; then
    echo "Submitting sample pre-selection"
    #runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/samples.json  -d ${indir} -o ${outdir}/summary/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue}; 
    runLocalAnalysisOverSamples.py -e runTopAnalysis -j ${outdir}/samples.json  -d ${indir} -o ${outdir}/summary/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -t _tW;
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "2" ]; then
    echo "Computing weights"
    runPlotter --iLumi 19736 --inDir ${outdir}/summary/ --json ${outdir}/samples.json --outFile ${outdir}/plotter.root --forceMerged;
fi
