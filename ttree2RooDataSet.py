import ROOT as r 
import numpy as np
from multiprocessing import Pool, cpu_count

#Listing lepton scale/smearing systematics
leptonUnc = ['ess', 'me']
mass = r.RooRealVar("CMS_emu_Mass", "m_{e#mu}", 90, 180, "GeV")
weight_dummy = r.RooRealVar("weight", "weight", -20, 20)
#Create dataframe for fast calulcations of systematics
for whichcat in ['GGcat', 'VBFcat']:
  #Get mva values corresponding to 100 quantiles 
  quantiles = np.arange(0,1.01,0.01) 
  #quantiles = np.load('inputs/'+whichcat+'_quantiles')
  #quantiles[0], quantiles[-1] = -0.001, 1.001
  #Get tree for mva/weight/e_m_Mass
  datasets = []
  fin = r.TFile('~/Flavour-Violating-Coffea/results/SenScan_v9/'+whichcat+'_tree.root', 'READ')

  #Loop through quantiles and turn tree into RooDataSet
  for i in range(len(quantiles)-1):
      tree_data = fin.Get('tree_'+str(i+1))
      datasets.append(r.RooDataSet("data_norm_range%i"%(i+1), "data_norm_range%i"%(i+1), tree_data, r.RooArgSet(mass)))

  #output all RooDataSet into workspace
  w = r.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
  for dataset in datasets:
    getattr(w, 'import')(dataset)
  w.Print()
  w.writeToFile("inputs/"+whichcat+".root")
  r.gDirectory.Add(w)

#pt cuts
#  mpt_cuts = [15, 20]
#  ept_cuts = [20, 25]
#  for mpt_cut in mpt_cuts:
#     for ept_cut in ept_cuts:
#       datasets = []
##       if mpt_cut == 15 and ept_cut == 20: continue
#       fin = r.TFile('inputs/'+whichcat+'_mpt'+str(mpt_cut)+'_ept'+str(ept_cut)+'_tree.root', 'READ')
#       for i in range(len(quantiles)-1):
#           tree_data = fin.Get('tree_'+str(i+1))
#           datasets.append(r.RooDataSet("data_norm_range%i"%(i+1), "data_norm_range%i"%(i+1), tree_data, r.RooArgSet(mass)))
#
#       #output all RooDataSet into workspace
#       w = r.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
#       for dataset in datasets:
#         getattr(w, 'import')(dataset)
#       w.Print()
#       w.writeToFile("inputs/"+whichcat+'_mpt'+str(mpt_cut)+'_ept'+str(ept_cut)+"_test.root")
#       r.gDirectory.Add(w)

  for masspt in ['120','125','130']:#['110','120','125','130','140','150','160']:  
    #Divide into GG/VBF ans masspt
    for whichcat_deep in ['GG', 'VBF']:

      def appendNcut(i):
        #Create tree for mva/weight/e_m_Mass/lep scale/smearing
        #Loop through quantiles and turn tree into RooDataSet
        fin = r.TFile("~/Flavour-Violating-Coffea/results/SenScan_v9/"+whichcat_deep+"_"+whichcat+"_"+masspt+"_tree.root", 'READ')
        tree = {}
        tree['nominal'] = fin.Get('tree_'+str(i+1))
        for sys in leptonUnc:
          for UpDown in ['Up', 'Down']:
            tree['%s_%s'%(sys,UpDown)] = fin.Get('tree_%s_%s_'%(sys,UpDown)+str(i+1))
        datasets_set = []
        datasets_set.append(r.RooDataSet("norm_range%i"%(i+1), "norm_range%i"%(i+1), tree['nominal'], r.RooArgSet(mass,weight_dummy), "", "weight"))
        for sys in leptonUnc:
          for UpDown in ['Up', 'Down']:
            datasets_set.append(r.RooDataSet("%s_%s_range%i"%(sys,UpDown,i+1), "%s_%s_range%i"%(sys,UpDown,i+1), tree['%s_%s'%(sys,UpDown)], r.RooArgSet(mass,weight_dummy), "", "weight"))
        return datasets_set
     
      #output all RooDataSet into workspace
      w = r.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
#      for i in range(len(quantiles)-1):
#        print(i)
#        datasets = appendNcut(i)
#        for i, dataset in enumerate(datasets):
#          getattr(w, 'import')(dataset)
      pool = Pool(processes=8)#cpu_count())
      datasets = pool.map(appendNcut, range(len(quantiles)-1)) 

      for i, dataset in enumerate(datasets):
        for ds in dataset:
          getattr(w, 'import')(ds)
      w.Print()
      w.writeToFile("inputs/"+whichcat_deep+"_"+whichcat+"_"+masspt+".root")
      r.gDirectory.Add(w)

