import ROOT as r
import numpy as np
import pandas as pd
r.gROOT.SetBatch(True)

def revRecur(frac_order):
  frac = list(frac_order)
  for i,j in enumerate(frac):
    if i==0: continue
    k = i-1
    while k>=0:
      frac[i]/=(1-frac_order[k])
      k-=1
  return frac

def calRecur(frac_order):
  frac = list(frac_order)
  for i,j in enumerate(frac):
    if i==0: continue
    k = i-1
    while k>=0:
      frac[i]*=(1-frac_order[k])
      k-=1
  return frac

masspts = ['110','120','125','130','140','150','160']
binning = [float(masspts[0]), float(masspts[-1])+1] + [(float(masspts[i])+float(masspts[i+1]))/2 for i in range(len(masspts)-1)]
binning.sort()
print np.array(binning)
cats = ['ggHcat0','ggHcat1','ggHcat2','ggHcat3','VBFcat0','VBFcat1','VBFcat2']
gausOrder =  pd.read_csv("gaus_ftest_result.csv", skipinitialspace=True)
orders = {'qqH':[2,2,2,2,2,2,2], 'ggH':[3,3,3,3,2,2,2]}
mh = r.RooRealVar('MH','MH',125,110,160)
e_res_hist, e_scale_hist, m_res_hist, m_scale_hist = [], [], [], []
e_res_datahist, e_scale_datahist, m_res_datahist, m_scale_datahist = [], [], [], []
e_res_func, e_scale_func, m_res_func, m_scale_func = [], [], [], []
norm_spline, sigma_spline, mean_spline, frac_spline = [], [], [], []
for c_index, cat in enumerate(cats):
  dh = []
  w = r.RooWorkspace("w_13TeV","w_13TeV") 
  for prod in ['ggH','qqH']:
    params = {'norm':[], 'e_scale':[], 'e_res':[], 'm_scale':[], 'm_res':[]}
    for i in range(orders[prod][c_index]):
      params['sigma_'+str(i)] = []
      params['mean_'+str(i)] = []
      if i != orders[prod][c_index]-1:
        params['frac_'+str(i)] = []
    for masspt in masspts:
      infile = r.TFile('Workspaces/workspace_sig_%s_%s_gaus.root'%(cat,masspt))
      ws = infile.Get("w_13TeV")
      mass_sig = ws.var("CMS_emu_Mass")
      dh.append(ws.data('data_%s_%s_%s'%(cat,masspt,prod)))
      print(cat, prod, masspt)
      params['norm'].append(ws.var('%s_%s_%s_pdf_norm'%(cat,masspt,prod)).getValV())
      print(params['norm'][-1])
      params['e_scale'].append(ws.var('CMS_hem_nuisance_scale_e_%s_%s_%s'%(cat,masspt,prod)).getValV())
      params['e_res'].append(ws.var('CMS_hem_nuisance_res_e_%s_%s_%s'%(cat,masspt,prod)).getValV())
      params['m_scale'].append(ws.var('CMS_hem_nuisance_scale_m_%s_%s_%s'%(cat,masspt,prod)).getValV())
      params['m_res'].append(ws.var('CMS_hem_nuisance_res_m_%s_%s_%s'%(cat,masspt,prod)).getValV())

      order_frac_og = [ws.var('%s_%s_%s_sigfrac_order%s'%(cat,masspt,prod,i)).getValV() for i in range(orders[prod][c_index]-1)]

      order_frac_og.append(1)
      order_frac = calRecur(order_frac_og)

      order_mean = [float(masspt)+ws.var('%s_%s_%s_mean_gaus_nom_order%s'%(cat,masspt,prod,i)).getValV() for i in range(orders[prod][c_index])]
      order_sigma = [ws.var('%s_%s_%s_sigma_gaus_nom_order%s'%(cat,masspt,prod,i)).getValV() for i in range(orders[prod][c_index])]

      order_frac_og, order_frac, order_mean, order_sigma = zip(*sorted(zip(order_frac_og, order_frac, order_mean, order_sigma), key=lambda pair: pair[3])) 
      if order_frac_og[0]==1: order_frac_og, order_frac, order_mean, order_sigma = zip(*sorted(zip(order_frac_og, order_frac, order_mean, order_sigma), key=lambda pair: pair[3], reverse=True))
      order_frac = list(order_frac)
      order_frac = revRecur(order_frac)

      for i in range(orders[prod][c_index]):
        params['mean_'+str(i)].append(order_mean[i])
        params['sigma_'+str(i)].append(order_sigma[i])
        if i!=orders[prod][c_index]-1:
          params['frac_'+str(i)].append(order_frac[i])

    e_res_hist.append(r.TH1F('e_res_%s_%s'%(cat,prod), 'e_res_%s_%s'%(cat,prod), len(binning)-1, np.array(binning)))
    e_scale_hist.append(r.TH1F('e_scale_%s_%s'%(cat,prod), 'e_scale_%s_%s'%(cat,prod), len(binning)-1, np.array(binning)))
    m_res_hist.append(r.TH1F('m_res_%s_%s'%(cat,prod), 'm_res_%s_%s'%(cat,prod), len(binning)-1, np.array(binning)))
    m_scale_hist.append(r.TH1F('m_scale_%s_%s'%(cat,prod), 'm_scale_%s_%s'%(cat,prod), len(binning)-1, np.array(binning)))

    for i in range(len(masspts)):
      e_scale_hist[-1].Fill(float(masspts[i]), params['e_scale'][i])
      m_scale_hist[-1].Fill(float(masspts[i]), params['m_scale'][i])
      e_res_hist[-1].Fill(float(masspts[i]), params['e_res'][i])
      m_res_hist[-1].Fill(float(masspts[i]), params['m_res'][i])
#    canv = r.TCanvas()
#    m_scale_hist[-1].Draw()
#    canv.SaveAs('m_scale_%s_%s.pdf'%(cat,prod))
#    canv = r.TCanvas()
#    e_scale_hist[-1].Draw()
#    canv.SaveAs('e_scale_%s_%s.pdf'%(cat,prod))
    e_res_datahist.append(r.RooDataHist('e_res_%s_%s'%(cat,prod), 'e_res_%s_%s'%(cat,prod), r.RooArgList(mh), e_res_hist[-1]))
    m_res_datahist.append(r.RooDataHist('m_res_%s_%s'%(cat,prod), 'm_res_%s_%s'%(cat,prod), r.RooArgList(mh), m_res_hist[-1]))
    e_scale_datahist.append(r.RooDataHist('e_scale_%s_%s'%(cat,prod), 'e_scale_%s_%s'%(cat,prod), r.RooArgList(mh), e_scale_hist[-1]))
    m_scale_datahist.append(r.RooDataHist('m_scale_%s_%s'%(cat,prod), 'm_scale_%s_%s'%(cat,prod), r.RooArgList(mh), m_scale_hist[-1]))
    e_res_func.append(r.RooHistFunc('e_res_func_%s_%s'%(cat,prod), 'e_res_func_%s_%s'%(cat,prod), r.RooArgSet(mh), e_res_datahist[-1]))
    e_scale_func.append(r.RooHistFunc('e_scale_func_%s_%s'%(cat,prod), 'e_scale_func_%s_%s'%(cat,prod), r.RooArgSet(mh), e_scale_datahist[-1]))
    m_res_func.append(r.RooHistFunc('m_res_func_%s_%s'%(cat,prod), 'm_res_func_%s_%s'%(cat,prod), r.RooArgSet(mh), m_res_datahist[-1]))
    m_scale_func.append(r.RooHistFunc('m_scale_func_%s_%s'%(cat,prod), 'm_scale_func_%s_%s'%(cat,prod), r.RooArgSet(mh), m_scale_datahist[-1]))


    norm_spline.append(r.RooSpline1D('%s_%s_spline_norm'%(cat,prod),'%s_%s_spline_norm'%(cat,prod),mh,len(masspts),np.array([float(mp) for mp in masspts]),np.array(params['norm'])))

    mean_dcb, sigma_dcb, subpdf = [], [], []
    gaus_List, frac_List = r.RooArgList(), r.RooArgList()
    
    for i in range(orders[prod][c_index]):
      mean_spline.append(r.RooSpline1D('%s_%s_mean_gaus_nom_order%s'%(cat,prod,i),'%s_%s_mean_gaus_nom_order%s'%(cat,prod,i),mh,len(masspts),np.array([float(mp) for mp in masspts]),np.array(params['mean_'+str(i)])))
      sigma_spline.append(r.RooSpline1D('%s_%s_sigma_gaus_nom_order%s'%(cat,prod,i),'%s_%s_sigma_gaus_nom_order%s'%(cat,prod,i),mh,len(masspts),np.array([float(mp) for mp in masspts]),np.array(params['sigma_'+str(i)])))
      if i!=orders[prod][c_index]-1:
        frac_spline.append(r.RooSpline1D('%s_%s_sigfrac_gaus_order%s'%(cat,prod,i),'%s_%s_sigfrac_gaus_order%s'%(cat,prod,i),mh,len(masspts),np.array([float(mp) for mp in masspts]),np.array(params['frac_'+str(i)])))
        frac_List.add(frac_spline[-1])

    mean_err_e = r.RooRealVar("CMS_hem_nuisance_scale_e_{}".format(prod), "CMS_hem_nuisance_scale_e_{}".format(prod), 0., -5, 5)
    mean_err_m = r.RooRealVar("CMS_hem_nuisance_scale_m_{}".format(prod), "CMS_hem_nuisance_scale_m_{}".format(prod), 0., -5, 5)
    sigma_err_e = r.RooRealVar("CMS_hem_nuisance_res_e_{}".format(prod), "CMS_hem_nuisance_res_e_{}".format(prod), 0., -5, 5)
    sigma_err_m = r.RooRealVar("CMS_hem_nuisance_res_m_{}".format(prod), "CMS_hem_nuisance_res_m_{}".format(prod), 0., -5, 5)

    for i in range(orders[prod][c_index]):
      mean_dcb.append(r.RooFormulaVar("{}_{}_mean_gaus_order{}".format(cat,prod,i), "{}_{}_mean_gaus_order{}".format(cat,prod,i), "(@0)*(1+@1*@2+@3*@4)", r.RooArgList(mean_spline[-orders[prod][c_index]+i], e_scale_func[-1], mean_err_e, m_scale_func[-1], mean_err_m)))
      sigma_dcb.append(r.RooFormulaVar("{}_{}_sigma_gaus_order{}".format(cat,prod,i), "{}_{}_sigma_gaus_order{}".format(cat,prod,i), "@0*(1+@1*@2+@3*@4)", r.RooArgList(sigma_spline[-orders[prod][c_index]+i], e_res_func[-1], sigma_err_e, m_res_func[-1], sigma_err_m)))
      subpdf.append(r.RooGaussian("{}_{}_pdf_order{}".format(cat,prod,i), "{}_{}_pdf_order{}".format(cat,prod,i), mass_sig, mean_dcb[-1], sigma_dcb[-1]))
      gaus_List.add(subpdf[-1])

    norm_dcb = r.RooFormulaVar('%s_%s_pdf_norm'%(cat,prod), '%s_%s_pdf_norm'%(cat,prod), "@0", r.RooArgList(norm_spline[-1]))

    pdf = r.RooAddPdf("{}_{}_pdf".format(cat,prod), "{}_{}_pdf".format(cat,prod), gaus_List, frac_List, True)

    getattr(w, 'import')(pdf)
    getattr(w, 'import')(norm_dcb)
    for h in dh:
      getattr(w, 'import')(h)
      
  r.gDirectory.Add(w)

  filename = "Workspaces/workspace_sig_"+cat+"_gaus.root"
  w.Print()
  w.writeToFile(filename)

