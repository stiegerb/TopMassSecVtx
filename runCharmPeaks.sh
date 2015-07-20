#!/bin/bash
WHAT=$1; if [[ "$1" == "" ]]; then echo "runCharmPeaks.sh <TREES/MERGE/UNFOLD/DIFF/DIFFZ>"; exit 1; fi

tag=Jul13
hash=bbbcb36
treedir=SVLInfo/${tag}/
eosdir=/store/cmst3/group/top/summer2015/${hash}/

# cands=("421")             # D0
# cands=("421013,421011")   # D0 with soft mu/e tag
# cands=("411")             # D+/-
# cands=("44300")           # J/Psi mumu
# cands=("413")             # K pi pi mass
# cands=("-413")            # mass difference 
cands=("44300" "411" "421013,421011" "-413")

echo "Running on "${treedir}
outdir=charmplots/${tag}
mkdir -p ${outdir}

case $WHAT in
    TREES )
	./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}              ${eosdir}           -p MC8TeV_TTJets_MSDecays_172v5
	./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}              ${eosdir}           -p Data8TeV
	./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}syst/         ${eosdir}syst/      -p MC8TeV_TTJets_TuneP11_
	./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}syst/         ${eosdir}syst/      -p MC8TeV_TT_Z2star_powheg_pythia
	./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}syst/         ${eosdir}syst/      -p MC8TeV_TT_AUET2_powheg_herwig
	./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}z_control/    ${eosdir}z_control/
	;;
    MERGE )
	./scripts/mergeSVLInfoFiles.py ${treedir}
	./scripts/mergeSVLInfoFiles.py ${treedir}syst/
	./scripts/mergeSVLInfoFiles.py ${treedir}z_control/
	;;
    PLOT)
	runPlotter.py ${treedir}/          -o ${treedir}/plots          --filter "JPsi,D0,Dpm,DMDsmD0" --cutUnderOverFlow --json test/topss2014/samples.json;
        runPlotter.py ${treedir}z_control/ -o ${treedir}z_control/plots --filter "JPsi,D0,Dpm,DMDsmD0" --cutUnderOverFlow --json test/topss2014/z_samples.json;
	;;
    UNFOLD )
        #here it is assuming we went to the directory and merged by hand
	inputs=(
            "Data8TeV_merged"
	    "MC8TeV_TTJets_MSDecays_172v5"
	    "syst/MC8TeV_TT_Z2star_powheg_pythia"
	    "syst/MC8TeV_TTJets_TuneP11"
	    "syst/MC8TeV_TT_AUET2_powheg_herwig"
	    "z_control/MC8TeV_DY_merged_filt23"
	    "z_control/Data8TeV_DoubleLepton_merged_filt23"
	)
	for c in ${cands[@]}; do
	    for i in ${inputs[@]}; do
		if [ ! -f ${treedir}/${i}.root ]; then
		    echo "ERROR: File not found ${treedir}${i}.root"
		    exit
		fi
		echo "  processing ${i}"
		ctag="${c}";
		ctag=${ctag/","/"_"}
		python scripts/unfoldResonanceProperties.py -c ${c} -i ${treedir}/${i}.root -o ${outdir}/c_${ctag};
		if [ "$i" == "MC8TeV_TTJets_MSDecays_172v5" ] || [ "$i" != "${i/DY_merged/}" ]; then
		    for w in {0..5}; do
			python scripts/unfoldResonanceProperties.py --weight BFragWeight[${w}] -c ${c} -i ${treedir}/${i}.root -o ${outdir}/c_${ctag};
		    done
		fi
		echo '-----------------------------'
		i="${i/syst/}"
		i="${i/z_control/}"
		python scripts/unfoldResonanceProperties.py -w ${outdir}/c_${ctag}/${i}/CharmInfo_workspace_${ctag}.root -o ${outdir}/c_${ctag}/${i}/diff;
		if [ "$i" == "MC8TeV_TTJets_MSDecays_172v5" ] || [ "$i" != "${i/DY_merged/}" ]; then
		    fragvars=("bfrag" "bfragup" "bfragdn" "bfragp11" "bfragpete" "bfraglund")
		    for w in ${fragvars[@]}; do
			echo "   ${w}"
			python scripts/unfoldResonanceProperties.py -w ${outdir}/c_${ctag}/${i}_${w}/CharmInfo_workspace_${ctag}.root -o ${outdir}/c_${ctag}/${i}_${w}/diff;
		    done
		fi
		echo ${i} "done"
		echo "########################################"
	    done
	    echo "ALL DONE"
	    echo "########################################"
	done
	;;
    DIFF )
	plotdir=${outdir}/plots/
	mkdir -p ${plotdir}
	a=("D0" "JPsi" "Dpm" "Dsm")
	
	for c in ${cands[@]}; do
	    a="D0"
	    if [[ ${c} == "411" ]]; then
		a="Dpm";
	    elif [[ ${c} == "44300" ]]; then
		a="JPsi";
	    elif [[ ${c} == "-413" ]]; then
		a="Dsm";
	    fi
	    mkdir -p ${plotdir}${a}
	    ctag="${c}"
	    ctag=${ctag/","/"_"}
	    
	    #differential measurements
	    python scripts/compareUnfoldedDistributions.py -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_eta_dS -m 0.75  --tag ${a} --showMean;
	    python scripts/compareUnfoldedDistributions.py -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_pt_dS  -m 0.75 --tag ${a} --showMean;
	    python scripts/compareUnfoldedDistributions.py -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_eta_dS -m 0.75  --tag ${a};
	    python scripts/compareUnfoldedDistributions.py -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_pt_dS  -m 0.75 --tag ${a};
	    
	    #unfolded
	    unfvars=("norm_ptrel_signal" "norm_pfrac_signal" "norm_ptfrac_signal" "norm_pzfrac_signal" "norm_ptchfrac_signal" "norm_pzchfrac_signal" "norm_dr_signal")
	    for var in ${unfvars[@]}; do
		python scripts/compareUnfoldedDistributions.py -d ${var} -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b UnfoldedDistributions -m 0.60 --tag ${a} --showMean;
		python scripts/compareUnfoldedDistributions.py -d ${var} -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b UnfoldedDistributions -m 0.60 --tag ${a};
	    done
	done
	;;
    DIFFZ )
	plotdir=${outdir}z_control/plots/
	mkdir -p ${plotdir}
	a=("D0" "JPsi" "Dpm" "Dsm")
	
	for c in ${cands[@]}; do
	    a="D0"
	    if [[ ${c} == "411" ]]; then
		a="Dpm";
	    elif [[ ${c} == "44300" ]]; then
		a="JPsi";
	    elif [[ ${c} == "-413" ]]; then
		a="Dsm";
	    fi
	    mkdir -p ${plotdir}${a}
	    ctag="${c}"
	    ctag=${ctag/","/"_"}
	    
	    #differential measurements
	    python scripts/compareUnfoldedDistributions.py -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_eta_dS -m 0.5  --tag ${a} -z;
	    python scripts/compareUnfoldedDistributions.py -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_pt_dS  -m 0.75 --tag ${a} -z;
	    python scripts/compareUnfoldedDistributions.py -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_eta_dS -m 0.5  --tag ${a} -z --showMean;
	    python scripts/compareUnfoldedDistributions.py -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_pt_dS  -m 0.75 --tag ${a} -z --showMean;
	    
	    #unfolded
	    unfvars=("norm_ptrel_signal" "norm_pfrac_signal" "norm_ptfrac_signal" "norm_pzfrac_signal" "norm_ptchfrac_signal" "norm_pzchfrac_signal" "norm_dr_signal")
	    for var in ${unfvars[@]}; do
		python scripts/compareUnfoldedDistributions.py -d ${var} -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b UnfoldedDistributions --tag ${a} -z;
		python scripts/compareUnfoldedDistributions.py -d ${var} -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b UnfoldedDistributions --tag ${a} -z --showMean;
	    done
	done
	;;
esac


