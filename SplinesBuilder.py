import ROOT as r
import numpy as np
masspts = ['120','125','130']
binning = [float(i) for i in masspts] + [(float(masspts[i])+float(masspts[i+1]))/2 for i in range(len(masspts)-1)]
binning.sort()
print np.array(binning)
cats = ['ggcat0']#,'ggcat1','ggcat2','ggcat3','vbfcat0','vbfcat1']
workspaces = ['Workspaces/workspace_sig_{cat}_{masspts}.root']
mh = r.RooRealVar('MH','MH',125,120,130)
e_res_hist, e_scale_hist, m_res_hist, m_scale_hist = [], [], [], []
e_res_datahist, e_scale_datahist, m_res_datahist, m_scale_datahist = [], [], [], []
e_res_func, e_scale_func, m_res_func, m_scale_func = [], [], [], []
norm_spline, sigma_spline, mean_spline, n1_spline, a1_spline, a2_spline = [], [], [], [], [], []
for cat in cats:
  for prod in ['ggH']:#,'qqH']:
    params = {'norm':[], 'dm':[], 'sigma':[], 'a1':[], 'a2':[], 'n1':[], 'e_scale':[], 'e_res':[], 'm_scale':[], 'm_res':[]}
    for masspt in masspts:
      infile = r.TFile('Workspaces/workspace_sig_%s_%s.root'%(cat,masspt))
      ws = infile.Get("w_13TeV")
      mass_sig = ws.var("CMS_emu_Mass")
      params['norm'].append(ws.var('%s_%s_%s_pdf_norm'%(cat,masspt,prod)).getValV())
      params['dm'].append(ws.var('%s_%s_%s_mean_cbe_nom'%(cat,masspt,prod)).getValV())
      params['sigma'].append(ws.var('%s_%s_%s_sigma_cbe_nom'%(cat,masspt,prod)).getValV())
      params['a1'].append(ws.var('%s_%s_%s_a1'%(cat,masspt,prod)).getValV())
      params['a2'].append(ws.var('%s_%s_%s_a2'%(cat,masspt,prod)).getValV())
      params['n1'].append(ws.var('%s_%s_%s_n1'%(cat,masspt,prod)).getValV())
      params['e_scale'].append(ws.var('CMS_hem_nuisance_scale_e_%s_%s_%s'%(cat,masspt,prod)).getValV())
      params['e_res'].append(ws.var('CMS_hem_nuisance_res_e_%s_%s_%s'%(cat,masspt,prod)).getValV())
      params['m_scale'].append(ws.var('CMS_hem_nuisance_scale_m_%s_%s_%s'%(cat,masspt,prod)).getValV())
      params['m_res'].append(ws.var('CMS_hem_nuisance_res_m_%s_%s_%s'%(cat,masspt,prod)).getValV())

    e_res_hist.append(r.TH1F('e_res_%s_%s'%(cat,prod), 'e_res_%s_%s'%(cat,prod), len(binning)-1, np.array(binning)))
    e_scale_hist.append(r.TH1F('e_scale_%s_%s'%(cat,prod), 'e_scale_%s_%s'%(cat,prod), len(binning)-1, np.array(binning)))
    m_res_hist.append(r.TH1F('m_res_%s_%s'%(cat,prod), 'm_res_%s_%s'%(cat,prod), len(binning)-1, np.array(binning)))
    m_scale_hist.append(r.TH1F('m_scale_%s_%s'%(cat,prod), 'm_scale_%s_%s'%(cat,prod), len(binning)-1, np.array(binning)))

    for i in range(len(masspt)):
      e_scale_hist[-1].Fill(int(masspt[i]), params['e_scale'][i])
      m_scale_hist[-1].Fill(int(masspt[i]), params['m_scale'][i])
      e_res_hist[-1].Fill(int(masspt[i]), params['e_res'][i])
      m_res_hist[-1].Fill(int(masspt[i]), params['m_res'][i])
    e_res_datahist.append(r.RooDataHist('e_res_%s_%s'%(cat,prod), 'e_res_%s_%s'%(cat,prod), r.RooArgList(mh), e_res_hist[-1]))
    m_res_datahist.append(r.RooDataHist('m_res_%s_%s'%(cat,prod), 'm_res_%s_%s'%(cat,prod), r.RooArgList(mh), m_res_hist[-1]))
    e_scale_datahist.append(r.RooDataHist('e_scale_%s_%s'%(cat,prod), 'e_scale_%s_%s'%(cat,prod), r.RooArgList(mh), e_scale_hist[-1]))
    m_scale_datahist.append(r.RooDataHist('m_scale_%s_%s'%(cat,prod), 'm_scale_%s_%s'%(cat,prod), r.RooArgList(mh), e_scale_hist[-1]))
    e_res_func.append(r.RooHistFunc('e_res_func_%s_%s'%(cat,prod), 'e_res_func_%s_%s'%(cat,prod), r.RooArgSet(mh), e_res_datahist[-1]))
    e_scale_func.append(r.RooHistFunc('e_scale_func_%s_%s'%(cat,prod), 'e_scale_func_%s_%s'%(cat,prod), r.RooArgSet(mh), e_scale_datahist[-1]))
    m_res_func.append(r.RooHistFunc('m_res_func_%s_%s'%(cat,prod), 'm_res_func_%s_%s'%(cat,prod), r.RooArgSet(mh), m_res_datahist[-1]))
    m_scale_func.append(r.RooHistFunc('m_scale_func_%s_%s'%(cat,prod), 'm_scale_func_%s_%s'%(cat,prod), r.RooArgSet(mh), m_scale_datahist[-1]))
    norm_spline.append(r.RooSpline1D('%s_%s_pdf_norm'%(cat,prod),'%s_%s_pdf_norm'%(cat,prod),mh,len(masspts),np.array([int(mp) for mp in masspts]),np.array(params['norm'])))
    
    mean_spline.append(r.RooSpline1D('%s_%s_mean_cbe_nom'%(cat,prod),'%s_%s_mean_cbe_nom'%(cat,prod),mh,len(masspts),np.array([int(mp) for mp in masspts]),np.array(params['dm'])))

    print np.array([int(mp) for mp in masspts]),np.array(params['dm'])
    plot = mh.frame()
    mean_spline[-1].plotOn(plot)
    canv = r.TCanvas()
    plot.Draw()
    canv.SaveAs('splinetest.png')
    sigma_spline.append(r.RooSpline1D('%s_%s_sigma_cbe_nom'%(cat,prod),'%s_%s_sigma_cbe_nom'%(cat,prod),mh,len(masspts),np.array([float(mp) for mp in masspts]),np.array(params['sigma'])))
    a1_spline.append(r.RooSpline1D('%s_%s_a1'%(cat,prod),'%s_%s_a1'%(cat,prod),mh,len(masspts),np.array([float(mp) for mp in masspts]),np.array(params['a1'])))
    a2_spline.append(r.RooSpline1D('%s_%s_a2'%(cat,prod),'%s_%s_a2'%(cat,prod),mh,len(masspts),np.array([float(mp) for mp in masspts]),np.array(params['a2'])))
    n1_spline.append(r.RooSpline1D('%s_%s_n1'%(cat,prod),'%s_%s_n1'%(cat,prod),mh,len(masspts),np.array([float(mp) for mp in masspts]),np.array(params['n1'])))

#    mean_err_e = r.RooRealVar("CMS_hem_nuisance_scale_e_{}".format(prod), "CMS_hem_nuisance_scale_e_{}".format(prod), 0., -5, 5)
#    mean_err_m = r.RooRealVar("CMS_hem_nuisance_scale_m_{}".format(prod), "CMS_hem_nuisance_scale_m_{}".format(prod), 0., -5, 5)
#    mean_dcb = r.RooFormulaVar("{}_{}_mean_cbe".format(cat,prod), "{}_{}_mean_cbe".format(cat,prod), "(@0)*(1+@1*@2+@3*@4)", r.RooArgList(mean_spline[-1], e_scale_func[-1], mean_err_e, m_scale_func[-1], mean_err_m))
#    sigma_err_e = r.RooRealVar("CMS_hem_nuisance_res_e_{}".format(prod), "CMS_hem_nuisance_res_e_{}".format(prod), 0., -5, 5)
#    sigma_err_m = r.RooRealVar("CMS_hem_nuisance_res_m_{}".format(prod), "CMS_hem_nuisance_res_m_{}".format(prod), 0., -5, 5)
#
#    sigma_dcb = r.RooFormulaVar("{}_{}_sigma_cbe".format(cat,prod), "{}_{}_sigma_cbe".format(cat,prod), "@0*(1+@1*@2+@3*@4)", r.RooArgList(sigma_spline[-1], e_res_func[-1], sigma_err_e, m_res_func[-1], sigma_err_m))
#
#    pdf = r.RooCBExp("{}_{}_pdf".format(cat,prod), "{}_{}_pdf".format(cat,prod), mass_sig, mean_dcb, sigma_dcb, a1_spline[-1], n1_spline[-1], a2_spline[-1])

#    dh = ws.data('data_ggcat0_ggH')
#    w = r.RooWorkspace("w_13TeV","w_13TeV") 
#    getattr(w, 'import')(pdf)
#    getattr(w, 'import')(norm_spline[-1])
#    #getattr(w, 'import')(dh)
#
#    filename = "Workspaces/workspace_sig_"+cat+"_test.root"
#  
#    w.Print()
#    w.writeToFile(filename)
#
