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
./scripts/runLxyTreeAnalysis.py -o treedir -j 8 /store/cmst3/group/top/summer2014/a176401/
./scripts/runLxyTreeAnalysis.py -o treedir/syst/ -j 8 /store/cmst3/group/top/summer2014/a176401/syst/
./scripts/runLxyTreeAnalysis.py -o treedir/mass_scan/ -j 8 /store/cmst3/group/top/summer2014/a176401/mass_scan/

```

------------------------------------------------------
### Merging the trees

```
./scripts/mergeSVLInfoFiles.py treedir/
./scripts/mergeSVLInfoFiles.py treedir/syst/
./scripts/mergeSVLInfoFiles.py treedir/mass_scan/

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
```
./scripts/runPlotter.py --rereadXsecWeights /store/cmst3/group/top/summer2014/a176401/ -j test/topss2014/samples.json,test/topss2014/syst_samples.json,test/topss2014/mass_scan_samples.json

```


------------------------------------------------------
### Running the fits 
=======
### Producing QCD Templates
makeSVLQCDTemplates.py produces MET and m(l,SV) distributions from the non-isolated data control region and stores them in qcd_templates.root.
qcdFitter.py fits the MET distribution in the l+jets signal region, using the shapes from the non-isolated region produced by makeSVLQCDTemplates.py and produces m(l,SV) templates scaled according to the outcome of the fit.
It takes as input a plotter.root file (from makeSVLDataMCPlots.py) with properly scaled MET distributions in the signal region.
```
./scripts/makeSVLQCDTemplates.py treedir/
./test/topss2014/qcdFitter.py plotter.root qcd_templates.root
```
./scripts/runSVLFits.py
```
Prepares the workspace for the fits
```
./scripts/runSVLFits.py -w SVLWorkspace.root -i /afs/cern.ch/work/s/stiegerb/public/forPedro/pe_inputs.root --spy
```
Will run the fits and put the RooFit workspace and plots in svlfits/ by default.

