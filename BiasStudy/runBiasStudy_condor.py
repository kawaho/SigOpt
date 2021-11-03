import ROOT
import os
from datetime import datetime
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so");
ROOT.gROOT.SetBatch(True)
cats = ['ggcat0','ggcat1','ggcat2','ggcat3','vbfcat0','vbfcat1','vbfcat2','vbfcat3']
orders = [[1,1,1,1],[1,1,1,1],[1,1,1,1],[2,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1]]

def run(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

bkgfile = ROOT.TFile('../Workspaces/CMS_Hemu_13TeV_multipdf.root')
bkgWS = bkgfile.Get('multipdf')
mass = bkgWS.var("CMS_emu_Mass") 
for (cat,order) in zip(cats,orders):
  multipdf = bkgWS.pdf('CMS_hemu_'+cat+'_13TeV_bkgshape')
  numofpdfcat = multipdf.getNumPdfs()
  frozen = []
  for i in range(numofpdfcat):
    pdfname = multipdf.getPdf(i).GetName()
    sets = multipdf.getPdf(i).getParameters(ROOT.RooArgSet(mass))
    frozen += sets.contentsString().split(",")
  for i in range(numofpdfcat):
    pdfname = multipdf.getPdf(i).GetName()
    split_string = pdfname.split("_")
    if 'bern' in pdfname and not 'bern%i'%order[0] in pdfname: continue
    if 'exp' in pdfname and not 'exp%i'%order[1] in pdfname: continue
    if 'lau' in pdfname and not 'lau%i'%order[2] in pdfname: continue
    if 'pow' in pdfname and not 'pow%i'%order[3] in pdfname: continue
    frozenstr = ''
    for fn in frozen:
      if not pdfname in fn:
        frozenstr += ","+fn
    Gen = "combine ../Datacards/datacard_" + cat + "_NoSys.txt -M GenerateOnly --setParameters pdfindex_" + cat + "_13TeV="+str(i)+" --toysNoSystematics -t 2000 --expectSignal 1 --saveToys -m 125 --freezeParameters pdfindex_" + cat + "_13TeV"+frozenstr+" --name "+split_string[3]+cat
    run(Gen)
    for j in range(numofpdfcat):
      pdfname2 = multipdf.getPdf(j).GetName()
      if not 'bern' in pdfname2: continue
      split_string2 = pdfname2.split("_")
      frozenstr = ''
      for fn in frozen:
        if not pdfname2 in fn:
          frozenstr += ","+fn
#      Fit = "combine ../Datacards/datacard_" + cat + "_NoSys.txt -M FitDiagnostics --setParameters pdfindex_" + cat +"_13TeV="+str(j)+" --toysFile higgsCombine"+split_string[3]+cat+".GenerateOnly.mH125.123456.root  -t 10 -m 125 --rMin -5 --rMax 5 --freezeParameters pdfindex_" + cat + "_13TeV"+frozenstr+" --cminDefaultMinimizerStrategy=0 -v 3 --name Gen"+split_string[3]+"Fit"+split_string2[3]+cat
      Fit = "combineTool.py --job-mode condor --sub-opts=\'+JobFlavour=\"longlunch\"\' --task-name Gen"+split_string[3]+"Fit"+split_string2[3] + cat + " ../Datacards/datacard_" + cat + "_NoSys.txt -M FitDiagnostics --setParameters pdfindex_" + cat +"_13TeV="+str(j)+" --toysFile higgsCombine"+split_string[3]+cat+".GenerateOnly.mH125.123456.root  -t 2000 -m 125 --rMin -5 --rMax 5 --freezeParameters pdfindex_" + cat + "_13TeV"+frozenstr+" --cminDefaultMinimizerStrategy=0 --name Gen"+split_string[3]+"Fit"+split_string2[3]+cat
      #Fit = "combineTool.py --job-mode crab3 --custom-crab custom_crab.py --task-name Gen"+split_string[3]+"Fit"+split_string2[3] + cat + " -d ../Datacards/datacard_" + cat + "_NoSys.txt -M FitDiagnostics --setParameters pdfindex_" + cat +"_13TeV="+str(j)+" --toysFile higgsCombine"+split_string[3]+cat+".GenerateOnly.mH125.123456.root  -t 10000 -m 125 --rMin -5 --rMax 5 --freezeParameters pdfindex_" + cat + "_13TeV"+frozenstr+" --cminDefaultMinimizerStrategy=0 -v 3 --name Gen"+split_string[3]+"Fit"+split_string2[3]+cat
      run(Fit) 
