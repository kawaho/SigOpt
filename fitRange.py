import ROOT
import math
#ROOT.gSystem.Load("/afs/crc.nd.edu/user/k/kho2/CMSSW_10_2_13/lib/slc7_amd64_gcc700/libHiggsAnalysisCombinedLimit.so")
ROOT.gSystem.Load("/afs/crc.nd.edu/user/k/kho2/CMSSW_10_2_13/lib/slc7_amd64_gcc700/libHiggsAnalysisGBRLikelihood.so")
ROOT.gROOT.SetBatch(True)
datafile = ROOT.TFile("dataws_final.root")
#Fit data
inWS = datafile.Get("CMS_emu_workspace")
mass = inWS.var("CMS_emu_Mass")
cat = 'ggcat0'
db = inWS.data("Data_13TeV_"+cat)#.Clone()
mass.setBins(50)
hmass = 160
mass.setRange("higgsRange2",110.,hmass)
mass.setRange("R1",110.,115.)
mass.setRange("R2",135.,hmass)
coeffList = ROOT.RooArgList()
order = 1
allvars = []
for i in range(order):
  param = ROOT.RooRealVar("pdf_{}_bern{}_p{}".format(cat,order,i), "pdf_{}_bern{}_p{}".format(cat,order,i), 0.1*(i+1), 0., 5.)
  coeffList.add(param)
  allvars.append([param])  

db.reduce(ROOT.RooArgSet(mass), "(CMS_emu_Mass < %f) & (CMS_emu_Mass > 110)"%hmass)

pdfb = ROOT.RooBernsteinFast(order)("pdf_{}_exp1".format(cat), "pdf_{}_exp1".format(cat), mass, coeffList) 

fitResultb = pdfb.fitTo(db, ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Save(1), ROOT.RooFit.SumW2Error(ROOT.kTRUE))#, ROOT.RooFit.Range("higgsRange2"))

canvas = ROOT.TCanvas("canvas","",0,0,800,800)
frame = mass.frame(ROOT.RooFit.Range("higgsRange2"))
db.plotOn(frame,  ROOT.RooFit.CutRange("R1,R2"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
pdfb.plotOn(frame, ROOT.RooFit.Normalization(db.sumEntries("1", "higgsRange2"), ROOT.RooAbsReal.NumEvent), ROOT.RooFit.NormRange("higgsRange2"), ROOT.RooFit.Range("higgsRange2"))

#coeffList2 = ROOT.RooArgList()
#for i in range(order):
#  param2 = ROOT.RooRealVar("pdf_{}_bern{}_p{}".format(cat,order,i), "pdf_{}_bern{}_p{}".format(cat,order,i), 0.1*(i+1), 0., 5.)
#  coeffList2.add(param2)
#  allvars.append([param2])  
#db.reduce(ROOT.RooArgSet(mass), "(CMS_emu_Mass < 160) & (CMS_emu_Mass > 110)")
#pdfb2 = ROOT.RooBernsteinFast(order)("pdf_{}_exp1".format(cat), "pdf_{}_exp1".format(cat), mass, coeffList2) 
#fitResultb = pdfb2.fitTo(db, ROOT.RooFit.Minimizer("Minuit2","minimize"), ROOT.RooFit.Save(1), ROOT.RooFit.SumW2Error(ROOT.kTRUE))#, ROOT.RooFit.Range("higgsRange2"))
#pdfb2.plotOn(frame, ROOT.RooFit.Normalization(db.sumEntries("1", "higgsRange2"), ROOT.RooAbsReal.NumEvent), ROOT.RooFit.NormRange("higgsRange2"), ROOT.RooFit.Range("higgsRange2"),ROOT.RooFit.LineColor(ROOT.kRed))

frame.Draw()
print(frame.chiSquare(1))
canvas.SaveAs('test1.png')

