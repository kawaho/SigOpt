import ROOT
import math
import signalModel
#ROOT.gSystem.Load("/afs/crc.nd.edu/user/k/kho2/CMSSW_10_2_13/lib/slc7_amd64_gcc700/libHiggsAnalysisCombinedLimit.so")
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
  

def fit(dataWS, ggWS, vbfWS, bkg, bins, cat, makePlot=False, saveData=True, sys_=True, bin_=True, masspt=125.):
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
  print "data_norm_range%i"%effl
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
    ##param = ROOT.RooRealVar("{}_POWER".format(cat), "{}_POWER".format(cat), -0.005, -0.01, 0.)
    #param = ROOT.RooRealVar("{}_POWER".format(cat), "{}_POWER".format(cat), 1, 0, 10.)
    #param2 = ROOT.RooRealVar("{}_EXP".format(cat), "{}_EXP".format(cat), 1, 0., 10.)
    #powb = ROOT.RooPower("pdf_{}_POWER".format(cat),"pdf_{}_POWER".format(cat),mass,param)
    ##pdfb = ROOT.RooGenericPdf("mypdf", "TMath::exp(pdf_{}_POWER)".format(cat), ROOT.RooArgList(powb));
    ##pdfb = ROOT.RooGenericPdf("mypdf", "exp(-@0*@2)*(@0**-@1)", ROOT.RooArgList(mass,param2,param));
    #pdfb = ROOT.RooGenericPdf("mypdf", "exp(-(@0**@1)*@2)", ROOT.RooArgList(mass,param2,param));
    ##pdfb = ROOT.RooGenericPdf("mypdf", "TMath::exp(Power(@0,@1)*@2)", ROOT.RooArgList(mass,param,param2));
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
    db.plotOn(frame, ROOT.RooFit.CutRange("higgsRange2"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2), ROOT.RooFit.Binning(80,90,180))
    pdfb.plotOn(frame, ROOT.RooFit.Normalization(db.sumEntries("1", "higgsRange2"), ROOT.RooAbsReal.NumEvent), ROOT.RooFit.NormRange("higgsRange2"), ROOT.RooFit.Range("higgsRange2"))
    data_chi2 = frame.chiSquare(2)
    data_chi2 = ROOT.TMath.Prob(data_chi2*(80-2),80-2);
    frame.Draw()
    canvas.SaveAs('Graphs/'+cat + "_"+str(effl) +"_"+str(effh)+"_"+str(data_chi2)+"_"+str(fitResultb.status())+"_bkg.png")
  
  if saveData:
    getattr(w, 'import')(pdfb)
    getattr(w, 'import')(neventb)
    getattr(w, 'import')(db)

  f = open('ShapeSys/Hem_shape_sys_%s.csv'%cat, 'w')
  f.write("Proc,Cat,Sys,Param,Value\n")
  sysname = ["ess_Up", "ess_Down", "me_Up", "me_Down"]
  #"eer_Up", "eer_Down"
  #Fit signal
  for inWS, proc in zip([ggWS, vbfWS],['ggH','qqH']):
    #inWS = rfile.Get("CMS_emu_workspace")
    mass_sig = inWS.var("CMS_emu_Mass")
    mass_sig.setBins(90)#540)
    mass_sig.setRange("higgsRange",masspt-15.,masspt+10.)
#    mass_sig.setRange(masspt-15.,masspt+10.)
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
    a1_dcb = ROOT.RooRealVar("{}_{}_a1".format(cat,proc), "{}_{}_a1".format(cat,proc), 2.5, .1, 5) #2.5, .1, 5 #0.6, .2, 1 
    a2_dcb = ROOT.RooRealVar("{}_{}_a2".format(cat,proc), "{}_{}_a2".format(cat,proc), 2.5, .1, 5) #2.5, .1, 5 #1, .6, 1.4
    dm_dcb = ROOT.RooRealVar("{}_{}_mean_cbe_nom".format(cat,proc), "{}_{}_mean_cbe_nom".format(cat,proc), masspt, masspt-1, masspt+1) #-0.1,-1,1
    mean_err_e_cat = ROOT.RooRealVar("CMS_hem_nuisance_scale_e_{}_{}".format(cat,proc), "CMS_hem_nuisance_scale_e_{}_{}".format(cat,proc), 1.)
    mean_err_m_cat = ROOT.RooRealVar("CMS_hem_nuisance_scale_m_{}_{}".format(cat,proc), "CMS_hem_nuisance_scale_m_{}_{}".format(cat,proc), 1.)
    mean_err_e = ROOT.RooRealVar("CMS_hem_nuisance_scale_e_{}".format(proc), "CMS_hem_nuisance_scale_e_{}".format(proc), 0., -5, 5)
    mean_err_m = ROOT.RooRealVar("CMS_hem_nuisance_scale_m_{}".format(proc), "CMS_hem_nuisance_scale_m_{}".format(proc), 0., -5, 5)
    mean_err_e_cat.setConstant(ROOT.kTRUE)
    mean_err_m_cat.setConstant(ROOT.kTRUE)
    mean_err_e.setConstant(ROOT.kTRUE)
    mean_err_m.setConstant(ROOT.kTRUE)
    mean_dcb = ROOT.RooFormulaVar("{}_{}_mean_cbe".format(cat,proc), "{}_{}_mean_cbe".format(cat,proc), "(@0)*(1+@1*@2+@3*@4)", ROOT.RooArgList(dm_dcb, mean_err_e_cat, mean_err_e, mean_err_m_cat, mean_err_m))
    
    n1_dcb = ROOT.RooRealVar("{}_{}_n1".format(cat,proc), "{}_{}_n1".format(cat,proc), 3.5, 0., 5.)  #3.5, 2., 5.

    sigma_nom_dcb = ROOT.RooRealVar("{}_{}_sigma_cbe_nom".format(cat,proc), "{}_{}_sigma_nom_cbe".format(cat,proc), 2, 1., 2.5) #1.5, .8, 2
    sigma_err_e_cat = ROOT.RooRealVar("CMS_hem_nuisance_res_e_{}_{}".format(cat,proc), "CMS_hem_nuisance_res_e_{}_{}".format(cat,proc), 1.)
    sigma_err_m_cat = ROOT.RooRealVar("CMS_hem_nuisance_res_m_{}_{}".format(cat,proc), "CMS_hem_nuisance_res_m_{}_{}".format(cat,proc), 1.)
    sigma_err_e = ROOT.RooRealVar("CMS_hem_nuisance_res_e_{}".format(proc), "CMS_hem_nuisance_res_e_{}".format(proc), 0., -5, 5)
    sigma_err_m = ROOT.RooRealVar("CMS_hem_nuisance_res_m_{}".format(proc), "CMS_hem_nuisance_res_m_{}".format(proc), 0., -5, 5)
    sigma_err_e_cat.setConstant(ROOT.kTRUE)
    sigma_err_m_cat.setConstant(ROOT.kTRUE)
    sigma_err_e.setConstant(ROOT.kTRUE)
    sigma_err_m.setConstant(ROOT.kTRUE)

    sigma_dcb = ROOT.RooFormulaVar("{}_{}_sigma_cbe".format(cat,proc), "{}_{}_sigma_cbe".format(cat,proc), "@0*(1+@1*@2+@3*@4)", ROOT.RooArgList(sigma_nom_dcb, sigma_err_e_cat, sigma_err_e, sigma_err_m_cat, sigma_err_m))
    nevent = ROOT.RooRealVar("{}_{}_pdf_norm".format(cat,proc), "{}_{}_pdf_norm".format(cat,proc), numofevent/100, 0, numofevent/10)
    nevent.setError(math.sqrt(sum(SumW2_array))/100)
    pdf = ROOT.RooCBExp("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), mass_sig, mean_dcb, sigma_dcb, a1_dcb, n1_dcb, a2_dcb)

    fitResult = pdf.fitTo(dh, ROOT.RooFit.Save(1), ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.SumW2Error(ROOT.kTRUE)) #ROOT.RooFit.Minimizer("Minuit2","minimize")

    a1_dcb.setConstant(ROOT.kTRUE)
    a2_dcb.setConstant(ROOT.kTRUE)
    dm_dcb.setConstant(ROOT.kTRUE)
    n1_dcb.setConstant(ROOT.kTRUE)
    sigma_nom_dcb.setConstant(ROOT.kTRUE)
    nevent.setConstant(ROOT.kTRUE)
    if sys_:
      mean_err_e.setConstant(ROOT.kFALSE)
      sigma_err_e.setConstant(ROOT.kFALSE)
      mean_err_m.setConstant(ROOT.kFALSE)
      sigma_err_m.setConstant(ROOT.kFALSE)

    constr = [0,0,0,0,0]
    constr[0] = a1_dcb.getVal()
    constr[1] = a2_dcb.getVal()
    constr[2] = dm_dcb.getVal()
    constr[3] = n1_dcb.getVal()
    constr[4] = sigma_nom_dcb.getVal()
    

    #plotting stuff
    if makePlot:
      signalModel.plot_model(cat, masspt, mass_sig, dh, pdf, fitResult, proc)

    fitstatus += fitResult.status()
    
    shapeSys = {sys:{'dm':0.01,'dsigma':0.01} for sys in sysname}
#Fit Systematics

    #dataFull = inWS.data("norm_range%i"%effl).Clone()

    for sys in sysname:
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
      a1_dcb_sys = ROOT.RooRealVar("{}_{}_a1_{}".format(cat,proc,sys), "{}_{}_a1_{}".format(cat,proc,sys), 2.5, .1, 5) 
      a2_dcb_sys = ROOT.RooRealVar("{}_{}_a2_{}".format(cat,proc,sys), "{}_{}_a2_{}".format(cat,proc,sys), 2.5, .1, 5)
      dm_dcb_sys = ROOT.RooRealVar("{}_{}_mean_cbe_nom".format(cat,proc), "{}_{}_mean_cbe_nom".format(cat,proc), masspt, masspt-1, masspt+1) #-0.1,-1,1
      mean_err_sys = ROOT.RooRealVar("CMS_hem_nuisance_scale_{}_{}".format(cat,proc), "CMS_hem_nuisance_scale_{}_{}".format(cat,proc), 0., -.1, .1)
      mean_dcb_sys = ROOT.RooFormulaVar("{}_{}_mean_cbe".format(cat,proc), "{}_{}_mean_cbe".format(cat,proc), "(@0)*(1+@1)", ROOT.RooArgList(dm_dcb_sys, mean_err_sys))
      
      n1_dcb_sys = ROOT.RooRealVar("{}_{}_n1_{}".format(cat,proc,sys), "{}_{}_n1_{}".format(cat,proc,sys), 3.5, 0., 15.)

      sigma_nom_dcb_sys = ROOT.RooRealVar("{}_{}_sigma_nom_cbe".format(cat,proc), "{}_{}_sigma_nom_cbe".format(cat,proc), 2, 1., 2.5) #1.5, .8, 2
      sigma_err_sys = ROOT.RooRealVar("CMS_hem_nuisance_res_{}_{}".format(cat,proc), "CMS_hem_nuisance_res_{}_{}".format(cat,proc), 0., -.1, .1)
      sigma_dcb_sys = ROOT.RooFormulaVar("{}_{}_sigma_cbe".format(cat,proc), "{}_{}_sigma_cbe".format(cat,proc), "@0*(1+@1)", ROOT.RooArgList(sigma_nom_dcb_sys, sigma_err_sys))
      
      pdf_sys = ROOT.RooCBExp("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), mass_sig, mean_dcb_sys, sigma_dcb_sys, a1_dcb_sys, n1_dcb_sys, a2_dcb_sys)
      
      a1_dcb_sys.setVal(constr[0])
      a2_dcb_sys.setVal(constr[1])
      dm_dcb_sys.setVal(constr[2]) 
      n1_dcb_sys.setVal(constr[3])
      sigma_nom_dcb_sys.setVal(constr[4])
      a1_dcb_sys.setConstant(ROOT.kTRUE)
      a2_dcb_sys.setConstant(ROOT.kTRUE)
      n1_dcb_sys.setConstant(ROOT.kTRUE)
      dm_dcb_sys.setConstant(ROOT.kTRUE)  
      sigma_nom_dcb_sys.setConstant(ROOT.kTRUE) 
#      if "ees" in sys:
#        sigma_err_sys.setConstant(ROOT.kTRUE)
#      elif "eer" in sys:
#        mean_err_sys.setConstant(ROOT.kTRUE)

      fitResult = pdf_sys.fitTo(dh_sys, ROOT.RooFit.Save(1), ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.SumW2Error(ROOT.kTRUE))#ROOT.RooFit.Minimizer("Minuit2","minimize")
      fitstatus += fitResult.status()
      
      changeindm = mean_err_sys.getVal()
      changeinsigma = sigma_err_sys.getVal()

      shapeSys[sys]['dm'] = changeindm
      shapeSys[sys]['dsigma'] = changeinsigma

      if "s" in sys:
        f.write("{},{},{},dm,{}\n".format(proc,cat,sys,changeindm))
      elif "r" in sys:
        f.write("{},{},{},sigma,{}\n".format(proc,cat,sys,changeinsigma))
      else:
        f.write("{},{},{},dm,{}\n".format(proc,cat,sys,changeindm))
        f.write("{},{},{},sigma,{}\n".format(proc,cat,sys,changeinsigma))

    mean_err_m_cat.setVal( max(abs(shapeSys['me_Up']['dm']),abs(shapeSys['me_Down']['dm'])) )
    sigma_err_m_cat.setVal( max(abs(shapeSys['me_Up']['dsigma']),abs(shapeSys['me_Down']['dsigma'])) )
    mean_err_e_cat.setVal( max(abs(shapeSys['ess_Up']['dm']),abs(shapeSys['ess_Down']['dm'])) )
    sigma_err_e_cat.setVal( max(abs(shapeSys['ess_Up']['dsigma']),abs(shapeSys['ess_Down']['dsigma'])) )

    mean_err_e_cat.setConstant(ROOT.kTRUE)
    sigma_err_e_cat.setConstant(ROOT.kTRUE)
    mean_err_m_cat.setConstant(ROOT.kTRUE)
    sigma_err_m_cat.setConstant(ROOT.kTRUE)

#    allvars.append([a1_dcb,a2_dcb,dm_dcb,n1_dcb,nevent,dh,sigma_nom_dcb,pdf])  
    getattr(w, 'import')(pdf)
    getattr(w, 'import')(nevent)
    getattr(w, 'import')(dh)

  filename = "Workspaces/workspace_sig_"+cat+".root"
#  ROOT.gDirectory.Add(w)
  
  w.Print()
  print(dh)
  w.writeToFile(filename)
  f.close()
  return fitstatus, numofeventb, numofevent
