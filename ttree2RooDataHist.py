import ROOT as r 
import numpy as np
from multiprocessing import Pool, cpu_count

#Listing lepton scale/smearing systematics
leptonUnc = ['ees', 'eer', 'me']
mass = r.RooRealVar("CMS_emu_Mass", "m_{e#mu}", 100, 170, "GeV")
mva_dummy = r.RooRealVar("mva", "mva", 0, 1)
weight_dummy = r.RooRealVar("weight", "weight", -20, 20)
mva_sys_dummy = {}
mass_sys = {}
for sys in leptonUnc:
  for UpDown in ['Up', 'Down']:
    mva_sys_dummy['mva_%s_%s'%(sys,UpDown)] = r.RooRealVar('mva_%s_%s'%(sys,UpDown), "mva", 0, 1)
#Create dataframe for fast calulcations of systematics
for whichcat in ['GGcat', 'VBFcat']:
  #Get mva values corresponding to 100 quantiles 
  quantiles = np.load('inputs/'+whichcat+'_quantiles')
  #quantiles = np.arange(0,1.01,0.01) #np.load('inputs/'+whichcat+'_quantiles')
  quantiles[0], quantiles[-1] = -0.001, 1.001
  #Get tree for mva/weight/e_m_Mass
  datasets = []
  fin = r.TFile('inputs/'+whichcat+'_tree.root', 'READ')
  tree_data = fin.Get('tree')

  #Loop through quantiles and turn tree into RooDataSet
  for i in range(len(quantiles)-1):
      datasets.append(r.RooDataSet("data_norm_range%i"%(i+1), "data_norm_range%i"%(i+1), tree_data, r.RooArgSet(mass,mva_dummy), "(mva<%f) && (mva>=%f)"%(quantiles[i+1], quantiles[i])))

  #output all RooDataSet into workspace
  w = r.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
  for dataset in datasets:
    getattr(w, 'import')(dataset)
  w.Print()
  w.writeToFile("inputs/"+whichcat+".root")
  r.gDirectory.Add(w)


  for masspt in ['125']:  
    #Divide into GG/VBF ans masspt
    for whichcat_deep in ['GG', 'VBF']:
      fin = r.TFile("inputs/"+whichcat_deep+"_"+whichcat+"_"+masspt+"_tree.root")
      tree = {}
      tree['nominal'] = fin.Get('nominal')
      for sys in leptonUnc:
        for UpDown in ['Up', 'Down']:
          tree['%s_%s'%(sys,UpDown)] = fin.Get('%s_%s'%(sys,UpDown))

      def appendNcut(i):
        #Create tree for mva/weight/e_m_Mass/lep scale/smearing
        subh = tree['nominal'].ProjectionX("norm_range%i"%(i+1), i, i+1)
        #Loop through quantiles and turn tree into RooDataSet
        datasets_set = []
        datasets_set.append(r.RooDataHist("norm_range%i"%(i+1),"norm_range%i"%(i+1),r.RooArgList(mass),r.RooFit.Import(subh)))
        for sys in leptonUnc:
          for UpDown in ['Up', 'Down']:
            subh = tree['%s_%s'%(sys,UpDown)].ProjectionX("%s_%s_range%i"%(sys,UpDown,i+1), i, i+1)
            datasets_set.append(r.RooDataHist("%s_%s_range%i"%(sys,UpDown,i+1), "%s_%s_range%i"%(sys,UpDown,i+1),r.RooArgList(mass),r.RooFit.Import(subh)))
        return datasets_set
     
      #pool = Pool(processes=4)#cpu_count())
      #datasets = pool.map(appendNcut, range(len(quantiles)-1)) 
      datasets = []
      for i in range(len(quantiles)-1):
         datasets.append(appendNcut(i))
      #output all RooDataSet into workspace
      w = r.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
      for i, dataset in enumerate(datasets):
        for ds in dataset:
          getattr(w, 'import')(ds)
      w.Print()
      w.writeToFile("inputs/"+whichcat_deep+"_"+whichcat+"_"+masspt+"_hist.root")
      r.gDirectory.Add(w)
      print('done with'+whichcat_deep+"_"+whichcat+"_"+masspt)
