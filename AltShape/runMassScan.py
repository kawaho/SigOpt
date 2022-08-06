import os
#allConstrainedNuisances
masspts = [125]#[120., 125., 130.]
cats = ['ggcat0', 'ggcat1', 'ggcat2', 'ggcat3', 'vbfcat0', 'vbfcat1']

def run(cmd):
  print "%s\n\n"%cmd
#  os.system(cmd)

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
  combineCommand_gaus = 'combineCards.py '
  combineCommand = 'combineCards.py '
  for cat in cats:
    for gaus in range(2):#,2):
      if gaus:
        replacewithgaus = 'sed -e \"s/workspace\(.*\).root/workspace\\1_125_gaus\.root/g\" -e \"s/w_13TeV:\(.*\)_\(.*\)_pdf/w_13TeV:\\1_125_\\2_pdf/g\" ../Datacards/datacard_%s_%i.txt > ../Datacards/datacard_%s_%i_gaus.txt'%(cat,mp,cat,mp)
#        run(replacewithgaus)
        combineCommand_gaus += '../Datacards/datacard_%s_%i_gaus.txt '%(cat,mp)
    	singleCat = 'combine -M AsymptoticLimits -m 125 ../Datacards/datacard_%s_125_gaus.txt -n %s_gaus'%(cat,cat)
  
      else:
    	singleCat = 'combine -M AsymptoticLimits -m 125 ../Datacards/datacard_%s_125.txt --freezeParameters MH --setParameters MH=125 -n %s'%(cat,cat)
        combineCommand += '../Datacards/datacard_%s_%i.txt '%(cat,mp)
  
      if mp ==125:
        run(singleCat)

  combineCommand_gaus += '> ../Datacards/datacard_comb_%i_gaus.txt'%(mp)
  combineCommand += '> ../Datacards/datacard_comb_%i.txt'%(mp)
#  run(combineCommand)
#  run(combineCommand_gaus)
  for i in [125]:#range(120, 131):
    closestMass = findclosestMass(i) 
    command = 'combine -M AsymptoticLimits -m %i ../Datacards/datacard_comb_%i.txt --freezeParameters MH  --setParameters MH=%i'%(i,closestMass,i)
    command_gaus = 'combine -M AsymptoticLimits -m %i ../Datacards/datacard_comb_%i_gaus.txt'%(i,i)
    run(command)
    run(command_gaus)
