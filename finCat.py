from writedatacard import writedatacard
from fitSB_CBE import fit
import pandas as pd
import ROOT
import argparse
parser = argparse.ArgumentParser(
    "Final Categories for LFV H analysis")
parser.add_argument(
    "--limit",
    action='store_true'
    )
parser.add_argument(
    "--card",
    action='store_true'
    )
parser.add_argument(
    "--mass", 
    type=str, 
    default='120,125,130')

args = parser.parse_args()
range_ =  { 
  'gg': [1, 48, 71, 88, 101],
  'vbf': [65, 86, 101]
}
file_data_full = {
  'gg': ROOT.TFile('inputs/GGcat.root'),
  'vbf': ROOT.TFile('inputs/VBFcat.root')
}
for m in args.mass.split(','):
  df_gg_full = {
    'gg': pd.read_csv('inputs/GG_GGcat_'+m+'.csv'),
    'vbf': pd.read_csv('inputs/GG_VBFcat_'+m+'.csv')
  }
  
  df_vbf_full = {
    'gg': pd.read_csv('inputs/VBF_GGcat_'+m+'.csv'),
    'vbf': pd.read_csv('inputs/VBF_VBFcat_'+m+'.csv')
  }
  
  file_gg_full = {
    'gg': ROOT.TFile('inputs/GG_GGcat_'+m+'.root'),
    'vbf': ROOT.TFile('inputs/GG_VBFcat_'+m+'.root')
  }
  
  file_vbf_full = {
    'gg': ROOT.TFile('inputs/VBF_GGcat_'+m+'.root'),
    'vbf': ROOT.TFile('inputs/VBF_VBFcat_'+m+'.root')
  }
  
  wsobject = []
  db = []
  numberOfBkg = {}
  
  for vbf_gg in ['gg', 'vbf']:
    catnames = []
    bins = []
    inWS = file_data_full[vbf_gg].Get("CMS_emu_workspace")
    mass = inWS.var("CMS_emu_Mass")
    wsobject.append(mass)
    for i in range(len(range_[vbf_gg])-1):
      rangl, rangh = range_[vbf_gg][i], range_[vbf_gg][i+1]
      catnames.append('%scat%i'%(vbf_gg,i))
      bins.append([rangl, rangh])
      if args.card: continue
      if args.limit:
        numberOfBkg[catnames[-1]] = fit(inWS, file_gg_full[vbf_gg].Get("CMS_emu_workspace"), file_vbf_full[vbf_gg].Get("CMS_emu_workspace"), 'exp1', [rangl, rangh], catnames[-1]+'_'+m, makePlot=True, saveData=False, sys_=True, bin_=True, masspt=float(m))[1]
      else:
        numberOfBkg[catnames[-1]] = fit(inWS, file_gg_full[vbf_gg].Get("CMS_emu_workspace"), file_vbf_full[vbf_gg].Get("CMS_emu_workspace"), 'exp1', [rangl, rangh], catnames[-1]+'_'+m, makePlot=True, saveData=False, sys_=False)[1]
      if m=='125':
        db.append(inWS.data("data_norm_range%i"%rangl))
        for j in range(rangl+1,rangh):
          db[-1].append(inWS.data("data_norm_range%i"%j))
        db[-1].SetNameTitle("Data_13TeV_"+catnames[-1], "Data_13TeV_"+catnames[-1])
    
    #Example of format
    #cats = [ggcat0,ggcat1]
    #bins = [[0,40],[40,100]]
    
    if args.limit:
      writedatacard(catnames, bins, df_gg_full[vbf_gg], df_vbf_full[vbf_gg], sys_=True, limit=True, masspt=m)
    else:
      catnames = [i+'_'+str(m) for i in catnames]
      writedatacard(catnames, bins, df_gg_full[vbf_gg], df_vbf_full[vbf_gg], sys_=False, limit=False)
  
  if not args.card and m=='125':
    outWS = ROOT.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
    getattr(outWS, 'import')(mass)
    print(db)
    for d in db:
      getattr(outWS, 'import')(d)
    outWS.Print()
    outWS.writeToFile("dataws_final.root")
    ROOT.gDirectory.Add(outWS)
    print('Number of Bkg Events', numberOfBkg)
