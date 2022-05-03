declare -a arr=("ggcat2")
#"ggcat0" "ggcat1" "ggcat2" "vbfcat0" "vbfcat1")
for i in "${arr[@]}"
do
  echo $i
  export cat=$i
  combineTool.py -M T2W -i ../Datacards/datacard_$i.txt -o datacard_$i.root --parallel 4 -m 125
  #limit=$(combine -M AsymptoticLimits -m 125 ../Datacards/datacard_$i.root --run blind | awk '{if(/Expected 50.0%: r < /) print $5}')
  #limit=$(echo "$limit * 10" | bc -l)
  #upper=$(echo "$limit * 2" | bc -l)
  #lower=$(echo "$limit * -2" | bc -l)
  combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 125 --doInitialFit -P r --rMin=0.9 --rMax=1.1 -t -1 --expectSignal=1 --parallel 16 --freezeParameters MH --setParameters MH=125
  combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 125 --doFits -t -1 --expectSignal=1 --parallel 16 --rMin=0.9 --rMax=1.1 --freezeParameters MH --setParameters MH=125
  #--autoBoundsPOIs
  #--rMin=$lower --rMax=$upper
  combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 125 -o impacts_$i.json -t -1 --expectSignal=1 --freezeParameters MH --setParameters MH=125
  plotImpacts.py -i impacts_$i.json -o impacts_$i
  mkdir -p $i
  mv *.root *.json *.pdf $i
done
mkdir -p results
find . -type f -not -path "./results/*" -name "*.pdf" -exec cp {} ./results/ \;

