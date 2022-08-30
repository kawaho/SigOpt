whichmass=$1
whichcard=$2
whichcat=$3
combine -M GoodnessOfFit -d datacard_${whichcat}_${whichcard}.root --algo=saturated --setParameters MH=${whichmass} -m ${whichmass} --freezeParameters MH 
mv higgsCombineTest.GoodnessOfFit.mH${whichmass}.root data_run.root
rm toys_run.root
hadd toys_run.root *${whichcat}_name_*batch*mH${whichmass}*root 
combineTool.py -M CollectGoodnessOfFit --input data_run.root toys_run.root -m ${whichmass}.0 -o gof.json
plotGof.py gof.json --statistic saturated --mass ${whichmass}.0 -o gof_plot_${whichcat} --title-right="${whichcat%%fine}, H(${whichmass})#rightarrow e#mu"
