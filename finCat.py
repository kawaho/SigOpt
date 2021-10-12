from writedatacard import writedatacard
from fitSB_tree import fit
import pandas as pd
import ROOT
import argparse

range_ =  
{ 
  'gg': [0, 9, 33, 53, 70, 100],
  'vbf': [0, 9, 33, 53, 70, 100],
}

file_data_full = 
{
  'gg': TFile('GGcat.root'),
  'vbf': TFile('VBFcat.root')
}

df_gg_full = 
{
  'gg': pd.read_csv('GG_GGcat.csv'),
  'vbf': pd.read_csv('VBF_GGcat.csv')
}

df_vbf_full = 
{
  'gg': pd.read_csv('GG_VBFcat.csv'),
  'vbf': pd.read_csv('VBF_VBFcat.csv')
}

file_gg_full = 
{
  'gg': TFile('GG_GGcat.root'),
  'vbf': TFile('VBF_GGcat.root')
}

file_vbf_full = 
{
  'gg': TFile('GG_VBFcat.root'),
  'vbf': TFile('VBF_VBFcat.root')
}

wsobject = []
catnames = []
db = []


for vbf_gg in ['gg', 'vbf']:
  inWS = file_data_full[vbf_gg].Get("CMS_emu_workspace")
  mass = inWS.var("CMS_emu_Mass")
  wsobject.append(mass)
  for i in range(len(range_[vbf_gg])-1):
    rangl, rangh = range_[vbf_gg][i], range_[vbf_gg][i+1]
    catnames.append('%scat%i'%(vbf_gg,i))
    fit(file_data_full[vbf_gg], file_gg_full[vbf_gg], file_vbf_full[vbf_gg], 'exp1', [rangl, rangh], catnames[-1], False)
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
  writedatacard(catnames, bins, df_gg_full[vbf_gg], df_vbf_full[vbf_gg], True, True)

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
