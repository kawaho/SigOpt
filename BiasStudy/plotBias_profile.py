import ROOT, re, os
from datetime import datetime
from runBiasStudy_condor_profile import cats, orders 
if not os.path.exists('BiasPlot'):
  os.makedirs('BiasPlot')
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so");
ROOT.gROOT.SetBatch(True)

bkgfile = ROOT.TFile('../Workspaces/CMS_Hemu_13TeV_multipdf_v2025_profile.root')
bkgWS = bkgfile.Get('multipdf')
#outRoot = ROOT.TFile("hist_bias_study.root","RECREATE")
outfile = open('BiasStudy_profile.txt','a', buffering=0) 
outfile.write("%s\n"%str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
for cat,order in zip(cats,orders):
  multipdf = bkgWS.pdf('CMS_hemu_'+cat+'_13TeV_bkgshape')
  numofpdfcat = multipdf.getNumPdfs()
  print "Total number of cats: ", numofpdfcat
  biasTable = {}
  for i in range(numofpdfcat):
    pdfname = multipdf.getPdf(i).GetName()
    split_string = pdfname.split("_")
    biasTable[split_string[3]] = [[True],[]]
    if 'bern' in pdfname and not 'bern%i'%order[0] in pdfname: continue
    if 'exp' in pdfname and not 'exp%i'%order[1] in pdfname: continue
    #if 'lau' in pdfname and not 'lau%i'%order[2] in pdfname: continue
    if 'pow' in pdfname and not 'pow%i'%order[2] in pdfname: continue
    print "Scanning fitDiagnosticsGen"+split_string[3]+"Fit.root"
    file_ = ROOT.TFile("fitDiagnosticsGen"+split_string[3]+"Fit"+cat+"_125_profile.root")
    tree = file_.Get("tree_fit_sb")
    if not tree: 
      print "Fit Failed: Gen"+split_string[3]+"Fit"
      outfile.write(cat + " " + split_string[3] + " " +" is missing\n")
      continue
    tree.Draw("(r-1)/(0.5*(rHiErr+rLoErr))>>h(100,-5,5)")
    h = ROOT.gPad.GetPrimitive("h")
    h.Fit("gaus")
    try:
      h_mean = h.GetFunction("gaus").GetParameter(1)
      h_sigma = h.GetFunction("gaus").GetParameter(2)
    except:
      h_mean = h.GetMean()
      h_sigma = h.GetStdDev()
    h_mean_num = h.GetMean()
    h_sigma_num = h.GetStdDev()
    h.SetTitle(cat+" Gen "+split_string[3]+" - Fit ;Pull;");
    h.SetName('%sGen%sFit'%(cat,split_string[3]))
    ROOT.gPad.SaveAs('BiasPlot/%sGen%sFit.png'%(cat,split_string[3]))
    print "Mean of bias of "+cat+" for pdf "+split_string[3], h_mean
    print "Standard Deviation of bias", h_sigma
    outfile.write(cat + " " + split_string[3] +" "+ str(round(h_mean*100,3)) + " " + str(round(h_sigma,3)) + "\n")
    outfile.write(cat + " " + split_string[3] +" "+ str(round(h_mean_num*100,3)) + " " + str(round(h_sigma_num,3)) + "\n")
    file_.Close()
outfile.close()
