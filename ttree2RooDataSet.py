import ROOT as r 
import numpy as np

#Listing lepton scale/smearing systematics
leptonUnc = ['me']#['ees', 'eer', 'me']
mass = r.RooRealVar("CMS_emu_Mass", "m_{e#mu}", 110, 160, "GeV")
mva_dummy = r.RooRealVar("mva", "mva", 0, 1)
weight_dummy = r.RooRealVar("weight", "weight", -20, 20)
mva_sys_dummy = {}
for sys in leptonUnc:
  for UpDown in ['Up', 'Down']:
    mva_sys_dummy['mva_%s_%s'%(sys,UpDown)] = r.RooRealVar('mva_%s_%s'%(sys,UpDown), "mva", 0, 1)
#Create dataframe for fast calulcations of systematics
for whichcat in ['GGcat', 'VBFcat']:
  #Get mva values corresponding to 100 quantiles 
  quantiles = np.load('inputs/'+whichcat+'_quantiles')

  #Get tree for mva/weight/e_m_Mass
  datasets = []
  fin = r.TFile('inputs/'+whichcat+'_tree.root')
  tree_data = fin.Get('tree')

  #Loop through quantiles and turn tree into RooDataSet
  for i in range(len(quantiles)-1):
      datasets.append(r.RooDataSet("data_norm_range%i"%(i+1), "data_norm_range%i"%(i+1), tree_data, r.RooArgSet(mass,mva_dummy), "(mva<%d) && (mva>=%d)"%(quantiles[i+1], quantiles[i])))

  #output all RooDataSet into workspace
  w = r.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
  for dataset in datasets:
    getattr(w, 'import')(dataset)
  w.Print()
  w.writeToFile("inputs/"+whichcat+".root")
  r.gDirectory.Add(w)

  #Divide into GG/VBF
  for whichcat_deep in ['GG', 'VBF']:
    #Create tree for mva/weight/e_m_Mass/lep scale/smearing
    datasets = []
    fin = r.TFile("inputs/"+whichcat_deep+"_"+whichcat+"_tree.root")
    tree = fin.Get('tree')
    for i in range(len(quantiles)-1):
    #Loop through quantiles and turn tree into RooDataSet
      datasets.append(r.RooDataSet("norm_range%i"%(i+1), "norm_range%i"%(i+1), tree, r.RooArgSet(mass,mva_dummy,weight_dummy), "(mva<%d) && (mva>=%d)"%(quantiles[i+1],quantiles[i]), "weight"))
      for sys in leptonUnc:
        for UpDown in ['Up', 'Down']:
          datasets.append(r.RooDataSet("%s_%s_range%i"%(sys,UpDown,i+1), "%s_%s_range%i"%(sys,UpDown,i+1), tree, r.RooArgSet(mass,mva_sys_dummy['mva_%s_%s'%(sys,UpDown)],weight_dummy), "(mva_%s_%s<%d) && (mva_%s_%s>=%d)"%(sys,UpDown,quantiles[i+1],sys,UpDown,quantiles[i]), "weight"))

    #output all RooDataSet into workspace
    w = r.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
    for dataset in datasets:
      getattr(w, 'import')(dataset)
    w.Print()
    w.writeToFile("inputs/"+whichcat_deep+"_"+whichcat+".root")
    r.gDirectory.Add(w)

