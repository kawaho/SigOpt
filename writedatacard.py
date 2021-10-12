from calmigration import calmigration
import collections
import re
import csv

procs = ['GGLFV', 'VBFLFV', 'bkg', 'data_obs']
datacard = []
ws = []
CMSnames = {
'jetAbsolute': 'CMS_scale_j_Absolute',
'jetAbsolute_2016preVFP': 'CMS_scale_j_Absolute_2016preVFP',
'jetAbsolute_2016postVFP': 'CMS_scale_j_Absolute_2016postVFP',
'jetAbsolute_2017': 'CMS_scale_j_Absolute_2017',
'jetAbsolute_2018': 'CMS_scale_j_Absolute_2018',
'jetBBEC1': 'CMS_scale_j_BBEC1',
'jetBBEC1_2016preVFP': 'CMS_scale_j_BBEC1_2016preVFP',
'jetBBEC1_2016postVFP': 'CMS_scale_j_BBEC1_2016postVFP',
'jetBBEC1_2017': 'CMS_scale_j_BBEC1_2017',
'jetBBEC1_2018': 'CMS_scale_j_BBEC1_2018',
'jetEC2': 'CMS_scale_j_EC2',
'jetEC2_2016preVFP': 'CMS_scale_j_EC2_2016preVFP', 
'jetEC2_2016postVFP': 'CMS_scale_j_EC2_2016postVFP', 
'jetEC2_2017': 'CMS_scale_j_EC2_2017', 
'jetEC2_2018': 'CMS_scale_j_EC2_2018',
'jetFlavorQCD': 'CMS_scale_j_FlavorQCD',
'jetHF': 'CMS_scale_j_HF',
'jetHF_2016preVFP': 'CMS_scale_j_HF_2016preVFP',
'jetHF_2016postVFP': 'CMS_scale_j_HF_2016postVFP',
'jetHF_2017': 'CMS_scale_j_HF_2017',
'jetHF_2018': 'CMS_scale_j_HF_2018',
'jetRelativeBal': 'CMS_scale_j_RelativeBal',
'jetRelativeSample_2016': 'CMS_scale_j_RelativeSample_2016',
'jetRelativeSample_2017': 'CMS_scale_j_RelativeSample_2017',
'jetRelativeSample_2018': 'CMS_scale_j_RelativeSample_2018',
'jer_2016preVFP': 'CMS_res_j_2016preVFP',
'jer_2016postVFP': 'CMS_res_j_2016postVFP',
'jer_2017': 'CMS_res_j_2017',
'jer_2018': 'CMS_res_j_2018',
'eer': 'CMS_res_e',
'ees': 'CMS_scale_e',
'me': 'CMS_scale_m',
'pu_2016': 'CMS_pileup_2016',
'pu_2017': 'CMS_pileup_2017',
'pu_2018': 'CMS_pileup_2018',
'pf_2016preVFP': 'CMS_prefiring_2016preVFP',
'pf_2016postVFP': 'CMS_prefiring_2016postVFP',
'pf_2017': 'CMS_prefiring_2017',
'bTag_2016': 'CMS_eff_btag_2016',
'bTag_2017': 'CMS_eff_btag_2017',
'bTag_2018': 'CMS_eff_btag_2018',
'UnclusteredEn_2016preVFP': 'CMS_scale_met_2016preVFP',
'UnclusteredEn_2016postVFP': 'CMS_scale_met_2016postVFP',
'UnclusteredEn_2017': 'CMS_scale_met_2017',
'UnclusteredEn_2018': 'CMS_scale_met_2018',
}
  
def addSyst(l,v):
  if len(v) == 2:
    vstr = "%.3f/%.3f"%(v[0],v[1])
    l += "%-25s "%vstr
  else:
    l += "%-25s "%"-"
  return l

def calyratio(df_gg,df_vbf):
  h2016gg = df_gg["weight2016"].sum() 
  h2017gg = df_gg["weight2017"].sum()
  h2018gg = df_gg["weight2018"].sum()
  hgg = h2016gg+h2017gg+h2018gg
  h2016vbf = df_vbf["weight2016"].sum() 
  h2017vbf = df_vbf["weight2017"].sum()
  h2018vbf = df_vbf["weight2018"].sum()
  hvbf = h2016vbf+h2017vbf+h2018vbf
  return [[h2016gg/hgg, h2016vbf/hvbf, '-'], [h2017gg/hgg, h2017vbf/hvbf, '-'], [h2018gg/hgg, h2018vbf/hvbf, '-']]

#Example of format
#cats = [ggcat0,ggcat1]
#bins = [[0,40],[40,100]]

def writedatacard(cats, bins, df_gg_full, df_vbf_full, sys_=True, limit=False):

  for cat in cats:
    f = open('Datacards/datacard_'+cat+'.txt','w')
    f.write("imax *\n")
    f.write("jmax *\n")
    f.write("kmax *\n")
    f.write("---------------------------------------------\n")
    ws = '../Workspaces/workspace_sig_'+cat+'.root'
    ws2 = 'workspace_sig_'+cat+'.root'
    dataws = 'CMS_Hemu_13TeV_multipdf.root'
    for proc in procs:
      if proc == 'bkg':
        if limit:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,dataws,'multipdf:env_pdf_'+cat+'_exp1'))
        elif sys_:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,ws,'w_13TeV:pdf_'+cat+'_exp1'))
        else:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,dataws,'multipdf:CMS_hemu_'+cat+'_13TeV_bkgshape'))
      elif proc == 'data_obs':
        if limit:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,dataws,'multipdf:roohist_data_mass_'+cat))
        elif sys_:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,ws,'w_13TeV:roohist_data_mass_'+cat))
        else:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,dataws,'multipdf:roohist_data_mass_'+cat))
      else:
        if proc == 'GGLFV':
          proc2 = 'ggH'  
        if proc == 'VBFLFV':
          proc2 = 'qqH'
        if limit or not sys_:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,ws2,'w_13TeV:'+cat+'_'+proc2+'_pdf'))
        else:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,ws,'w_13TeV:'+cat+'_'+proc2+'_pdf'))
  
    lbreak = '---------------------------------------------'
    lbin_cat = '%-25s'%"bin"
    lobs_cat = '%-25s'%"observation"
    lbin_procXcat = '%-61s'%"bin"
    lproc = '%-61s'%"process"
    lprocid = '%-61s'%"process"
    lrate = '%-61s'%"rate"        
    lbin_cat += "%-30s "%cat
    lobs_cat += "%-30s "%"-1"
    sigID = 0
    for proc in procs:
      if proc == 'data_obs': continue  
      lbin_procXcat += "%-25s "%cat
      lproc += "%-25s "%proc
      if proc == "bkg": 
        lprocid += "%-25s "%"1"
        lrate += "%-25s "%"1"
      else:
        lprocid += "%-25s "%sigID
        sigID -= 1
        lrate += "%-25s "%"1"
    f.write("\n")
    for l in [lbreak,lbin_cat,lobs_cat,lbreak,lbin_procXcat,lproc,lprocid,lrate,lbreak]: 
      l = l[:-1]
      f.write("%s\n"%l)
    if sys_:
      catnum = cats.index(cat)
      df_gg, df_vbf = df_gg_full.iloc[bins[catnum][0]:bins[catnum][1]-1].sum(), df_vbf_full.iloc[bins[catnum][0]:bins[catnum][1]-1].sum()
      QCDscale_ggH = 0.5*(df_gg['scalep5p5'] - df_gg['scalep22'])/df_gg['acc'] 
      QCDscale_qqH = 0.5*(df_vbf['scalep5p5'] - df_vbf['scalep22'])/df_vbf['acc']
      print "Finished QCDscale" 
      acceptance_scale_gg = (df_gg['weight_lhe102'] - df_gg['weight_lhe101'])*0.375/df_gg['acc']
      acceptance_scale_vbf = (df_vbf['weight_lhe102'] - df_vbf['weight_lhe101'])*0.375/df_vbf['acc']
      print "Finished scale acceptance" 
  
      lhe_pdf = ['weight_lhe%i'%i for i in range(1,101)]  
      acceptance_pdf_gg = df_gg[['weight_lhe%i'%i for i in range(1,101)]].std()
      acceptance_pdf_vbf = df_vbf[['weight_lhe%i'%i for i in range(1,101)]].std()
      print "Finished pdf acceptance" 
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_Trigger_emu_13TeV','lnN','1.02','1.02','-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_eff_e','lnN','1.02','1.02','-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_eff_m','lnN','1.02','1.02','-'))
      yrratio = calyratio(df_gg, df_vbf)
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_lumi_2016_13TeV','lnN', str(round(1+.012*yrratio[0][0],4)), str(round(1+.012*yrratio[0][1],3)),'-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_lumi_2017_13TeV','lnN', str(round(1+.023*yrratio[1][0],4)), str(round(1+.023*yrratio[1][1],3)),'-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_lumi_2018_13TeV','lnN', str(round(1+.025*yrratio[2][0],4)), str(round(1+.025*yrratio[2][1],3)),'-'))
      
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('QCDscale_ggH','lnN', str(round(1+QCDscale_ggH,4)),'-','-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('QCDscale_qqH','lnN','-',str(round(1+QCDscale_qqH,4)),'-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('acceptance_pdf_gg','lnN',str(round(1+acceptance_pdf_gg,4)),'-','-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('acceptance_pdf_vbf','lnN','-',str(round(1+acceptance_pdf_vbf,4)),'-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('acceptance_scale_gg','lnN',str(round(1+acceptance_scale_gg,4)),'-','-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('acceptance_scale_vbf','lnN','-',str(round(1+acceptance_scale_vbf,4)),'-'))
      
      sys = {'GGLFV':{}, 'VBLFV':{}}
      sys['GGLFV'] = calmigration(df_gg) 
      sys['VBLFV'] = calmigration(df_vbf)
      for key, value in sys['GGLFV'].items():
        lsyst = '%-35s  %-20s    '%(CMSnames[key],'lnN')
        sval = addSyst(lsyst, [value['Down'],value['Up']])
        sval = addSyst(sval, [sys['VBLFV'][key]['Down'], sys['VBLFV'][key]['Up']])
        sval = addSyst(sval, [])
        f.write("%s\n"%sval)
    
      shapeSys = {}
      with open('ShapeSys/Hem_shape_sys_%s.csv'%cat, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
          shapeSys[row['Proc']+'_'+row['Cat']+'_'+row['Param']+'_'+row['Sys']] = row['Value'] 
    
      f.write("---------------------------------------------\n")
      for proc in procs:
        if proc == 'bkg' or proc == 'data_obs': continue      
        else:
          if proc == 'GGLFV':
            proccatMER = 'ggH_'+cat+'_sigma_me'
            proccatMES = 'ggH_'+cat+'_dm_me'
            proccatEER = 'ggH_'+cat+'_sigma_eer'
            proccatEES = 'ggH_'+cat+'_dm_ees'
            proc2 = 'ggH'
          if proc == 'VBFLFV':
            proccatMER = 'qqH_'+cat+'_sigma_me'
            proccatMES = 'qqH_'+cat+'_dm_me'
            proccatEER = 'qqH_'+cat+'_sigma_eer'
            proccatEES = 'qqH_'+cat+'_dm_ees'
            proc2 = 'qqH'
        f.write('CMS_hem_nuisance_scale_e_%s_%s    param  0  %.4f\n'%(cat, proc2, max(abs(float(shapeSys[proccatEES+'Up'])), abs(float(shapeSys[proccatEES+'Down'])))))
        f.write('CMS_hem_nuisance_scale_m_%s_%s    param  0  %.4f\n'%(cat, proc2, max(abs(float(shapeSys[proccatMES+'Up'])), abs(float(shapeSys[proccatMES+'Down'])))))
        f.write('CMS_hem_nuisance_res_e_%s_%s      param  0  %.4f\n'%(cat, proc2, max(abs(float(shapeSys[proccatEER+'Up'])), abs(float(shapeSys[proccatEER+'Down'])))))
        f.write('CMS_hem_nuisance_res_m_%s_%s      param  0  %.4f\n'%(cat, proc2, max(abs(float(shapeSys[proccatMER+'Up'])), abs(float(shapeSys[proccatMER+'Down'])))))
    else:
      f.write('pdfindex_' +cat+'_13TeV    discrete\n') 
