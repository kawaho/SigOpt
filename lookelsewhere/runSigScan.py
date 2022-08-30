import os
import time

masspts = [110., 120., 125., 130., 140., 150., 160.]
cats = ['ggHcat0', 'ggHcat1', 'ggHcat2', 'ggHcat3', 'VBFcat0', 'VBFcat1']

def run(cmd):
  print "%s\n\n"%cmd
  os.system(cmd)

def findclosestMass(i):
  nearMass, Massdiff = -1, 999
  for mp in masspts:
    if abs(i-mp) < Massdiff:
      nearMass=mp
      Massdiff=abs(i-mp)
    else:
      return nearMass
  return nearMass

def makeCards():
  for mp in masspts:
    combineCommand = 'combineCards.py '
    for cat in cats:
      combineCommand += cat+'=../Datacards/datacard_%s_%i.txt '%(cat,mp)
    combineCommand += '> ../Datacards/datacard_comb_%i.txt'%(mp)
    run(combineCommand)

import argparse
parser = argparse.ArgumentParser(description='Convert coffea output to csv files')
parser.add_argument('-t', '--runToys', action='store_true', help='do scan for toys')
args = parser.parse_args()

if __name__=='__main__':
#  if not args.runToys: makeCards()
  for i in [155]:#range(155, 161):
    closestMass = findclosestMass(i) 
    if args.runToys:
      for nt in range(1,101):
        command = 'combineTool.py --job-mode condor --sub-opts=\'+JobFlavour=\"longlunch\"\' --task-name _mass%iToy%i -M Significance -m %i ../Datacards/datacard_comb_%i.root --freezeParameters MH --setParameters MH=%i --toysFile higgsCombine_b_toy%i.GenerateOnly.mH146.%i.root -t %i -n mass%iToy%i &'%(i,nt,i,closestMass,i,nt,nt,1000,i,nt)
        run(command)
        if nt%5==0: time.sleep(10)
    else:
      command = 'combine -M Significance -m %i ../Datacards/datacard_comb_%i.root --freezeParameters MH --setParameters MH=%i &'%(i,closestMass,i)
      run(command)
