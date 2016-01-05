#!/bin/bash

step=$1
outdir="${CMSSW_BASE}/src/UserCode/TopMassSecVtx/test/topss2014"
indir="/store/cmst3/user/psilva/5311_ntuples"
cfg="$CMSSW_BASE/src/UserCode/TopMassSecVtx/test/runAnalysis_cfg.py.templ"
queue=2nd
hash=bbbcb36

#prepare output directories
mkdir -p ${outdir}/summary/

if [ "$step" == "presel" ]; then
    echo "Submitting sample pre-selection"
    runLocalAnalysisOverSamples.py -e runDileptonAnalysis -j ${outdir}/samples.json  -d ${indir} -o ${outdir}/summary/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "syst" ]; then
    echo "Submitting systematic samples"
    runLocalAnalysisOverSamples.py -e runDileptonAnalysis -j ${outdir}/syst_samples.json  -d ${indir} -o ${outdir}/summary_systs/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "mass" ]; then
    echo "Submitting mass scan samples"
    runLocalAnalysisOverSamples.py -e runDileptonAnalysis -j ${outdir}/mass_scan_samples.json  -d ${indir} -o ${outdir}/mass_scan/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "${step}" == "pdf" ]; then
    runLocalAnalysisOverSamples.py -e computePDFvariations -j ${outdir}/samples.json -o ${outdir}/summary/${hash} -d ${indir} -c ${cfg} -t MC -s 2nw;
fi
