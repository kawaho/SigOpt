import ROOT
def plot_model(cat, masspt, mass_sig, dh, pdf, fitResult, proc, gaus=False):
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
  dh.plotOn(frame, ROOT.RooFit.CutRange("higgsRange"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))#, ROOT.RooFit.Binning(25,masspt-15.,masspt+10.))#, ROOT.RooFit.Rescale(0.0059))
  pdf.plotOn(frame)#, ROOT.RooFit.Normalization(dh.sumEntries("1", "higgsRange"), ROOT.RooAbsReal.NumEvent))
  fitted_parms = fitResult.floatParsFinal()
  iter_ = fitted_parms.createIterator()
  var = iter_.Next()
  parm_plot = ""
  while var :
    Varname = var.GetName()
    if gaus:
      parm_plot+=Varname.split('_',4)[-2].replace('sigfrac','frac') + Varname[-1]  + " = "
    else:
      parm_plot+=Varname.split('_',4)[-2]+" = "
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
  lumi  = ROOT.TPaveText(lowX, lowY, lowX+0.30, lowY+0.2, "NDC");
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

  parmtxt  = ROOT.TPaveText(lowX, lowY-0.35, lowX+0.3, lowY, "NDC");
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
  if gaus:
    canvas.SaveAs('Graphs/'+cat + '_' + proc +"_gaus.png")
  else:
    canvas.SaveAs('Graphs/'+cat + '_' + proc +"_CBE.png")
   
