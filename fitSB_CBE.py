import ROOT
import math
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

  f = open('ShapeSys/Hem_shape_sys_%s.csv'%cat, 'w')
  f.write("Proc,Cat,Sys,Param,Value\n")
  sysname = ["ees_Up", "ees_Down", "eer_Up", "eer_Down", "me_Up", "me_Down"]
  #Fit signal
  for inWS, proc in zip([ggWS, vbfWS],['ggH','qqH']):
    #inWS = rfile.Get("CMS_emu_workspace")
    mass_sig = inWS.var("CMS_emu_Mass")
    mass_sig.setBins(360)
    mass_sig.setRange("higgsRange",masspt-15.,masspt+10.)
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
    a1_dcb = ROOT.RooRealVar("{}_{}_a1".format(cat,proc), "{}_{}_a1".format(cat,proc), 2.5, .1, 5) #2.5, .1, 5 #0.6, .2, 1 
    a2_dcb = ROOT.RooRealVar("{}_{}_a2".format(cat,proc), "{}_{}_a2".format(cat,proc), 2.5, .1, 5) #2.5, .1, 5 #1, .6, 1.4
    dm_dcb = ROOT.RooRealVar("{}_{}_mean_cbe_nom".format(cat,proc), "{}_{}_mean_cbe_nom".format(cat,proc), masspt, masspt-1, masspt+1) #-0.1,-1,1
    dm_gaus = ROOT.RooRealVar("{}_{}_mean_gaus_nom".format(cat,proc), "{}_{}_mean_gaus_nom".format(cat,proc), 125, 124, 126) #-0.1,-1,1
    mean_err_e_cat = ROOT.RooRealVar("CMS_hem_nuisance_scale_e_{}_{}".format(cat,proc), "CMS_hem_nuisance_scale_e_{}_{}".format(cat,proc), 1.)
    mean_err_m_cat = ROOT.RooRealVar("CMS_hem_nuisance_scale_m_{}_{}".format(cat,proc), "CMS_hem_nuisance_scale_m_{}_{}".format(cat,proc), 1.)
    mean_err_e = ROOT.RooRealVar("CMS_hem_nuisance_scale_e_{}".format(proc), "CMS_hem_nuisance_scale_e_{}".format(proc), 0., -5, 5)
    mean_err_m = ROOT.RooRealVar("CMS_hem_nuisance_scale_m_{}".format(proc), "CMS_hem_nuisance_scale_m_{}".format(proc), 0., -5, 5)
    mean_err_e_cat.setConstant(ROOT.kTRUE)
    mean_err_m_cat.setConstant(ROOT.kTRUE)
    mean_err_e.setConstant(ROOT.kTRUE)
    mean_err_m.setConstant(ROOT.kTRUE)
    mean_dcb = ROOT.RooFormulaVar("{}_{}_mean_cbe".format(cat,proc), "{}_{}_mean_cbe".format(cat,proc), "(@0)*(1+@1*@2+@3*@4)", ROOT.RooArgList(dm_dcb, mean_err_e_cat, mean_err_e, mean_err_m_cat, mean_err_m))
    
    n1_dcb = ROOT.RooRealVar("{}_{}_n1".format(cat,proc), "{}_{}_n1".format(cat,proc), 3.5, 2., 10.)  #3.5, 2., 5.

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

    pdf = ROOT.RooCBExp("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), mass_sig, mean_dcb, sigma_dcb, a1_dcb, n1_dcb, a2_dcb)
    numofevent = dh.sumEntries("1", "higgsRange")
    nevent = ROOT.RooRealVar("{}_{}_pdf_norm".format(cat,proc), "{}_{}_pdf_norm".format(cat,proc), numofevent, 0, 10*numofevent)
    
    fitResult = pdf.fitTo(dh, ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Save(1), ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.SumW2Error(ROOT.kTRUE))
    if makePlot:
      canvas = ROOT.TCanvas("canvas","",0,0,800,800)
      ROOT.gPad.SetFillColor(0);
      ROOT.gPad.SetBorderMode(0);
      ROOT.gPad.SetBorderSize(10);
      ROOT.gPad.SetTickx(1);
      ROOT.gPad.SetTicky(1);
      ROOT.gPad.SetFrameFillStyle(0);
      ROOT.gPad.SetFrameLineStyle(0);
      ROOT.gPad.SetFrameLineWidth(3);
      ROOT.gPad.SetFrameBorderMode(0);
      ROOT.gPad.SetFrameBorderSize(10);
      canvas.SetLeftMargin(0.16);
      canvas.SetRightMargin(0.05);
      canvas.SetBottomMargin(0.14);
      latex = ROOT.TLatex();
      latex.SetNDC();
      latex.SetTextFont(43);
      latex.SetTextSize(20);
      latex.SetTextAlign(31);
      latex.SetTextAlign(11);
      frame = mass_sig.frame(ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.Title(" "))
      dh.plotOn(frame, ROOT.RooFit.CutRange("higgsRange"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2), ROOT.RooFit.Binning(25,masspt-15.,masspt+10.))#, ROOT.RooFit.Rescale(0.0059))
      pdf.plotOn(frame, ROOT.RooFit.Normalization(dh.sumEntries("1", "higgsRange"), ROOT.RooAbsReal.NumEvent))
      fitted_parms = fitResult.floatParsFinal()
      iter_ = fitted_parms.createIterator()
      var = iter_.Next()
      parm_plot = ""
      while var :
        parm_plot+=var.GetName().split("_",2)[2].replace('_cbe_nom','')+" = "
        parm_plot+=str(round(var.getVal(),3))+" #pm "
        parm_plot+=str(round(var.getError(),3))+"\n" 
        var = iter_.Next()
      frame.SetTitle("");
      frame.SetXTitle("m_{e#mu} [GeV]");
      
      frame.SetMaximum(frame.GetMaximum());#*0.0059);
      frame.SetMinimum(0);
      frame.GetXaxis().SetTitleFont(42);
      frame.GetYaxis().SetTitleFont(42);
      frame.GetXaxis().SetTitleSize(0.05);
      frame.GetYaxis().SetTitleSize(0.05);
      frame.GetXaxis().SetLabelSize(0.045);
      frame.GetYaxis().SetLabelSize(0.045);
      
      frame.GetYaxis().SetTitleOffset(1.4);
      frame.GetXaxis().SetTitleOffset(1.2);
      frame.Draw();

      label2 = cat.split('_')[0] + ", " + proc + " mode";
      label3 = cat.split('_')[1];

      lowX=0.65;
      lowY=0.83;
      lumi  = ROOT.TPaveText(lowX,lowY, lowX+0.30, lowY+0.2, "NDC");
      lumi.SetBorderSize(   0 );
      lumi.SetFillStyle(    0 );
      lumi.SetTextAlign(   12 );
      lumi.SetTextColor(    1 );
      lumi.SetTextSize(0.038);
      lumi.SetTextFont (   42 );
      lumi.AddText("138 fb^{-1} (13 TeV)");
      lumi.Draw("same");
 
      lowX=0.18;
      lowY=0.71;
      cmstxt  = ROOT.TPaveText(lowX, lowY+0.06, lowX+0.15, lowY+0.16, "NDC");
      cmstxt.SetTextFont(61);
      cmstxt.SetTextSize(0.055);
      cmstxt.SetBorderSize(   0 );
      cmstxt.SetFillStyle(    0 );
      cmstxt.SetTextAlign(   12 );
      cmstxt.SetTextColor(    1 );
      cmstxt.AddText("CMS");
      cmstxt.Draw("same");
 
      lowX=0.18;
      lowY=0.64;
      cattxt  = ROOT.TPaveText(lowX, lowY+0.06, lowX+0.3, lowY+0.16, "NDC");
      cattxt.SetTextFont(42);
      cattxt.SetTextSize(0.055*0.8*0.76);
      cattxt.SetBorderSize(   0 );
      cattxt.SetFillStyle(    0 );
      cattxt.SetTextAlign(   12 );
      cattxt.SetTextColor(    1 );
      cattxt.AddText(label2);
      cattxt.Draw("same");

      lowX=0.18;
      lowY=0.59;
      cattxt2  = ROOT.TPaveText(lowX, lowY+0.06, lowX+0.3, lowY+0.16, "NDC");
      cattxt2.SetTextFont(42);
      cattxt2.SetTextSize(0.055*0.8*0.76);
      cattxt2.SetBorderSize(   0 );
      cattxt2.SetFillStyle(    0 );
      cattxt2.SetTextAlign(   12 );
      cattxt2.SetTextColor(    1 );
      cattxt2.AddText('m_{H} = %s GeV'%label3);
      cattxt2.Draw("same");

      lowY=0.64;
      #paramsbc = ROOT.RooArgList(pdf.getParameters(ROOT.RooArgSet(mass_sig))
      #massbc = ROOT.RooArgList(mass_sig)
      #h1bc = dh.createHistogram("CMS_emu_Mass", mass_sig)
      #
      #f1bc = pdf.asTF(massbc)#, paramsbc, ROOT.RooArgSet(mass_sig))

      #def pdf_norm(x):
      #  return f1bc.EvalPar(x)*h1bc.GetSumOfWeights()*h1bc.GetBinWidth(1)

      #fcor = ROOT.TF1("f2", pdf_norm, 110, 135, 0)
      #chi2 = h1bc.Chisquare(fcor,"L")
      #c = ROOT.TCanvas()
      #c.cd()
      #f1bc.Draw()
      #fcor.Draw("Same")
      ##h1bc.Draw()
      #c.SaveAs("bc_trial.png")
      #txt = "#chi^{2} / ndf = %.2f / %i" %(chi2, 25-6);
      #txt = "#chi^{2} / ndf = %.2f / %i" %(frame.chiSquare()*0.0059*25, 25-6);
      #chitxt  = ROOT.TPaveText(lowX, lowY-0.01, lowX+0.3, lowY+0.09, "NDC");
      #chitxt.SetTextFont(42);
      #chitxt.SetTextSize(0.055*0.8*0.76);
      #chitxt.SetBorderSize(   0 );
      #chitxt.SetFillStyle(    0 );
      #chitxt.SetTextAlign(   12 );
      #chitxt.SetTextColor(    1 );
      #chitxt.AddText(txt);
      #chitxt.Draw("same");

      parmtxt  = ROOT.TPaveText(lowX, lowY-0.25, lowX+0.3, lowY-0.01, "NDC");
      parmtxt.SetTextFont(42);
      parmtxt.SetTextSize(0.055*0.8*0.76);
      parmtxt.SetBorderSize(   0 );
      parmtxt.SetFillStyle(    0 );
      parmtxt.SetTextAlign(   12 );
      parmtxt.SetTextColor(    1 );
      for parm_text in parm_plot.split("\n"):
        parmtxt.AddText(parm_text);
      parmtxt.Draw("same");

      lowX=0.30;
      lowY=0.71;
      pretxt  = ROOT.TPaveText(lowX, lowY+0.05, lowX+0.15, lowY+0.15, "NDC");
      pretxt.SetTextFont(52);
      pretxt.SetTextSize(0.055*0.8*0.76);
      pretxt.SetBorderSize(   0 );
      pretxt.SetFillStyle(    0 );
      pretxt.SetTextAlign(   12 );
      pretxt.SetTextColor(    1 );
      pretxt.AddText("Preliminary");
      pretxt.Draw("same");
      canvas.SaveAs('Graphs/'+cat + '_' + proc +'_'+str(int(masspt))+"_CBE.png")

    fitstatus += fitResult.status()
    
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

    shapeSys = {sys:{'dm':0.01,'dsigma':0.01} for sys in sysname}
#Fit Systematics

    #dataFull = inWS.data("norm_range%i"%effl).Clone()

    for sys in sysname:
      mass_sig_sys = inWS.var("CMS_emu_Mass_{}".format(sys))
      mass_sig_sys.setRange("higgsRange",masspt-15.,masspt+10.)

      dh_full_sys = inWS.data("{}_range{}".format(sys,effl)).Clone()
      if bin_:
        dh_sys = ROOT.RooDataHist("data_{}_{}_{}".format(cat,proc,sys),"data_{}_{}_{}".format(cat,proc,sys), ROOT.RooArgSet(mass_sig_sys), dh_full_sys)
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
      
      n1_dcb_sys = ROOT.RooRealVar("{}_{}_n1_{}".format(cat,proc,sys), "{}_{}_n1_{}".format(cat,proc,sys), 3.5, 2., 15.)

      sigma_nom_dcb_sys = ROOT.RooRealVar("{}_{}_sigma_nom_cbe".format(cat,proc), "{}_{}_sigma_nom_cbe".format(cat,proc), 2, 1., 2.5) #1.5, .8, 2
      sigma_err_sys = ROOT.RooRealVar("CMS_hem_nuisance_res_{}_{}".format(cat,proc), "CMS_hem_nuisance_res_{}_{}".format(cat,proc), 0., -.1, .1)
      sigma_dcb_sys = ROOT.RooFormulaVar("{}_{}_sigma_cbe".format(cat,proc), "{}_{}_sigma_cbe".format(cat,proc), "@0*(1+@1)", ROOT.RooArgList(sigma_nom_dcb_sys, sigma_err_sys))
      
      pdf_sys = ROOT.RooCBExp("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), mass_sig_sys, mean_dcb_sys, sigma_dcb_sys, a1_dcb_sys, n1_dcb_sys, a2_dcb_sys)
      
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
      if "ees" in sys:
        sigma_err_sys.setConstant(ROOT.kTRUE)
      elif "eer" in sys:
        mean_err_sys.setConstant(ROOT.kTRUE)

      fitResult = pdf_sys.fitTo(dh_sys, ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Save(1), ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.SumW2Error(ROOT.kTRUE))
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
    mean_err_e_cat.setVal( max(abs(shapeSys['ees_Up']['dm']),abs(shapeSys['ees_Down']['dm'])) )
    sigma_err_e_cat.setVal( max(abs(shapeSys['eer_Up']['dsigma']),abs(shapeSys['eer_Down']['dsigma'])) )

    mean_err_e_cat.setConstant(ROOT.kTRUE)
    sigma_err_e_cat.setConstant(ROOT.kTRUE)
    mean_err_m_cat.setConstant(ROOT.kTRUE)
    sigma_err_m_cat.setConstant(ROOT.kTRUE)

    allvars.append([a1_dcb,a2_dcb,dm_dcb,n1_dcb,nevent,dh,sigma_nom_dcb,pdf])  
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
