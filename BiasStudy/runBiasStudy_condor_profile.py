import ROOT
import os, argparse
from datetime import datetime
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so");
ROOT.gROOT.SetBatch(True)
cats = ['ggHcat0','ggHcat1','ggHcat2','ggHcat3','VBFcat0','VBFcat1']
orders = [[3,1,1],[2,1,1],[2,1,1],[2,1,1],[1,1,1],[1,1,1]]

def run(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
      "Bias Study for LFV H analysis")
  parser.add_argument(
      "-m",
      action="store",
      default=125,
      type=int,
      help="mass point")
  
  args = parser.parse_args()
  
  bkgfile = ROOT.TFile('../Workspaces/CMS_Hemu_13TeV_multipdf_v2025_profile.root')
  bkgWS = bkgfile.Get('multipdf')
  mass = bkgWS.var("CMS_emu_Mass") 
  for cat,order in zip(cats,orders):
    multipdf = bkgWS.pdf('CMS_hemu_'+cat+'_13TeV_bkgshape')
    numofpdfcat = multipdf.getNumPdfs()
    frozen = []
    for i in range(numofpdfcat):
      pdfname = multipdf.getPdf(i).GetName()
      sets = multipdf.getPdf(i).getParameters(ROOT.RooArgSet(mass))
      frozen += sets.contentsString().split(",")
      split_string = pdfname.split("_")
      if 'bern' in pdfname and not 'bern%i'%order[0] in pdfname: continue
      if 'exp' in pdfname and not 'exp%i'%order[1] in pdfname: continue
      if 'pow' in pdfname and not 'pow%i'%order[2] in pdfname: continue
      frozenstr = ''
      for fn in frozen:
        if not pdfname in fn:
          frozenstr += ","+fn
      print(frozenstr)
      Gen = "combine ../Datacards/datacard_" + cat + "_"+str(args.m)+"_NoSys_profile.txt -M GenerateOnly --setParameters pdfindex_" + cat + "_13TeV="+str(i)+" --toysNoSystematics -t 2000 --expectSignal 1 --saveToys -m 125 --freezeParameters pdfindex_" + cat + "_13TeV --X-rtd MINIMIZER_freezeDisassociatedParams --name "+split_string[3]+cat+'_'+str(args.m)+'_profile'
      run(Gen)
      Fit = "combineTool.py --job-mode condor --sub-opts=\'+JobFlavour=\"longlunch\"\' --task-name Gen"+split_string[3]+"Fit" + cat + "_"+str(args.m)+ " ../Datacards/datacard_" + cat + "_"+str(args.m)+ "_NoSys_profile.txt -M FitDiagnostics --toysFile higgsCombine"+split_string[3]+cat+'_'+str(args.m)+'_profile'+".GenerateOnly.mH125.123456.root -t 2000 -m 125 --rMin -10 --rMax 10  --robustFit 1 --cminDefaultMinimizerStrategy=0 --X-rtd MINIMIZER_freezeDisassociatedParams --name Gen"+split_string[3]+"Fit"+cat+"_"+str(args.m)+'_profile'
      run(Fit) 
