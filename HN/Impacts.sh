declare -a arr=("ggcat0")
for i in "${arr[@]}"
do
  echo $i
  export cat=$i
  combineTool.py -M T2W -i datacard_$i.txt -o datacard_$i.root --parallel 4 -m 125
  combineTool.py -M Impacts -d datacard_$i.root -m 125 --doInitialFit --robustFit 1 -P r --rMin=-.1 --rMax=.1 -t -1 --expectSignal=0 --parallel 16
  combineTool.py -M Impacts -d datacard_$i.root -m 125 --robustFit 1 --doFits --rMin=-.1 --rMax=.1 -t -1 --expectSignal=0 --parallel 16
  combineTool.py -M Impacts -d datacard_$i.root -m 125 -o impacts_$i.json -t -1 -expectSignal=0
  plotImpacts.py -i impacts_$i.json -o impacts_$i
done




