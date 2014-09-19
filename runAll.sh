#!/bin/bash
WHAT=$1; if [[ "$1" == "" ]]; then echo "runAll.sh <TREES/MERGE/UNFOLD/DIFF>"; exit 1; fi

tag=Aug28
# tag=Sep18
treedir=/data/stiegerb/topss2014/hidde/lxyplots_${tag}/

# cands=("421")
# cands=("411")
# cands=("44300")
# cands=("421013,421011")
cands=("44300" "411" "421013,421011")

echo "Running on "${treedir}

case $WHAT in
	TREES )
		./scripts/runLxyTreeAnalysis.py -p MC8TeV_TTJets_MSDecays_172v5 -o ${treedir} -j 8 /store/cmst3/group/top/summer2014/62dc494/
		./scripts/runLxyTreeAnalysis.py -p Data8TeV -o ${treedir} -j 8 /store/cmst3/group/top/summer2014/62dc494/
		./scripts/runLxyTreeAnalysis.py -p MC8TeV_TTJets_TuneP11_ -o ${treedir} -j 8 /store/cmst3/group/top/summer2014/62dc494/syst/
		./scripts/runLxyTreeAnalysis.py -p MC8TeV_TT_Z2star_powheg_pythia -o ${treedir} -j 8 /store/cmst3/group/top/summer2014/62dc494/syst/
		./scripts/runLxyTreeAnalysis.py -p MC8TeV_TT_AUET2_powheg_herwig -o ${treedir} -j 8 /store/cmst3/group/top/summer2014/62dc494/syst/
		;;
	MERGE )
		hadd ${treedir}/Data8TeV_merged.root ${treedir}/Data8TeV_*.root
		hadd ${treedir}/MC8TeV_TT_AUET2_powheg_herwig.root ${treedir}/MC8TeV_TT_AUET2_powheg_herwig_?.root
		hadd ${treedir}/MC8TeV_TTJets_MSDecays_172v5.root ${treedir}/MC8TeV_TTJets_MSDecays_172v5_*.root
		hadd ${treedir}/MC8TeV_TT_Z2star_powheg_pythia.root ${treedir}/MC8TeV_TT_Z2star_powheg_pythia_*.root
		hadd ${treedir}/MC8TeV_TTJets_TuneP11.root ${treedir}/MC8TeV_TTJets_TuneP11_?.root

		# Cleanup the non-merged files
		# rm ${treedir}/MC8TeV_TTJets_MSDecays_172v5_*
		# rm ${treedir}/MC8TeV_TT_Z2star_powheg_pythia_*
		# rm ${treedir}/MC8TeV_TT_AUET2_powheg_herwig_*
		# rm ${treedir}/MC8TeV_TTJets_TuneP11_*
		# rm ${treedir}/Data8TeV_*_*.root
		;;
	UNFOLD )
		outdir=unfolded_${tag}
		inputs=("Data8TeV_merged" "MC8TeV_TTJets_MSDecays_172v5" "MC8TeV_TT_Z2star_powheg_pythia" "MC8TeV_TTJets_TuneP11" "MC8TeV_TT_AUET2_powheg_herwig")

		for c in ${cands[@]}; do
		    for i in ${inputs[@]}; do
			ctag="${c}";
			ctag=${ctag/","/"_"}
			python scripts/unfoldResonanceProperties.py -c ${c} -i ${treedir}/${i}.root -o ${outdir}/c_${ctag};
			python scripts/unfoldResonanceProperties.py -w ${outdir}/c_${ctag}/${i}/CharmInfo_workspace_${ctag}.root;
			echo ${i} "done"
		    done
		done
		;;
	DIFF )
		outdir=unfolded_${tag}
		plotdir=unfolded_${tag}/finalplots/
		mkdir -p ${plotdir}
		a=("D0" "JPsi" "Dpm")

		for c in ${cands[@]}; do
			a="D0"
			if [[ ${c} == "411" ]]; then
				a="Dpm";
			elif [[ ${c} == "44300" ]]; then
				a="JPsi";
			fi
			ctag="${c}"
			ctag=${ctag/","/"_"}

		    titles="Madgraph+Pythia+Z2^{*},Madgraph+Pythia+P11,Powheg+Herwig+AUET2,Powheg+Pythia+Z2^{*},Data";

		    #differential measurements
		    mcs="${outdir}/c_${ctag}/MC8TeV_TTJets_MSDecays_172v5/diff/,${outdir}/c_${ctag}/MC8TeV_TTJets_TuneP11/diff/,${outdir}/c_${ctag}/MC8TeV_TT_AUET2_powheg_herwig/diff,${outdir}/c_${ctag}/MC8TeV_TT_Z2star_powheg_pythia/diff,${outdir}/c_${ctag}/Data8TeV_merged/diff/";

		    python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -b CharmInfo_diff -d norm_eta_dS -m 0.5 --tag ${a};
		    mv norm_eta_dS.pdf ${plotdir}/c_${ctag}_diffeta.pdf;
		    mv norm_eta_dS.png ${plotdir}/c_${ctag}_diffeta.png;
		    mv norm_eta_dS.C ${plotdir}/c_${ctag}_diffeta.C;

		    python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -b CharmInfo_diff -d norm_pt_dS -m 0.75 --tag ${a};
		    mv norm_pt_dS.pdf ${plotdir}/c_${ctag}_diffpt.pdf;
		    mv norm_pt_dS.png ${plotdir}/c_${ctag}_diffpt.png;
		    mv norm_pt_dS.C ${plotdir}/c_${ctag}_diffpt.C;

		    #unfolded
		    mcs="${outdir}/c_${ctag}/MC8TeV_TTJets_MSDecays_172v5/,${outdir}/c_${ctag}/MC8TeV_TTJets_TuneP11/,${outdir}/c_${ctag}/MC8TeV_TT_AUET2_powheg_herwig/,${outdir}/c_${ctag}/MC8TeV_TT_Z2star_powheg_pythia/,${outdir}/c_${ctag}/Data8TeV_merged/";

		    python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -b UnfoldedDistributions -d norm_ptrel_signal -m 0.35 --tag ${a}
		    mv norm_ptrel_signal.pdf ${plotdir}/c_${ctag}_ptrel.pdf
		    mv norm_ptrel_signal.png ${plotdir}/c_${ctag}_ptrel.png
		    mv norm_ptrel_signal.C ${plotdir}/c_${ctag}_ptrel.C

		    python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -b UnfoldedDistributions -d norm_pfrac_signal -m 0.45 --tag ${a}
		    mv norm_pfrac_signal.pdf ${plotdir}/c_${ctag}_pfrac.pdf
		    mv norm_pfrac_signal.png ${plotdir}/c_${ctag}_pfrac.png
		    mv norm_pfrac_signal.C ${plotdir}/c_${ctag}_pfrac.C

		    python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -b UnfoldedDistributions -d norm_ptfrac_signal -m 0.45 --tag ${a}
		    mv norm_ptfrac_signal.pdf ${plotdir}/c_${ctag}_ptfrac.pdf
		    mv norm_ptfrac_signal.png ${plotdir}/c_${ctag}_ptfrac.png
		    mv norm_ptfrac_signal.C ${plotdir}/c_${ctag}_ptfrac.C

		    python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -b UnfoldedDistributions -d norm_pzfrac_signal -m 0.45 --tag ${a}
		    mv norm_pzfrac_signal.pdf ${plotdir}/c_${ctag}_pzfrac.pdf
		    mv norm_pzfrac_signal.png ${plotdir}/c_${ctag}_pzfrac.png
		    mv norm_pzfrac_signal.C ${plotdir}/c_${ctag}_pzfrac.C

		    python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -b UnfoldedDistributions -d norm_ptchfrac_signal -m 0.4 --tag ${a}
		    mv norm_ptchfrac_signal.pdf ${plotdir}/c_${ctag}_ptchfrac.pdf
		    mv norm_ptchfrac_signal.png ${plotdir}/c_${ctag}_ptchfrac.png
		    mv norm_ptchfrac_signal.C ${plotdir}/c_${ctag}_ptchfrac.C

		    python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -b UnfoldedDistributions -d norm_pzchfrac_signal -m 0.4 --tag ${a}
		    mv norm_pzchfrac_signal.pdf ${plotdir}/c_${ctag}_pzchfrac.pdf
		    mv norm_pzchfrac_signal.png ${plotdir}/c_${ctag}_pzchfrac.png
		    mv norm_pzchfrac_signal.C ${plotdir}/c_${ctag}_pzchfrac.C

		    python scripts/compareUnfoldedDistributions.py -i ${mcs} -t ${titles} -b UnfoldedDistributions -d norm_dr_signal -m 0.5 --tag ${a}
		    mv norm_dr_signal.pdf ${plotdir}/c_${ctag}_deltar.pdf
		    mv norm_dr_signal.png ${plotdir}/c_${ctag}_deltar.png
		    mv norm_dr_signal.C ${plotdir}/c_${ctag}_deltar.C
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

