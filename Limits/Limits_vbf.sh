combineCards.py Name1=datacard_vbfcat0.txt Name2=datacard_vbfcat1.txt > datacard_comb_vbf.txt

combine -M AsymptoticLimits -m 125 datacard_vbfcat0.txt --run blind #--freezeParameters pdfindex_ggcat1_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.vbfcat0.mH125.root

combine -M AsymptoticLimits -m 125 datacard_vbfcat1.txt --run blind #--freezeParameters pdfindex_ggcat1_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.vbfcat1.mH125.root

combine -M AsymptoticLimits -m 125 datacard_comb_vbf.txt --run blind #--freezeParameters pdfindex_ggcat0_13TeV,pdfindex_ggcat1_13TeV,pdfindex_ggcat2_13TeV,pdfindex_ggcat3_13TeV,pdfindex_vbf_13TeV
mv higgsCombineTest.AsymptoticLimits.mH125.root higgsCombineTest.AsymptoticLimits.vbfcat.mH125.root
