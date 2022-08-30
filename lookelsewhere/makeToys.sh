for i in `seq 1 100`
do
  combineTool.py --job-mode condor --sub-opts='+JobFlavour=\"longlunch\"' --task-name _b_toy${i} ../Datacards/datacard_comb_150.root -M GenerateOnly --toysFrequentist -m 146 -t 1000 --saveToys --expectSignal=0 -s ${i} -n _b_toy${i} & 
done
