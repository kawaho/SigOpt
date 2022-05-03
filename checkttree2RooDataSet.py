import ROOT as r 
import numpy as np
from multiprocessing import Pool, cpu_count

mass = r.RooRealVar("CMS_emu_Mass", "m_{e#mu}", 90, 180, "GeV")
mva_dummy = r.RooRealVar("mva", "mva", 0, 1)

#Create dataframe for fast calulcations of systematics
for whichcat in ['GGcat', 'VBFcat']:
  #Get mva values corresponding to 100 quantiles 
  quantiles = np.load('inputs/'+whichcat+'_quantiles')
#  quantiles[0], quantiles[-1] = -0.001, 1.001
  #Get tree for mva/weight/e_m_Mass
  fin = r.TFile('inputs/'+whichcat+'_tree.root', 'READ')
  tree_data = fin.Get('tree')
  print(tree_data.GetEntries())
  set_total = 0
  #Loop through quantiles and turn tree into RooDataSet
  for i in range(len(quantiles)-1):
      set_ = r.RooDataSet("data_norm_range%i"%(i+1), "data_norm_range%i"%(i+1), tree_data, r.RooArgSet(mass,mva_dummy), "(mva<%f) && (mva>=%f)"%(quantiles[i+1], quantiles[i]))
      set_total+=set_.sumEntries()
  print(set_total)
