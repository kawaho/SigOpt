import ROOT as r 
import numpy as np
from multiprocessing import Pool, cpu_count

#pt scan
mpt_scan = [15, 20]
ept_scan = [20, 25]

#Listing lepton scale/smearing systematics
leptonUnc = ['ees', 'eer', 'me']
mass = r.RooRealVar("CMS_emu_Mass", "m_{e#mu}", 100, 170, "GeV")
mva_dummy = r.RooRealVar("mva", "mva", 0, 1)
weight_dummy = r.RooRealVar("weight", "weight", -20, 20)
ept_dummy = r.RooRealVar("ept", "ept", 20, 9999)
mpt_dummy = r.RooRealVar("mpt", "mpt", 15, 9999)
mva_sys_dummy = {}
mass_sys = {}
for sys in leptonUnc:
  for UpDown in ['Up', 'Down']:
    mva_sys_dummy['mva_%s_%s'%(sys,UpDown)] = r.RooRealVar('mva_%s_%s'%(sys,UpDown), "mva", 0, 1)
    mass_sys['CMS_emu_Mass_%s_%s'%(sys,UpDown)] = r.RooRealVar('CMS_emu_Mass_%s_%s'%(sys,UpDown), "m_{e#mu}", 100, 170, "GeV")
#Create dataframe for fast calulcations of systematics

#Get mva values corresponding to 100 quantiles 
quantiles = np.arange(0,1.01,0.01) #np.load('inputs/'+whichcat+'_quantiles')
quantiles[0], quantiles[-1] = -0.001, 1.001

for whichcat in ['GGcat', 'VBFcat']:
  for mpt in mpt_scan:
    for ept in ept_scan:
    
      #Get tree for mva/weight/e_m_Mass
      datasets = []
      fin = r.TFile('inputs/'+whichcat+'_tree.root', 'READ')
      tree_data = fin.Get('tree')
    
      #Loop through quantiles and turn tree into RooDataSet
      for i in range(len(quantiles)-1):
          datasets.append(r.RooDataSet("data_norm_range%i"%(i+1), "data_norm_range%i"%(i+1), tree_data, r.RooArgSet(mass,mva_dummy,ept_dummy,mpt_dummy), "(mva<%f) && (mva>=%f) && (mpt>%f) && (ept>%f)"%(quantiles[i+1], quantiles[i],mpt,ept)))
    
      #output all RooDataSet into workspace
      w = r.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
      for dataset in datasets:
        getattr(w, 'import')(dataset)
      w.Print()
      w.writeToFile("inputs/"+whichcat+"_ept%i_mpt%i.root"%(ept,mpt))
      r.gDirectory.Add(w)


  for masspt in ['120','125','130']:  
    #Divide into GG/VBF ans masspt
    for whichcat_deep in ['GG', 'VBF']:

      def appendNcut(i):
        #Create tree for mva/weight/e_m_Mass/lep scale/smearing
        fin = r.TFile("inputs/"+whichcat_deep+"_"+whichcat+"_"+masspt+"_tree.root")
        tree = fin.Get('tree')
        #Loop through quantiles and turn tree into RooDataSet
        datasets_set = []
        datasets_set.append(r.RooDataSet("norm_range%i"%(i+1), "norm_range%i"%(i+1), tree, r.RooArgSet(mass,mva_dummy,weight_dummy), "(mva<%f) && (mva>=%f)"%(quantiles[i+1],quantiles[i]), "weight"))
        for sys in leptonUnc:
          for UpDown in ['Up', 'Down']:
            datasets_set.append(r.RooDataSet("%s_%s_range%i"%(sys,UpDown,i+1), "%s_%s_range%i"%(sys,UpDown,i+1), tree, r.RooArgSet(mass_sys['CMS_emu_Mass_%s_%s'%(sys,UpDown)],mva_sys_dummy['mva_%s_%s'%(sys,UpDown)],weight_dummy), "(mva_%s_%s<%f) && (mva_%s_%s>=%f)"%(sys,UpDown,quantiles[i+1],sys,UpDown,quantiles[i]), "weight"))
        return datasets_set
     
      pool = Pool(processes=cpu_count())
      datasets = pool.map(appendNcut, range(len(quantiles)-1)) 

      #output all RooDataSet into workspace
      w = r.RooWorkspace("CMS_emu_workspace", "CMS_emu_workspace")
      for i, dataset in enumerate(datasets):
        for ds in dataset:
          getattr(w, 'import')(ds)
      w.Print()
      w.writeToFile("inputs/"+whichcat_deep+"_"+whichcat+"_"+masspt+".root")
      r.gDirectory.Add(w)

