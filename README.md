------------------------------------------------------
### Installation

```
ssh lxplus
scramv1 project CMSSW CMSSW_5_3_20
cd CMSSW_5_3_20/src/
cmsenv
git clone git@github.com:stiegerb/TopMassSecVtx.git UserCode/TopMassSecVtx
scram b -j 9
```

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
There is a version of the trees from Nov14 that is still current in:
```
/afs/cern.ch/work/s/stiegerb/TopSecVtx/SVLInfo/Nov14
```

------------------------------------------------------
### Producing plots and histogram file

```
./scripts/makeSVLControlPlots.py treedir/

```
Will run the plots and put them in svlplots/ by default. Also produces a histos.root file to be used for the further analysis.


------------------------------------------------------
### Running the fits (work in progress...)

```
./scripts/SVLFitting/createMassTemplates.py -i svlplots/histos.root -s mrankinc
./scripts/SVLFitting/createMassTemplates.py -i svlplots/histos.root -s drrankinc

./scripts/SVLFitting/createMassTemplates.py -w svlfits/mSVL_Workspace_mrankinc.root -s mrankinc
./scripts/SVLFitting/createMassTemplates.py -w svlfits/mSVL_Workspace_drrankinc.root -s drrankinc

```
Will run the plots and put them in svlplots/ by default. Also produces a histos.root file to be used for the further analysis.

