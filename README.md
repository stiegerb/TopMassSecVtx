------------------------------------------------------
### Overview
This is the starting point for an analysis of the shape of the lepton-bjet invariant mass (mlb) distribution in top events. It runs in the framework and ntuples for the top quark mass measurement using secondary vertices and leptons by Pedro Silva and Benjamin Stieger.

The original ntuples are stored on eos in 
```
eos/cms/store/cmst3/user/psilva/5311_ntuples/
```
and the smaller lxy trees (which will be used for this analysis) can be found in
```
eos/cms/store/cmst3/group/top/summer2014/a176401/
```
Information on the samples and the datasets they correspond to is stored in the ```test/topss2014/samples.json``` file:
https://github.com/stiegerb/TopMassSecVtx/blob/mlbwidth/test/topss2014/samples.json

Note that the larger samples, like the data and the signal ttbar sample are split into several files.

The code that produces the lxy trees is concentrated in the runTopAnalysis class:
https://github.com/stiegerb/TopMassSecVtx/blob/mlbwidth/bin/runTopAnalysis.cc


The instructions below show how to install and compile the framework, run the already implemented dummy analysis (MlbWidthAnalysis), and produce a simple data/mc comparison plot.

To get started, open the files defining the MlbWidthAnalysis class and start implementing your event selection and analysis logic:
```
src/MlbWidthAnalysis.cc
interface/MlbWidthAnalysis.hh
```

You can find the information available from the lxy trees in the ```LxyAnalysis.cc``` file:
https://github.com/stiegerb/TopMassSecVtx/blob/mlbwidth/src/LxyAnalysis.cc#L111-L186


------------------------------------------------------
### Installation

```
ssh lxplus
scramv1 project CMSSW CMSSW_5_3_22
cd CMSSW_5_3_22/src/
cmsenv
wget -q -O - --no-check-certificate https://raw.github.com/stiegerb/TopMassSecVtx/master/TAGS.txt | sh
git clone git@github.com:stiegerb/TopMassSecVtx.git UserCode/TopMassSecVtx
git checkout mlbwidth
scram b -j 9
```

------------------------------------------------------
### Running the analysis
To run on a single file for testing purposes (recommended before producing all samples):
```
./scripts/runMlbWidthAnalysis.py -o treedir -n 100000 /store/cmst3/group/top/summer2014/a176401/MC8TeV_TTJets_MSDecays_172v5_0.root
```
This will process only 100000 events of the ttbar signal sample, and should take less than a minute or so. The output is stored in ```treedir```, which can be changed with the ```-o``` option.


To run on all the events and all the samples, including data:
```
./scripts/runMlbWidthAnalysis.py -o treedir -j 8 /store/cmst3/group/top/summer2014/a176401/
```

This will process about 300 files with up to several millions of events, and take about 30 min.

To afterwards merge the output files from the samples that are split into several input files, use this script:

```
./scripts/mergeSVLInfoFiles.py treedir/
```

There are more samples in the ```syst``` sub-folder on eos, which will be needed to estimate systematic uncertainties. They are variations of the ttbar and single top signal samples.

------------------------------------------------------
### Making data/MC comparison plots

The histograms defined in MlbWidthAnalysis are stored in the output files and can be used to produce a plot comparing data and simulation, using the ```runPlotter.py``` script:
```
runPlotter.py --cutUnderOverFlow -l 19701 -j test/topss2014/samples.json -o treedir/plots treedir
```

To work properly, we first need to generate a cache file that stores the proper normalizations for each simulated sample:
```
./scripts/runPlotter.py --rereadXsecWeights /store/cmst3/group/top/summer2014/a176401/ -j test/topss2014/samples.json
```
(This needs to be done only once.)

------------------------------------------------------
