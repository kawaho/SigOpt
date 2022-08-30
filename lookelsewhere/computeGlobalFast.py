import ROOT as r
import math
import numpy as np
import scipy.stats as st

def p2Sig(p):
  Z = st.norm.ppf(p)
  if p==1 or Z<0: return 0
  return Z

def getBonlyNLL(tree):
  for t in b_tree:
    nll = t.nll
    nll0 = t.nll0
  return nll+nll0

def getSBNLL(tree, nll_b):
  MH_list, sig_list = [], []
  for t in tree:
    MH_list.append(t.MH)
    rel_nll = t.nll+t.nll0+t.deltaNLL - nll_b
    if rel_nll > 0: rel_nll = 0
    sig_list.append(math.sqrt(2*math.fabs(rel_nll)))
  return MH_list, sig_list

sig = []
for i in range(110, 161):
  sig_file = r.TFile("higgsCombineTest.Significance.mH%i.root"%(i))
  sig_tree = sig_file.Get("limit")
  for t in sig_tree: sig.append(t.limit)

nToys = 100*1000
maxSig = [-999]*(nToys)
maxSig.append(-999)
for i in range(110, 161):
  sig_file_toy = r.TFile("higgsCombinemass%icToy.Significance.mH%i.123456.root"%(i,i))
  sig_tree_toy = sig_file_toy.Get("limit")
  for wt, t in enumerate(sig_tree_toy):
    if maxSig[wt] < t.limit: maxSig[wt] = t.limit
      
globalP =  np.array([sum([float(maxSig_>i) for maxSig_ in maxSig]) for i in sig])/nToys
print(globalP)
globalZ = [p2Sig(1-i) for i in globalP]
for i,j,k in zip(range(110, 161), globalZ, sig):
  print(i,j,k) 
np.savez('Zvalues.npz', localZ=np.array(sig), globalZ=np.array(globalZ))

