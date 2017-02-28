#!/bin/bash

#
# full analysis
#

step=$1
outdir="${CMSSW_BASE}/src/UserCode/TopMassSecVtx/test/topppref"
indir="/store/cmst3/user/psilva/5311_ntuples"
plotsdir="${HOME}/public/html/topppref/"
cfg="$CMSSW_BASE/src/UserCode/TopMassSecVtx/test/runAnalysis_cfg.py.templ"
queue=1nd
hash=c025091
rootDir=${outdir}/summary/${hash}

#prepare output directories
mkdir -p ${outdir}/summary/

if [ "$step" == "presel" ]; then
    echo "Submitting sample pre-selection"
    runLocalAnalysisOverSamples.py -e runLJppReferenceAnalysis -j ${outdir}/samples.json  -d ${indir} -o ${outdir}/summary/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "syst" ]; then
    echo "Submitting systematic samples"
    runLocalAnalysisOverSamples.py -e runLJppReferenceAnalysis -j ${outdir}/syst_samples.json  -d ${indir} -o ${outdir}/summary_systs/ -c ${cfg} -p "@saveSummaryTree=True @weightsFile='data/weights/'" -s ${queue} -f ${hash};
    echo "You can find a summary with the selected events @ ${outdir} after all jobs have finished"
fi

if [ "$step" == "weights" ]; then
    echo "Computing weights and checking missing files"
    ./scripts/runPlotter.py ${rootDir} -j test/topppref/samples.json --rereadXsecWeights -c 
fi

if [ "$step" == "merge" ]; then
    echo "Merging output files and moving fragments to Chunks"
    ./scripts/mergeSVLInfoFiles.py ${rootDir}
fi

if [ "$step" == "plot" ]; then
    echo "Plotting, estimating QCD and re-plotting"
    #./scripts/runPlotter.py ${rootDir} -j test/topppref/samples.json -o ${rootDir}/plots --outFile raw_plotter.root 
    python test/topppref/runQCDEstimation.py --in ${rootDir}/plots/raw_plotter.root  --out test/topppref/summary/c025091/
    ./scripts/runPlotter.py ${rootDir} -j test/topppref/samples.json -o ${rootDir}/plots --filter mt
fi

if [ "$step" == "www" ]; then
    echo "Moving plots to http://`whoami`.web.cern.ch/`whoami`/LJets-ppref/"
    mkdir -p ~/www/LJets-ppref
    mv ${rootDir}/plots/*.{png,pdf} ~/www/LJets-ppref
fi