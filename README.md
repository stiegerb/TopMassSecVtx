------------------------------------------------------
### Installation

```
ssh lxplus
scramv1 project CMSSW CMSSW_5_3_22
cd CMSSW_5_3_22/src/
cmsenv
wget -q -O - --no-check-certificate https://raw.github.com/stiegerb/TopMassSecVtx/master/TAGS.txt | sh
git clone git@github.com:stiegerb/TopMassSecVtx.git UserCode/TopMassSecVtx
scram b -j 9
```

Note: the ntuplizer is running without pileup jet id and IVF-related b-tagging variables

------------------------------------------------------
### Producing the trees

```
sh test/topss2014/submitNtupleProduction.sh [sample=presel,syst,mass,control,pdf]
```
Will create the base ntuple summary
```
./scripts/runPlotter.py --rereadXsecWeights /store/cmst3/group/top/summer2014/a176401/ -j test/topss2014/samples.json,test/topss2014/syst_samples.json,test/topss2014/mass_scan_samples.json,test/topss2014/qcd_samples.json,test/topss2014/z_samples.json,test/topss2014/photon_samples.json
```
Will create a pickle file summarizing all the cross section-based normalization to be used
```
./scripts/runLxyTreeAnalysis.py -o treedir -j 8 /store/cmst3/group/top/summer2014/a176401/
./scripts/runLxyTreeAnalysis.py -o treedir/syst/ -j 8 /store/cmst3/group/top/summer2014/a176401/syst/
./scripts/runLxyTreeAnalysis.py -o treedir/mass_scan/ -j 8 /store/cmst3/group/top/summer2014/a176401/mass_scan/
./scripts/runLxyTreeAnalysis.py -o treedir/qcd_control/ -j 8 /store/cmst3/group/top/summer2014/a176401/qcd_control/
./scripts/runLxyTreeAnalysis.py -o treedir/z_control/ -j 8 /store/cmst3/group/top/summer2014/a176401/z_control/
./scripts/runLxyTreeAnalysis.py -o treedir/photon_control/ -j 8 /store/cmst3/group/top/summer2014/a176401/photon_control/
```
Creates the SVLInfo/CharmInfo trees with the condensed summary info for the final analysis
------------------------------------------------------
### Merging the trees

```
./scripts/mergeSVLInfoFiles.py treedir/
./scripts/mergeSVLInfoFiles.py treedir/syst/
./scripts/mergeSVLInfoFiles.py treedir/mass_scan/
./scripts/mergeSVLInfoFiles.py treedir/qcd_control/
./scripts/mergeSVLInfoFiles.py treedir/z_control/
./scripts/mergeSVLInfoFiles.py treedir/photon_control/
```
Will merge all the chunks and then move them into treedir/Chunks/
There is a version of the trees from Feb10 that is still current in:
```
/afs/cern.ch/work/s/stiegerb/TopSecVtx/SVLInfo/Feb10
```
You can draw the plots with
runPlotter.py -l 19701  -j test/topss2014/samples.json -o treedir/plots treedir

------------------------------------------------------
### Producing systematics plots and mass scans

```
./scripts/makeSVLSystPlots.py treedir/
./scripts/makeSVLMassHistos.py treedir/
```
Will run the plots and put them in svlplots/ by default. Also saves the histograms in a cachefile. To rerun only the plotting part, run with -c option.


------------------------------------------------------
### Producing data/MC comparison plots

```
./scripts/makeSVLDataMCPlots.py treedir/

```
Produces a number of data/MC comparison plots (both from the SVLInfo trees, and from the histograms produced in the LxyTreeAnalysis). Default output directory is plots/. This is based on the runPlotter.py script. In order to have correct xsection weights and number of generated events, one needs to run on the eos/ directory first to produce a cache file with the weights, like so:


------------------------------------------------------
### Running the fits

```
./scripts/runSVLFits.py
```
Prepares the workspace for the fits and put the RooFit workspace and plots in svlfits/ by default.
```
./scripts/runSVLPseudoExperiments.py SVLWorkspace.root pe_inputs.root nominal_172v5
```
Will run the pseudoexperiment for one variation (e.g. nominal_172v5).

```
./scripts/runSVLPseudoExperiments.py SVLWorkspace.root pe_inputs.root
```
Will run all the pseudoexperiments for all variation on batch.

------------------------------------------------------
### Producing QCD Templates
makeSVLQCDTemplates.py produces MET and m(l,SV) distributions from the non-isolated data control region and stores them in qcd_templates.root.
qcdFitter.py fits the MET distribution in the l+jets signal region, using the shapes from the non-isolated region produced by makeSVLQCDTemplates.py and produces m(l,SV) templates scaled according to the outcome of the fit.
It takes as input a plotter.root file (from makeSVLDataMCPlots.py) with properly scaled MET distributions in the signal region.
```
./scripts/makeSVLQCDTemplates.py treedir/
./test/topss2014/qcdFitter.py plotter.root qcd_templates.root
```
Control region analysis
```
./scripts/fitSecVtxProperties.py -i treedir/qcd_control    -o treedir/qcd_control/plots/    --weightPt --onlyCentral --minLxySig 10
./scripts/fitSecVtxProperties.py -i treedir/z_control      -o treedir/z_control/plots/      --weightPt --vetoCentral
./scripts/fitSecVtxProperties.py -i treedir/photon_control -o treedir/photon_control/plots/ --weightPt --rebin 2
`````
After creating the workspace you can use it directly by using -w workspace.root instead of -i ntuple_dir

