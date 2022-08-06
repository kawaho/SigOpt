import ROOT as r
import numpy as np
import pandas as pd
import math
from SplinesBuilder_gaus import revRecur, calRecur, orders
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
for c_index, cat in enumerate(['ggHcat0','ggHcat1', 'ggHcat2', 'ggHcat3', 'VBFcat0', 'VBFcat1', 'VBFcat2']):
  inws = r.TFile('Workspaces/workspace_sig_%s_gaus.root'%cat).Get('w_13TeV')
  mh = inws.var('MH')
  mh.setRange("fullRange", masspts[0], masspts[-1])
  emumass = inws.var('CMS_emu_Mass')
  emumass.setBins(50)
  for prod in ['ggH', 'qqH']:
    pdf = inws.pdf('%s_%s_pdf'%(cat,prod))
    plot = emumass.frame(100,170,70)
    frameformat(plot)
    canv = newCan()
    for mp, cr in zip(masspts, [r.kRed, r.kBlue, r.kGreen, r.kMagenta, r.kYellow, r.kOrange, r.kCyan]): 
      dh = inws.data('data_%s_%s_%s'%(cat,str(int(mp)),prod))
      mh.setVal(mp)
      dh.plotOn(plot, r.RooFit.Binning(90,90,180), r.RooFit.LineColor(cr), r.RooFit.MarkerColor(cr))
      pdf.plotOn(plot, r.RooFit.Normalization(inws.function('%s_%s_pdf_norm'%(cat,prod)).getVal()*100, r.RooAbsReal.NumEvent), r.RooFit.LineColor(cr), r.RooFit.LineWidth(2))
      #pdf.plotOn(plot, r.RooFit.Normalization(inws.function('%s_%s_pdf_norm'%(cat,prod)).getVal()*100, r.RooAbsReal.NumEvent), r.RooFit.LineColor(cr), r.RooFit.LineWidth(2))
#      print dh.sumEntries(), inws.function('%s_%s_pdf_norm'%(cat,prod)).getVal()
#      totalnu[mp] += dh.sumEntries()
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
    canv.SaveAs('Graphs/splines_gaus/pdfs/%s_%s_pdf.png'%(cat,prod))
    err_ref = {}
    for ii in masspts:    
      inws_err = r.TFile('Workspaces/workspace_sig_%s_%i_gaus.root'%(cat,int(ii))).Get('w_13TeV')
      order_mean = [inws_err.var('%s_%i_%s_mean_gaus_nom_order%i'%(cat,int(ii),prod,norder)).getValV() for norder in range(orders[prod][c_index])]
      order_sigma = [inws_err.var('%s_%i_%s_sigma_gaus_nom_order%i'%(cat,int(ii),prod,norder)).getValV() for norder in range(orders[prod][c_index])] 
      order_frac = [inws_err.var('%s_%i_%s_sigfrac_order%i'%(cat,int(ii),prod,norder)).getValV() for norder in range(orders[prod][c_index]-1)]
      order_frac.append(1)

      order_mean_err= [inws_err.var('%s_%i_%s_mean_gaus_nom_order%i'%(cat,int(ii),prod,norder)).getError() for norder in range(orders[prod][c_index])]
      order_sigma_err = [inws_err.var('%s_%i_%s_sigma_gaus_nom_order%i'%(cat,int(ii),prod,norder)).getError() for norder in range(orders[prod][c_index])] 
      norm_err = inws_err.var('%s_%i_%s_pdf_norm'%(cat,int(ii),prod)).getError()
      order_frac_err = [inws_err.var('%s_%i_%s_sigfrac_order%i'%(cat,int(ii),prod,norder)).getError() for norder in range(orders[prod][c_index]-1)]
      order_frac_err.append(0)

      order_frac, order_mean, order_sigma, order_frac_err, order_mean_err, order_sigma_err = zip(*sorted(zip(order_frac, order_mean, order_sigma, order_frac_err, order_mean_err, order_sigma_err), key=lambda pair: pair[2])) 

      if order_frac[0]==1: 
        order_frac, order_mean, order_sigma, order_frac_err, order_mean_err, order_sigma_err = zip(*sorted(zip(order_frac, order_mean, order_sigma, order_frac_err, order_mean_err, order_sigma_err), key=lambda pair: pair[2], reverse=True)) 
     
      print(cat,prod,order_frac)
      print('1',prod,order_frac_err)
      if orders[prod][c_index]==3: 
        order_frac_err = [order_frac_err[0],math.sqrt( (order_frac_err[2]/(1-order_frac[0]))**2+(order_frac_err[0]*order_frac[2]/(1-order_frac[0])**2)**2 ) ,0]
      print(cat,prod,order_frac_err)
      err_ref[ii] = {'sigfrac':order_frac_err, 'mean':order_mean_err, 'sigma':order_sigma_err, 'norm':norm_err}

    list_of_parameters = [f for norder in range(orders[prod][c_index]) for f in ('%s_%s_sigfrac_gaus_order%i'%(cat,prod,norder), '%s_%s_sigma_gaus_nom_order%i'%(cat,prod,norder), '%s_%s_mean_gaus_nom_order%i'%(cat,prod,norder))] + ['%s_%s_pdf_norm'%(cat,prod)]

    for spline_name in list_of_parameters:
      if spline_name == '%s_%s_sigfrac_gaus_order%i'%(cat,prod,orders[prod][c_index]-1): continue
      mean_spline = inws.function(spline_name)
      
      ori_pt = []
      err_ = []
      for mt in masspts:
        mh.setVal(mt)
        ori_pt.append(mean_spline.getVal()) 
        if 'norm' in spline_name:
          err_.append(err_ref[mt]['norm'])
        else:
          err_.append(err_ref[mt][spline_name.split('_')[2]][int(spline_name[-1])])
      #gr = r.TGraphErrors(len(masspts),masspts,np.array(ori_pt))
      gr = r.TGraphErrors(len(masspts),masspts,np.array(ori_pt),r.nullptr,np.array(err_))
      if 'mean' in spline_name: 
        gr.Fit('pol1') 
      else:   
        gr.Fit('pol2') 
      plot = mh.frame(r.RooFit.Title(" "))
     # plot.SetYTitle(spline_name)
      if 'norm' in spline_name:
        plot.SetYTitle("normalization")
      else:
        print(spline_name)
        plot.SetYTitle(spline_name.split('_')[2]+spline_name[-1])
     # elif 'mean' in spline_name:
     #   plot.SetYTitle("#mu")
     # elif 'n1' in spline_name:
     #   plot.SetYTitle("n_{L}")
     # elif 'a1' in spline_name:
     #   plot.SetYTitle("a_{L}")
     # elif 'a2' in spline_name:
     #   plot.SetYTitle("a_{R}")
      frameformat(plot)
      #mean_spline.plotOn(plot, r.RooFit.Range("fullRange",r.kFALSE))
      plot.SetAxisRange(min(np.array(ori_pt)-np.array(err_))*0.8, max(np.array(ori_pt)+np.array(err_))*1.2, "Y")
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
      canv.SaveAs('Graphs/splines_gaus/params/'+spline_name+'.png')
#print totalnu
