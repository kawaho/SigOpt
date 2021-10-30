from writedatacard import writedatacard
from fitSB_CBE import fit
import pandas as pd
import ROOT
import argparse

range_ =  { 
  'gg': [1, 13, 40, 73, 101],
  'vbf': [1, 16, 56, 77, 101]
}
file_data_full = {
  'gg': ROOT.TFile('inputs/GGcat.root'),
  'vbf': ROOT.TFile('inputs/VBFcat.root')
}

df_gg_full = {
  'gg': pd.read_csv('inputs/GG_GGcat.csv'),
  'vbf': pd.read_csv('inputs/VBF_GGcat.csv')
}

df_vbf_full = {
  'gg': pd.read_csv('inputs/GG_VBFcat.csv'),
  'vbf': pd.read_csv('inputs/VBF_VBFcat.csv')
}

file_gg_full = {
  'gg': ROOT.TFile('inputs/GG_GGcat.root'),
  'vbf': ROOT.TFile('inputs/GG_VBFcat.root')
}

file_vbf_full = {
  'gg': ROOT.TFile('inputs/VBF_GGcat.root'),
  'vbf': ROOT.TFile('inputs/VBF_VBFcat.root')
}

bins = []
wsobject = []
catnames = []
db = []
numberOfBkg = {}

for vbf_gg in ['gg', 'vbf']:
  inWS = file_data_full[vbf_gg].Get("CMS_emu_workspace")
  mass = inWS.var("CMS_emu_Mass")
  wsobject.append(mass)
  for i in range(len(range_[vbf_gg])-1):
    rangl, rangh = range_[vbf_gg][i], range_[vbf_gg][i+1]
    catnames.append('%scat%i'%(vbf_gg,i))
    bins.append([rangl, rangh])
    numberOfBkg[catnames[-1]] = fit(inWS, file_gg_full[vbf_gg].Get("CMS_emu_workspace"), file_vbf_full[vbf_gg].Get("CMS_emu_workspace"), 'exp1', [rangl, rangh], catnames[-1], True, False, True)[1]
    db.append(inWS.data("data_norm_range%i"%rangl))
    for j in range(rangl+1,rangh):
      db[-1].append(inWS.data("data_norm_range%i"%j))
    db[-1].SetNameTitle("Data_13TeV_"+catnames[-1], "Data_13TeV_"+catnames[-1])
  
  #Example of format
  #cats = [ggcat0,ggcat1]
  #bins = [[0,40],[40,100]]
  
  #writedatacard(catnames, bins, False)
  writedatacard(catnames, bins, df_gg_full[vbf_gg], df_vbf_full[vbf_gg], True, True)

#lumi = ROOT.RooRealVar("IntLumi", "Integrated luminosity", 137.6, "fb^{-1}")
#sqrts = ROOT.RooRealVar("SqrtS","Center of Mass Energy", 13, "TeV")
outWS = ROOT.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
#wsobject.append([sqrts,lumi])
getattr(outWS, 'import')(mass)
#getattr(outWS, 'import')(sqrts)
#getattr(outWS, 'import')(lumi)
for d in db:
  getattr(outWS, 'import')(d)
outWS.Print()
outWS.writeToFile("dataws_final.root")
ROOT.gDirectory.Add(outWS)
print('Number of Bkg Events', numberOfBkg)
