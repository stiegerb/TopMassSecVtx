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
./scripts/runPlotter.py --rereadXsecWeights /store/cmst3/group/top/summer2015/bbbcb36/ -j test/topss2014/samples.json,test/topss2014/syst_samples.json,test/topss2014/mass_scan_samples.json,test/topss2014/qcd_samples.json,test/topss2014/z_samples.json,test/topss2014/z_syst_samples.json,test/topss2014/photon_samples.json
```
Will create a pickle file summarizing all the cross section-based normalization to be used
```
./scripts/runLxyTreeAnalysis.py -o treedir -j 8 /store/cmst3/group/top/summer2015/bbbcb36/
./scripts/runLxyTreeAnalysis.py -o treedir/syst/ -j 8 /store/cmst3/group/top/summer2015/bbbcb36/syst/
./scripts/runLxyTreeAnalysis.py -o treedir/mass_scan/ -j 8 /store/cmst3/group/top/summer2015/bbbcb36/mass_scan/
./scripts/runLxyTreeAnalysis.py -o treedir/qcd_control/ -j 8 /store/cmst3/group/top/summer2015/bbbcb36/qcd_control/
./scripts/runLxyTreeAnalysis.py -o treedir/z_control/ -j 8 /store/cmst3/group/top/summer2015/bbbcb36/z_control/
./scripts/runLxyTreeAnalysis.py -o treedir/photon_control/ -j 8 /store/cmst3/group/top/summer2015/bbbcb36/photon_control/
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
./scripts/makeSVLMassHistos.py treedir/ -j 8 -o outDir/
./scripts/makeSVLSystPlots.py treedir/ -j 8 -o outDir/
```
Will run the plots and put them in svlplots/ by default. Also saves the histograms in a cachefile. To rerun only the plotting part, run with -c option.
(makeSVLMassHistos takes about 10 min to run with -j 8, makeSVLSystPlots takes about 50 min. Run both with -c to just produce the plots from pre-cached files.)


------------------------------------------------------
### Producing data/MC comparison plots

In order to have correct xsection weights and number of generated events, one needs to run on the eos/ directory first to produce a cache file with the weights, like so:
```
./scripts/runPlotter.py --rereadXsecWeights /store/cmst3/group/top/summer2015/bbbcb36/ -j test/topss2014/samples.json,test/topss2014/syst_samples.json,test/topss2014/mass_scan_samples.json
```
Then use ```makeSVLDataMCPlots.py``` to produce data/MC comparison plots:
```
./scripts/makeSVLDataMCPlots.py treedir/ -j test/topss2014/samples.json -o outDir/
```
This produces a number of data/MC comparison plots (both from the SVLInfo trees, and from the histograms produced in the LxyTreeAnalysis). Default output directory is plots/. This is based on the runPlotter.py script.
The script also produces the DY scale factors and applies them directly. It puts the control plots in a sub-directory called ```dy_control```. Note that they are read from the cachefile (.svldyscalefactors.pck) by default. To reproduced them from scratch, delete the cachfile first. To produce only the scale factors, use the ```extractDYScaleFactor.py``` script, e.g. 
```
./scripts/extractDYScaleFactor.py outDir/plotter.root  --verbose 5
```
Notice it is not needed to run it explicitely after makeSVLDataMCPlots.py has been run.
To print event yields, run ```printSVLEventYields.py``` on the output of the script above:
```
./scripts/printSVLEventYields.py outDir/plotter.root
```
To extract the parametrization to reweight the number of tracks in the SVtx to data
```
python scripts/extractNtrkWeights.py outDir/plotter.root -v 5
````

---------------------------------------------------
### Produce QCD Templates

```makeSVLQCDTemplates.py``` produces MET and m(l,SV) distributions from the non-isolated data control region and stores them in qcd_templates.root. (Takes about 5 min to run. Run with --cached to run from cached files.)

```qcdFitter.py``` fits the MET distribution in the l+jets signal region, using the shapes from the non-isolated region produced by ```makeSVLQCDTemplates.py``` and produces m(l,SV) templates scaled according to the outcome of the fit.
It takes as input a runPlotter output file produced by ```makeSVLQCDTemplates.py``` called ```scaled_met_inputs.root``` with properly scaled MET distributions in the signal region, and a file with the final qcd templates, also produced by ```makeSVLQCDTemplates.py``` called ```qcd_templates.root```.
```
./scripts/makeSVLQCDTemplates.py treedir/ -o svlplots/qcd/
./test/topss2014/qcdFitter.py svlplots/qcd/scaled_met_inputs.root svlplots/qcd/qcd_templates.root -s
```


------------------------------------------------------
### Running the fits

Prepare the pseudoexperiment inputs, which also prepares the background templates for the fitting model.

```
./scripts/prepareSVLPEInputs.py treedir -o svlplots/ -v 5
```
Reads the mass scans, systematics histos, and qcd templates from the corresponding cache files, and produces a ```pe_inputs.root``` file with the input histograms for running pseudo experiments. Also produces the correctly scaled and added background template shapes and writes them to a cache file to be used in the fitting.

Produce summary plots of the pseudoexperiment inputs:
```
./scripts/summarizeSVLresults.py --pe svlplots/pe_inputs.root --rebin 2
```
By default the plots are put in the input directory, under ```plots/```.

```
./scripts/runSVLFits.py -o svlfits/
```
Prepares the workspace for the fits and put the RooFit workspace and plots in svlfits/ by default. By default, takes ```.svlmasshistos.pck``` and ```.svlbgtemplates.pck``` as input for the shapes. (Takes about 45 min to run.)

```
./scripts/runSVLPseudoExperiments.py svlfits/SVLWorkspace.root svlplots/pe_inputs.root nominal_172v5
```
Will run the pseudoexperiments for a single variation (e.g. nominal_172v5). Verbose level above 5 prints the result of each channel for each single experiment.

```
./scripts/runSVLPseudoExperiments.py svlfits/SVLWorkspace.root svlplots/pe_inputs.root -s optmrank
```
Will run all the pseudoexperiments for all variation on batch. The output (and individual scripts) will be stored under ```svlPEJobs/```. Use ```-f --filter``` option to process only selected variations.

```
./scripts/summarizeSVLresults.py --calib svlPEJobs/optmrank/Apr25/
```
Will parse the summaries of the pseudo-experiments and produce a calibration file.

```
./scripts/runSVLPseudoExperiments.py svlfits/SVLWorkspace.root svlplots/pe_inputs.root -c svlPEJobs/optmrank/Apr25/.svlcalib.pck -s optmrank
```
Will run the calibrated pseudo-experiments
```
./scripts/summarizeSVLresults.py --syst svlPEJobs_calib/optmrank/Apr25/.svlcalib.pck
```
Will printout the "final" systematics table

---------------------------------------------------
### Control region analysis
```
./scripts/fitSecVtxProperties.py -i treedir/qcd_control    -o treedir/qcd_control/plots/    --weightPt --onlyCentral --minLxySig 10
./scripts/fitSecVtxProperties.py -i treedir/z_control      -o treedir/z_control/plots/      --weightPt --vetoCentral --rebin 3
./scripts/fitSecVtxProperties.py -i treedir/photon_control -o treedir/photon_control/plots/ --weightPt --rebin 2
`````
After creating the workspace you can use it directly by using -w workspace.root instead of -i ntuple_dir

