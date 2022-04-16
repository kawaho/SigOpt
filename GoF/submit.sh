for idx in {123..124}; do
  combineTool.py -d datacard_comb_125.root -M GoodnessOfFit --freezeParameters MH --setParameters MH=125 --toysFreq -m 125 -t 50 -n name_batch${idx} --job-mode condor --task-name GoF_MC_batch${idx} --sub-opts="+JobFlavour = \"microcentury\"\n+JobBatchName=\"GoF MC\"" --algo=saturated -s ${idx} 
done
