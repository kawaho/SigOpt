#!/bin/bash
ulimit -s unlimited
set -e
cd /afs/cern.ch/work/k/kaho/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/SigOpt/S+Btoys/SplusBModels/toys
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`

itoy=$1

#Generate command
combine /afs/cern.ch/work/k/kaho/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/SigOpt/S+Btoys/higgsCombineTest.MultiDimFit.mH146.root -m 146.000 -M GenerateOnly --saveWorkspace --toysFrequentist --bypassFrequentistFit -t 1 --setParameters r=1.102 -s -1 -n _${itoy}_gen_step

#Fit command
mv higgsCombine_${itoy}_gen_step*.root gen_${itoy}.root
combine gen_${itoy}.root -m 146.000 -M MultiDimFit -P r --floatOtherPOIs=1 --saveWorkspace --toysFrequentist --bypassFrequentistFit -t 1 --setParameters r=1.102 -s -1 -n _${itoy}_fit_step --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2

#Throw command
mv higgsCombine_${itoy}_fit_step*.root fit_${itoy}.root
combine fit_${itoy}.root -m 146.000 --snapshotName MultiDimFit -M GenerateOnly --saveToys --toysFrequentist --bypassFrequentistFit -t -1 -n _${itoy}_throw_step --setParameters r=0

mv higgsCombine_${itoy}_throw_step*.root toy_${itoy}.root
rm gen_${itoy}.root fit_${itoy}.root
