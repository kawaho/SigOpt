from writedatacard import writedatacard
from fitSB_CBE import fit
import fitSB_Gaus 
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
    default='110,120,125,130,140,150,160')
parser.add_argument(
    "--refit",
    type=str, 
    default='')

args = parser.parse_args()

range_ =  { 
  'ggH': [1, 52, 78, 90, 101],
  'VBF': [64, 89, 94, 101]
}

#file_data_full = {'ggH': {}, 'VBF': {}}

#mpt_cuts = [15, 20]
#ept_cuts = [20, 25]

#for mpt_cut in mpt_cuts:
#   for ept_cut in ept_cuts:
#     file_data_full['ggH'][str(mpt_cut)+'_ept'+str(ept_cut)] = ROOT.TFile('inputs/GGcat_mpt'+str(mpt_cut)+'_ept'+str(ept_cut)+'_test.root', 'READ')
#     file_data_full['VBF'][str(mpt_cut)+'_ept'+str(ept_cut)] = ROOT.TFile('inputs/VBFcat_mpt'+str(mpt_cut)+'_ept'+str(ept_cut)+'_test.root', 'READ')
#print(file_data_full)

file_data_full = {
  'ggH': ROOT.TFile('inputs/GGcat.root'),
  'VBF': ROOT.TFile('inputs/VBFcat.root')
}
for m in args.mass.split(','):
  df_ggH_full = {
    'ggH': pd.read_csv('inputs/GG_GGcat_'+m+'.csv'),
    'VBF': pd.read_csv('inputs/GG_VBFcat_'+m+'.csv')
  }
  
  df_VBF_full = {
    'ggH': pd.read_csv('inputs/VBF_GGcat_'+m+'.csv'),
    'VBF': pd.read_csv('inputs/VBF_VBFcat_'+m+'.csv')
  }
  
  file_ggH_full = {
    'ggH': ROOT.TFile('inputs/GG_GGcat_'+m+'.root'),
    'VBF': ROOT.TFile('inputs/GG_VBFcat_'+m+'.root')
  }
  
  file_VBF_full = {
    'ggH': ROOT.TFile('inputs/VBF_GGcat_'+m+'.root'),
    'VBF': ROOT.TFile('inputs/VBF_VBFcat_'+m+'.root')
  }
  
  wsobject = []
  db = []
  numberOfBkg = {}

  gausOrder =  pd.read_csv("gaus_ftest_result.csv", skipinitialspace=True)
  
  for VBF_ggH in ['ggH', 'VBF']:
    catnames = []
    bins = []
    inWS = file_data_full[VBF_ggH].Get("CMS_emu_workspace")
    mass = inWS.var("CMS_emu_Mass")
    wsobject.append(mass)
    for i in range(len(range_[VBF_ggH])-1):
      rangl, rangh = range_[VBF_ggH][i], range_[VBF_ggH][i+1]
      catnames.append('%scat%i'%(VBF_ggH, len(range_[VBF_ggH])-2-i))
      if args.refit!='' and (catnames[-1]!=args.refit.split(',')[0] or m!=args.refit.split(',')[1]): continue
      bins.append([rangl, rangh])
      if args.card: continue
      #norder = {'ggH': 2, 'qqH': 3}
      df_gaus = gausOrder[(gausOrder['cat']==catnames[-1]) & (gausOrder['mass']==125)]
      norder = dict(zip(df_gaus.proc, df_gaus.order.astype(int)))
      if args.limit:
       # numberOfBkg[catnames[-1]] = fit(inWS, file_ggH_full[VBF_ggH].Get("CMS_emu_workspace"), file_VBF_full[VBF_ggH].Get("CMS_emu_workspace"), 'exp1', [rangl, rangh], catnames[-1]+'_'+m, makePlot=True, saveData=False, sys_=True, bin_=True, masspt=float(m))[1]
         fitSB_Gaus.fit(inWS, file_ggH_full[VBF_ggH].Get("CMS_emu_workspace"), file_VBF_full[VBF_ggH].Get("CMS_emu_workspace"), 'exp1', [rangl, rangh], catnames[-1]+'_'+m, 3, makePlot=True, saveData=False, sys_=True, masspt=float(m))
        #fitSB_Gaus.fit(inWS, file_ggH_full[VBF_ggH].Get("CMS_emu_workspace"), file_VBF_full[VBF_ggH].Get("CMS_emu_workspace"), 'exp1', [rangl, rangh], catnames[-1]+'_'+m, norder, makePlot=True, saveData=False, sys_=True, masspt=float(m))
      else:
        #numberOfBkg[catnames[-1]] = fit(inWS, file_ggH_full[VBF_ggH].Get("CMS_emu_workspace"), file_VBF_full[VBF_ggH].Get("CMS_emu_workspace"), 'exp1', [rangl, rangh], catnames[-1]+'_'+m, makePlot=True, saveData=False, sys_=False, masspt=float(m))[1]
        fitSB_Gaus.fit(inWS, file_ggH_full[VBF_ggH].Get("CMS_emu_workspace"), file_VBF_full[VBF_ggH].Get("CMS_emu_workspace"), 'exp1', [rangl, rangh], catnames[-1]+'_'+m, norder, makePlot=True, saveData=False, sys_=False, masspt=float(m))[1]
      if m=='125':
        db.append(inWS.data("data_norm_range%i"%rangl))
        for j in range(rangl+1,rangh):
          db[-1].append(inWS.data("data_norm_range%i"%j))
        db[-1].SetNameTitle("Data_13TeV_"+catnames[-1], "Data_13TeV_"+catnames[-1])
     
    #Example of format
    #cats = [ggHcat0,ggHcat1]
    #bins = [[0,40],[40,100]]
     
    if args.limit:
      #writedatacard(catnames, bins, df_ggH_full[VBF_ggH], df_VBF_full[VBF_ggH], sys_=False, limit=True, masspt=m, ShapeUnc=True)
      writedatacard(catnames, bins, df_ggH_full[VBF_ggH], df_VBF_full[VBF_ggH], sys_=True, limit=True, masspt=m)
    else:
      catnames = [i+'_'+str(m) for i in catnames]
      writedatacard(catnames, bins, df_ggH_full[VBF_ggH], df_VBF_full[VBF_ggH], sys_=False, limit=False)#, ShapeUnc=True)
#      writedatacard(catnames, bins, df_ggH_full[VBF_ggH], df_VBF_full[VBF_ggH], sys_=False, limit=False, useGaus=True, ShapeUnc=True)

  if not args.card and m=='125':
    outWS = ROOT.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
    getattr(outWS, 'import')(mass)
    print(db)
    for d in db:
      getattr(outWS, 'import')(d)
    outWS.Print()
    outWS.writeToFile("dataws_final.root")
    ROOT.gDirectory.Add(outWS)
       
