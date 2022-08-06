from calmigration import *
import collections, re, csv, math
import numpy as np
procs = ['GGLFV', 'VBFLFV', 'bkg', 'data_obs']
datacard = []
ws = []
CMSnames = {
'mTrg': 'CMS_trig_mu',
'mID': 'CMS_id_mu',
'mIso': 'CMS_iso_mu',
'eReco': 'CMS_reco_e',
'eID': 'CMS_id_e',
'jesAbsolute': 'CMS_scale_j_Absolute',
'jesAbsolute_2016': 'CMS_scale_j_Absolute_2016',
'jesAbsolute_2017': 'CMS_scale_j_Absolute_2017',
'jesAbsolute_2018': 'CMS_scale_j_Absolute_2018',
'jesBBEC1': 'CMS_scale_j_BBEC1',
'jesBBEC1_2016': 'CMS_scale_j_BBEC1_2016',
'jesBBEC1_2017': 'CMS_scale_j_BBEC1_2017',
'jesBBEC1_2018': 'CMS_scale_j_BBEC1_2018',
'jesEC2': 'CMS_scale_j_EC2',
'jesEC2_2016': 'CMS_scale_j_EC2_2016', 
'jesEC2_2017': 'CMS_scale_j_EC2_2017', 
'jesEC2_2018': 'CMS_scale_j_EC2_2018',
'jesFlavorQCD': 'CMS_scale_j_FlavorQCD',
'jesHF': 'CMS_scale_j_HF',
'jesHF_2016': 'CMS_scale_j_HF_2016',
'jesHF_2017': 'CMS_scale_j_HF_2017',
'jesHF_2018': 'CMS_scale_j_HF_2018',
'jesRelativeBal': 'CMS_scale_j_RelativeBal',
'jesRelativeSample_2016': 'CMS_scale_j_RelativeSample_2016',
'jesRelativeSample_2017': 'CMS_scale_j_RelativeSample_2017',
'jesRelativeSample_2018': 'CMS_scale_j_RelativeSample_2018',
'jer_2016': 'CMS_res_j_2016',
'jer_2017': 'CMS_res_j_2017',
'jer_2018': 'CMS_res_j_2018',
'eer': 'CMS_res_e',
'ess': 'CMS_scale_e',
'me': 'CMS_scale_m',
'pu_2016': 'CMS_pileup_2016',
'pu_2017': 'CMS_pileup_2017',
'pu_2018': 'CMS_pileup_2018',
'pf_2016': 'CMS_prefiring_2016',
'pf_2017': 'CMS_prefiring_2017',
'bTag_2016': 'CMS_eff_btag_2016',
'bTag_2017': 'CMS_eff_btag_2017',
'bTag_2018': 'CMS_eff_btag_2018',
'UnclusteredEn': 'CMS_scale_met',
}
  
def addSyst(l,value):
  if len(value) == 2:
    if smallUnc(value[0]) and smallUnc(value[1]):
      vstr = "-"
 #   if smallUnc(value[0]):
 #     value[0] = 1
 #   if smallUnc(value[1]):
 #     value[1] = 1
    else: 
      vstr = "%.3f/%.3f"%(value[0],value[1])
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

def writedatacard(cats, bins, df_gg_full, df_vbf_full, sys_=True, limit=False, masspt=None, useGaus=False, ShapeUnc=False):
  systable = {} 
  bkg_func = {'ggcat0':'bern1', 'ggcat1':'bern3', 'ggcat2':'bern3', 'ggcat3':'bern2', 'vbfcat0':'bern1', 'vbfcat1':'bern1'}
  for cat in cats:
    systable[cat] = {'jet':[999,-999], 'unc':[999,-999], 'b':[999,-999], 'pf':[999,-999], 'pu':[999,-999], 'muon':[999,-999], 'electron':[999,-999], 'QCDacc_gg':0, 'QCDacc_vbf':0,'PDFacc_gg':0,'PDFacc_vbf':0,'Parton':0, 'others':[999,-999]}
    print('Writing datacards for '+cat)
    file_string = 'Datacards/datacard_'+cat
    if masspt:
      file_string+='_'+masspt
    if not sys_:
      file_string+='_NoSys'
    if ShapeUnc:
       file_string+='_ShapeUnc'
    if useGaus:
       file_string+='_gaus'

    f = open(file_string+'.txt','w')

    f.write("imax *\n")
    f.write("jmax *\n")
    f.write("kmax *\n")
    f.write("---------------------------------------------\n")
    ws = '../Workspaces/workspace_sig_'+cat+'.root'
    ws2 = 'workspace_sig_'+cat+'.root'
    if useGaus:
      ws = ws.replace('.root','_gaus.root')
      ws2 = ws2.replace('.root','_gaus.root')
    if limit or ShapeUnc:
      dataws = '../Workspaces/CMS_Hemu_13TeV_multipdf.root'
    else:
      dataws = '../Workspaces/CMS_Hemu_13TeV_multipdf_'+cat.split('_')[-1]+'.root'
    for proc in procs:
      if proc == 'bkg':
        if limit or ShapeUnc:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,dataws,'multipdf:env_pdf_'+cat.split('_')[0]+'_'+bkg_func[cat.split('_')[0]]))
        elif not sys_:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,dataws,'multipdf:CMS_hemu_'+cat.split('_')[0]+'_13TeV_bkgshape'))
        else:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,ws,'w_13TeV:pdf_'+cat+'_exp1'))
      elif proc == 'data_obs':
        if limit or not sys_ or ShapeUnc:
          #f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,dataws,'multipdf:roohist_data_mass_'+cat.split('_')[0]))
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,dataws,'multipdf:Data_13TeV_'+cat.split('_')[0]))
        else:
          f.write("shapes      %-10s %-10s %-20s %s\n"%(proc,cat,ws,'w_13TeV:roohist_data_mass_'+cat))
      else:
        if proc == 'GGLFV':
          proc2 = 'ggH'  
        if proc == 'VBFLFV':
          proc2 = 'qqH'
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
      df_gg, df_vbf = df_gg_full.loc[bins[catnum][0]:bins[catnum][1]-1].sum(), df_vbf_full.loc[bins[catnum][0]:bins[catnum][1]-1].sum()
      QCDscale_ggH = 0.5*(-df_gg['weight_scalep5p5'] + df_gg['weight_scale22'])/df_gg['acc'] 
      QCDscale_qqH = 0.5*(-df_vbf['weight_scalep5p5'] + df_vbf['weight_scale22'])/df_vbf['acc']
      #print "Finished QCDscale" 
      acceptance_scale_gg = (df_gg['weight_lhe102'] - df_gg['weight_lhe101'])*0.375/df_gg['acc']
      acceptance_scale_vbf = (df_vbf['weight_lhe102'] - df_vbf['weight_lhe101'])*0.375/df_vbf['acc']
      #print "Finished scale acceptance" 
  
      lhe_pdf = ['weight_lhe%i'%i for i in range(1,101)]  

      acceptance_pdf_gg = df_gg[lhe_pdf].values.std()/df_gg['acc']
      acceptance_pdf_vbf = df_vbf[lhe_pdf].values.std()/df_vbf['acc']

      #print "Finished pdf acceptance" 

      if abs(acceptance_pdf_gg) > abs(acceptance_scale_gg):
        acceptance_pdf_scale_sign_gg = math.copysign(1, acceptance_pdf_gg)
      else:
        acceptance_pdf_scale_sign_gg = math.copysign(1, acceptance_scale_gg)
      acceptance_pdf_scale_gg = acceptance_pdf_scale_sign_gg*math.sqrt(acceptance_scale_gg**2+acceptance_pdf_gg**2) 
      if abs(acceptance_pdf_vbf) > abs(acceptance_scale_vbf):
        acceptance_pdf_scale_sign_vbf = math.copysign(1, acceptance_pdf_vbf)
      else:
        acceptance_pdf_scale_sign_vbf = math.copysign(1, acceptance_scale_vbf)
      acceptance_pdf_scale_vbf = acceptance_pdf_scale_sign_vbf*math.sqrt(acceptance_scale_vbf**2+acceptance_pdf_vbf**2) 


      ps_vbf = df_vbf['weight_herwig']/df_vbf['weight']
#      print(QCDscale_ggH, QCDscale_qqH)
#      print(acceptance_scale_gg, acceptance_scale_vbf)
#      print(acceptance_pdf_gg, acceptance_pdf_vbf)
#      print(acceptance_pdf_scale_gg, acceptance_pdf_scale_vbf)
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('pdf_Higgs_gg','lnN','1.032','-','-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('pdf_Higgs_qqbar','lnN','-','1.021','-'))

      if False:#smallUnc(1+acceptance_pdf_scale_gg):
        f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('pdf_Higgs_gg_ACCEPT','lnN','-','-','-'))
      else:
        f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('pdf_Higgs_gg_ACCEPT','lnN',str(round(1+acceptance_pdf_scale_gg,5)),'-','-'))
      systable[cat]['QCDacc_gg'] = round(acceptance_pdf_scale_gg*100,3)
      if smallUnc(1+acceptance_pdf_scale_vbf,'check'):
        f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('pdf_Higgs_qqbar_ACCEPT','lnN','-','-','-'))
      else:
        f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('pdf_Higgs_qqbar_ACCEPT','lnN','-',str(round(1+acceptance_pdf_scale_vbf,3)),'-'))
      systable[cat]['QCDacc_vbf'] = round(acceptance_pdf_scale_vbf*100,3)

#      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_Trigger_emu_13TeV','lnN','1.02','1.02','-'))
#      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_eff_e','lnN','1.02','1.02','-'))
#      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_eff_m','lnN','1.02','1.02','-'))
      yrratio = calyratio(df_gg, df_vbf)
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('lumi_13TeV_2016','lnN', str(round(1+.01*yrratio[0][0],3)), str(round(1+.01*yrratio[0][1],3)),'-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('lumi_13TeV_2017','lnN', str(round(1+.02*yrratio[1][0],3)), str(round(1+.02*yrratio[1][1],3)),'-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('lumi_13TeV_2018','lnN', str(round(1+.015*yrratio[2][0],3)), str(round(1+.015*yrratio[2][1],3)),'-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('lumi_13TeV_correlated','lnN', str(round(1+.006*yrratio[0][0]+.009*yrratio[1][0]+.02*yrratio[2][0],3)), str(round(1+.006*yrratio[0][1]+.009*yrratio[1][1]+.02*yrratio[2][1],3)),'-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('lumi_13TeV_1718','lnN', str(round(1+.006*yrratio[1][0]+.002*yrratio[2][0],3)), str(round(1+.006*yrratio[1][1]+.002*yrratio[2][1],3)),'-'))

      if smallUnc(ps_vbf):
        f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_ps','lnN','-','-','-'))
      else:
        f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('CMS_ps','lnN','-',str(round(ps_vbf,3)),'-'))
      systable[cat]['Parton'] = round(abs(1-ps_vbf)*100,3)
      
      sys = {'GGLFV':{}, 'VBLFV':{}}
      #print('Calculating migration for gg')
      sys['GGLFV'] = calmigration(df_gg) 
      #print('Calculating migration for vbf')
      sys['VBLFV'] = calmigration(df_vbf)
      for subproc in sys:
        for subsys in sys[subproc]:
          min_subsys, max_subsys = sorted(tuple((round(abs(sys[subproc][subsys]['Up']-1)*100,3), round(abs(sys[subproc][subsys]['Down']-1)*100,3))))
          if 'jer' in subsys or 'jes' in subsys:
            which_systable = 'jet'
          elif 'pu' in subsys:
            which_systable = 'pu'
          elif 'bTag' in subsys:
            which_systable = 'b'
          elif 'UnclusteredEn' in subsys:
            which_systable = 'unc'
          elif 'pf' in subsys:
            which_systable = 'pf'
          else:
            which_systable = 'others'
          if min_subsys < systable[cat][which_systable][0]:  systable[cat][which_systable][0]=min_subsys
          if max_subsys > systable[cat][which_systable][1]:  systable[cat][which_systable][1]=max_subsys


      for key in sorted(sys['GGLFV']):
        if key in ['mTrg', 'mID', 'mIso', 'eReco', 'eID', 'eIso', 'eTrig']: continue
        lsyst = '%-35s  %-20s    '%(CMSnames[key],'lnN')
        sval = addSyst(lsyst, [sys['GGLFV'][key]['Down'],sys['GGLFV'][key]['Up']])
        sval = addSyst(sval, [sys['VBLFV'][key]['Down'], sys['VBLFV'][key]['Up']])
        sval = addSyst(sval, [])
        f.write("%s\n"%sval)

      lsyst = '%-35s  %-20s    '%('CMS_eff_m','lnN')
      muon_gg_combined = [sys['GGLFV']['mTrg']['Down']*sys['GGLFV']['mID']['Down']*sys['GGLFV']['mIso']['Down'],sys['GGLFV']['mTrg']['Up']*sys['GGLFV']['mID']['Up']*sys['GGLFV']['mIso']['Up']]
      muon_vbf_combined = [sys['VBLFV']['mTrg']['Down']*sys['VBLFV']['mID']['Down']*sys['VBLFV']['mIso']['Down'], sys['VBLFV']['mTrg']['Up']*sys['VBLFV']['mID']['Up']*sys['VBLFV']['mIso']['Up']] 
      electron_gg_combined = [sys['GGLFV']['eReco']['Down']*sys['GGLFV']['eID']['Down']*sys['GGLFV']['eIso']['Down']*sys['GGLFV']['eTrig']['Down'],sys['GGLFV']['eReco']['Up']*sys['GGLFV']['eID']['Up']*sys['GGLFV']['eIso']['Up']*sys['GGLFV']['eTrig']['Up']]
      electron_vbf_combined = [sys['VBLFV']['eReco']['Down']*sys['VBLFV']['eID']['Down']*sys['VBLFV']['eIso']['Down']*sys['VBLFV']['eTrig']['Down'], sys['VBLFV']['eReco']['Up']*sys['VBLFV']['eID']['Up']*sys['VBLFV']['eIso']['Up']*sys['VBLFV']['eTrig']['Up']] 

      min_subsys = min( round(abs(muon_gg_combined[0]-1)*100,3), round(abs(muon_gg_combined[1]-1)*100,3), round(abs(muon_vbf_combined[0]-1)*100,3), round(abs(muon_vbf_combined[1]-1)*100,3) )
      max_subsys = max( round(abs(muon_gg_combined[0]-1)*100,3), round(abs(muon_gg_combined[1]-1)*100,3), round(abs(muon_vbf_combined[0]-1)*100,3), round(abs(muon_vbf_combined[1]-1)*100,3) )
      if min_subsys < systable[cat]['muon'][0]:  systable[cat]['muon'][0]=min_subsys
      if max_subsys > systable[cat]['muon'][1]:  systable[cat]['muon'][1]=max_subsys

      min_subsys = min( round(abs(electron_gg_combined[0]-1)*100,3), round(abs(electron_gg_combined[1]-1)*100,3), round(abs(electron_vbf_combined[0]-1)*100,3), round(abs(electron_vbf_combined[1]-1)*100,3) )
      max_subsys = max( round(abs(electron_gg_combined[0]-1)*100,3), round(abs(electron_gg_combined[1]-1)*100,3), round(abs(electron_vbf_combined[0]-1)*100,3), round(abs(electron_vbf_combined[1]-1)*100,3) )
      if min_subsys < systable[cat]['electron'][0]:  systable[cat]['electron'][0]=min_subsys
      if max_subsys > systable[cat]['electron'][1]:  systable[cat]['electron'][1]=max_subsys

      sval = addSyst(lsyst, muon_gg_combined)
      sval = addSyst(sval, muon_vbf_combined)
      sval = addSyst(sval, [])
      f.write("%s\n"%sval)

      lsyst = '%-35s  %-20s    '%('CMS_eff_e','lnN')
      sval = addSyst(lsyst, electron_gg_combined)
      sval = addSyst(sval, electron_vbf_combined)
      sval = addSyst(sval, [])
      f.write("%s\n"%sval)

      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('QCDscale_ggH','lnN', '1.039','-','-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('QCDscale_qqH','lnN','-','1.005','-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('QCDscale_ggH_ACCEPT','lnN', str(round(1+QCDscale_ggH,3)),'-','-'))
      f.write('%-35s  %-20s    %-25s %-25s %-25s\n'%('QCDscale_qqH_ACCEPT','lnN','-',str(round(1+QCDscale_qqH,3)),'-'))
      systable[cat]['QCDacc_gg'] = round(QCDscale_ggH*100,3)
      systable[cat]['QCDacc_vbf'] = round(QCDscale_qqH*100,3)
    
      f.write('CMS_hem_nuisance_scale_m_ggH    param  0  1\n')
      f.write('CMS_hem_nuisance_res_m_ggH      param  0  1\n')
      f.write('CMS_hem_nuisance_scale_e_ggH    param  0  1\n')
      f.write('CMS_hem_nuisance_res_e_ggH      param  0  1\n')
      f.write('CMS_hem_nuisance_scale_m_qqH    param  0  1\n')
      f.write('CMS_hem_nuisance_res_m_qqH      param  0  1\n')
      f.write('CMS_hem_nuisance_scale_e_qqH    param  0  1\n')
      f.write('CMS_hem_nuisance_res_e_qqH      param  0  1\n')

#      shapeSys = {}
#      with open('ShapeSys/Hem_shape_sys_%s.csv'%cat, mode='r') as csv_file:
#        csv_reader = csv.DictReader(csv_file)
#        line_count = 0
#        for row in csv_reader:
#          shapeSys[row['Proc']+'_'+row['Cat']+'_'+row['Param']+'_'+row['Sys']] = row['Value'] 
#      f.write("---------------------------------------------\n")
#      for proc in procs:
#        if proc == 'bkg' or proc == 'data_obs': continue      
#        else:
#          if proc == 'GGLFV':
#            proccatMER = 'ggH_'+cat+'_sigma_me'
#            proccatMES = 'ggH_'+cat+'_dm_me'
#            proccatEER = 'ggH_'+cat+'_sigma_eer'
#            proccatEES = 'ggH_'+cat+'_dm_ees'
#            proc2 = 'ggH'
#          if proc == 'VBFLFV':
#            proccatMER = 'qqH_'+cat+'_sigma_me'
#            proccatMES = 'qqH_'+cat+'_dm_me'
#            proccatEER = 'qqH_'+cat+'_sigma_eer'
#            proccatEES = 'qqH_'+cat+'_dm_ees'
#            proc2 = 'qqH'
#        f.write('CMS_hem_nuisance_scale_e_%s_%s    param  0  %.3f\n'%(cat, proc2, 0.01))
#        f.write('CMS_hem_nuisance_res_e_%s_%s      param  0  %.3f\n'%(cat, proc2, 0.01))
#        #if max(abs(float(shapeSys[proccatEES+'_Up'])), abs(float(shapeSys[proccatEES+'_Down']))) > 0.001: 
##          f.write('CMS_hem_nuisance_scale_e_%s_%s    param  0  %.3f\n'%(cat, proc2, max(abs(float(shapeSys[proccatEES+'_Up'])), abs(float(shapeSys[proccatEES+'_Down'])))))
#        if max(abs(float(shapeSys[proccatMES+'_Up'])), abs(float(shapeSys[proccatMES+'_Down']))) > 0.001: 
#          f.write('CMS_hem_nuisance_scale_m_%s_%s    param  0  %.3f\n'%(cat, proc2, max(abs(float(shapeSys[proccatMES+'_Up'])), abs(float(shapeSys[proccatMES+'_Down'])))))
#        else:
#          f.write('CMS_hem_nuisance_scale_m_%s_%s    param  0  %.3f\n'%(cat, proc2, 0.001))
#        #if max(abs(float(shapeSys[proccatEER+'_Up'])), abs(float(shapeSys[proccatEER+'_Down']))) > 0.001: 
##          f.write('CMS_hem_nuisance_res_e_%s_%s      param  0  %.3f\n'%(cat, proc2, max(abs(float(shapeSys[proccatEER+'_Up'])), abs(float(shapeSys[proccatEER+'_Down'])))))
#        if max(abs(float(shapeSys[proccatMER+'_Up'])), abs(float(shapeSys[proccatMER+'_Down']))) > 0.001: 
#          f.write('CMS_hem_nuisance_res_m_%s_%s      param  0  %.3f\n'%(cat, proc2, max(abs(float(shapeSys[proccatMER+'_Up'])), abs(float(shapeSys[proccatMER+'_Down'])))))
#        else:
#          f.write('CMS_hem_nuisance_res_m_%s_%s    param  0  %.3f\n'%(cat, proc2, 0.001))
    elif False:
      f.write('pdfindex_' +cat.split('_')[0]+'_13TeV    discrete\n')
    f_systable = open('ShapeSys/systable.txt', 'a')
    f_systable.write(str(cats))
    f_systable.write(str(systable))
#signalMultiplier rateParam * *LFV 0.01\nnuisance edit freeze signalMultiplier\n') 
