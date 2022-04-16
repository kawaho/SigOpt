combine -M GoodnessOfFit -d datacard_comb_125.root --algo=saturated --freezeParameters MH --setParameters MH=125 -m 125
mv higgsCombineTest.GoodnessOfFit.mH125.root data_run.root
hadd toys_run.root *batch*root 
combineTool.py -M CollectGoodnessOfFit --input data_run.root toys_run.root -m 125.0 -o gof.json
plotGof.py gof.json --statistic saturated --mass 125.0 -o gof_plot --title-right="H#rightarrow e#mu"
