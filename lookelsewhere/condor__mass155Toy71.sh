#!/bin/sh
ulimit -s unlimited
set -e
cd /afs/cern.ch/work/k/kaho/CMSSW_10_2_13/src
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/k/kaho/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/SigOpt/lookelsewhere

if [ $1 -eq 0 ]; then
  combine ../Datacards/datacard_comb_150.root --freezeParameters MH --setParameters MH=155 --toysFile higgsCombine_b_toy71.GenerateOnly.mH146.71.root -t 1000 -M Significance -m 155 -n mass155Toy71
fi