import os

masspts = [120., 125., 130.]
cats = ['ggcat0', 'ggcat1', 'ggcat2', 'ggcat3', 'vbfcat0', 'vbfcat1']

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

for mp in masspts:
  combineCommand = 'combineCards.py '
  for cat in cats:
    combineCommand += '../Datacards/datacard_%s_%i.txt '%(cat,mp)
  combineCommand += '> ../Datacards/datacard_comb_%i.txt'%(mp)
  run(combineCommand)

for i in range(120, 131):
  closestMass = findclosestMass(i) 
  #command = 'combine -M AsymptoticLimits -m %i ../Datacards/datacard_comb_%i.txt --freezeParameters MH --setParameters MH=%i'%(i,closestMass,i)
  command = 'combine -M AsymptoticLimits -m %i ../Datacards/datacard_comb_%i.txt --freezeParameters MH --setParameters MH=%i'%(i,closestMass,i)
  run(command)
