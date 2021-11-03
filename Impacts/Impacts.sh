declare -a arr=("ggcat0" "ggcat1" "ggcat2" "ggcat3" "vbfcat0" "vbfcat1" "vbfcat2" "vbfcat3")
for i in "${arr[@]}"
do
  echo $i
  export cat=$i
  combineTool.py -M T2W -i ../Datacards/datacard_$i.txt -o datacard_$i.root --parallel 4 -m 125
  combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 125 --doInitialFit --robustFit 1 -P r --expectSignal=0 --rMin=-.5 --rMax=.5 -t -1
  combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 125 --robustFit 1 --doFits --rMin=-.5 --rMax=.5 -t -1 --parallel 4
  combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 125 -o impacts_$i.json -t -1
  plotImpacts.py -i impacts_$i.json -o impacts_$i
  mkdir -p $i
  mv *.root *.json *.pdf $i
done
mkdir -p results
find . -type f -not -path "./results/*" -name "*.pdf" -exec cp {} ./results/ \;




