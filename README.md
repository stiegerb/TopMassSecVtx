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
./scripts/runLxyTreeAnalysis.py -o treedir -j 8 /store/cmst3/group/top/summer2014/e1fa735/
./scripts/runLxyTreeAnalysis.py -o treedir/syst/ -j 8 /store/cmst3/group/top/summer2014/e1fa735/syst/
./scripts/runLxyTreeAnalysis.py -o treedir/mass_scan/ -j 8 /store/cmst3/group/top/summer2014/e1fa735/mass_scan/

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

------------------------------------------------------
### Producing systematics plots and mass scans

```
./scripts/makeSVLControlPlots.py treedir/

```
Will run the plots and put them in svlplots/ by default. Also produces a histos.root file to be used for the further analysis. Also saves the histograms in a cachefile. To rerun only the plotting part, run with -c option.


------------------------------------------------------
### Producing data/MC comparison plots

```
./scripts/makeSVLDataMCPlots.py treedir/

```
Produces a number of data/MC comparison plots (both from the SVLInfo trees, and from the histograms produced in the LxyTreeAnalysis). Default output directory is plots/. This is based on the runPlotter.py script. In order to have correct xsection weights and number of generated events, one needs to run on the eos/ directory first to produce a cache file with the weights, like so:
```
./scripts/runPlotter.py --rereadXsecWeights /store/cmst3/group/top/summer2014/e1fa735/

```


------------------------------------------------------
### Running the fits (work in progress...)

```
./scripts/makeSVLWorkspace.py -i .svlhistos.pck
```
Will run the fits and put the RooFit workspace and plots in svlfits/ by default.

