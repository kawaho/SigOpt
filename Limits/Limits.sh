combineStr=""
declare -a arr=("ggcat0" "ggcat1" "ggcat2" "ggcat3" "vbfcat0" "vbfcat1")
for i in "${arr[@]}"
do
  echo $i
  combineStr+=" $i=../Datacards/datacard_${i}_125.txt"
  combine -M AsymptoticLimits -m 125 ../Datacards/datacard_${i}_125.txt  --freezeParameters MH --setParameters MH=125 
  #combine -M AsymptoticLimits -m 125 ../Datacards/datacard_${i}_125.txt --run blind --freezeParameters MH --setParameters MH=125 
  mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.${i}.mH125.root
done
echo "Combined"
combineCards.py$combineStr > ../Datacards/datacard_comb_125.txt
combine -M AsymptoticLimits -m 125 ../Datacards/datacard_comb_125.txt --freezeParameters MH --setParameters MH=125
#combine -M AsymptoticLimits -m 125 ../Datacards/datacard_comb_125.txt --run blind --freezeParameters MH --setParameters MH=125
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.Combined.mH125.root

