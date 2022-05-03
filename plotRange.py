import ROOT
import math
#ROOT.gSystem.Load("/afs/crc.nd.edu/user/k/kho2/CMSSW_10_2_13/lib/slc7_amd64_gcc700/libHiggsAnalysisCombinedLimit.so")
ROOT.gSystem.Load("/afs/crc.nd.edu/user/k/kho2/CMSSW_10_2_13/lib/slc7_amd64_gcc700/libHiggsAnalysisGBRLikelihood.so")
ROOT.gROOT.SetBatch(True)

cat = 'ggcat2'
datafile2 = ROOT.TFile("/afs/crc.nd.edu/user/k/kho2/CMSSW_10_2_13/src/flashggFinalFit/Background/CMS_Hemu_13TeV_multipdf_wide.root")
inWS2 = datafile2.Get("multipdf")
db2 = inWS2.data("Data_13TeV_"+cat)#.Clone()
pdfb2 = inWS2.pdf('env_pdf_'+cat+'_bern3') 

datafile = ROOT.TFile("/afs/crc.nd.edu/user/k/kho2/CMSSW_10_2_13/src/flashggFinalFit/Background/CMS_Hemu_13TeV_multipdf_narrow.root")
inWS = datafile.Get("multipdf")
db = inWS.data("Data_13TeV_"+cat)#.Clone()
pdfb = inWS.pdf('env_pdf_'+cat+'_bern3') 

mass2 = inWS2.var("CMS_emu_Mass")
mass2.setBins(60)
hmass = 160
mass2.setRange("higgsRange2",110.,hmass)
mass2.setRange("higgsRange3",110.,170)
mass2.setRange("R1",110.,115.)
mass2.setRange("R2",135.,160)
mass2.setRange("R4",135.,170)

mass = inWS.var("CMS_emu_Mass")
mass.setBins(60)
hmass = 160
mass.setRange("higgsRange2",110.,hmass)
mass.setRange("higgsRange3",110.,170)
mass.setRange("R1",110.,115.)
mass.setRange("R2",135.,160)
mass.setRange("R4",135.,170)

canvas = ROOT.TCanvas("canvas","",0,0,800,800)
frame = mass.frame(ROOT.RooFit.Title(" "), ROOT.RooFit.Range("higgsRange3"))
pdfb.plotOn(frame, ROOT.RooFit.Normalization(db.sumEntries("1", "higgsRange2"), ROOT.RooAbsReal.NumEvent), ROOT.RooFit.Range("higgsRange2"),ROOT.RooFit.Name("110,160"))

frame2 = mass2.frame(ROOT.RooFit.Title(cat), ROOT.RooFit.Range("higgsRange3"))
db2.plotOn(frame2,  ROOT.RooFit.CutRange("R1,R4"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
pdfb2.plotOn(frame2, ROOT.RooFit.Normalization(db2.sumEntries("1", "higgsRange3"), ROOT.RooAbsReal.NumEvent), ROOT.RooFit.Range("higgsRange3"),  ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.Name("110,170"))

leg1 = ROOT.TLegend(0.65,0.73,0.86,0.87)
leg1.AddEntry(frame.findObject("110,160"), "110,160", "L")
leg1.AddEntry(frame2.findObject("110,170"), "110,170", "L")
frame2.Draw()
frame.Draw('same')
leg1.Draw('same')



print(frame.chiSquare(1))
canvas.SaveAs('test1.png')

