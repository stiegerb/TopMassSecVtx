#!/bin/bash
WHAT=$1; if [[ "$1" == "" ]]; then echo "runCharmPeaks.sh <TREES/MERGE/UNFOLD/DIFF>"; exit 1; fi

# tag=May4
tag=May7
hash="a176401"
treedir=SVLInfo/${tag}/
eosdir=/store/cmst3/group/top/summer2014/${hash}/

# cands=("421")
# cands=("411")
# cands=("44300") ## j/psi mumu
# cands=("421013,421011")
cands=("44300" "411" "421013,421011")

echo "Running on "${treedir}
outdir=charmplots/${tag}
mkdir -p ${outdir}

case $WHAT in
	TREES )
		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}      ${eosdir}      -p MC8TeV_TTJets_MSDecays_172v5
		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}      ${eosdir}      -p Data8TeV
		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}syst/ ${eosdir}syst/ -p MC8TeV_TTJets_TuneP11_
		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}syst/ ${eosdir}syst/ -p MC8TeV_TT_Z2star_powheg_pythia
		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}syst/ ${eosdir}syst/ -p MC8TeV_TT_AUET2_powheg_herwig
	;;
	MERGE )
		./scripts/mergeSVLInfoFiles.py ${treedir}
		./scripts/mergeSVLInfoFiles.py ${treedir}syst/
	;;
	UNFOLD )
		# inputs=("MC8TeV_TTJets_MSDecays_172v5")
		inputs=("Data8TeV_merged"
		        "MC8TeV_TTJets_MSDecays_172v5"
		        "syst/MC8TeV_TT_Z2star_powheg_pythia"
		        "syst/MC8TeV_TTJets_TuneP11"
		        "syst/MC8TeV_TT_AUET2_powheg_herwig")
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
				if [[ ${i} == "MC8TeV_TTJets_MSDecays_172v5" ]]; then
					for w in {0..5}; do
						python scripts/unfoldResonanceProperties.py --weight BFragWeight[${w}] -c ${c} -i ${treedir}/${i}.root -o ${outdir}/c_${ctag};
					done
				fi
				echo '-----------------------------'
				i="${i#syst/}"
				python scripts/unfoldResonanceProperties.py -w ${outdir}/c_${ctag}/${i}/CharmInfo_workspace_${ctag}.root -o ${outdir}/c_${ctag}/${i}/diff;
				if [[ ${i} == "MC8TeV_TTJets_MSDecays_172v5" ]]; then
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
		plotdir=${outdir}/finalplots/
		mkdir -p ${plotdir}
		a=("D0" "JPsi" "Dpm")

		for c in ${cands[@]}; do
			a="D0"
			if [[ ${c} == "411" ]]; then
				a="Dpm";
			elif [[ ${c} == "44300" ]]; then
				a="JPsi";
			fi
			mkdir -p ${plotdir}${a}
			ctag="${c}"
			ctag=${ctag/","/"_"}

			#differential measurements
			python scripts/compareUnfoldedDistributions.py -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_eta_dS -m 0.5  --tag ${a} --pullrange -3.8,3.8;
			python scripts/compareUnfoldedDistributions.py -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_pt_dS  -m 0.75 --tag ${a} --pullrange -3.8,3.8;

			#unfolded
			unfvars=("norm_ptrel_signal" "norm_pfrac_signal" "norm_ptfrac_signal" "norm_pzfrac_signal" "norm_ptchfrac_signal" "norm_pzchfrac_signal" "norm_dr_signal")
			for var in ${unfvars[@]}; do
				python scripts/compareUnfoldedDistributions.py -d ${var} --pullrange -6.8,10.8 -i ${outdir}/c_${ctag}/ -o ${plotdir}${a}/ -b UnfoldedDistributions --tag ${a}
			done
		done
	;;
esac


# Deprecated:
# for f in ${treedir}*.root ; do ./scripts/unfoldResonanceProperties.py -i $f -c 44300 -o unfolded_JPsi_${tag}/ ; done
# for f in ${treedir}*.root ; do ./scripts/unfoldResonanceProperties.py -i $f -c 421011,421013 -o unfolded_D0_${tag}/ ; done
# for f in ${treedir}*.root ; do ./scripts/unfoldResonanceProperties.py -i $f -c 411 -o unfolded_Dpm_${tag}/ ; done
# for f in unfolded_JPsi_${tag}/* ; do ./scripts/unfoldResonanceProperties.py -w unfolded_JPsi_${tag}/$f/CharmInfo_workspace_44300.root ; done
# for f in unfolded_D0_${tag}/* ; do ./scripts/unfoldResonanceProperties.py -w unfolded_D0_${tag}/$f/CharmInfo_workspace_421013_421011.root ; done
# for f in unfolded_Dpm_${tag}/* ; do ./scripts/unfoldResonanceProperties.py -w unfolded_Dpm_${tag}/$f/CharmInfo_workspace_411.root ; done

