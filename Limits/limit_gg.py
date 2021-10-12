from ROOT import TFile, TPave, TH2F, TLatex, TCanvas, gStyle, TGraphAsymmErrors, TLine, TLegend, TLatex, TLegendEntry,gROOT
from array import array
import math
def ComputeSumYLimit(BranchingRatio = 0.1):
  #Higgs Mass
  mh = 125
  #Higgs Width at 125 GeV is 4.1 MeV
  gammah = 4.1/1000
  # Magic Formulas, #26 and #27 from
  # BR(h->mutau) = Width(h->mutau) / ( Width(h->mutau) + SM_Higgs_Width)
  # Width(h->mutau) = mh / 8Pi * (|Y(mutau)|**2 + |Y(taumu)|**2)
  # (|Y(mutau)|**2 + |Y(taumu)|**2) = (BR * SM_Higgs_Width) / ()*(1- BR)
  LimitOnSumY = 8 * math.pi / mh * BranchingRatio * gammah / (1 - BranchingRatio)
  return LimitOnSumY

gROOT.SetBatch(True)
#catnames = ["Combined","vbfcat1","ggcat0"]
catnames = ["ggcat","ggcat4","ggcat3","ggcat2","ggcat1","ggcat0"]
ncats = len(catnames)
limits = []
for c in catnames: 
  inFile = TFile("higgsCombineTest.AsymptoticLimits." + c + ".mH125.root", "READONLY");
  limitTree = inFile.Get("limit")
  nentries = limitTree.GetEntries()
  limits.append([])
  for k in range(nentries):
    limitTree.GetEntry(k)
    limits[-1].append(limitTree.limit*1e2)
print limits
print "==============================="
print "         SUMMARY TABLE         "
print "==============================="
print " Expected 95%% CL limits on BR "
print "==============================="

for c in catnames:
  print "\t %s"%c,
print 
for l in limits:
  print "\t < %2.4f"%l[2],
print
print "==============================="
print "          YUKAWA LIMIT         "
print "==============================="

yukawa = math.sqrt(ComputeSumYLimit(limits[-1][2]/100.))
print "   Yukawa limit: < %2.6f   "%(yukawa)

gStyle.SetOptFit(1)
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

PLOTLIMIT = TCanvas("PLOTLIMIT", "BEST FIT", 800, 800)
PLOTLIMIT.Range(-1.298202, -1.436207, 2.706292, 7.434483)
PLOTLIMIT.SetFillColor(0)
PLOTLIMIT.SetBorderMode(0)
PLOTLIMIT.SetBorderSize(2)
PLOTLIMIT.SetTickx(1)
PLOTLIMIT.SetTicky(1)
PLOTLIMIT.SetLeftMargin(0.2)
PLOTLIMIT.SetRightMargin(0.05)
PLOTLIMIT.SetTopMargin(0.12)
PLOTLIMIT.SetBottomMargin(0.12)
PLOTLIMIT.SetFrameFillStyle(0)
PLOTLIMIT.SetFrameLineWidth(3)
PLOTLIMIT.SetFrameBorderMode(0)
PLOTLIMIT.SetFrameFillStyle(0)
PLOTLIMIT.SetFrameLineWidth(4)
PLOTLIMIT.SetFrameBorderMode(0)

#for i in range(len(limits)):
#  limits[i][0] = -limits[i][0]+limits[i][2] 
#  limits[i][1] = -limits[i][1]+limits[i][2] 
#  limits[i][3] = limits[i][3]-limits[i][2] 
#  limits[i][4] = limits[i][4]-limits[i][2] 
#print limits
channels = []
for i in range(ncats):
  if i == 0:
    channels.append("#splitline{Combined}{#splitline{ggcat}{#scale[0.8]{(%1.2f #upoint 10^{-4})}}}"%(limits[i][2]))
  else:
    channels.append("#splitline{%s}{#scale[0.8]{(%1.2f #upoint 10^{-4})}}"%(catnames[i], limits[i][2]))
print channels
PLOTLIMIT.cd()

h = TH2F("h", "test", 1, -5, 25, ncats, 0, ncats)
for ch in channels:
  h.Fill(1, ch, 0)
h.SetXTitle("95% CL limit on #bf{#it{#Beta}}(H#rightarrow e#mu), 10^{-4}")
h.GetXaxis().SetLabelSize(0.04)
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.GetYaxis().CenterLabels()
h.Draw()
paves = []
for i in range(ncats):
  pave = TPave(limits[i][0], i + 0.75, limits[i][4], i + 0.25, 4, "br");
  pave.Draw()
  pave.SetBorderSize(0)
  pave.SetFillColor(800)
  pave2 = TPave(limits[i][1], i + 0.75, limits[i][3], i + 0.25, 4, "br");
  pave2.Draw()
  pave2.SetBorderSize(0)
  pave2.SetFillColor(417)
  paves.append(pave)
  paves.append(pave2)
MEDIANplot, erry, y = array('f'), array('f'), array('f')

for i in range(ncats):
  MEDIANplot.append(limits[i][2])
  y.append(0.5+i)
  erry.append(0)

print MEDIANplot
print y
GRAPHMEDIAN = TGraphAsymmErrors(ncats, MEDIANplot, y);
#GRAPHMEDIAN.SetLineColor(600) 
GRAPHMEDIAN.SetMarkerStyle(5) 
#GRAPHMEDIAN.SetMarkerColor(602) 
GRAPHMEDIAN.SetMarkerSize(.6)
GRAPHMEDIAN.SetLineWidth(1)
GRAPHMEDIAN.Draw("P,sames")

lineV = TLine(0, 0, 0, ncats)
lineV.SetLineStyle(3)
lineV.SetLineColor(920)
lineV.Draw()

lineH = TLine(-5, 1, 25, 1)
lineH.SetLineWidth(3)
lineH.Draw()

leg = TLegend(0.645, 0.60, 0.98, 0.80, "", "brNDC")
leg.SetTextFont(62)
leg.SetTextSize(0.02721088)
leg.SetFillColor(0)
leg.SetFillStyle(0)
leg.SetBorderSize(0)

entry = TLegendEntry()
leg.SetHeader("Limit Plot")
entry = leg.AddEntry(GRAPHMEDIAN, "Median expected", "p")
entry = leg.AddEntry("NULL", "68% expected", "f")
entry.SetFillColor(417)
entry.SetFillStyle(1001)
entry.SetLineStyle(1)
entry = leg.AddEntry("NULL", "95% expected", "f")
entry.SetFillColor(800)
entry.SetFillStyle(1001)
entry.SetLineStyle(1)
leg.Draw()

latex = TLatex()
latex.SetNDC()
latex.SetTextSize(0.04)
latex.SetTextSize(0.04 * 0.80)
latex.SetTextFont(42)
latex.SetTextAlign(31)
latex.DrawLatex(0.95, 0.9, "137.2 fb^{-1} (13 TeV)")
latex.SetTextSize(0.04)
latex.SetTextFont(61)
latex.SetTextAlign(11)
latex.DrawLatex(0.21, 0.9, "CMS")
latex.SetTextFont(52)
latex.DrawLatex(0.3, 0.9, "Preliminary")

PLOTLIMIT.SaveAs("Comb_Limits_pow1.png")

