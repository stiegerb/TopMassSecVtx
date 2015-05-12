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
#cands=("421013,421011")
cands=("44300" "411" "421013,421011")

echo "Running on "${treedir}
outdir=charmplots/${tag}
mkdir -p ${outdir}

case $WHAT in
	TREES )
#		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}              ${eosdir}           -p MC8TeV_TTJets_MSDecays_172v5
#		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}              ${eosdir}           -p Data8TeV
#		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}syst/         ${eosdir}syst/      -p MC8TeV_TTJets_TuneP11_
#		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}syst/         ${eosdir}syst/      -p MC8TeV_TT_Z2star_powheg_pythia
#		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}syst/         ${eosdir}syst/      -p MC8TeV_TT_AUET2_powheg_herwig
		./scripts/runLxyTreeAnalysis.py -j 8 -o ${treedir}z_control/    ${eosdir}z_control/ 
	;;
	MERGE )
#		./scripts/mergeSVLInfoFiles.py ${treedir}
#		./scripts/mergeSVLInfoFiles.py ${treedir}syst/
		./scripts/mergeSVLInfoFiles.py ${treedir}z_control/
	;;
	UNFOLD )
		# inputs=("MC8TeV_TTJets_MSDecays_172v5")
		inputs=(#"Data8TeV_merged"
		        #"MC8TeV_TTJets_MSDecays_172v5"
		        #"syst/MC8TeV_TT_Z2star_powheg_pythia"
		        #"syst/MC8TeV_TTJets_TuneP11"
		        #"syst/MC8TeV_TT_AUET2_powheg_herwig"
		        "z_control/MC8TeV_DY_merged_filt23"
		        "z_control/Data8TeV_DoubleLepton_merged_filt23")
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
				    fragvars=("bfragup" "bfragdn" "bfragp11" "bfragpete" "bfraglund")
				    for w in ${fragvars}; do
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

			titles="Madgraph+Pythia+Z2*,Madgraph+Pythia+P11,Powheg+Herwig+AUET2,Powheg+Pythia+Z2*,Data";

			#differential measurements
			mcs="${outdir}/c_${ctag}/MC8TeV_TTJets_MSDecays_172v5/diff/,${outdir}/c_${ctag}/MC8TeV_TTJets_TuneP11/diff/,${outdir}/c_${ctag}/MC8TeV_TT_AUET2_powheg_herwig/diff,${outdir}/c_${ctag}/MC8TeV_TT_Z2star_powheg_pythia/diff,${outdir}/c_${ctag}/Data8TeV_merged/diff/";

			python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_eta_dS -m 0.5 --tag ${a};
			python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -o ${plotdir}${a}/ -b CharmInfo_diff -d norm_pt_dS -m 0.75 --tag ${a};
			#unfolded
			mcs="${outdir}/c_${ctag}/MC8TeV_TTJets_MSDecays_172v5/,${outdir}/c_${ctag}/MC8TeV_TTJets_TuneP11/,${outdir}/c_${ctag}/MC8TeV_TT_AUET2_powheg_herwig/,${outdir}/c_${ctag}/MC8TeV_TT_Z2star_powheg_pythia/,${outdir}/c_${ctag}/Data8TeV_merged/";

			python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -o ${plotdir}${a}/ -b UnfoldedDistributions -m 0.35 --tag ${a} -d norm_ptrel_signal
			python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -o ${plotdir}${a}/ -b UnfoldedDistributions -m 0.45 --tag ${a} -d norm_pfrac_signal
			python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -o ${plotdir}${a}/ -b UnfoldedDistributions -m 0.45 --tag ${a} -d norm_ptfrac_signal
			python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -o ${plotdir}${a}/ -b UnfoldedDistributions -m 0.45 --tag ${a} -d norm_pzfrac_signal
			python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -o ${plotdir}${a}/ -b UnfoldedDistributions -m 0.40 --tag ${a} -d norm_ptchfrac_signal
			python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -o ${plotdir}${a}/ -b UnfoldedDistributions -m 0.40 --tag ${a} -d norm_pzchfrac_signal
			python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -o ${plotdir}${a}/ -b UnfoldedDistributions -m 0.50 --tag ${a} -d norm_dr_signal
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

