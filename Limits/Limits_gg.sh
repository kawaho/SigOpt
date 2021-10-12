combineCards.py Name1=datacard_ggcat0.txt Name2=datacard_ggcat1.txt Name3=datacard_ggcat2.txt Name4=datacard_ggcat3.txt Name5=datacard_ggcat4.txt > datacard_comb_ggcat.txt

combine -M AsymptoticLimits -m 125 datacard_comb_ggcat.txt --run blind #--freezeParameters pdfindex_ggcat0_13TeV,pdfindex_ggcat1_13TeV,pdfindex_ggcat2_13TeV,pdfindex_ggcat3_13TeV,pdfindex_vbf_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.ggcat.mH125.root
