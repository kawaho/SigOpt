import ROOT
import math
#ROOT.gSystem.Load("/afs/crc.nd.edu/user/k/kho2/CMSSW_10_2_13/lib/slc7_amd64_gcc700/libHiggsAnalysisCombinedLimit.so")
ROOT.gSystem.Load("/afs/crc.nd.edu/user/k/kho2/CMSSW_10_2_13/lib/slc7_amd64_gcc700/libHiggsAnalysisGBRLikelihood.so")
#ROOT.gSystem.Load("/afs/cern.ch/work/k/kaho/CMSSW_10_2_13/lib/slc7_amd64_gcc700/libHiggsAnalysisCombinedLimit.so")
ROOT.gROOT.SetBatch(True)

def fit(dataWS, ggWS, vbfWS, bkg, bins, cat, makePlot=False, saveData=True, sys_=True):
  effl, effh = bins[0], bins[1]
  allvars = []
  fitstatus = 0
  w = ROOT.RooWorkspace("w_13TeV","w_13TeV") 

  #Fit data
  inWS = dataWS #datafile.Get("CMS_emu_workspace")
  mass = inWS.var("CMS_emu_Mass")
  #if saveData:
  #  mass.setBins(50)
  mass.setRange("higgsRange",110.,135.)
  mass.setRange("higgsRange2",110.,160.)
  mass.setRange("R1",110.,115.)
  mass.setRange("R2",135.,160.)
  db = inWS.data("data_norm_range%i"%effl).Clone()
  for i in range(effl+1, effh):
    db.append(inWS.data("data_norm_range%i"%i))
  db.SetName("roohist_data_mass_{}".format(cat))
  numofeventb = db.sumEntries()
  if db.sumEntries("1", "R1") + db.sumEntries("1", "R2") < 5:
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
    #pdfb = ROOT.RooBernstein("pdf_{}_exp1".format(cat), "pdf_{}_exp1".format(cat), mass, coeffList)

  fitResultb = pdfb.fitTo(db, ROOT.RooFit.Minimizer("Minuit2","Migrad"), ROOT.RooFit.Save(1), ROOT.RooFit.SumW2Error(ROOT.kTRUE))
  #dataBinned = ROOT.RooDataHist("roohist_data_mass_{}".format(cat), "roohist_data_mass_{}".format(cat), ROOT.RooArgSet(mass), db) 
  
  allvars.append([db,neventb,pdfb])  
  fitstatus += fitResultb.status()
  neventb.setConstant(ROOT.kTRUE)
#  fitstatus = fitstatus/math.sqrt(numofeventb)
  if makePlot:
    canvas = ROOT.TCanvas("canvas","",0,0,800,800)
    frame = mass.frame(ROOT.RooFit.Range("higgsRange2"))
    db.plotOn(frame, ROOT.RooFit.CutRange("higgsRange2"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2), ROOT.RooFit.Binning(100,110,160))
    pdfb.plotOn(frame, ROOT.RooFit.Normalization(db.sumEntries("1", "higgsRange2"), ROOT.RooAbsReal.NumEvent), ROOT.RooFit.NormRange("higgsRange2"), ROOT.RooFit.Range("higgsRange2"))
    frame.Draw()
    canvas.SaveAs('Graphs/'+cat + "_"+str(effl) +"_"+str(effh)+"_bkg.png")
  
  if saveData:
    getattr(w, 'import')(pdfb)
    getattr(w, 'import')(neventb)
    getattr(w, 'import')(db)
    #getattr(w, 'import')(dataBinned)

  f = open('ShapeSys/Hem_shape_sys_%s.csv'%cat, 'w')
  f.write("Proc,Cat,Sys,Param,Value\n")
#  f = open('Hem_shape_sys.csv', 'a')
#  if os.stat("Hem_shape_sys.csv").st_size == 0:
#    f.write("Proc,Cat,Sys,Param,Value\n")
  sysname = ["me_Up", "me_Down"] #"ees_Up", "ees_Down", "eer_Up", "eer_Down", "me_Up", "me_Down"]
  #Fit signal
  for inWS, proc in zip([ggWS, vbfWS],['ggH','qqH']):
    #inWS = rfile.Get("CMS_emu_workspace")
    dh = inWS.data("norm_range%i"%effl).Clone()
    for i in range(effl+1, effh):
      dh.append(inWS.data("norm_range%i"%i))
    dh.SetName("data_{}_{}".format(cat,proc))
    a1_dcb = ROOT.RooRealVar("{}_{}_a1".format(cat,proc), "{}_{}_a1".format(cat,proc), 2.5, .1, 5) #2.5, .1, 5 #0.6, .2, 1 
    a2_dcb = ROOT.RooRealVar("{}_{}_a2".format(cat,proc), "{}_{}_a2".format(cat,proc), 2.5, .1, 5) #2.5, .1, 5 #1, .6, 1.4
    dm_dcb = ROOT.RooRealVar("{}_{}_mean_cbe_nom".format(cat,proc), "{}_{}_mean_cbe_nom".format(cat,proc), 125, 124, 126) #-0.1,-1,1
    dm_gaus = ROOT.RooRealVar("{}_{}_mean_gaus_nom".format(cat,proc), "{}_{}_mean_gaus_nom".format(cat,proc), 125, 124, 126) #-0.1,-1,1
    mean_err_e = ROOT.RooRealVar("CMS_hem_nuisance_scale_e_{}_{}".format(cat,proc), "CMS_hem_nuisance_scale_e_{}_{}".format(cat,proc), 0., -.1, .1)
    mean_err_m = ROOT.RooRealVar("CMS_hem_nuisance_scale_m_{}_{}".format(cat,proc), "CMS_hem_nuisance_scale_m_{}_{}".format(cat,proc), 0., -.1, .1)
    mean_err_e.setConstant(ROOT.kTRUE)
    mean_err_m.setConstant(ROOT.kTRUE)
    mean_dcb = ROOT.RooFormulaVar("{}_{}_mean_cbe".format(cat,proc), "{}_{}_mean_cbe".format(cat,proc), "(@0)*(1+@1+@2)", ROOT.RooArgList(dm_dcb, mean_err_e, mean_err_m))
    mean_gaus = ROOT.RooFormulaVar("{}_{}_mean_gaus".format(cat,proc), "{}_{}_mean_gaus".format(cat,proc), "(@0)*(1+@1+@2)", ROOT.RooArgList(dm_gaus, mean_err_e, mean_err_m))
    
    n1_dcb = ROOT.RooRealVar("{}_{}_n1".format(cat,proc), "{}_{}_n1".format(cat,proc), 3.5, 2., 15.)  #3.5, 2., 5.
    n2_dcb = ROOT.RooRealVar("{}_{}_n2".format(cat,proc), "{}_{}_n2".format(cat,proc), 20., 0., 5000.) #20., 0., 100.

    sigma_nom_dcb = ROOT.RooRealVar("{}_{}_sigma_cbe_nom".format(cat,proc), "{}_{}_sigma_nom_cbe".format(cat,proc), 2, .1, 2.5) #1.5, .8, 2
    sigma_nom_gaus = ROOT.RooRealVar("{}_{}_sigma_gaus_nom".format(cat,proc), "{}_{}_sigma_nom_gaus".format(cat,proc), 2, .1, 5.) #1.5, .8, 2
    sigma_err_e = ROOT.RooRealVar("CMS_hem_nuisance_res_e_{}_{}".format(cat,proc), "CMS_hem_nuisance_res_e_{}_{}".format(cat,proc), 0., -.1, .1)
    sigma_err_m = ROOT.RooRealVar("CMS_hem_nuisance_res_m_{}_{}".format(cat,proc), "CMS_hem_nuisance_res_m_{}_{}".format(cat,proc), 0., -.1, .1)
    sigma_err_e.setConstant(ROOT.kTRUE)
    sigma_err_m.setConstant(ROOT.kTRUE)

    sigma_dcb = ROOT.RooFormulaVar("{}_{}_sigma_cbe".format(cat,proc), "{}_{}_sigma_cbe".format(cat,proc), "@0*(1+@1+@2)", ROOT.RooArgList(sigma_nom_dcb, sigma_err_e, sigma_err_m))
    sigma_gaus = ROOT.RooFormulaVar("{}_{}_sigma_gaus".format(cat,proc), "{}_{}_sigma_gaus".format(cat,proc), "@0*(1+@1+@2)", ROOT.RooArgList(sigma_nom_gaus, sigma_err_e, sigma_err_m))
    frac_gaus = ROOT.RooRealVar("{}_{}_frac_gaus".format(cat,proc), "{}_{}_frac_gaus".format(cat,proc), 0.15, 0.1, 0.9)
#    pdf = ROOT.RooGausDoubleExp("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), mass, mean_dcb, sigma_dcb, a1_dcb, a2_dcb)
#    pdf_dcb = ROOT.RooCBShape("{}_{}_dcb".format(cat,proc), "{}_{}_dcb".format(cat,proc), mass, mean_dcb, sigma_dcb, a1_dcb, n1_dcb)
    pdf = ROOT.RooDoubleCBFast("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), mass, mean_dcb, sigma_dcb, a1_dcb, n1_dcb, a2_dcb, n2_dcb)
    #pdf_dcb = ROOT.RooDoubleCBFast("{}_{}_dcb".format(cat,proc), "{}_{}_dcb".format(cat,proc), mass, mean_dcb, sigma_dcb, a1_dcb, n1_dcb, a2_dcb, n2_dcb)
#    pdf_dcb = ROOT.RooCBExp("{}_{}_cbe".format(cat,proc), "{}_{}_cbe".format(cat,proc), mass, mean_dcb, sigma_dcb, a1_dcb, n1_dcb, a2_dcb)
#    pdf_gaus = ROOT.RooGaussian("{}_{}_gaus".format(cat,proc), "{}_{}_gaus".format(cat,proc),mass,mean_gaus,sigma_gaus)
#    pdf = ROOT.RooAddPdf("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), ROOT.RooArgList(pdf_dcb, pdf_gaus), ROOT.RooArgList(frac_gaus))
    numofevent = dh.sumEntries("1", "higgsRange")
    nevent = ROOT.RooRealVar("{}_{}_pdf_norm".format(cat,proc), "{}_{}_pdf_norm".format(cat,proc), numofevent, 0, 10*numofevent)
    
    fitResult = pdf.fitTo(dh, ROOT.RooFit.Minimizer("Minuit2","Migrad"), ROOT.RooFit.Save(1), ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.SumW2Error(ROOT.kTRUE))
    #fitResult = pdf.fitTo(dh, ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Save(1), ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.SumW2Error(ROOT.kTRUE))

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
      frame = mass.frame(ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.Title(" "))
      dh.plotOn(frame, ROOT.RooFit.CutRange("higgsRange"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2), ROOT.RooFit.Binning(25,110,135))
      pdf.plotOn(frame, ROOT.RooFit.Normalization(dh.sumEntries("1", "higgsRange"), ROOT.RooAbsReal.NumEvent), ROOT.RooFit.NormRange("higgsRange"), ROOT.RooFit.Range("higgsRange"))
      print('Chi2', frame.chiSquare(6))
      txt = "#chi^{2} / ndf = %.2f / %i" %(frame.chiSquare()*50, 50-6);
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

      label2 = cat + ", " + proc + " mode";

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

      chitxt  = ROOT.TPaveText(lowX, lowY-0.01, lowX+0.3, lowY+0.09, "NDC");
      chitxt.SetTextFont(42);
      chitxt.SetTextSize(0.055*0.8*0.76);
      chitxt.SetBorderSize(   0 );
      chitxt.SetFillStyle(    0 );
      chitxt.SetTextAlign(   12 );
      chitxt.SetTextColor(    1 );
      chitxt.AddText(txt);
      chitxt.Draw("same");
      #latex = ROOT.TLatex();
      #latex.SetNDC();
      #latex.SetTextFont(42);
      #latex.SetTextSize(0.055*0.8*0.76);
      #latex.SetTextAlign(12);
      #latex.DrawLatex(lowX, lowY+0.05, txt);

      parmtxt  = ROOT.TPaveText(lowX, lowY-0.27, lowX+0.3, lowY-0.01, "NDC");
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
      canvas.SaveAs('Graphs/'+cat + '_' + proc +"_DCB.png")

    fitstatus += fitResult.status()
    #fitstatus += numofevent
    
    a1_dcb.setConstant(ROOT.kTRUE)
    a2_dcb.setConstant(ROOT.kTRUE)
    dm_dcb.setConstant(ROOT.kTRUE)
    dm_gaus.setConstant(ROOT.kTRUE)
    n1_dcb.setConstant(ROOT.kTRUE)
    n2_dcb.setConstant(ROOT.kTRUE)
    frac_gaus.setConstant(ROOT.kTRUE)
    sigma_nom_dcb.setConstant(ROOT.kTRUE)
    sigma_nom_gaus.setConstant(ROOT.kTRUE)
    nevent.setConstant(ROOT.kTRUE)
    if sys_:
      mean_err_e.setConstant(ROOT.kFALSE)
      sigma_err_e.setConstant(ROOT.kFALSE)
      mean_err_m.setConstant(ROOT.kFALSE)
      sigma_err_m.setConstant(ROOT.kFALSE)

    allvars.append([a1_dcb,a2_dcb,dm_dcb,dm_gaus,n1_dcb,n2_dcb,frac_gaus,nevent,dh,sigma_nom_dcb,sigma_nom_gaus,pdf])  
    getattr(w, 'import')(pdf)
    getattr(w, 'import')(nevent)
    getattr(w, 'import')(dh)
  
    constr = [0,0,0,0,0,0,0,0,0]
    constr[0] = a1_dcb.getVal()
    constr[1] = a2_dcb.getVal()
    constr[2] = dm_dcb.getVal()
    constr[3] = n1_dcb.getVal()
    constr[4] = n2_dcb.getVal()
    constr[5] = sigma_nom_dcb.getVal()
    constr[6] = dm_gaus.getVal()
    constr[7] = sigma_nom_gaus.getVal()
    constr[8] = frac_gaus.getVal()

#Fit Systematics
    for sys in sysname:
      dh = inWS.data("{}_range{}".format(sys,effl)).Clone()
      for i in range(effl+1, effh):
        dh.append(inWS.data("{}_range{}".format(sys,i)))

      dh.SetName("data_{}_{}_{}".format(cat,proc,sys))
      a1_dcb = ROOT.RooRealVar("{}_{}_a1_{}".format(cat,proc,sys), "{}_{}_a1_{}".format(cat,proc,sys), 2.5, .1, 5) 
      a2_dcb = ROOT.RooRealVar("{}_{}_a2_{}".format(cat,proc,sys), "{}_{}_a2_{}".format(cat,proc,sys), 2.5, .1, 5)
      dm_dcb = ROOT.RooRealVar("{}_{}_mean_cbe_nom".format(cat,proc), "{}_{}_mean_cbe_nom".format(cat,proc), 125, 124, 126) #-0.1,-1,1
      dm_gaus = ROOT.RooRealVar("{}_{}_mean_gaus_nom".format(cat,proc), "{}_{}_mean_gaus_nom".format(cat,proc), 125, 124, 126) #-0.1,-1,1
      mean_err = ROOT.RooRealVar("CMS_hem_nuisance_scale_{}_{}".format(cat,proc), "CMS_hem_nuisance_scale_{}_{}".format(cat,proc), 0., -.1, .1)
      mean_dcb = ROOT.RooFormulaVar("{}_{}_mean_cbe".format(cat,proc), "{}_{}_mean_cbe".format(cat,proc), "(@0)*(1+@1)", ROOT.RooArgList(dm_dcb, mean_err))
      mean_gaus = ROOT.RooFormulaVar("{}_{}_mean_gaus".format(cat,proc), "{}_{}_mean_gaus".format(cat,proc), "(@0)*(1+@1)", ROOT.RooArgList(dm_gaus, mean_err))
      
      n1_dcb = ROOT.RooRealVar("{}_{}_n1_{}".format(cat,proc,sys), "{}_{}_n1_{}".format(cat,proc,sys), 3.5, 2., 15.)
      n2_dcb = ROOT.RooRealVar("{}_{}_n2_{}".format(cat,proc,sys), "{}_{}_n2_{}".format(cat,proc,sys), 20., 0., 150.)

      sigma_nom_dcb = ROOT.RooRealVar("{}_{}_sigma_nom_cbe".format(cat,proc), "{}_{}_sigma_nom_cbe".format(cat,proc), 2, 1., 2.5) #1.5, .8, 2
      sigma_nom_gaus = ROOT.RooRealVar("{}_{}_sigma_nom_gaus".format(cat,proc), "{}_{}_sigma_nom_gaus".format(cat,proc), 2, 1., 5.) #1.5, .8, 2
      sigma_err = ROOT.RooRealVar("CMS_hem_nuisance_res_{}_{}".format(cat,proc), "CMS_hem_nuisance_res_{}_{}".format(cat,proc), 0., -.1, .1)
      sigma_dcb = ROOT.RooFormulaVar("{}_{}_sigma_cbe".format(cat,proc), "{}_{}_sigma_cbe".format(cat,proc), "@0*(1+@1)", ROOT.RooArgList(sigma_nom_dcb, sigma_err))
      sigma_gaus = ROOT.RooFormulaVar("{}_{}_sigma_gaus".format(cat,proc), "{}_{}_sigma_gaus".format(cat,proc), "@0*(1+@1)", ROOT.RooArgList(sigma_nom_gaus, sigma_err))
      frac_gaus = ROOT.RooRealVar("{}_{}_frac_gaus".format(cat,proc), "{}_{}_frac_gaus".format(cat,proc), 0.15, 0.1, 0.9)
      
      #pdf = ROOT.RooCBExp("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), mass, mean_dcb, sigma_dcb, a1_dcb, n1_dcb, a2_dcb)
      #pdf = ROOT.RooGausDoubleExp("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), mass, mean_dcb, sigma_dcb, a1_dcb, a2_dcb)
      #pdf = ROOT.RooGausDoubleExp("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), mass, mean_dcb, sigma_dcb, a1_dcb, a2_dcb)
      #pdf = ROOT.RooDoubleCBFast("{}_{}_pdf_{}".format(cat,proc,sys), "{}_{}_pdf_{}".format(cat,proc,sys), mass, mean_dcb, sigma_dcb, a1_dcb, n1_dcb, a2_dcb, n2_dcb)
      pdf_dcb = ROOT.RooCBExp("{}_{}_cbe".format(cat,proc), "{}_{}_cbe".format(cat,proc), mass, mean_dcb, sigma_dcb, a1_dcb, n1_dcb, a2_dcb)
      pdf_gaus = ROOT.RooGaussian("{}_{}_gaus".format(cat,proc), "{}_{}_gaus".format(cat,proc),mass,mean_gaus,sigma_gaus)
      pdf = ROOT.RooAddPdf("{}_{}_pdf".format(cat,proc), "{}_{}_pdf".format(cat,proc), ROOT.RooArgList(pdf_dcb, pdf_gaus), ROOT.RooArgList(frac_gaus))
      
      a1_dcb.setVal(constr[0])
      a2_dcb.setVal(constr[1])
      dm_dcb.setVal(constr[2]) 
      n1_dcb.setVal(constr[3])
      n2_dcb.setVal(constr[4])
      sigma_nom_dcb.setVal(constr[5])
      dm_gaus.setVal(constr[6]) 
      sigma_nom_gaus.setVal(constr[7])
      frac_gaus.setVal(constr[8])
      a1_dcb.setConstant(ROOT.kTRUE)
      a2_dcb.setConstant(ROOT.kTRUE)
      dm_dcb.setConstant(ROOT.kTRUE)  
      n1_dcb.setConstant(ROOT.kTRUE)
      n2_dcb.setConstant(ROOT.kTRUE)
      sigma_nom_dcb.setConstant(ROOT.kTRUE) 
      dm_gaus.setConstant(ROOT.kTRUE) 
      sigma_nom_gaus.setConstant(ROOT.kTRUE) 
      frac_gaus.setConstant(ROOT.kTRUE)
      if "ees" in sys:
        sigma_err.setConstant(ROOT.kTRUE)
      elif "eer" in sys:
        mean_err.setConstant(ROOT.kTRUE)

      fitResult = pdf.fitTo(dh, ROOT.RooFit.Minimizer("Minuit2","Migrad"), ROOT.RooFit.Save(1), ROOT.RooFit.Range("higgsRange"), ROOT.RooFit.SumW2Error(ROOT.kTRUE))
      fitstatus += fitResult.status()
      
      changeindm = mean_err.getVal()
      changeinsigma = sigma_err.getVal()
      if "s" in sys:
        f.write("{},{},{},dm,{}\n".format(proc,cat,sys,changeindm))
      elif "r" in sys:
        f.write("{},{},{},sigma,{}\n".format(proc,cat,sys,changeinsigma))
      else:
        f.write("{},{},{},dm,{}\n".format(proc,cat,sys,changeindm))
        f.write("{},{},{},sigma,{}\n".format(proc,cat,sys,changeinsigma))
  
  filename = "Workspaces/workspace_sig_"+cat+".root"
#  ROOT.gDirectory.Add(w)
  w.Print()
  w.writeToFile(filename)
  f.close()
  return fitstatus, numofeventb, numofevent
