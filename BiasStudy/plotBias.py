import ROOT, re, os
from datetime import datetime
from runBiasStudy_condor import cats, orders 
if not os.path.exists('BiasPlot'):
  os.makedirs('BiasPlot')
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so");
ROOT.gROOT.SetBatch(True)

bkgfile = ROOT.TFile('../Workspaces/CMS_Hemu_13TeV_multipdf.root')
bkgWS = bkgfile.Get('multipdf')
#outRoot = ROOT.TFile("hist_bias_study.root","RECREATE")
for cat,order in zip(cats,orders):
  if cat!='VBFcat0': continue 
  outfile = open(cat+'BiasStudy.txt','a', buffering=0) 
  outfile.write("%s\n"%str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
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
    for j in range(numofpdfcat):
      pdfname2 = multipdf.getPdf(j).GetName()
      split_string2 = pdfname2.split("_")
      print "Scanning fitDiagnosticsGen"+split_string[3]+"Fit"+split_string2[3]+".root"
      file_ = ROOT.TFile("fitDiagnosticsGen"+split_string[3]+"Fit"+split_string2[3]+cat+"_125.root")
      tree = file_.Get("tree_fit_sb")
      if not tree: 
        print "Fit Failed: Gen"+split_string[3]+"Fit"+split_string2[3]
        outfile.write(cat + " " + split_string[3] + " " + split_string2[3] +" is missing\n")
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
      h.SetTitle(cat+" Gen "+split_string[3]+" - Fit "+split_string2[3]+";Pull;");
      h.SetName('%sGen%sFit%s'%(cat,split_string[3],split_string2[3]))
      ROOT.gPad.SaveAs('BiasPlot/%sGen%sFit%s.png'%(cat,split_string[3],split_string2[3]))
      print "Mean of bias of "+cat+" for pdf "+split_string[3]+" generated with pdf "+split_string2[3], h_mean
      print "Standard Deviation of bias", h_sigma
      outfile.write(cat + " " + split_string[3] + " " + split_string2[3] +" "+ str(round(h_mean*100,3)) + " " + str(round(h_sigma,3)) + "\n")
      #if abs(h.GetMean()*100) > 14:
      #  biasTable[split_string2[3]][0] = False
      #else:
      #  biasTable[split_string2[3]][1].append(h.GetMean()*100)
      file_.Close()
  #minBias = 20
  #pdfname = ''
  #order = 10
  #for key, value in biasTable.items():
  #  if value[0] == False: 
  #    continue
  #  value[1].sort()
  #  if int(re.findall("\d+", key)[0]) < order:
  #    print re.findall("\d+", key)[0]
  #    minBias = value[1][0]
  #    pdfname = key
  #    order = int(re.findall("\d+", key)[0])
  #  elif re.findall("\d+", key)[0] == order:
  #    if value[1][0] < minBias:
  #      minBias = value[1][0]
  #      pdfname = key
  #      order = int(re.findall("\d+", key)[0])
  #outfile.write("----Final Choice----\n")
  #outfile.write("{}        {}\n".format(pdfname,round(minBias,3)))
  outfile.close()
#outRoot.Close()
