import os, time, sys, glob, math, array, argparse
from ROOT import TLatex, gROOT, gPad, TFile, TH1F, TH2F, TGraph, TCanvas, TLine, gPad, TMultiGraph, TPaveText
from writedatacard import writedatacard
from fitSB_CBE import fit
import numpy as np
import pandas as pd
import random as rd
from multiprocessing import Pool, cpu_count
parser = argparse.ArgumentParser(
    "Optimizer for LFV H analysis")
parser.add_argument(
    "--limit",
    action='store_true'
    )
parser.add_argument(
    "--bkg",
    action="store",
    dest="bkg",
    default="bern3",
    help="Which bkg model")
parser.add_argument(
    "--cat",
    action="store",
    dest="cat",
    default="gg",
    help="Which category")
parser.add_argument(
    "--expectedSig",
    action="store",
    dest="exSig",
    default=0.59,
    help="Expected Signal Strength")

args = parser.parse_args()

gROOT.SetBatch(True)
can = TCanvas("can","",0,0,800,800)
can2 = TCanvas("can2","",0,0,800,800)
def add_lumi():
    lowX=0.65
    lowY=0.82
    lumi  = TPaveText(lowX, lowY, lowX+0.30, lowY+0.2, "NDC")
    lumi.SetBorderSize(   0 )
    lumi.SetFillStyle(    0 )
    lumi.SetTextAlign(   12 )
    lumi.SetTextColor(    1 )
    lumi.SetTextSize(0.038)
    lumi.SetTextFont (   42 )
    lumi.AddText("138 fb^{-1} (13 TeV)")
    return lumi

def add_CMS():
    lowX=0.16
    lowY=0.82
    lumi  = TPaveText(lowX, lowY+0.06, lowX+0.15, lowY+0.16, "NDC")
    lumi.SetTextFont(61)
    lumi.SetTextSize(0.055)
    lumi.SetBorderSize(   0 )
    lumi.SetFillStyle(    0 )
    lumi.SetTextAlign(   12 )
    lumi.SetTextColor(    1 )
    lumi.AddText("CMS")
    return lumi

def add_Preliminary():
    lowX=0.28
    lowY=0.82
    lumi  = TPaveText(lowX, lowY+0.05, lowX+0.15, lowY+0.15, "NDC")
    lumi.SetTextFont(52)
    lumi.SetTextSize(0.055*0.8*0.76)
    lumi.SetBorderSize(   0 )
    lumi.SetFillStyle(    0 )
    lumi.SetTextAlign(   12 )
    lumi.SetTextColor(    1 )
    lumi.AddText("Preliminary")
    return lumi

def runCMD(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

def checkBkg(lis_):
  pass_ = True
  for i in lis_:
    if i < 10*hmvaS2D[0].GetNbinsY(): pass_ = False
  return pass_

def PlotSig(Multigr, Sigx, Sigy, canvas, lim=False):
   gPad.SetFillColor(0)
   gPad.SetBorderMode(0)
   gPad.SetBorderSize(10)
   gPad.SetTickx(1)
   gPad.SetTicky(1)
   gPad.SetFrameFillStyle(0)
   gPad.SetFrameLineStyle(0)
   gPad.SetFrameLineWidth(3)
   gPad.SetFrameBorderMode(0)
   gPad.SetFrameBorderSize(10)
   gr = TGraph(len(Sigx), Sigx, Sigy)
   gr.GetXaxis().SetTitle("BDT Discriminant")
   if lim:
     gr.GetYaxis().SetTitle("95% CL Expected Limit, 10^{-4}")
   else:
     gr.GetYaxis().SetTitle("Expected Significance (#sigma)")
   gr.GetXaxis().SetLimits(0, 1)
   gr.GetXaxis().SetTitleFont(42)
   gr.GetYaxis().SetTitleFont(42)
   gr.GetXaxis().SetTitleSize(0.05)
   gr.GetYaxis().SetTitleSize(0.05)
   gr.GetXaxis().SetLabelSize(0.045)
   gr.GetYaxis().SetLabelSize(0.045)
   gr.GetYaxis().SetTitleOffset(1.60)
#  gr.GetYaxis().SetNdivisions(7)
   canvas.SetLeftMargin(0.16)
   canvas.SetRightMargin(0.05)
   canvas.SetBottomMargin(0.13)
   gr.SetTitle("")
#   gr.GetYaxis().SetRangeUser(np.max(Sigy)-20,  np.max(Sigy)+5)
#  gr.SetMarkerSize(5)
   gr.SetMarkerStyle(8)
   Multigr.Add(gr, 'ap')
   return gr.GetYaxis().GetXmax()

def PlotCat(Multigr, catsSig, ymax_):
  for cat in catsSig:
    line = TGraph(2)
    line.SetPoint(0, cat/100., 0)
    line.SetPoint(1, cat/100., ymax_)
    Multigr.Add(line, 'l')
    line.SetLineWidth(3)

def PlotMax(Multigr, maxSigI, ymax_):
  line = TGraph(2)
  line.SetPoint(0, maxSigI, 0)
  line.SetPoint(1, maxSigI, ymax_)
  line.SetLineColor(2)
  line.SetLineWidth(3)
  Multigr.Add(line, 'l')

def DrawNSave(Multigr, ncats, canvas, lim=False):
  canvas.cd()
  Multigr.Draw()
  l1 = add_lumi()
  l1.Draw("same")
  l2 = add_CMS()
  l2.Draw("same")
  l3 = add_Preliminary()
  l3.Draw("same")
  if lim:
    canvas.SaveAs('Graphs/' + args.bkg + '_' + str(ncats) + '_' + str(args.exSig) + '_' + args.cat + '_limit_check.png')
  else:
    canvas.SaveAs('Graphs/' + args.bkg + '_' + str(ncats) + '_' + str(args.exSig) + '_' + args.cat + '_check.png')

class hitCat(Exception): pass

def BoundaryScan(screen, cats):
  for i in range(len(cats)-1):
    if screen > cats[i] and screen < cats[i+1]:
      return i
  raise hitCat() 

def Initialize(lis_):
  for  i in range(len(lis_)):
    lis_[i] = 0

run = True
#run = 1
cats = [1,101]
catsSig = []
catdiff = []
ranges = [[], []]
maxCombprev = 0.000001
maxComb = 0
minLim = 0
maxI = [-1,-1,-1]
maxSigI = -1
fResults = open('ScanResult_'+args.bkg+'_'+str(args.exSig)+'_'+str(args.cat)+'_corrected_check_sys.txt', 'w')

#read the csv files to pd for quick systematics calculations as well as root files where ws for signal/data is saved
if args.cat=='gg':
  df_gg_full, df_vbf_full = pd.read_csv('inputs/GG_GGcat_125.csv', index_col='quantiles'), pd.read_csv('inputs/VBF_GGcat_125.csv', index_col='quantiles')
  file_gg_full, file_vbf_full = TFile('inputs/GG_GGcat_125.root').Get("CMS_emu_workspace"), TFile('inputs/VBF_GGcat_125.root').Get("CMS_emu_workspace")
  file_data_full = TFile('inputs/GGcat.root').Get("CMS_emu_workspace")
else:
  df_gg_full, df_vbf_full = pd.read_csv('inputs/GG_VBFcat_125.csv', index_col='quantiles'), pd.read_csv('inputs/VBF_VBFcat_125.csv', index_col='quantiles')
  file_gg_full, file_vbf_full = TFile('inputs/GG_VBFcat_125.root').Get("CMS_emu_workspace"), TFile('inputs/VBF_VBFcat_125.root').Get("CMS_emu_workspace")
  file_data_full = TFile('inputs/VBFcat.root').Get("CMS_emu_workspace")
#cats = [1, 40, 50, 100] so 1st cat is from 1 to 40, 2nd cat is 40 to 50...etc
#i is which percentile you scanning
#if i hit a boundry, raise exception 
def SigScan(i):
  try:
    if i in cats:  raise hitCat()
    inBetween = BoundaryScan(i, cats) 
    #Define boundaries for new scans
    for c in range(len(cats)):
      if c==inBetween:
        ranges[c] = [cats[c], i]
      elif c==inBetween+1:
        ranges[c] = [i, cats[c]]
      elif c>inBetween:
        ranges[c] = [cats[c-1], cats[c]]
      else:
        ranges[c] = [cats[c], cats[c+1]]
  except hitCat:
    return -1

  #return [rd.randint(1, 500)/100., 0,0,0]
  catname = []
  combinestr = ''
  fitstatus = 0

  for c in range(len(cats)):
    fitstatus, numofeventb, numofevent = fit(file_data_full, file_gg_full, file_vbf_full, args.bkg, ranges[c], '%scat%i_%i'%(args.cat,c,i))#, makePlot=True)
    if numofeventb == -1:
      return -1
    catname.append('%scat%i_%i'%(args.cat,c,i))
    combinestr += 'Name%i=Datacards/datacard_%scat%i_%i.txt '%(c+1,args.cat,c,i)
  writedatacard(catname, ranges, df_gg_full, df_vbf_full, sys_=True)
#  if fitstatus != 0:
#    return -1

### Atlas Limit: 6.2*10^{-5} (5.9*10^{-5}).
  runCMD("combineCards.py " + combinestr + "> Datacards/datacard_comb_%i.txt"%i)
  lim = 0.6
  if args.limit:
    runCMD("combine -M AsymptoticLimits -m 125 Datacards/datacard_comb_%i.txt --run blind --name %i"%(i,i))
    input_ = TFile("higgsCombine%i.AsymptoticLimits.mH125.root"%i)
    limitTree = input_.Get("limit")
    limitTree.GetEntry(2)
    lim = limitTree.limit*100
  runCMD("combine -M Significance Datacards/datacard_comb_%i.txt -m 125 -t -1 --expectSignal=%s --freezeParameters allConstrainedNuisances --name %i"%(i,str(args.exSig),i))
  input_ = TFile("higgsCombine%i.Significance.mH125.root"%i)
  limitTree = input_.Get("limit")
  limitTree.GetEntry(0)
  sig = limitTree.limit
#  sig = rd.randint(0, 500)
  #return [i,sig,lim] 
  return [sig,lim,numofeventb,numofevent] 
#if True:
#while run < 3:    
while run:    
  ncats = len(catdiff) + 2
  Sigx, Sigy, Limy = array.array('f'), array.array('f'), array.array('f')
  Sigx_plot, Sigy_plot, Limy_plot = array.array('f'), array.array('f'), array.array('f')
  Comb = []
  #Comb= SigScan(88)
  #for k in range(23):
  #  Comb.append(SigScan(k))
  pool = Pool(64)#processes=cpu_count())
  Comb = pool.map(SigScan, range(1,101)) 
  for i in range(len(Comb)): 
    if isinstance(Comb[i], list): #Comb[i]!=-1:
      if Comb[i][0] > 5 or Comb[i][0]==0:
        print('Failing %i'%(i+1))
        print('Bkg %f, Sig %f'%(Comb[i][-2], Comb[i][-1]))
  #      if isinstance(Comb[i-1], list):  
  #        Comb[i][0] = Comb[i-1][0]
  #      if isinstance(Comb[i+1], list):  
  #        Comb[i][0] = Comb[i+1][0]
  #      print('Failing %i'%(i+1))
  #    if Comb[i][0] == 0:
  #      print('Failing %i'%(i+1))
  #print(Comb)
  #for i in range(2,len(Comb)-1): 
  #  if Comb[i][0] > 1.2*Comb[i+1][0]:
  #    Comb[i][0] = 0
  #  if Comb[i][0] > 1.2*Comb[i-1][0]:
  #    Comb[i][0] = 0
  fResults.write("%s\n"%str(Comb))
  for i in range(len(Comb)):
    #if isinstance(Comb[i], list):
    #  if Comb[i][0] == 0:
    #    if isinstance(Comb[i-1], list) and isinstance(Comb[i+1], list):  
    #      Comb[i][0] = (Comb[i-1][0] + Comb[i+1][0])/2
    #    elif isinstance(Comb[i+1], list):  
    #      Comb[i][0] = Comb[i+1][0]
    #    elif isinstance(Comb[i-1], list):  
    #      Comb[i][0] = Comb[i-1][0]
    #if Comb[i] == -1 or Comb[i][0] > 5 or Comb[i][0]==0:  
    #  Sigx.append(i+1)
    #  Sigy.append(0)
    #  Limy.append(100)
    #else:
    if isinstance(Comb[i], list):
      Sigx.append(i+1)
      Sigy.append(Comb[i][0])
      Limy.append(Comb[i][1])
      Sigx_plot.append((i+1)/100.)
      Sigy_plot.append(Comb[i][0])
      Limy_plot.append(Comb[i][1])

  Multigr = TMultiGraph()
  ymax_ = PlotSig(Multigr, Sigx_plot, Sigy_plot, can)
  PlotCat(Multigr, cats[1:-1], ymax_)

  if args.limit:
    Multigr2 = TMultiGraph()
    ymax2_ = PlotSig(Multigr2, Sigx_plot, Limy_plot, can2, True)
    PlotCat(Multigr2, cats[1:-1], ymax2_)

  #maxComb_idx = np.argmax(Sigy)+1
  maxComb_idx = int(Sigx[np.argmax(Sigy)])
  maxComb = np.max(Sigy)

  diff = (maxComb - maxCombprev)/maxCombprev
  if diff > 0.01:
    catdiff.append(diff)
    cats.append(maxComb_idx)
    cats.sort()
    ranges = [[] for i in cats]
    PlotMax(Multigr, maxComb_idx/100., ymax_)
    DrawNSave(Multigr, ncats, can)
    
    if args.limit:
      PlotMax(Multigr2, maxComb_idx, ymax2_)
      DrawNSave(Multigr2, ncats, can2, True)
    maxCombprev = maxComb
    minLim = np.min(Limy)
#    run += 1
    run = True
  else: 
#    run += 1
    run = False
    DrawNSave(Multigr, ncats, can)
    if args.limit:
      DrawNSave(Multigr2, ncats, can2, True)
    fResults.write("Final Cats: %s\n"%str(cats))
    fResults.write("Cat Diff: %s\n"%str(catdiff))
    fResults.write("Final Sig: %f, Lim: %f\n"%(maxCombprev, minLim))
    mvaCuts = []
    for c in cats[1:-1]:
      mvaCuts.append(df_gg_full.loc[c]['lowerMVA'])
    fResults.write("MVA Cuts: %s\n"%str(mvaCuts))

    print "Final Cats ", cats
    print "Final Cats on Paper", [100-(i+1) for i in cats]
    print "Cat Diff ", catdiff
    print "MVA Cuts ", mvaCuts
    print "Final Sig: ", maxCombprev, " Lim: ", minLim

fResults.close()
