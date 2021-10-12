from writedatacard import writedatacard
from fitSB_tree import fit
import pandas as pd
import ROOT
import argparse

parser = argparse.ArgumentParser(
    "Optimizer for LFV H analysis")
parser.add_argument(
    "--cat",
    action="store",
    dest="cat",
    default="gg",
    help="Which category")
args = parser.parse_args()

range_ =  [0, 9, 33, 53, 70, 100]

if args.cat=='gg':
  df_gg_full, df_vbf_full = pd.read_csv('GG_GGcat.csv'), pd.read_csv('VBF_GGcat.csv')
  file_gg_full, file_vbf_full = TFile('GG_GGcat.root'), TFile('VBF_GGcat.root')
  file_data_full = TFile('GGcat.root')
else:
  df_gg_full, df_vbf_full = pd.read_csv('GG_VBFcat.csv'), pd.read_csv('VBF_VBFcat.csv')
  file_gg_full, file_vbf_full = TFile('GG_VBFcat.root'), TFile('VBF_VBFcat.root')
  file_data_full = TFile('VBFcat.root')

bins = []
catnames = []
wsobject = []
db = []

inWS = file_data_full.Get("CMS_emu_workspace")
mass = inWS.var("CMS_emu_Mass")
wsobject.append(mass)
for i in range(len(range_)-1):
  rangl, rangh = range_[i], range_[i+1]
  catnames.append('ggcat%i'%i)
  fit(file_data_full, file_gg_full, file_vbf_full, 'exp1', [rangl, rangh], catnames[-1], False)
  db.append(inWS.data("data_norm_range%i"%rangl))
  wsobject.append(inWS.data("data_norm_range%i"%rangl))
  for j in range(rangl+1,rangh):
    db[-1].append(inWS.data("data_norm_range%i"%j))
    wsobject.append(inWS.data("data_norm_range%i"%j))
  db[-1].SetNameTitle("Data_13TeV_"+catnames[-1], "Data_13TeV_"+catnames[-1])
#  wsobject.append(db)
rfile.Close()

#Example of format
#cats = [ggcat0,ggcat1]
#bins = [[0,40],[40,100]]

bins =  [ range_[i:i+1] for i in range(len(range_)-1)]

#writedatacard(catnames, bins, False)
writedatacard(catnames, bins, df_gg_full, df_vbf_full, True, True)

lumi = ROOT.RooRealVar("IntLumi", "Integrated luminosity", 1, "fb^{-1}")
sqrts = ROOT.RooRealVar("SqrtS","Center of Mass Energy", 13, "TeV")
outWS = ROOT.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
wsobject.append([sqrts,lumi])
getattr(outWS, 'import')(mass)
getattr(outWS, 'import')(sqrts)
getattr(outWS, 'import')(lumi)
for d in db:
  getattr(outWS, 'import')(d)
outWS.Print()
outWS.writeToFile("dataws_final.root")
ROOT.gDirectory.Add(outWS)
