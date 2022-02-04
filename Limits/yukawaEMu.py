import ROOT as r
import numpy as np
import math
from array import array

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

r.gROOT.SetBatch(True)

r.gStyle.SetOptFit(1)
r.gStyle.SetOptStat(0)
r.gStyle.SetOptTitle(0)

PLOTLIMIT = r.TCanvas("PLOTLIMIT", "BEST FIT", 800, 800)
#PLOTLIMIT.Range(-1.298202, -1.436207, 2.706292, 7.434483)
PLOTLIMIT.SetLogy(True)
PLOTLIMIT.SetLogx(True)
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

ymin, ymax = 1e-7, 1e-3
fullspace = r.TH2D("fullspace","fullspace",12,ymin,ymax,12,ymin,ymax)
fullspace.Draw()
fullspace.GetXaxis().SetTitle("|Y_{e#mu}|")
fullspace.GetYaxis().SetTitle("|Y_{#mu e}|")
fullspace.GetXaxis().SetTitleOffset(1.5)
fullspace.GetYaxis().SetTitleOffset(1.5)

#Expected Limit
inFile = r.TFile("higgsCombineTest.AsymptoticLimits.Combined.mH125.root", "READONLY");
limitTree = inFile.Get("limit")
nentries = limitTree.GetEntries()
YLimitExpect = []
for k in range(nentries):
  limitTree.GetEntry(k)
  YLimitExpect.append(ComputeSumYLimit(limitTree.limit*10**-2))

ExpectedPlusTwoSigmaLimitCombined = r.TF1("ExpectedPlusTwoSigmaLimitCombined","sqrt([0]-x*x)",ymin,math.sqrt(YLimitExpect[4]))
ExpectedPlusTwoSigmaLimitCombined.SetParameter(0,YLimitExpect[4])

ExpectedMinusTwoSigmaLimitCombined = r.TF1("ExpectedMinusTwoSigmaLimitCombined","sqrt([0]-x*x)",ymin,math.sqrt(YLimitExpect[0]))
ExpectedMinusTwoSigmaLimitCombined.SetParameter(0,YLimitExpect[0])

npf = 100000
dxf = (ymax-ymin)/(npf-1)

xf =  [ymin + dxf*i for i in range(npf)]
xf += [ymax - dxf*i for i in range(npf)]
yf =  [ExpectedPlusTwoSigmaLimitCombined.Eval(xf[i]) for i in range(npf)]
yf += [ExpectedMinusTwoSigmaLimitCombined.Eval(xf[npf+i]) for i in range(npf)]
xf.append(xf[0])
yf.append(yf[0])

xf = array('f', xf)
yf = array('f', yf)
grf2 = r.TGraph(2*npf+1,xf,yf)
grf2.SetFillColor(r.kYellow-7) #kyellow
grf2.SetLineWidth(0)
grf2.Draw("f")

ExpectedPlusOneSigmaLimitCombined = r.TF1("ExpectedPlusOneSigmaLimitCombined","sqrt([0]-x*x)",ymin,math.sqrt(YLimitExpect[3]))
ExpectedPlusOneSigmaLimitCombined.SetParameter(0,YLimitExpect[3])

ExpectedMinusOneSigmaLimitCombined = r.TF1("ExpectedMinusOneSigmaLimitCombined","sqrt([0]-x*x)",ymin,math.sqrt(YLimitExpect[1]))
ExpectedMinusOneSigmaLimitCombined.SetParameter(0,YLimitExpect[1])

yf =  [ExpectedPlusOneSigmaLimitCombined.Eval(xf[i]) for i in range(npf)]
yf += [ExpectedMinusOneSigmaLimitCombined.Eval(xf[npf+i]) for i in range(npf)]
yf.append(yf[0])

yf = array('f', yf)
grf1 = r.TGraph(2*npf+1,xf,yf)
grf1.SetFillColor(r.kGreen+1) #kyellow
grf1.SetLineWidth(0)
grf1.Draw("f")

#expected, mu->e+gamma, mu->3e, mu->e
inDirectLim = [(1.5e-6)**2, (3.1e-5)**2, (4.6e-5)**2, YLimitExpect[2]]
colors = [r.kPink+1, r.kBlue, r.kWhite, r.kRed+1]
Limits, lines = [], []
for lim, color in zip(inDirectLim, colors):
  Limits.append(r.TF1("","sqrt([0]-x*x)",ymin,math.sqrt(lim)))
  Limits[-1].SetParameter(0,lim)
  lineyy = list(np.arange(ymin, math.sqrt(lim)/2, 1e-7))
  linexx = [Limits[-1].Eval(i) for i in lineyy]
  firstHalf = len(linexx)
  linexx += list(np.arange(ymin, linexx[-1], 1e-8))
  lineyy += [Limits[-1].Eval(i) for i in linexx[firstHalf:]]
  lineyy = [i for _, i in sorted(zip(linexx, lineyy))]
  linexx.sort()
  lineyy = array('f', lineyy)
  linexx = array('f', linexx)
  lines.append(r.TGraph(len(linexx), linexx, lineyy))
  lines[-1].SetLineColor(color)
  lines[-1].SetLineWidth(3)

yf =  [ Limits[0].Eval(xf[i]) for i in range(npf)]
yf += [ ymin for i in range(npf)]
yf.append(yf[0])
yf = array('f', yf)
grf4 = r.TGraph(2*npf+1,xf,yf)
grf4.SetFillColor(r.kWhite)
grf4.Draw("lf")

yf =  [ ymax for i in range(npf)]
yf += [ExpectedPlusTwoSigmaLimitCombined.Eval(xf[npf+i]) for i in range(npf)]
yf.append(yf[0])
yf = array('f', yf)
grf3 = r.TGraph(2*npf+1,xf,yf)
grf3.SetFillColor(r.kGreen+4)
grf3.Draw("lf")

grfl = []
color_gr = [r.kCyan-9, r.kCyan, r.kCyan+2]
for k in range(3):
  yf =  [ Limits[k].Eval(xf[i]) for i in range(npf)]
  if k!=2:
    yf += [ Limits[k+1].Eval(xf[npf+i]) for i in range(npf)]
  else:
    yf += [ ExpectedMinusTwoSigmaLimitCombined.Eval(xf[npf+i]) for i in range(npf)]
  yf.append(yf[0])
  yf = array('f', yf)
  grfl.append(r.TGraph(2*npf+1,xf,yf))
  grfl[-1].SetFillColor(color_gr[k])
  grfl[-1].Draw("lf")

for lts in Limits:
  lts.Draw("same")
for le in lines:
  le.Draw("same")

GuideLim = [ComputeSumYLimit(j) for j in [1e-5, 1e-6, 1e-7, 1e-8]]
GuideLimits = []
for lim in GuideLim:
  GuideLimits.append(r.TF1("","sqrt([0]-x*x)",ymin,math.sqrt(lim)))
  GuideLimits[-1].SetParameter(0,lim)
  lineyy = list(np.arange(ymin, math.sqrt(lim)/2, 1e-8))
  linexx = [GuideLimits[-1].Eval(i) for i in lineyy]
  firstHalf = len(linexx)
  linexx += list(np.arange(ymin, linexx[-1], 1e-8))
  lineyy += [GuideLimits[-1].Eval(i) for i in linexx[firstHalf:]]
  lineyy = [i for _, i in sorted(zip(linexx, lineyy))]
  linexx.sort()
  lineyy = array('f', lineyy)
  linexx = array('f', linexx)
  lines.append(r.TGraph(len(linexx), linexx, lineyy))
  lines[-1].SetLineColor(r.kBlue+4)
  lines[-1].SetLineWidth(1)
  lines[-1].SetLineStyle(3)
  lines[-1].Draw('same')  

#naturalness
naturalnessLimit= 0.1057*(0.511/1000)/(246**2)
naturalness = r.TF1("dipole","[0]/x",ymin,ymax)
naturalness.SetParameter(0,naturalnessLimit)
naturalness.SetLineWidth(2)
naturalness.SetNpx(500)
naturalness.SetParName(0,"YLimit")
naturalness.SetLineColor(r.kMagenta+2) #naturalness->SetLineStyle(kDashed);
naturalness.Draw("same")

tt = []
for lim, label in zip(GuideLim, ['10^{-5}', '10^{-6}', '10^{-7}', '10^{-8}']):
  tt.append(r.TLatex(math.sqrt(lim)/1.4,3*ymin,"B<"+label))
  tt[-1].SetTextAlign(11)
  tt[-1].SetTextSize(0.027)
  tt[-1].SetTextColor(r.kBlue+4)
  tt[-1].SetTextAngle(-90)
  tt[-1].Draw()

labels = ['#mu#rightarrow e#gamma', '#mu#rightarrow 3e', '#mu#rightarrow e conv.', 'expected H#rightarrow e#mu']
for i in range(len(inDirectLim)):
  tt.append(r.TLatex(ymin*1.2,1.1*math.sqrt(inDirectLim[i]),labels[i]))
  tt[-1].SetTextAlign(11)
  tt[-1].SetTextSize(0.03)
  tt[-1].SetTextColor(colors[i])
  tt[-1].Draw()

tt.append(r.TLatex(1.8e-5,1e-4,"|Y_{e #mu}Y_{#mu e}|=m_{e}m_{#mu}/v^{2}"))
tt[-1].SetTextAlign(11)
tt[-1].SetTextSize(0.03)
tt[-1].SetTextColor(r.kMagenta+2)
tt[-1].SetTextAngle(-45)
tt[-1].Draw()


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

PLOTLIMIT.RedrawAxis()
PLOTLIMIT.SaveAs('yukawa_EMu.pdf')
