combineStr=""
declare -a arr=("ggcat0" "ggcat1" "ggcat2" "ggcat3" "vbfcat0" "vbfcat1")
for i in "${arr[@]}"
do
  echo $i
  combineStr+=" $i=../Datacards/datacard_$i.txt"
  combine -M AsymptoticLimits -m 125 ../Datacards/datacard_$i.txt --run blind 
  mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.$i.mH125.root
done
echo "Combined"
combineCards.py$combineStr > ../Datacards/datacard_comb.txt
combine -M AsymptoticLimits -m 125 ../Datacards/datacard_comb.txt --run blind
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.Combined.mH125.root

