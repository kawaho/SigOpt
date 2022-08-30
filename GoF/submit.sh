whichmass=$1
whichcard=$2
whichcat=$3
for idx in {123..142}; do
  combineTool.py -d datacard_${whichcat}_${whichcard}.root -M GoodnessOfFit --bypassFrequentistFit --setParameters MH=${whichmass} --freezeParameters MH -m ${whichmass} -t 50 -n ${whichcat}_name_batch${idx} --job-mode condor --task-name ${whichcat}_GoF_MC_batch${idx} --sub-opts="+JobFlavour = \"microcentury\"\n+JobBatchName=\"${whichcat} GoF MC\"" --algo=saturated -s ${idx} --toysFreq
done
