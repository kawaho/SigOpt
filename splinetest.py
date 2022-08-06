import ROOT as r
import numpy as np
import math
r.gROOT.SetBatch(True)

def newCan():
  canvas = r.TCanvas("canvas","",0,0,800,800)
  r.gPad.SetFillColor(0);
  r.gPad.SetBorderMode(0);
  r.gPad.SetBorderSize(10);
  r.gPad.SetTickx(1);
  r.gPad.SetTicky(1);
  r.gPad.SetFrameFillStyle(0);
  r.gPad.SetFrameLineStyle(0);
  r.gPad.SetFrameLineWidth(3);
  r.gPad.SetFrameBorderMode(0);
  r.gPad.SetFrameBorderSize(10);
  canvas.SetLeftMargin(0.16);
  canvas.SetRightMargin(0.05);
  canvas.SetBottomMargin(0.14);
  latex = r.TLatex();
  latex.SetNDC();
  latex.SetTextFont(43);
  latex.SetTextSize(20);
  latex.SetTextAlign(31);
  latex.SetTextAlign(11);
  return canvas

def extraText(canv, cat, proc):
  label = cat + ", " + proc + " mode";
  canv.cd()
  lowX=0.65;
  lowY=0.83;
  lumi  = r.TPaveText(lowX, lowY, lowX+0.30, lowY+0.2, "NDC");
  lumi.SetBorderSize(   0 );
  lumi.SetFillStyle(    0 );
  lumi.SetTextAlign(   12 );
  lumi.SetTextColor(    1 );
#  lumi.SetTextSize(0.038);
  lumi.SetTextFont (   42 );
  lumi.AddText("138 fb^{-1} (13 TeV)");

  lowX=0.16;
  cmstxt  = r.TPaveText(lowX, lowY, lowX+0.13, lowY+0.2, "NDC");
  cmstxt.SetTextFont(61);
#  cmstxt.SetTextSize(0.055);
  cmstxt.SetBorderSize(   0 );
  cmstxt.SetFillStyle(    0 );
  cmstxt.SetTextAlign(   12 );
  cmstxt.SetTextColor(    1 );
  cmstxt.AddText("CMS");

  lowX=0.30;
  pretxt  = r.TPaveText(lowX, lowY, lowX+0.2, lowY+0.2, "NDC");
  pretxt.SetTextFont(52);
#  pretxt.SetTextSize(0.055*0.8*0.76);
  pretxt.SetBorderSize(   0 );
  pretxt.SetFillStyle(    0 );
  pretxt.SetTextAlign(   12 );
  pretxt.SetTextColor(    1 );
  pretxt.AddText("Preliminary");

  lowX=0.62;
  lowY=0.72;
  cattxt  = r.TPaveText(lowX, lowY+0.06, lowX+0.3, lowY+0.16, "NDC");
  cattxt.SetTextFont(42);
#  cattxt.SetTextSize(0.055*0.8*0.76);
  cattxt.SetBorderSize(   0 );
  cattxt.SetFillStyle(    0 );
  cattxt.SetTextAlign(   12 );
  cattxt.SetTextColor(    1 );
  cattxt.AddText(label);

  return lumi, cmstxt, cattxt, pretxt 

def frameformat(frame, mh=False):
  frame.SetTitle("");
  if mh:
    frame.SetXTitle("m_{e#mu} [GeV]");
  else:
    frame.SetXTitle("m_{H} [GeV]");
  #frame.SetMaximum(frame.GetMaximum()*0.0001);
  #frame.SetMinimum(0);
  frame.GetXaxis().SetTitleFont(42);
  frame.GetYaxis().SetTitleFont(42);
  frame.GetXaxis().SetTitleSize(0.05);
  frame.GetYaxis().SetTitleSize(0.05);
  frame.GetXaxis().SetLabelSize(0.045);
  frame.GetYaxis().SetLabelSize(0.045);
  
  frame.GetYaxis().SetTitleOffset(1.4);
  frame.GetXaxis().SetTitleOffset(1.2);

masspts = np.array([110., 120., 125., 130., 140., 150., 160.])
totalnu = {mpt:0 for mpt in masspts}
for cat in ['ggcat0', 'ggcat1', 'ggcat2', 'ggcat3', 'vbfcat0', 'vbfcat1', 'vbfcat2']:
  inws = r.TFile('Workspaces/workspace_sig_%s.root'%cat).Get('w_13TeV')
  mh = inws.var('MH')
  mh.setRange("fullRange", masspts[0], masspts[-1])
  emumass = inws.var('CMS_emu_Mass')
  emumass.setBins(50)
  for prod in ['ggH', 'qqH']:
    pdf = inws.pdf('%s_%s_pdf'%(cat,prod))
    plot = emumass.frame(100,170,70)
    frameformat(plot)
    canv = newCan()
    for mp, cr in zip(masspts, [r.kRed, r.kOrange+1, r.kPink-9, r.kBlue, r.kGreen+4, r.kGreen, r.kMagenta, r.kCyan-7]): 
      dh = inws.data('data_%s_%s_%s'%(cat,str(int(mp)),prod))
      mh.setVal(mp)
      dh.plotOn(plot, r.RooFit.Binning(90,90,180), r.RooFit.LineColor(cr), r.RooFit.MarkerColor(cr))
      pdf.plotOn(plot, r.RooFit.Normalization(inws.function('%s_%s_pdf_norm'%(cat,prod)).getVal()*100, r.RooAbsReal.NumEvent), r.RooFit.LineColor(cr), r.RooFit.LineWidth(2))
      print dh.sumEntries(), inws.function('%s_%s_pdf_norm'%(cat,prod)).getVal()
      totalnu[mp] += dh.sumEntries()
    for mp in range(int(masspts[0])+1,int(masspts[-1]),1):
      mh.setVal(mp)
      pdf.plotOn(plot, r.RooFit.Normalization(inws.function('%s_%s_pdf_norm'%(cat,prod)).getVal()*100, r.RooAbsReal.NumEvent), r.RooFit.LineStyle(r.kDashed), r.RooFit.LineColor(r.kBlack), r.RooFit.LineWidth(1))
    plot.Draw()
    lumi, cmstxt, cattxt, pretxt = extraText(canv, cat, prod)
    lumi.Draw('Same')
    cmstxt.Draw('Same')
    cattxt.Draw('Same')
    pretxt.Draw('Same')
    canv.Update()
    canv.SaveAs('Graphs/splines_cbe/pdfs/%s_%s_pdf.png'%(cat,prod))
    
    for spline_name in ['%s_%s_sigma_cbe_nom'%(cat,prod), '%s_%s_mean_cbe_nom'%(cat,prod), '%s_%s_pdf_norm'%(cat,prod), '%s_%s_n1'%(cat,prod), '%s_%s_a1'%(cat,prod), '%s_%s_a2'%(cat,prod)]:
      mean_spline = inws.function(spline_name)
      
      ori_pt = []
      for mt in masspts:
        mh.setVal(mt)
        ori_pt.append(mean_spline.getVal())
      
      inws_errs = [r.TFile('Workspaces/workspace_sig_%s_%i.root'%(cat,int(ii))).Get('w_13TeV') for ii in masspts]
      if 'norm' in spline_name:
        err_ = np.array([0 for ii in ori_pt])
      else:
        err_ = np.array([inws_err.var(spline_name.replace(cat,cat+'_'+str(int(ii)))).getError() for inws_err,ii in zip(inws_errs,masspts)])
      gr = r.TGraphErrors(len(masspts),masspts,np.array(ori_pt),r.nullptr,err_)
      
      plot = mh.frame(r.RooFit.Title(" "))
      if 'norm' in spline_name:
        plot.SetYTitle("normalization")
      elif 'sigma' in spline_name:
        plot.SetYTitle("#sigma")
      elif 'mean' in spline_name:
        plot.SetYTitle("#mu")
      elif 'n1' in spline_name:
        plot.SetYTitle("n_{L}")
      elif 'a1' in spline_name:
        plot.SetYTitle("a_{L}")
      elif 'a2' in spline_name:
        plot.SetYTitle("a_{R}")
      frameformat(plot)
      mean_spline.plotOn(plot, r.RooFit.Range("fullRange",r.kFALSE))
      min_max1 = [ii+jj for ii,jj in zip(err_,ori_pt)]
      min_max2 = [jj-ii for ii,jj in zip(err_,ori_pt)]
      plot.SetAxisRange(min(min_max2)*0.8, max(min_max1)*1.2, "Y")
      plot.SetAxisRange(masspts[0]-5, masspts[-1]+5, "X")
      canv = newCan()
      plot.Draw()
      #gr.SetMarkerSize(10)
      gr.SetMarkerStyle(8)
      gr.Draw('PSAME')
      lumi, cmstxt, cattxt, pretxt = extraText(canv, cat, prod)
      lumi.Draw('Same')
      cmstxt.Draw('Same')
      cattxt.Draw('Same')
      pretxt.Draw('Same')
      canv.Update()
      canv.Update()
      canv.SaveAs('Graphs/splines_cbe/params/'+spline_name+'.png')
print totalnu
