------------------------------------------------------
### Installation (Top SummerStudents Project 2014)

- Set up a CMSSW 5_3_15 release area
```
export SCRAM_ARCH=slc5_amd64_gcc462
scramv1 project CMSSW CMSSW_5_3_15
cd CMSSW_5_3_15/src/
cmsenv
```

- Checkout the llvv_fwk framework
```
mkdir -p UserCode/llvv_fwk
cd UserCode/llvv_fwk/
git init
git config core.sparsecheckout true
/bin/cp /afs/cern.ch/user/s/stiegerb/public/TopSS2014/topss2014-sparse-checkout .git/info/sparse-checkout
git remote add -t topss2014 --no-tags origin /afs/cern.ch/work/s/stiegerb/TopSummerStudents/CMSSW_5_3_15/src/UserCode/llvv_fwk

git fetch origin +topss2014:topss2014
git checkout topss2014
```

- Compile the code:
```
scram b -j 20
```