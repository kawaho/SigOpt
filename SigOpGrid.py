import os, time, sys, glob, math, array, argparse
from ROOT import TFile
from writedatacard import writedatacard
from fitSB_CBE import fit, GetNBkg 
import numpy as np
import pandas as pd
import random as rd
import itertools
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
    default="bern1",
    help="Which bkg model")
parser.add_argument(
    "--cat",
    action="store",
    dest="cat",
    default="VBFcat",
    help="Which category")
parser.add_argument(
    "--expectedSig",
    action="store",
    dest="exSig",
    default=0.0059,
    help="Expected Signal Strength")
parser.add_argument(
    "--step",
    action="store",
    dest="step",
    default=5,
    type=int,
    help="Step size of grid")
parser.add_argument(
    "--itr",
    action="store",
    dest="itr",
    default=500,
    help="Number of Iterations")
parser.add_argument(
    "--ncat",
    action="store",
    dest="ncat",
    default=4,
    help="Number of Categories")

args = parser.parse_args()

#Open a log file
fResults = open('ScanResult_'+args.bkg+'_'+str(args.exSig)+'_'+str(args.cat)+'_grid.txt', 'w')

#make a list of steps to scan
stepList = list(range(0, 100, args.step))[1:]
completestepList = [1] + stepList + [101]
rd.seed(123)

def runCMD(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

def GenListBkg(ncat):
  nbkgList = GetNBkg(file_data_full, completestepList)
  possibleList = list(itertools.combinations(stepList, ncat))
  possibleBkg = []
  for l in possibleList:
    shortList = [ sum(nbkgList[ : stepList.index(l[0]) + 1]) ]
    for i in range(len(l)-1):
      shortList+= [ sum(nbkgList[ stepList.index(l[i]) + 1: stepList.index(l[i+1]) + 1])]
    shortList.append( sum(nbkgList[ stepList.index(l[-1]) + 1 : ]) )
    possibleBkg.append(shortList)
  tosave = []
  #for p in possibleBkg:
  #  if not all(elem > 10 for elem in p):
  #    print('fail', p, possibleList[possibleBkg.index(p)])
  for p in possibleBkg:
    if all(elem > 10 for elem in p):
      tosave.append(possibleBkg.index(p))
  possibleList = [[1]+list(i)+[101] for j, i in enumerate(possibleList) if j in tosave]
  possibleList = rd.sample(possibleList, len(possibleList))
  return possibleList[:min(len(possibleList), args.itr)]

def GenList(ncat, cutList = [], itr=args.itr):
  #create a big list of boundaries to run fit on
  while len(cutList) < itr:
    replicate = False
    newList = [1]
    newList+=rd.sample(stepList, len(stepList))[:ncat]
    for _list in cutList:
      if set(_list) == set(newList):
        replicate = True
        continue
    if not replicate: 
      newList.append(101)
      cutList.append(sorted(newList))
  return cutList
 
#read the csv files to pd for quick systematics calculations as well as root files where ws for signal/data is saved
df_gg_full, df_vbf_full = pd.read_csv('inputs/GG_%s.csv'%(args.cat), index_col='quantiles'), pd.read_csv('inputs/VBF_%s.csv'%(args.cat), index_col='quantiles')
file_gg_full, file_vbf_full = TFile('inputs/GG_%s.root'%(args.cat)).Get("CMS_emu_workspace"), TFile('inputs/VBF_%s.root'%(args.cat)).Get("CMS_emu_workspace")
file_data_full = TFile('inputs/%s.root'%(args.cat)).Get("CMS_emu_workspace")

#cats = [1, 40, 50, 100] so 1st cat is from 1 to 40, 2nd cat is 40 to 50...etc
#i is which percentile you scanning
def SigScan(nargs):
  catname = []
  combinestr = ''
  fitstatus = 0
  cats, whichList = nargs[0], nargs[1]
  ranges = [[cats[i],cats[i+1]] for i in range(len(cats)-1)]
  fResults.write(str(ranges)+'\n')
  for c in range(len(cats)-1):
    fitstatus, numofeventb, numofevent = fit(file_data_full, file_gg_full, file_vbf_full, args.bkg, ranges[c], '%s%i_%i'%(args.cat,c,whichList))#, False, True, False)
    if numofeventb == -1:
      return [-999,-999,-999,-999]
    catname.append('%s%i_%i'%(args.cat,c,whichList))
    combinestr += 'Name%i=Datacards/datacard_%s%i_%i.txt '%(c+1,args.cat,c,whichList)
  writedatacard(catname, ranges, df_gg_full, df_vbf_full, sys_=True)
### Atlas Limit: 6.2*10^{-5} (5.9*10^{-5}).
  runCMD("combineCards.py " + combinestr + "> Datacards/datacard_comb_%i.txt"%whichList)
  lim = 0.6
  if args.limit:
    runCMD("combine -M AsymptoticLimits -m 125 Datacards/datacard_comb_%i.txt --run blind --name %i"%(whichList,whichList))
    input_ = TFile("higgsCombine%i.AsymptoticLimits.mH125.root"%whichList)
    limitTree = input_.Get("limit")
    limitTree.GetEntry(2)
    lim = limitTree.limit*100
  runCMD("combine -M Significance Datacards/datacard_comb_%i.txt -m 125 -t -1 --expectSignal=%s --name %i"%(whichList,str(args.exSig),whichList))
  input_ = TFile("higgsCombine%i.Significance.mH125.root"%whichList)
  limitTree = input_.Get("limit")
  limitTree.GetEntry(0)
  sig = limitTree.limit
  return [sig,lim,numofeventb,numofevent] 

premax = 0
gain=100
n = 1
while gain>1:
  if n==1:
    BList = [[1,i,101] for i in stepList]
  else:
    BList = GenListBkg(n) #GenList(n)
    print(BList)
    print(len(BList))
  #For loop
  #for j in range(len(BList)):
  #  fResults.write(str(SigScan([BList[j],j])))
 
  #Concurrent
  pool = Pool(64)#processes=cpu_count())
  Comb = pool.map(SigScan, [[BList[j],j] for j in range(len(BList))]) 

#  if n!=1:
#    nfail = 0
#    for c in Comb:
#      if -999 in c: 
#        nfail+=1
#    maxAttempt = 0
#    while nfail > 0 and maxAttempt < 100:
#      maxAttempt += 1 
#      preLen = len(BList)
#      BList = GenList(n, BList, itr=len(BList)+nfail)
#      print(BList)
#      #Concurrent
#      pool = Pool(64)#processes=cpu_count())
#      Comb += pool.map(SigScan, [[BList[j],j] for j in range(preLen, len(BList))]) 
#      nfail = 0
#      for c in Comb[preLen:]:
#        if -999 in c: nfail+=1

  signi = [i[0] for i in Comb]
  
  fResults.write("ncats "+str(n+1)+'\n')
  fResults.write("Blist "+str(BList)+'\n')
  fResults.write("Comb "+str(Comb)+'\n')
  fResults.write("Max Sig "+str(max(signi))+'\n')
  fResults.write("Max Sig Cuts "+str(BList[signi.index(max(signi))])+'\n')
  if premax!=0:
    gain = (max(signi)-premax)*100/premax 
    fResults.write("Gain "+str( gain )+'\n')

  premax = max(signi)
  n+=1

fResults.write("done")
runCMD('source clean.sh')
