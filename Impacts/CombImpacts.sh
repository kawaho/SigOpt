#combineCards.py ggcat0=../Datacards/datacard_ggcat0.txt ggcat1=../Datacards/datacard_ggcat1.txt ggcat2=../Datacards/datacard_ggcat2.txt ggcat3=../Datacards/datacard_ggcat3.txt vbfcat0=../Datacards/datacard_vbfcat0.txt vbfcat1=../Datacards/datacard_vbfcat1.txt vbfcat2=../Datacards/datacard_vbfcat2.txt > ../Datacards/datacard_comb.txt

i="comb"
echo $i
export cat=$i
combineTool.py -M T2W -i ../Datacards/datacard_$i.txt -o datacard_$i.root --parallel 4 -m 125
combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 125 --doInitialFit -P r --rMin=0.1 --rMax=1.1 -t -1 --expectSignal=1 --parallel 16
combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 125 --doFits -t -1 --expectSignal=1 --parallel 16 --autoBoundsPOIs r
#--autoBoundsPOIs
#--rMin=$lower --rMax=$upper
#--robustFit 1
combineTool.py -M Impacts -d ../Datacards/datacard_$i.root -m 125 -o impacts_$i.json -t -1 --expectSignal=1
plotImpacts.py -i impacts_$i.json -o impacts_$i
mkdir -p $i
mv *.root *.json *.pdf $i
mkdir -p results
find . -type f -not -path "./results/*" -name "*.pdf" -exec cp {} ./results/ \;

