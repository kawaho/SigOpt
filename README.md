# Signifiance Optimization with BDT
This is a repository to categorize and optimize LFV H -> e + mu analysis Signifiance with Combine
# Setup
```bash
#Setup CMSSW
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
#Clone the GBRLikelihood package for additional useful pdf not in combine
git clone git@github.com:jonathon-langford/HiggsAnalysis.git
#Install combine following the instructions here: http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.2.0
#Get also the combineTools to submit grid jobs: http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/#combine-tool
cd $CMSSW_BASE/src
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-ssh.sh)
#Copy RooCBExp to combine from GBRLikelihood
cp HiggsAnalysis/GBRLikelihood/interface/RooCBExp.h HiggsAnalysis/CombinedLimit/interface
cp HiggsAnalysis/GBRLikelihood/src/RooCBExp.cc HiggsAnalysis/CombinedLimit/src
#Add the line "#include "HiggsAnalysis/CombinedLimit/interface/RooCBExp.h"" in 
vim HiggsAnalysis/CombinedLimit/src/classes.h 
#Add "<class name="RooCBExp" />" in
vim HiggsAnalysis/CombinedLimit/src/classes_def.xml
#Build it 
scramv1 b clean; scramv1 b -j 16
#Clone this repo
git clone git@github.com:kawaho/SigOpt.git
```
