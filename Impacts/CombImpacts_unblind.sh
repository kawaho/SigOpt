#combineCards.py ggcat0=../Datacards/datacard_ggcat0.txt ggcat1=../Datacards/datacard_ggcat1.txt ggcat2=../Datacards/datacard_ggcat2.txt vbfcat0=../Datacards/datacard_vbfcat0.txt vbfcat1=../Datacards/datacard_vbfcat1.txt > ../Datacards/datacard_comb.txt

i="comb"
echo ${i}
export cat=${i}
combineTool.py -M T2W -i ../Datacards/datacard_${i}_130.txt -o datacard_$i.root --parallel 4 -m 130 
combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 130 --doInitialFit -P r --parallel 16 --freezeParameters MH --setParameters MH=130 --rMax 2.5 --rMin -2.5
 combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 130 --doFits --parallel 16  --freezeParameters MH --setParameters MH=130 --rMax 2.5 --rMin -2.5
#--autoBoundsPOIs r
#--rMin=$lower --rMax=$upper
#--robustFit 1
combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 130 -o impacts_$i.json --freezeParameters MH --setParameters MH=130 --rMax 2.5 --rMin -2.5 
plotImpacts.py -i impacts_${i}.json -o impacts_${i}_130 --blind
mkdir -p $i
mv *.root *.json *.pdf $i
mkdir -p results
find . -type f -not -path "./results/*" -name "*.pdf" -exec cp {} ./results/ \;

