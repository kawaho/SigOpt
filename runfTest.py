import ROOT
import pandas as pd
from fTest import *
import argparse
#from finCat import *
ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser(
    "Final Categories for LFV H analysis")
parser.add_argument(
    "--mass", 
    type=str, 
    default='125')

args = parser.parse_args()
df = pd.DataFrame()

range_ =  { 
  'ggH': [1, 52, 78, 90, 101],
  'VBF': [64, 89, 94, 101]
}

  
for m in args.mass.split(','):
  file_gg_full = {
    'ggH': ROOT.TFile('inputs/GG_GGcat_'+m+'.root'),
    'VBF': ROOT.TFile('inputs/GG_VBFcat_'+m+'.root')
  }
  
  file_vbf_full = {
    'ggH': ROOT.TFile('inputs/VBF_GGcat_'+m+'.root'),
    'VBF': ROOT.TFile('inputs/VBF_VBFcat_'+m+'.root')
  }
  for vbf_gg in ['ggH', 'VBF']:
    catnames = []
    bins = []
    for i in range(len(range_[vbf_gg])-1):
      rangl, rangh = range_[vbf_gg][i], range_[vbf_gg][i+1]
      catnames.append('%scat%i'%(vbf_gg,i))
      bins.append([rangl, rangh])
      for subproc in ['ggH', 'qqH']:
        forder, preNll, thisNll, chi2 = fTest(file_gg_full[vbf_gg].Get("CMS_emu_workspace"), file_vbf_full[vbf_gg].Get("CMS_emu_workspace"), catnames[-1]+'_'+m, subproc, int(m), [rangl, rangh], bin_=True)
        df = df.append({'proc': subproc, 'mass': int(m), 'cat': catnames[-1], 'order': forder, 'preNll':preNll, 'thisNll':thisNll, 'chi2':chi2}, ignore_index = True)
df.to_csv('gaus_ftest_result.csv',index=False)
print(df.to_string())
