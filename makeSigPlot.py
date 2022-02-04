import ROOT
ROOT.gROOT.SetBatch(True)
list_of_hist = []
outfile = ROOT.TFile("Signal.root", "recreate")
for cat in ['ggcat0','ggcat1','ggcat2','vbfcat0','vbfcat1']:
  infile = ROOT.TFile("Workspaces/workspace_sig_"+cat+".root")
  ws = infile.Get("w_13TeV")
  mass = ws.var("CMS_emu_Mass")
  pdf_gg = ws.function(cat+"_ggH_pdf")
  pdf_gg_norm = ws.var(cat+"_ggH_pdf_norm").getVal()
  hist_gg = pdf_gg.createHistogram(cat+'_gg', mass, ROOT.RooFit.Binning(25, 110, 135))
  hist_gg.Scale(pdf_gg_norm)
  
  pdf_vbf = ws.function(cat+"_qqH_pdf")
  pdf_vbf_norm = ws.var(cat+"_qqH_pdf_norm").getVal()
  hist_vbf = pdf_vbf.createHistogram(cat+'_vbf', mass, ROOT.RooFit.Binning(25, 110, 135))
  hist_vbf.Scale(pdf_vbf_norm)

  hist_gg.Add(hist_vbf)
#  hist_gg.Scale(pdf_vbf_norm+pdf_gg_norm)
  hist_gg.SetName(cat)  
  
  outfile.cd()
  hist_gg.Write()
