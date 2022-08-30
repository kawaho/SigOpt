import ROOT
import os, argparse
from datetime import datetime
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so");
ROOT.gROOT.SetBatch(True)
cats = ['ggcat0','ggcat1','ggcat2','ggcat3','vbfcat0','vbfcat1']

parser = argparse.ArgumentParser(
    "Bias Study for LFV H analysis")
parser.add_argument(
    "-m",
    action="store",
    default=125,
    type=int,
    help="mass point")

args = parser.parse_args()

def run(cmd):
  print "%s\n\n"%cmd
#  os.system(cmd)

for cat in cats:
  for sigtype in ['cb', 'gaus']:
    altsigtype = 'cb' if sigtype=='gaus' else 'gaus'
    Gen = "combine ../Datacards/datacard_" + cat + "_"+str(args.m)+"_NoSys_ShapeUnc.txt -M GenerateOnly --toysNoSystematics -t 2000 --expectSignal 1 --saveToys -m 125 --name "+sigtype+"_"+cat+'_'+str(args.m)
    if sigtype == 'gaus':
      Gen = Gen.replace('.txt', '_gaus.txt')
    run(Gen)
    Fit = "combineTool.py --job-mode condor --sub-opts=\'+JobFlavour=\"longlunch\"\' --task-name Gen"+sigtype+"Fit" + altsigtype +"_"+ cat + "_"+str(args.m)+ " ../Datacards/datacard_" + cat + "_"+str(args.m)+ "_NoSys_ShapeUnc.txt -M FitDiagnostics --toysFile higgsCombine"+sigtype+"_"+cat+'_'+str(args.m)+".GenerateOnly.mH125.123456.root -t 2000 -m 125 --rMin -2.5 --rMax 2.5 --cminDefaultMinimizerStrategy=0 --name Gen"+sigtype+"Fit"+altsigtype+"_"+cat+"_"+str(args.m)
    if altsigtype == 'gaus':
      Fit = Fit.replace('.txt', '_gaus.txt')
    run(Fit) 
