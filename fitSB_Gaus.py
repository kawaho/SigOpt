import ROOT
import math
import signalModel
from fTest import pLUT2, pLUT3
ROOT.gSystem.Load("/afs/crc.nd.edu/user/k/kho2/CMSSW_10_2_13/lib/slc7_amd64_gcc700/libHiggsAnalysisGBRLikelihood.so")
ROOT.gROOT.SetBatch(True)

def GetNBkg(dataWS, bins):
  #Fit data
  inWS = dataWS #datafile.Get("CMS_emu_workspace")
  mass = inWS.var("CMS_emu_Mass")
  mass.setRange("R1",90.,115.)
  mass.setRange("R2",135.,180.)
  nbkg = [0 for i in range(len(bins)-1)]
  for i in range(len(bins)-1):
    effl, effh = bins[i], bins[i+1]
    for j in range(effl, effh):
      nbkg[i]+=inWS.data("data_norm_range%i"%j).sumEntries("1", "R1") + inWS.data("data_norm_range%i"%j).sumEntries("1", "R2")
  return nbkg 
  

def fit(dataWS, ggWS, vbfWS, bkg, bins, cat, norder, makePlot=False, saveData=True, sys_=True, bin_=True, masspt=125.):
  effl, effh = bins[0], bins[1]
  allvars = []
  fitstatus = 0
  w = ROOT.RooWorkspace("w_13TeV","w_13TeV") 

  #Fit data
  inWS = dataWS #datafile.Get("CMS_emu_workspace")
  mass = inWS.var("CMS_emu_Mass")
  #if saveData:
  #  mass.setBins(50)
  mass.setRange("higgsRange",masspt-15.,masspt+10.)
  mass.setRange("higgsRange2",90.,180.)
  mass.setRange("R1",90.,115.)
  mass.setRange("R2",135.,180.)
  db = inWS.data("data_norm_range%i"%effl).Clone()
  for i in range(effl+1, effh):
    db.append(inWS.data("data_norm_range%i"%i))
  db.SetName("roohist_data_mass_{}".format(cat))
  numofeventb = db.sumEntries()
  if db.sumEntries("1", "R1") + db.sumEntries("1", "R2") < 10:
    return -1, -1, -1
  neventb = ROOT.RooRealVar("pdf_{}_exp1_norm".format(cat), "pdf_{}_exp1_norm".format(cat), numofeventb, 0, 10*numofeventb)
  if bkg == 'exp1':
    param = ROOT.RooRealVar("pdf_{}_exp1_p1".format(cat), "pdf_{}_exp1_p1".format(cat), -0.04, -5., 0.)
    pdfb = ROOT.RooExponential("pdf_{}_exp1".format(cat), "pdf_{}_exp1".format(cat), mass, param)
    allvars.append([param])  
  elif bkg == 'pow1':
    param = ROOT.RooRealVar("pdf_{}_pow1_p1".format(cat), "pdf_{}_pow1_p1".format(cat), -2, -10., 0.)
    pdfb = ROOT.RooPower("pdf_{}_exp1".format(cat), "pdf_{}_exp1".format(cat), mass, param)
    allvars.append([param])  
  elif 'bern' in bkg:
    coeffList = ROOT.RooArgList()
    order = int(bkg[-1])
    for i in range(order):
      param = ROOT.RooRealVar("pdf_{}_bern{}_p{}".format(cat,order,i), "pdf_{}_bern{}_p{}".format(cat,order,i), 0.1*(i+1), -10., 10.)
      form = ROOT.RooFormulaVar("pdf_{}_bern{}_sq{}".format(cat,order,i), "pdf_{}_bern{}_sq{}".format(cat,order,i), "@0*@0", ROOT.RooArgList(param))
      coeffList.add(form)
      allvars.append([param,form])  

    pdfb = ROOT.RooBernsteinFast(order)("pdf_{}_exp1".format(cat), "pdf_{}_exp1".format(cat), mass, coeffList) 

  fitResultb = pdfb.fitTo(db, ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Save(1), ROOT.RooFit.SumW2Error(ROOT.kTRUE))
  
  allvars.append([db,neventb,pdfb])  
  fitstatus += fitResultb.status()
  neventb.setConstant(ROOT.kTRUE)
  if makePlot:
    canvas = ROOT.TCanvas("canvas","",0,0,800,800)
    frame = mass.frame(ROOT.RooFit.Range("higgsRange2"))
    db.plotOn(frame, ROOT.RooFit.CutRange("higgsRange2"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2), ROOT.RooFit.Binning(90,90,180))
    pdfb.plotOn(frame, ROOT.RooFit.Normalization(db.sumEntries("1", "higgsRange2"), ROOT.RooAbsReal.NumEvent), ROOT.RooFit.NormRange("higgsRange2"), ROOT.RooFit.Range("higgsRange2"))
    frame.Draw()
    canvas.SaveAs('Graphs/'+cat + "_"+str(effl) +"_"+str(effh)+"_bkg.png")
  
  if saveData:
    getattr(w, 'import')(pdfb)
    getattr(w, 'import')(neventb)
    getattr(w, 'import')(db)

  f = open('ShapeSys/Hem_shape_sys_%s_gaus.csv'%cat, 'w')
  f.write("Proc,Cat,Sys,Param,Value\n")
  sysname = ["ess_Up", "ess_Down", "me_Up", "me_Down"]
  #Fit signal
  for inWS, proc in zip([ggWS, vbfWS],['ggH','qqH']):
    mass_sig = inWS.var("CMS_emu_Mass")
    mass_sig.setBins(360)
    mass_sig.setRange("higgsRange",masspt-15.,masspt+10.)
    #mass_sig.setRange(masspt-15.,masspt+10.)
    dataFull = inWS.data("norm_range%i"%effl).Clone()
    if bin_:
      dh = ROOT.RooDataHist("data_{}_{}".format(cat,proc),"data_{}_{}".format(cat,proc), ROOT.RooArgSet(mass_sig), dataFull)
      for i in range(effl+1, effh):
        dh.add(inWS.data("norm_range%i"%i))
    else:
      dh = dataFull
      for i in range(effl+1, effh):
        dh.append(inWS.data("norm_range%i"%i))
#    dh = dh.binnedClone()

    dh.SetName("data_{}_{}".format(cat,proc))
    numofevent = dh.sumEntries("1")
    th1 = dh.createHistogram("CMS_emu_Mass",90)
    smallcan = ROOT.TCanvas()
    SumW2_array = list(th1.GetSumw2())
    nevent = ROOT.RooRealVar("{}_{}_pdf_norm".format(cat,proc), "{}_{}_pdf_norm".format(cat,proc), numofevent/100, 0, 10*numofevent/100)
    nevent.setError(math.sqrt(sum(SumW2_array))/100)

    mean_err_e_cat = ROOT.RooRealVar("CMS_hem_nuisance_scale_e_{}_{}".format(cat,proc), "CMS_hem_nuisance_scale_e_{}_{}".format(cat,proc), 0., -1, 1)
    mean_err_m_cat = ROOT.RooRealVar("CMS_hem_nuisance_scale_m_{}_{}".format(cat,proc), "CMS_hem_nuisance_scale_m_{}_{}".format(cat,proc), 0., -1, 1)
    mean_err_e = ROOT.RooRealVar("CMS_hem_nuisance_scale_e_{}".format(proc), "CMS_hem_nuisance_scale_e_{}".format(proc), 0., -5, 5)
    mean_err_m = ROOT.RooRealVar("CMS_hem_nuisance_scale_m_{}".format(proc), "CMS_hem_nuisance_scale_m_{}".format(proc), 0., -5, 5)
    mean_err_e_cat.setConstant(ROOT.kTRUE)
    mean_err_m_cat.setConstant(ROOT.kTRUE)
    mean_err_e.setConstant(ROOT.kTRUE)
    mean_err_m.setConstant(ROOT.kTRUE)

    sigma_err_e_cat = ROOT.RooRealVar("CMS_hem_nuisance_res_e_{}_{}".format(cat,proc), "CMS_hem_nuisance_res_e_{}_{}".format(cat,proc), 0., -1., 1.)
    sigma_err_m_cat = ROOT.RooRealVar("CMS_hem_nuisance_res_m_{}_{}".format(cat,proc), "CMS_hem_nuisance_res_m_{}_{}".format(cat,proc), 0., -1., 1.)
    sigma_err_e = ROOT.RooRealVar("CMS_hem_nuisance_res_e_{}".format(proc), "CMS_hem_nuisance_res_e_{}".format(proc), 0., -5, 5)
    sigma_err_m = ROOT.RooRealVar("CMS_hem_nuisance_res_m_{}".format(proc), "CMS_hem_nuisance_res_m_{}".format(proc), 0., -5, 5)
    sigma_err_e_cat.setConstant(ROOT.kTRUE)
    sigma_err_m_cat.setConstant(ROOT.kTRUE)
    sigma_err_e.setConstant(ROOT.kTRUE)
    sigma_err_m.setConstant(ROOT.kTRUE)

    sigfrac, dm_dcb, mean_dcb, sigma_nom_dcb, sigma_dcb, subpdf = [], [], [], [], [], []
    gaus_List, frac_List = ROOT.RooArgList(), ROOT.RooArgList()
    pLUT = pLUT2 if norder[proc]==2 else pLUT3
    for i in range(norder[proc]):
      dm_dcb.append(ROOT.RooRealVar("{}_{}_mean_gaus_nom_order{}".format(cat,proc,i), "{}_{}_mean_gaus_nom_order{}".format(cat,proc,i), pLUT['dm'][proc][i][0], pLUT['dm'][proc][i][1], pLUT['dm'][proc][i][2])) #-0.1,-1,1

#      mean_dcb.append(ROOT.RooFormulaVar("{}_{}_mean_gaus_order{}".format(cat,proc,i), "{}_{}_mean_gaus_order{}".format(cat,proc,i), "@0", ROOT.RooArgList(dm_dcb[-1])))
      mean_dcb.append(ROOT.RooFormulaVar("{}_{}_mean_gaus_order{}".format(cat,proc,i), "{}_{}_mean_gaus_order{}".format(cat,proc,i), "(@0+{})*(1+@1*@2+@3*@4)".format(masspt), ROOT.RooArgList(dm_dcb[-1], mean_err_e_cat, mean_err_e, mean_err_m_cat, mean_err_m)))
    
      sigma_nom_dcb.append(ROOT.RooRealVar("{}_{}_sigma_gaus_nom_order{}".format(cat,proc,i), "{}_{}_sigma_gaus_nom_order{}".format(cat,proc,i), pLUT['sigma'][proc][i][0], pLUT['sigma'][proc][i][1], pLUT['sigma'][proc][i][2])) #1.5, .8, 2

#      sigma_dcb.append(ROOT.RooFormulaVar("{}_{}_sigma_gaus_order{}".format(cat,proc,i), "{}_{}_sigma_gaus_order{}".format(cat,proc,i), "@0", ROOT.RooArgList(sigma_nom_dcb[-1])))
      sigma_dcb.append(ROOT.RooFormulaVar("{}_{}_sigma_gaus_order{}".format(cat,proc,i), "{}_{}_sigma_gaus_order{}".format(cat,proc,i), "@0*(1+@1*@2+@3*@4)", ROOT.RooArgList(sigma_nom_dcb[-1], sigma_err_e_cat, sigma_err_e, sigma_err_m_cat, sigma_err_m)))

      subpdf.append(ROOT.RooGaussian("{}_{}_pdf_order{}".format(cat,proc,i), "{}_{}_pdf_order{}".format(cat,proc,i), mass_sig, mean_dcb[-1], sigma_dcb[-1]))
      gaus_List.add(subpdf[-1])
      if i!=norder[proc]-1:
        sigfrac.append(ROOT.RooRealVar("{}_{}_sigfrac_order{}".format(cat,proc,i),"{}_{}_sigfrac_order{}".format(cat,proc,i),0.6+i*0.1,0.,1.))
        frac_List.add(sigfrac[-1])

    pdf = ROOT.RooAddPdf("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), gaus_List, frac_List, True)
    fitResult = pdf.fitTo(dh, ROOT.RooFit.Save(1), ROOT.RooFit.SumW2Error(ROOT.kTRUE), ROOT.RooFit.Range("higgsRange")) #ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Save(1), ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.SumW2Error(ROOT.kTRUE))

    nevent.setConstant(ROOT.kTRUE)
    for i in sigfrac:
      i.setConstant(ROOT.kTRUE)
  
    for j,k in zip(dm_dcb, sigma_nom_dcb):
      j.setConstant(ROOT.kTRUE)
      k.setConstant(ROOT.kTRUE)
      
    #plotting stuff
    if makePlot:
      signalModel.plot_model(cat, masspt, mass_sig, dh, pdf, fitResult, proc, gaus=True)

    #Take a snapshot of fit values
    params_norm = pdf.getParameters(ROOT.RooArgSet(mass_sig))
    savedParams = params_norm.snapshot() 

    fitstatus += fitResult.status()
    
    shapeSys = {sys:{'dm':0.01,'dsigma':0.01} for sys in sysname}
#Fit Systematics

    for sys in sysname:
      #go back to snapshot
      params_norm.assignValueOnly(savedParams)

      #get sys dataset
      dh_full_sys = inWS.data("{}_range{}".format(sys,effl)).Clone()
      if bin_:
        dh_sys = ROOT.RooDataHist("data_{}_{}_{}".format(cat,proc,sys),"data_{}_{}_{}".format(cat,proc,sys), ROOT.RooArgSet(mass_sig), dh_full_sys)
        for i in range(effl+1, effh):
          dh_sys.add(inWS.data("{}_range{}".format(sys,i)))
      else:
        dh_sys = dh_full_sys
        for i in range(effl+1, effh):
          dh_sys.append(inWS.data("{}_range{}".format(sys,i)))

      dh_sys.SetName("data_{}_{}_{}".format(cat,proc,sys))

     # print(mean_err_m_cat.getVal(), mean_err_e_cat.getVal(), mean_err_e.getVal(), mean_err_m.getVal(), 'helooooooo')

      mean_err_e_cat.setConstant(ROOT.kTRUE)
      mean_err_m_cat.setConstant(ROOT.kTRUE)
      sigma_err_e_cat.setConstant(ROOT.kTRUE)
      sigma_err_m_cat.setConstant(ROOT.kTRUE)
      mean_err_e.setConstant(ROOT.kTRUE)
      mean_err_m.setConstant(ROOT.kTRUE)
      sigma_err_m.setConstant(ROOT.kTRUE)
      sigma_err_e.setConstant(ROOT.kTRUE)

      if "ess" in sys:
        mean_err_e_cat.setConstant(ROOT.kFALSE)
        mean_err_e.setVal(1)
        mean_err_e.setConstant(ROOT.kTRUE)
        sigma_err_e_cat.setConstant(ROOT.kFALSE)
        sigma_err_e.setVal(1)
        sigma_err_e.setConstant(ROOT.kTRUE)
      else:
        mean_err_m_cat.setConstant(ROOT.kFALSE)
        mean_err_m.setVal(1)
        mean_err_m.setConstant(ROOT.kTRUE)
        sigma_err_m_cat.setConstant(ROOT.kFALSE)
        sigma_err_m.setVal(1)
        sigma_err_m.setConstant(ROOT.kTRUE)

      fitResult = pdf.fitTo(dh_sys, ROOT.RooFit.Save(1), ROOT.RooFit.SumW2Error(ROOT.kTRUE), ROOT.RooFit.Range("higgsRange"))#ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Save(1), ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.SumW2Error(ROOT.kTRUE))
    #if makePlot:
    #  signalModel.plot_model(cat+sys, masspt, mass_sig, dh, pdf, fitResult, proc)
    #  fitstatus += fitResult.status()
      if 'm' in sys:
        changeindm = mean_err_m_cat.getVal()
        changeinsigma = sigma_err_m_cat.getVal()
      else:
        changeindm = mean_err_e_cat.getVal()
        changeinsigma = sigma_err_e_cat.getVal()

      shapeSys[sys]['dm'] = changeindm
      shapeSys[sys]['dsigma'] = changeinsigma

      if "s" in sys:
        f.write("{},{},{},dm,{}\n".format(proc,cat,sys,changeindm))
      elif "r" in sys:
        f.write("{},{},{},sigma,{}\n".format(proc,cat,sys,changeinsigma))
      else:
        f.write("{},{},{},dm,{}\n".format(proc,cat,sys,changeindm))
        f.write("{},{},{},sigma,{}\n".format(proc,cat,sys,changeinsigma))


#    allvars.append([a1_dcb,a2_dcb,dm_dcb,n1_dcb,nevent,dh,sigma_nom_dcb,pdf])  
    params_norm.assignValueOnly(savedParams)

    mean_err_m_cat.setVal( max(abs(shapeSys['me_Up']['dm']),abs(shapeSys['me_Down']['dm'])) )
    sigma_err_m_cat.setVal( max(abs(shapeSys['me_Up']['dsigma']),abs(shapeSys['me_Down']['dsigma'])) )
    mean_err_e_cat.setVal( max(abs(shapeSys['ess_Up']['dm']),abs(shapeSys['ess_Down']['dm'])) )

    mean_err_e_cat.setConstant(ROOT.kTRUE)
    sigma_err_e_cat.setConstant(ROOT.kTRUE)
    mean_err_m_cat.setConstant(ROOT.kTRUE)
    sigma_err_m_cat.setConstant(ROOT.kTRUE)

    if sys_:
      mean_err_e.setConstant(ROOT.kFALSE)
      sigma_err_e.setConstant(ROOT.kFALSE)
      mean_err_m.setConstant(ROOT.kFALSE)
      sigma_err_m.setConstant(ROOT.kFALSE)
    else:
      mean_err_e.setConstant(ROOT.kTRUE)
      mean_err_m.setConstant(ROOT.kTRUE)
      sigma_err_m.setConstant(ROOT.kTRUE)
      sigma_err_e.setConstant(ROOT.kTRUE)

    getattr(w, 'import')(pdf)
    getattr(w, 'import')(nevent)
    getattr(w, 'import')(dh)


  filename = "Workspaces/workspace_sig_"+cat+"_gaus.root"
  ROOT.gDirectory.Add(w)
  
  w.Print()
  print(dh)
  w.writeToFile(filename)
  f.close()
  return fitstatus, numofeventb, numofevent
