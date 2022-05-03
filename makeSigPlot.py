import ROOT
ROOT.gROOT.SetBatch(True)
list_of_hist = []
outfile = ROOT.TFile("Signal.root", "recreate")
for cat in ['ggcat0','ggcat1','ggcat2','ggcat3','vbfcat0','vbfcat1']:
  infile = ROOT.TFile("Workspaces/workspace_sig_"+cat+"_125.root")
  ws = infile.Get("w_13TeV")
  mass = ws.var("CMS_emu_Mass")
  pdf_gg = ws.function(cat+"_125_ggH_pdf")
  pdf_gg_norm = ws.var(cat+"_125_ggH_pdf_norm").getVal()
  hist_gg = pdf_gg.createHistogram(cat+'_gg', mass, ROOT.RooFit.Binning(25, 110, 135))
  hist_gg.Scale(pdf_gg_norm)
  print(hist_gg.Integral()) 
  pdf_vbf = ws.function(cat+"_125_qqH_pdf")
  pdf_vbf_norm = ws.var(cat+"_125_qqH_pdf_norm").getVal()
  hist_vbf = pdf_vbf.createHistogram(cat+'_vbf', mass, ROOT.RooFit.Binning(25, 110, 135))
  hist_vbf.Scale(pdf_vbf_norm)
  print(hist_vbf.Integral()) 

  hist_gg.Add(hist_vbf)
  print("hi",cat,hist_gg.Integral()) 
  hist_gg.SetName(cat)  
  outfile.cd()
  hist_gg.Write()
