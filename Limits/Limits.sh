combineCards.py Name1=../Datacards/datacard_ggcat0.txt Name2=../Datacards/datacard_ggcat1.txt Name3=../Datacards/datacard_ggcat2.txt Name4=../Datacards/datacard_ggcat3.txt Name5=../Datacards/datacard_vbfcat0.txt Name6=../Datacards/datacard_vbfcat1.txt Name7=../Datacards/datacard_vbfcat2.txt > ../Datacards/datacard_comb.txt

combine -M AsymptoticLimits -m 125 ../Datacards/datacard_ggcat0.txt --run blind #--freezeParameters pdfindex_ggcat0_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.ggcat0.mH125.root

combine -M AsymptoticLimits -m 125 ../Datacards/datacard_ggcat1.txt --run blind #--freezeParameters pdfindex_ggcat1_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.ggcat1.mH125.root

combine -M AsymptoticLimits -m 125 ../Datacards/datacard_ggcat2.txt --run blind #--freezeParameters pdfindex_ggcat2_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.ggcat2.mH125.root

combine -M AsymptoticLimits -m 125 ../Datacards/datacard_ggcat3.txt --run blind #--freezeParameters pdfindex_ggcat1_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.ggcat3.mH125.root

combine -M AsymptoticLimits -m 125 ../Datacards/datacard_vbfcat0.txt --run blind #--freezeParameters pdfindex_ggcat1_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.vbfcat0.mH125.root

combine -M AsymptoticLimits -m 125 ../Datacards/datacard_vbfcat1.txt --run blind #--freezeParameters pdfindex_ggcat1_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.vbfcat1.mH125.root

combine -M AsymptoticLimits -m 125 ../Datacards/datacard_vbfcat2.txt --run blind #--freezeParameters pdfindex_ggcat1_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.vbfcat2.mH125.root

combine -M AsymptoticLimits -m 125 ../Datacards/datacard_comb.txt --run blind #--freezeParameters pdfindex_ggcat0_13TeV,pdfindex_ggcat1_13TeV,pdfindex_ggcat2_13TeV,pdfindex_ggcat3_13TeV,pdfindex_vbf_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.Combined.mH125.root

