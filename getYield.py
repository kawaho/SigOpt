import math
def AMS(s, b):
    return round(math.sqrt(2*((s+b)*math.log(1+s/b)-s)),3)

import ROOT as r
r.gROOT.SetBatch(True)
cats = ['ggcat0', 'ggcat1', 'ggcat2', 'ggcat3', 'vbfcat0', 'vbfcat1', 'vbfcat2']

bkgf_in = r.TFile('dataws_final.root', 'READ')
bkgw_in = bkgf_in.Get('CMS_emu_workspace') 
dataset = [bkgw_in.data('Data_13TeV_'+i) for i in cats]

mass = bkgw_in.var("CMS_emu_Mass")

print '---------------------------------------'
for mh in ['110','120','125','130','140','150','160']:
  f_in = [r.TFile('Workspaces/workspace_sig_'+i+'_'+mh+'_gaus.root', 'READ') for i in cats] 
  w_in = [i.Get('w_13TeV') for i in f_in] 
  norm_ggH, norm_qqH = [], []
  for i,j in enumerate(w_in):
    norm_ggH.append(j.var(cats[i]+'_'+mh+'_ggH_pdf_norm').getValV())
    norm_qqH.append(j.var(cats[i]+'_'+mh+'_qqH_pdf_norm').getValV())
  norm = [sum(x) for x in zip(norm_ggH, norm_qqH)] 
  mass.setRange("R1",int(mh)-15,int(mh)+10)
  norm_bkg = [d.sumEntries("1", "R1") for d in dataset]
  print ' mH     signal 5.9e-5(ggH,qqH)     bkg     AMS'
  print '%s        %.3f(%.3f,%.3f)      %i    %.3f'%(mh, sum(norm), sum(norm_ggH), sum(norm_qqH), sum(norm_bkg), AMS(sum(norm)*0.59, sum(norm_bkg)))
  for i, j in enumerate(cats):
    print '%s      %.3f(%.3f,%.3f)           %i    %.3f'%(j, norm_ggH[i]+norm_qqH[i],norm_ggH[i],norm_qqH[i], norm_bkg[i], AMS((norm_ggH[i]+norm_qqH[i])*0.59, norm_bkg[i]))
  print '---------------------------------------'


#f_in = [r.TFile('Workspaces/workspace_sig_'+i+'.root', 'READ') for i in cats]
#w_in = [i.Get('w_13TeV') for i in f_in] 
#mh = [i.var('MH') for i in w_in]
#norm = []
#
##for ff,dh in enumerate(dataset):
##  frame = mass.frame()
##  canvas = r.TCanvas("canvas","",0,0,800,800)
##  dh.plotOn(frame)
##  frame.Draw()
##  canvas.SaveAs(str(ff)+'bkgggg.png')
##  del canvas
#for i,j in enumerate(w_in):
#  norm.append(j.function(cats[i]+'_qqH_spline_norm'))
#  norm.append(j.function(cats[i]+'_ggH_spline_norm'))
#
#for i in range(120,131):
#  for sub_mh in mh:
#    sub_mh.setVal(i)
#  mass.setRange("R1",i-15,i+10)
#  norm_bkg = [d.sumEntries("1", "R1") for d in dataset]
#  norm_mh = [k.getVal() for k in norm]
#  print i, sum(norm_mh), sum(norm_bkg), AMS(sum(norm_mh), sum(norm_bkg))
