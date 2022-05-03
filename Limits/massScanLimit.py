import ROOT as r
from array import array
limits = {}
for i in range(120, 131):
  inFile = r.TFile("higgsCombineTest.AsymptoticLimits.mH%i.root"%i, "READONLY")
  limitTree = inFile.Get("limit")
  nentries = limitTree.GetEntries()
  limits[i] = []
  for k in range(nentries):
    limitTree.GetEntry(k)
    limits[i].append(limitTree.limit*10)

limitcheck = [(i, limits[i][2]) for i in limits]
print limitcheck
r.gROOT.SetBatch(True)

r.gStyle.SetOptFit(1)
r.gStyle.SetOptStat(0)
r.gStyle.SetOptTitle(0)

PLOTLIMIT = r.TCanvas("PLOTLIMIT", "BEST FIT", 800, 800)
PLOTLIMIT.SetFillColor(0)
PLOTLIMIT.SetBorderMode(0)
PLOTLIMIT.SetBorderSize(2)
PLOTLIMIT.SetTickx(1)
PLOTLIMIT.SetTicky(1)
PLOTLIMIT.SetLeftMargin(0.12)
PLOTLIMIT.SetRightMargin(0.05)
PLOTLIMIT.SetTopMargin(0.12)
PLOTLIMIT.SetBottomMargin(0.12)
PLOTLIMIT.SetFrameFillStyle(0)
PLOTLIMIT.SetFrameBorderMode(0)
PLOTLIMIT.SetFrameFillStyle(0)
PLOTLIMIT.SetFrameLineWidth(3)
PLOTLIMIT.SetFrameBorderMode(0)
PLOTLIMIT.cd()

fullspace = r.TH2D("fullspace","fullspace",25,115,140,10,2,12)
#fullspace = r.TH2D("fullspace","fullspace",10,120,130,10,2,12)
fullspace.Draw()
fullspace.GetXaxis().SetTitle("m_{H} [GeV]")
fullspace.GetYaxis().SetTitle("95% CL limit on #bf{#it{#Beta}}(H#rightarrow e#mu), 10^{-5}")
fullspace.GetXaxis().SetTitleOffset(1.5)
fullspace.GetYaxis().SetTitleOffset(1.5)

xf =  range(120, 131)
ytop =  [limits[i][4] for i in range(120, 131)]
ybottom = [limits[i][0] for i in range(120, 131)]
N = len(range(120, 131))
grshade = r.TGraph(2*N);
for j in range(N):
  grshade.SetPoint(j,xf[j],ytop[j]);
  grshade.SetPoint(N+j,xf[N-j-1],ybottom[N-j-1]);

grshade.SetFillColor(800)
grshade.Draw('FL')
grshade.SetLineWidth(0)

ytop2 =  [limits[i][3] for i in range(120, 131)]
ybottom2 = [limits[i][1] for i in range(120, 131)]

gr2 = r.TGraph(2*N);
for j in range(N):
  gr2.SetPoint(j,xf[j],ytop2[j]);
  gr2.SetPoint(N+j,xf[N-j-1],ybottom2[N-j-1]);

gr2.SetFillColor(417)
gr2.Draw('FL,SAME')
gr2.SetLineWidth(0)


y3 =  [limits[i][2] for i in range(120, 131)]

gr3 = r.TGraph(N);
for j in range(N):
  gr3.SetPoint(j,xf[j],y3[j]);

#gr3.SetMarkerStyle(8)
gr3.SetLineStyle(2)
gr3.Draw('SAME')

y4 =  [limits[i][-1] for i in range(120, 131)]

gr4 = r.TGraph(N);
for j in range(N):
  gr4.SetPoint(j,xf[j],y4[j]);

gr4.SetMarkerStyle(8)
#gr4.SetLineStyle(2)
gr4.Draw('SAME,LP')


latex = r.TLatex()
latex.SetNDC()
latex.SetTextSize(0.04)
latex.SetTextSize(0.04 * 0.80)
latex.SetTextFont(42)
latex.SetTextAlign(31)
latex.DrawLatex(0.95, 0.9, "138 fb^{-1} (13 TeV)")
latex.SetTextSize(0.04)
latex.SetTextFont(61)
latex.SetTextAlign(11)
latex.DrawLatex(0.12, 0.9, "CMS")
latex.SetTextFont(52)
latex.DrawLatex(0.21, 0.9, "Preliminary")

leg = r.TLegend(0.645, 0.60, 0.98, 0.80, "", "brNDC")
leg.SetTextFont(62)
leg.SetTextSize(0.02721088)
leg.SetFillColor(0)
leg.SetFillStyle(0)
leg.SetBorderSize(0)

entry = r.TLegendEntry()
leg.SetHeader("Limit Plot")
entry = leg.AddEntry(gr3, "Median expected", "l")
entry = leg.AddEntry(gr4, "Observed", "pl")
entry = leg.AddEntry("NULL", "68% expected", "f")
entry.SetFillColor(417)
entry.SetFillStyle(1001)
entry.SetLineStyle(1)
entry = leg.AddEntry("NULL", "95% expected", "f")
entry.SetFillColor(800)
entry.SetFillStyle(1001)
entry.SetLineStyle(1)
leg.Draw()

PLOTLIMIT.RedrawAxis()
PLOTLIMIT.SaveAs('massscan.pdf')
